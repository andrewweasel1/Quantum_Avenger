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
