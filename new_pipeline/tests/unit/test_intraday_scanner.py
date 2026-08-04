"""Scanner signal menu, variant ranking, and the IC diagnostic."""

from datetime import date, timedelta

import polars as pl
from new_pipeline.intraday.scanner import (
    SIGNALS,
    VARIANTS,
    apply_floors,
    build_signal_frame,
    scan_day,
    signal_ic,
)

D0 = date(2026, 3, 2)


def _daily(rows):
    return pl.DataFrame(rows, schema=["date", "ticker", "open", "high", "low",
                                      "close", "volume", "dollar_vol"], orient="row")


def _series(ticker, n, dv, close=10.0, open_=10.0, spread=0.02):
    return [(D0 + timedelta(days=i), ticker, open_, close * (1 + spread), close * (1 - spread),
             close, int(dv / close), float(dv)) for i in range(n)]


def _flex_series(ticker, n, dv, close, spread, gap=0.0, vol_mult=1.0):
    """A series whose signal axes can be set independently.

    ``gap`` moves only the FINAL session's open (so gap_abs/gap_up fire there);
    ``vol_mult`` spikes only the PRIOR session's dollar volume (so rvol fires
    without meaningfully moving the 20d median that becomes adv_dollar)."""
    rows = []
    for i in range(n):
        open_ = close * (1.0 + gap) if i == n - 1 else close
        day_dv = dv * vol_mult if i == n - 2 else dv
        rows.append((D0 + timedelta(days=i), ticker, open_,
                     max(close * (1 + spread), open_), close * (1 - spread),
                     close, int(day_dv / close), float(day_dv)))
    return rows


def test_signal_frame_is_causal_and_complete():
    rows = _series("AAA", 30, 10_000_000)
    frame = build_signal_frame(_daily(rows))
    last = frame.filter(pl.col("date") == D0 + timedelta(days=29))
    for signal in SIGNALS:
        assert signal in frame.columns
        assert last[signal][0] is not None, signal
    # causality: perturbing day-T close/volume must not move day-T signals
    bumped = list(rows)
    d, t, o, h, low, c, v, dv = bumped[29]
    bumped[29] = (d, t, o, h * 3, low, c * 3, v * 10, dv * 10)
    frame2 = build_signal_frame(_daily(bumped))
    last2 = frame2.filter(pl.col("date") == D0 + timedelta(days=29))
    for signal in ("rvol", "adv_dollar", "price", "atr_pct", "range_pct", "spread_bps"):
        assert last[signal][0] == last2[signal][0], signal
    # ...but today's OPEN legitimately moves the gap signals
    gapped = list(rows)
    d, t, o, h, low, c, v, dv = gapped[29]
    gapped[29] = (d, t, o * 1.1, h, low, c, v, dv)
    last3 = build_signal_frame(_daily(gapped)).filter(pl.col("date") == D0 + timedelta(days=29))
    assert last3["gap_up"][0] > last["gap_up"][0]


def test_floors_and_variant_ranking_orientation():
    rows = []
    for i in range(8):
        # wider spread + lower ADV as i grows; T0 is the most tradable name
        rows += _series(f"T{i}", 25, dv=10_000_000 / (i + 1), spread=0.005 * (i + 1))
    rows += _series("PENNY", 25, dv=10_000_000, close=1.0, open_=1.0)
    signals = apply_floors(build_signal_frame(_daily(rows)), 1_000_000, 3.0)
    day = D0 + timedelta(days=24)
    picks = scan_day(signals, day, top_n=3, weights="tradable")
    assert "PENNY" not in picks  # price floor
    assert picks[0] == "T0"      # deepest + tightest spread ranks first
    # spread is a LOW-is-better signal: inverting its weight flips the order
    worst = scan_day(signals, day, top_n=3, weights={"spread_bps": -1.0})
    assert worst[0] != "T0" and SIGNALS["spread_bps"] is False
    # every pre-registered variant produces a deterministic, floor-respecting list
    for name in VARIANTS:
        out = scan_day(signals, day, top_n=4, weights=name)
        assert out == scan_day(signals, day, top_n=4, weights=name)
        assert "PENNY" not in out and len(out) <= 4


def test_signal_ic_detects_a_planted_ranking_relationship():
    rows = []
    for i in range(10):
        rows += _series(f"T{i}", 25, dv=(i + 1) * 2_000_000)
    signals = apply_floors(build_signal_frame(_daily(rows)), 1_000_000, 3.0)
    days = [D0 + timedelta(days=k) for k in range(20, 25)]
    # plant it: gross outcome rises with adv_dollar (T9 best) on every session
    ledger = pl.DataFrame({
        "day": [d for d in days for _ in range(10)],
        "ticker": [f"T{i}" for _ in days for i in range(10)],
        "gross_bps": [float(i * 10) for _ in days for i in range(10)],
    })
    ic = signal_ic(ledger, signals, outcome="gross_bps")
    assert ic["adv_dollar"]["mean_ic"] > 0.9  # near-perfect rank agreement
    assert ic["adv_dollar"]["hit_rate"] == 1.0
    assert ic["adv_dollar"]["n_sessions"] == len(days)
    # a signal with no planted relationship must not claim a strong IC
    assert abs(ic.get("ret_5d", {"mean_ic": 0.0})["mean_ic"]) < 0.9


def test_signal_ic_skips_thin_cross_sections():
    rows = _series("AAA", 25, 10_000_000) + _series("BBB", 25, 10_000_000)
    signals = apply_floors(build_signal_frame(_daily(rows)), 1_000_000, 3.0)
    ledger = pl.DataFrame({"day": [D0 + timedelta(days=24)] * 2,
                           "ticker": ["AAA", "BBB"], "gross_bps": [10.0, -10.0]})
    assert signal_ic(ledger, signals, min_names=5) == {}  # 2 names -> no IC


def test_union_ranks_consensus_ahead_of_a_higher_scoring_solo_pick():
    """Agreement leads because it earns it: on meanrev_v4's z2.5 trades,
    2-3 scanner consensus netted 38.6/34.0 bps against 17.2 for solo picks.
    A name every member selects therefore outranks one that only a single
    member likes, even when that solo name carries the higher blended score."""
    from new_pipeline.intraday.scanner import UNION_MEMBERS, scan_day_union, score_day

    rows = []
    for i in range(12):
        rows += _series(f"T{i}", 25, dv=(i + 1) * 2_000_000, spread=0.002 * (12 - i))
    signals = apply_floors(build_signal_frame(_daily(rows)), 1_000_000, 3.0)
    day = D0 + timedelta(days=24)
    # each member's own top-3, and the union's top-3 over the same pool
    per_member = {m: scan_day(signals, day, 3, weights=m) for m in UNION_MEMBERS}
    union = scan_day_union(signals, day, top_n=3, per_member_n=3)
    agreement = {t: sum(t in sel for sel in per_member.values()) for t in union}
    # the union never puts a lower-agreement name above a higher-agreement one
    counts = [agreement[t] for t in union]
    assert counts == sorted(counts, reverse=True)
    # consensus names (in every member's list) all make the cut
    consensus = set.intersection(*(set(v) for v in per_member.values()))
    assert consensus <= set(union)
    # deterministic
    assert union == scan_day_union(signals, day, top_n=3, per_member_n=3)
    # blended score orders WITHIN an agreement tier
    scores = {m: dict(score_day(signals, day, m).iter_rows()) for m in UNION_MEMBERS}
    blended = {t: sum(s.get(t, 0.0) for s in scores.values()) / 3 for t in union}
    for tier in (3, 2, 1):
        same = [t for t in union if agreement[t] == tier]
        assert [blended[t] for t in same] == sorted((blended[t] for t in same), reverse=True)


def test_union_widens_coverage_beyond_any_single_scanner():
    """The point of the union: more distinct qualifying names than the best
    single weighting, since event count is the binding constraint.

    The fixture decouples the signal axes the way a real cross-section does —
    ADV, spread, gap, volume-spike and price ranks are five DIFFERENT
    permutations of the same 30 names (multipliers coprime to 30). Without
    that, one latent liquidity factor drives every signal and all three
    weightings collapse onto the same ordering, which is not the regime the
    union exists to exploit."""
    from new_pipeline.intraday.scanner import UNION_MEMBERS, scan_day_union

    rows = []
    for i in range(30):
        rows += _flex_series(
            f"T{i:02d}", 25,
            dv=(i + 1) * 1_000_000,                   # adv rank:    i
            spread=0.001 * (30 - (7 * i) % 30),       # spread rank: 7i mod 30
            gap=0.002 * ((11 * i) % 30),              # gap rank:    11i mod 30
            vol_mult=1.0 + 0.2 * ((13 * i) % 30),     # rvol rank:   13i mod 30
            close=5.0 + (17 * i) % 30,                # price rank:  17i mod 30
        )
    signals = apply_floors(build_signal_frame(_daily(rows)), 500_000, 3.0)
    day = D0 + timedelta(days=24)
    union = set(scan_day_union(signals, day, top_n=20, per_member_n=10))
    singles = {m: set(scan_day(signals, day, 10, weights=m)) for m in UNION_MEMBERS}
    pool = set().union(*singles.values())
    # the members genuinely disagree here, so the pool exceeds any one list
    assert len(pool) > max(len(s) for s in singles.values()) == 10
    # the union covers more names than the best single scanner, and every name
    # it takes was selected by at least one member (it invents nothing)
    assert len(union) > max(len(s) for s in singles.values())
    assert union <= pool
    # and it reaches beyond each individual member's own picks
    assert all(union - singles[m] for m in UNION_MEMBERS)


def test_union_is_reachable_through_the_standard_scan_entry_point():
    from new_pipeline.intraday.scanner import UNION_VARIANT, scan_day_union

    rows = []
    for i in range(8):
        rows += _series(f"T{i}", 25, dv=(i + 1) * 2_000_000)
    signals = apply_floors(build_signal_frame(_daily(rows)), 1_000_000, 3.0)
    day = D0 + timedelta(days=24)
    assert (scan_day(signals, day, 5, weights=UNION_VARIANT)
            == scan_day_union(signals, day, 5))
