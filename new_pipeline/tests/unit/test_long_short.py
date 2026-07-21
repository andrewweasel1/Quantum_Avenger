"""Long-short book construction: weights, costs, thin dates, permutation null."""

from datetime import date

import numpy as np
import polars as pl
from new_pipeline.tournament.long_short import (
    build_long_short_book,
    permutation_null_margin,
    sector_neutral_scores,
)

D1, D2, D3 = date(2021, 1, 4), date(2021, 1, 5), date(2021, 1, 6)


def _panel(rows):
    return pl.DataFrame(
        rows, schema=["date", "ticker", "sector", "score", "next_ret"], orient="row"
    )


def test_book_weights_are_dollar_neutral_and_unit_gross():
    # 4 names, quantile 0.25 -> k=1: +1/2 top, -1/2 bottom.
    panel = _panel([
        (D1, "A", "X", 4.0, 0.02),
        (D1, "B", "X", 3.0, 0.01),
        (D1, "C", "X", 2.0, -0.01),
        (D1, "D", "X", 1.0, -0.03),
    ])
    book = build_long_short_book(panel, quantile=0.25, cost_bps=0.0, min_names=4,
                                 sector_neutral=False)
    # gross = 0.5*r_A - 0.5*r_D; weights sum to 0 (dollar-neutral), |w| sums to 1.
    np.testing.assert_allclose(book.gross, [0.5 * 0.02 - 0.5 * (-0.03)])
    np.testing.assert_allclose(book.turnover, [0.5])  # inception: 0.5 * sum|w| = 0.5
    assert book.avg_names_per_leg == 1.0


def test_net_charges_turnover_including_rebalance_and_forced_exit():
    # Day1: long A short D. Day2: same book (zero turnover). Day3: A absent ->
    # forced exit of A (long leg moves to B), D stays short.
    rows = []
    for day, names in [(D1, "ABCD"), (D2, "ABCD"), (D3, "BCD")]:
        scores = {"A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0}
        rows += [(day, t, "X", scores[t], 0.0) for t in names]
    book = build_long_short_book(_panel(rows), quantile=0.25, cost_bps=100.0,
                                 min_names=3, sector_neutral=False)
    # turnover: day1 inception 0.5; day2 0; day3 A: |0-0.5|, B: |0.5-0|, D unchanged -> 0.5
    np.testing.assert_allclose(book.turnover, [0.5, 0.0, 0.5])
    # gross is 0 everywhere (all next_ret 0) so net = -cost: 100bps * turnover
    np.testing.assert_allclose(book.net, [-0.01 * 0.5, 0.0, -0.01 * 0.5])


def test_thin_date_is_flat_and_unwinds():
    rows = [
        (D1, "A", "X", 2.0, 0.05), (D1, "B", "X", 1.0, -0.05),
        (D2, "A", "X", 2.0, 0.05),  # only one name: below min_names -> flat
    ]
    book = build_long_short_book(_panel(rows), quantile=0.5, cost_bps=0.0,
                                 min_names=2, sector_neutral=False)
    assert book.gross[1] == 0.0
    np.testing.assert_allclose(book.turnover[1], 0.5)  # full unwind charged


def test_sector_neutral_scores_zero_on_degenerate_dispersion():
    panel = _panel([
        (D1, "A", "X", 1.0, 0.0), (D1, "B", "X", 1.0, 0.0),  # zero std in X
        (D1, "C", "Y", 2.0, 0.0), (D1, "D", "Y", 1.0, 0.0),
    ])
    out = sector_neutral_scores(panel)
    by = dict(zip(out["ticker"].to_list(), out["score"].to_list(), strict=True))
    assert by["A"] == 0.0 and by["B"] == 0.0  # degenerate sector -> neutral
    assert by["C"] > 0.0 > by["D"]  # real dispersion -> signed z-scores


def test_permutation_null_margin_separates_oracle_from_noise():
    from new_pipeline.core.seeding import seed_everything

    seed_everything(0)
    rng = np.random.default_rng(3)
    rows = []
    day = date(2021, 1, 4)
    from datetime import timedelta

    for d in range(60):
        rets = rng.normal(0.0, 0.01, 20)
        for i in range(20):
            # oracle score == realized next-day return
            rows.append((day + timedelta(days=d), f"T{i:02d}", "X", float(rets[i]),
                         float(rets[i])))
    panel = _panel(rows)
    from new_pipeline.tournament.long_short import build_long_short_book as bb
    from new_pipeline.tournament.simulator import sharpe_ratio

    champ = sharpe_ratio(bb(panel, 0.2, 0.0, 10, False).net)
    margin, nulls = permutation_null_margin(panel, 0.2, 0.0, 10, False, 12, 0.95, champ)
    assert len(nulls) == 12
    assert margin > 0.0  # oracle scores demolish the informationless null

    seed_everything(0)
    noise = panel.with_columns(pl.Series("score", rng.normal(size=panel.height)))
    noise_champ = sharpe_ratio(bb(noise, 0.2, 0.0, 10, False).net)
    noise_margin, _ = permutation_null_margin(noise, 0.2, 0.0, 10, False, 12, 0.95,
                                              noise_champ)
    assert noise_margin < margin  # random scores don't beat their own null like the oracle


def test_rebalance_days_holds_between_and_charges_forced_exits():
    # rebalance_days=2: day1 ranks (long A / short C), day2 HOLDS despite flipped
    # scores — but B... A vanishes on day2 -> forced exit charged; day3 re-ranks.
    rows = [
        (D1, "A", "X", 3.0, 0.01), (D1, "B", "X", 2.0, 0.0), (D1, "C", "X", 1.0, -0.01),
        (D2, "B", "X", 9.0, 0.02), (D2, "C", "X", 8.0, 0.02),  # A missing (delisted)
        (D3, "B", "X", 2.0, 0.0), (D3, "C", "X", 1.0, 0.0),
    ]
    book = build_long_short_book(_panel(rows), quantile=0.34, cost_bps=0.0,
                                 min_names=2, sector_neutral=False, rebalance_days=2)
    # day1 (rebalance): +0.5 A, -0.5 C; inception turnover 0.5
    np.testing.assert_allclose(book.turnover[0], 0.5)
    np.testing.assert_allclose(book.gross[0], 0.5 * 0.01 - 0.5 * (-0.01))
    # day2 (hold): A force-exited (0.5*|0.5| = 0.25 turnover); C held -> gross = -0.5*0.02
    np.testing.assert_allclose(book.turnover[1], 0.25)
    np.testing.assert_allclose(book.gross[1], -0.5 * 0.02)
    # day3 (rebalance): from {C:-0.5} to {B:+0.5, C:-0.5} -> turnover 0.25
    np.testing.assert_allclose(book.turnover[2], 0.25)


def _churn_panel():
    # 5 names, quantile 0.4 -> k=2. Day1 top-2 = A,B. Day2 C overtakes B, pushing
    # B to rank 2 (still inside a band of k_exit=3): a band holds B; band=0 swaps B->C.
    from datetime import timedelta
    d = [date(2021, 1, 4) + timedelta(days=i) for i in range(2)]
    rows = [
        (d[0], "A", "X", 5.0, 0.01), (d[0], "B", "X", 4.0, 0.02),
        (d[0], "C", "X", 3.0, 0.0), (d[0], "D", "X", 2.0, -0.01), (d[0], "E", "X", 1.0, -0.02),
        (d[1], "A", "X", 5.0, 0.01), (d[1], "C", "X", 4.0, 0.0),
        (d[1], "B", "X", 3.0, 0.02), (d[1], "D", "X", 2.0, -0.01), (d[1], "E", "X", 1.0, -0.02),
    ]
    return _panel(rows)


def test_rebalance_band_zero_is_identical_to_no_band():
    panel = _churn_panel()
    kw = dict(quantile=0.4, cost_bps=50.0, min_names=5, sector_neutral=False, rebalance_days=1)
    base = build_long_short_book(panel, **kw)
    banded0 = build_long_short_book(panel, **kw, rebalance_band=0.0)
    np.testing.assert_array_equal(base.net, banded0.net)
    np.testing.assert_array_equal(base.turnover, banded0.turnover)  # default path untouched


def test_rebalance_band_holds_boundary_name_and_cuts_turnover():
    panel = _churn_panel()
    kw = dict(quantile=0.4, cost_bps=50.0, min_names=5, sector_neutral=False, rebalance_days=1)
    no_band = build_long_short_book(panel, **kw, rebalance_band=0.0)
    band = build_long_short_book(panel, **kw, rebalance_band=0.5)  # k_exit=int(5*0.4*1.5)=3
    # Day 2: band retains B (rank 2, inside the band) instead of swapping to C,
    # so its day-2 turnover is strictly lower than the churny no-band book.
    assert band.turnover[1] < no_band.turnover[1]
    assert band.turnover.sum() < no_band.turnover.sum()
    # Day-1 inception is identical (no prior holdings to retain).
    np.testing.assert_allclose(band.turnover[0], no_band.turnover[0])
    # Both legs stay unit-gross / dollar-neutral under the band.
    assert band.avg_names_per_leg == 2.0


def test_daily_rebalance_matches_legacy_semantics():
    # rebalance_days=1 must reproduce the original daily book bit-for-bit.
    rows = [
        (D1, "A", "X", 4.0, 0.02), (D1, "B", "X", 3.0, 0.01),
        (D1, "C", "X", 2.0, -0.01), (D1, "D", "X", 1.0, -0.03),
        (D2, "A", "X", 1.0, 0.01), (D2, "B", "X", 2.0, 0.02),
        (D2, "C", "X", 3.0, -0.02), (D2, "D", "X", 4.0, -0.01),
    ]
    daily = build_long_short_book(_panel(rows), 0.25, 10.0, 4, False, rebalance_days=1)
    np.testing.assert_allclose(daily.gross[0], 0.5 * 0.02 - 0.5 * (-0.03))
    np.testing.assert_allclose(daily.gross[1], 0.5 * (-0.01) - 0.5 * 0.01)  # D long, A short
    np.testing.assert_allclose(daily.turnover, [0.5, 1.0])  # full flip on day2


def test_score_smoothing_is_trailing_per_ticker_mean():
    from new_pipeline.tournament.long_short import smooth_scores

    panel = _panel([
        (D1, "A", "X", 1.0, 0.0), (D2, "A", "X", 3.0, 0.0), (D3, "A", "X", 5.0, 0.0),
        (D1, "B", "X", 10.0, 0.0), (D2, "B", "X", 0.0, 0.0), (D3, "B", "X", 2.0, 0.0),
    ])
    out = smooth_scores(panel, 2).sort(["ticker", "date"])
    a = out.filter(out["ticker"] == "A")["score"].to_list()
    b = out.filter(out["ticker"] == "B")["score"].to_list()
    assert a == [1.0, 2.0, 4.0]   # trailing mean of (1), (1,3), (3,5)
    assert b == [10.0, 5.0, 1.0]  # (10), (10,0), (0,2)
    assert smooth_scores(panel, 1) is panel  # no-op passthrough


def test_slow_book_cuts_turnover_on_noisy_scores():
    from datetime import timedelta

    from new_pipeline.tournament.long_short import smooth_scores

    rng = np.random.default_rng(5)
    rows = []
    for d in range(40):
        day = D1 + timedelta(days=d)
        for i in range(20):
            rows.append((day, f"T{i:02d}", "X", float(rng.normal()), float(rng.normal(0, 0.01))))
    panel = _panel(rows)
    fast = build_long_short_book(panel, 0.2, 10.0, 10, False, rebalance_days=1)
    slow = build_long_short_book(smooth_scores(panel, 5), 0.2, 10.0, 10, False,
                                 rebalance_days=5)
    assert slow.turnover.mean() < 0.35 * fast.turnover.mean()  # >65% turnover cut


def test_vol_target_derisk_is_causal_and_never_levers():
    from datetime import timedelta

    # 30 days, 4 names; unit book vol is large -> a tiny target must shrink
    # exposure, but only AFTER the lookback warmup (causality).
    rng = np.random.default_rng(9)
    rows = []
    for d in range(30):
        day = D1 + timedelta(days=d)
        for i, t in enumerate("ABCD"):
            rows.append((day, t, "X", float(3 - i), float(rng.normal(0, 0.02))))
    panel = _panel(rows)
    plain = build_long_short_book(panel, 0.25, 0.0, 4, False, 1)
    capped = build_long_short_book(panel, 0.25, 0.0, 4, False, 1,
                                   vol_target_annual=0.01, vol_lookback=10)
    # warmup: first 10 days identical (scalar 1 until enough unit history)
    np.testing.assert_allclose(capped.gross[:10], plain.gross[:10])
    # after warmup the tiny target binds: exposure and gross shrink
    assert capped.avg_gross_exposure < 1.0
    assert np.abs(capped.gross[15:]).sum() < np.abs(plain.gross[15:]).sum()
    # gross scales linearly with the scalar: day-15 ratio equals exposure ratio
    day = 20
    exp_ratio = np.abs(capped.gross[day]) / max(np.abs(plain.gross[day]), 1e-12)
    assert exp_ratio <= 1.0 + 1e-9
    # never levers above unit gross
    assert max(capped.turnover) <= max(plain.turnover) + 1e-9


def test_vol_target_off_is_bit_stable():
    rows = [
        (D1, "A", "X", 4.0, 0.02), (D1, "B", "X", 3.0, 0.01),
        (D1, "C", "X", 2.0, -0.01), (D1, "D", "X", 1.0, -0.03),
    ]
    a = build_long_short_book(_panel(rows), 0.25, 10.0, 4, False, 1)
    b = build_long_short_book(_panel(rows), 0.25, 10.0, 4, False, 1,
                              vol_target_annual=0.0, vol_lookback=20)
    np.testing.assert_array_equal(a.net, b.net)
    np.testing.assert_array_equal(a.turnover, b.turnover)


def test_eval_start_floors_the_book_window(tmp_path):
    """With ``eval_start`` set, the sleeve trades ONLY dates >= the floor (the
    strategy the universe fixture defines); every artifact/diagnostic follows.
    Default None keeps the full window bit-identical."""
    from types import SimpleNamespace

    from new_pipeline.tournament.long_short import run_universe_long_short

    rng = np.random.default_rng(0)
    days = [date(2018, 8, 27), date(2018, 8, 28), date(2018, 8, 29),
            date(2018, 9, 3), date(2018, 9, 4), date(2018, 9, 5)]
    tickers = [f"T{i}" for i in range(6)]
    rows = []
    for d in days:
        for t in tickers:
            rows.append({
                "date": d, "ticker": t, "next_ret": float(rng.normal(0, 0.01)),
                "proba_c0_p0": float(rng.uniform()), "proba_c0_p1": float(rng.uniform()),
            })
    pl.DataFrame(rows).write_parquet(tmp_path / "tech_oos_proba.parquet")
    (tmp_path / "tech_candidate.json").write_text("{}")
    results = {"Tech": {"candidate_path": str(tmp_path / "tech_candidate.json")}}

    def cfg(eval_start):
        return SimpleNamespace(long_short=SimpleNamespace(
            enabled=True, quantile=0.34, cost_bps=0.0, min_names_per_day=4,
            sector_neutral=False, null_iterations=2, null_quantile=0.95,
            rebalance_days=1, score_smoothing_days=1, vol_target_annual=0.0,
            vol_lookback_days=20, rebalance_band=0.0, regime_gate_enabled=False,
            regime_experts_enabled=False, eval_start=eval_start,
        ))

    out_full = tmp_path / "full"
    out_floor = tmp_path / "floored"
    out_full.mkdir(), out_floor.mkdir()
    full = run_universe_long_short(results, out_full, cfg(None))
    floored = run_universe_long_short(results, out_floor, cfg("2018-09-01"))
    full_dates = pl.read_parquet(out_full / "universe_long_short_sample_dates.parquet")["date"]
    floor_dates = pl.read_parquet(out_floor / "universe_long_short_sample_dates.parquet")["date"]
    assert full["diagnostics"]["n_days"] == 6 and full_dates.min() == days[0]
    assert floored["diagnostics"]["n_days"] == 3
    assert floor_dates.min() == date(2018, 9, 3)
    assert floored["diagnostics"]["eval_start"] == "2018-09-01"
    assert full["diagnostics"]["eval_start"] is None


def test_short_borrow_charged_on_actual_short_exposure_only():
    """Borrow accrues daily on |short notional|; a book with no shorts pays 0."""
    rows = [[d, t, "Tech", s, 0.0] for d in (D1, D2)
            for t, s in (("A", 3.0), ("B", 2.0), ("C", 1.0), ("D", 0.0))]
    base = build_long_short_book(_panel(rows), 0.25, 0.0, 4)
    borrowed = build_long_short_book(_panel(rows), 0.25, 0.0, 4, short_borrow_bps=252e4)
    # unit-gross book: short exposure 0.5 -> drag = 252e4/1e4/252 * 0.5 = 0.5/day
    np.testing.assert_allclose(base.net - 0.5, borrowed.net)
    from new_pipeline.tournament.long_short import build_hedged_book

    long_only = build_hedged_book(_panel(rows), 0.25, 0.0, 4, short_default=0.0,
                                  short_borrow_bps=252e4)
    zero_borrow = build_hedged_book(_panel(rows), 0.25, 0.0, 4, short_default=0.0)
    np.testing.assert_allclose(long_only.net, zero_borrow.net)  # no shorts held


def test_hedged_book_gates_single_name_shorts_by_state():
    """short_state_scalars=0 dates hold NO single-name shorts (borrow-probe:
    a huge borrow rate changes nothing on gated dates, bites on open dates)."""
    from new_pipeline.tournament.long_short import build_hedged_book

    rows = [[d, t, "Tech", s, 0.01] for d in (D1, D2, D3)
            for t, s in (("A", 3.0), ("B", 2.0), ("C", 1.0), ("D", 0.0))]
    gate = {D1: 0.0, D2: 1.0, D3: 1.0}
    quiet = build_hedged_book(_panel(rows), 0.25, 0.0, 4, rebalance_days=1,
                              short_state_scalars=gate)
    pricey = build_hedged_book(_panel(rows), 0.25, 0.0, 4, rebalance_days=1,
                               short_state_scalars=gate, short_borrow_bps=252e4)
    assert quiet.net[0] == pricey.net[0]          # gated: no short, no borrow
    assert pricey.net[1] < quiet.net[1]           # open: borrow bites


def test_hedged_book_neutralizes_market_beta_causally():
    """With every name = market + noise, the hedged long-only book's market
    correlation collapses vs the unhedged one (rolling-beta hedge, no
    look-ahead: warmup uses the dollar hedge)."""
    from new_pipeline.tournament.long_short import build_hedged_book, panel_market_by_date

    rng = np.random.default_rng(9)
    d0 = date(2021, 1, 4)
    days = [date.fromordinal(d0.toordinal() + i) for i in range(220)]
    mkt_path = rng.normal(0.0006, 0.012, len(days))
    rows = []
    for i, d in enumerate(days):
        for j in range(12):
            rows.append([d, f"T{j}", "Tech", float(rng.uniform()),
                         float(mkt_path[i] + rng.normal(0, 0.004))])
    panel = _panel(rows)
    mkt = panel_market_by_date(panel)
    unhedged = build_hedged_book(panel, 0.25, 0.0, 6, short_default=0.0,
                                 market_by_date=None, hedge_cost_bps=0.0)
    hedged = build_hedged_book(panel, 0.25, 0.0, 6, short_default=0.0,
                               market_by_date=mkt, hedge_cost_bps=0.0)
    m = np.array([mkt[d] for d in hedged.dates])
    c_un = abs(np.corrcoef(unhedged.net, m)[0, 1])
    c_hg = abs(np.corrcoef(hedged.net, m)[0, 1])
    assert c_un > 0.9 and c_hg < 0.35


def test_structure_variants_expand_the_trial_matrix(tmp_path):
    """structure_variants: 4 constructions x n_combos trial columns in ONE
    matrix, champion labeled, paths built under the champion construction."""
    from types import SimpleNamespace

    from new_pipeline.tournament.long_short import run_universe_long_short

    rng = np.random.default_rng(1)
    days = [date.fromordinal(date(2021, 1, 4).toordinal() + i) for i in range(90)]
    rows = []
    for d in days:
        for t in [f"T{i}" for i in range(8)]:
            rows.append({
                "date": d, "ticker": t, "next_ret": float(rng.normal(0, 0.01)),
                "proba_c0_p0": float(rng.uniform()), "proba_c0_p1": float(rng.uniform()),
            })
    pl.DataFrame(rows).write_parquet(tmp_path / "tech_oos_proba.parquet")
    (tmp_path / "tech_candidate.json").write_text("{}")
    cfg = SimpleNamespace(long_short=SimpleNamespace(
        enabled=True, quantile=0.25, cost_bps=5.0, min_names_per_day=6,
        sector_neutral=False, null_iterations=2, null_quantile=0.95,
        rebalance_days=5, score_smoothing_days=1, vol_target_annual=0.0,
        vol_lookback_days=20, rebalance_band=0.0, regime_gate_enabled=False,
        regime_experts_enabled=False, eval_start=None, structure_variants=True,
        short_borrow_bps=50.0, hedge_cost_bps=2.0,
    ))
    entry = run_universe_long_short(
        {"Tech": {"candidate_path": str(tmp_path / "tech_candidate.json")}}, tmp_path, cfg
    )
    matrix = pl.read_parquet(tmp_path / "universe_long_short_returns_matrix.parquet")
    assert matrix.width == 4  # 4 constructions x 1 combo
    assert len(entry["trial_sharpes"]) == 4
    diag = entry["diagnostics"]
    assert set(diag["structure_trials"]) == {
        "ls|combo0", "ls_gated|combo0", "lo_hedged|combo0", "lo_hedged_disp|combo0"
    }
    assert diag["construction"] in ("ls", "ls_gated", "lo_hedged", "lo_hedged_disp")
    assert entry["best_params"]["construction"] == diag["construction"]
    assert diag["short_borrow_bps"] == 50.0
    paths = pl.read_parquet(tmp_path / "universe_long_short_paths.parquet")
    assert paths.width == 2  # phi


def test_calm_cost_policy_only_fires_in_calm_states():
    """No-calm-dates map == bit-identical legacy book; calm-day cadence skip
    holds the book (zero rebalance turnover) while forced exits still charge."""
    rows = []
    d0 = date(2021, 1, 4)
    days = [date.fromordinal(d0.toordinal() + i) for i in range(12)]
    rng = np.random.default_rng(2)
    for d in days:
        for j, t in enumerate("ABCDEFGH"):
            # tightly spaced scores + noise -> ranks genuinely churn each day
            rows.append([d, t, "Tech", 1.0 - 0.1 * j + float(rng.normal(0, 0.5)), 0.01])
    panel = _panel(rows)
    base = build_long_short_book(panel, 0.25, 10.0, 8, rebalance_days=2)
    never_calm = build_long_short_book(
        panel, 0.25, 10.0, 8, rebalance_days=2,
        calm_states={d: False for d in days},
        calm_rebalance_band=2.0, calm_rebalance_days=6,
    )
    np.testing.assert_array_equal(base.net, never_calm.net)  # policy inert
    assert base.turnover[2:].sum() > 0.0  # churn actually happens post-inception
    always_calm = build_long_short_book(
        panel, 0.25, 10.0, 8, rebalance_days=2,
        calm_states={d: True for d in days}, calm_rebalance_days=6,
    )
    # scheduled re-ranks at t=2,4 (and 8,10) are skipped inside each 6-day
    # window after a rebalance -> strictly less total turnover
    assert always_calm.turnover.sum() < base.turnover.sum()
    assert always_calm.turnover[2] == 0.0 and always_calm.turnover[4] == 0.0
    assert always_calm.turnover[6] > 0.0  # spacing elapsed -> re-rank happens


def test_calm_band_widens_exit_band_only_when_calm():
    """A name drifting to a rank inside the wide calm band is HELD on calm
    rebalances but rotated out under the baseline band."""
    d0 = date(2021, 1, 4)
    days = [date.fromordinal(d0.toordinal() + i) for i in range(2)]
    tick = [("A", 8.0), ("B", 7.0), ("C", 6.0), ("D", 5.0),
            ("E", 4.0), ("F", 3.0), ("G", 2.0), ("H", 1.0)]
    rows = [[days[0], t, "Tech", s, 0.0] for t, s in tick]
    # day 2: A (held long) drifts to rank 3 of 8 — outside the tight exit band
    # (k_exit=3 keeps ranks 0-2) but inside the wide calm band; H symmetric.
    day2 = [("B", 8.0), ("C", 7.0), ("D", 6.0), ("A", 5.0),
            ("H", 4.0), ("E", 3.0), ("F", 2.0), ("G", 1.0)]
    rows += [[days[1], t, "Tech", s, 0.0] for t, s in day2]
    panel = _panel(rows)
    tight = build_long_short_book(panel, 0.25, 0.0, 8, rebalance_days=1,
                                  rebalance_band=0.5)
    calm_wide = build_long_short_book(panel, 0.25, 0.0, 8, rebalance_days=1,
                                      rebalance_band=0.5,
                                      calm_states={d: True for d in days},
                                      calm_rebalance_band=3.0)
    assert calm_wide.turnover[1] < tight.turnover[1]  # A/H held, not rotated


def test_calm_cost_variants_expand_the_trial_matrix(tmp_path):
    from types import SimpleNamespace

    from new_pipeline.tournament.long_short import run_universe_long_short

    rng = np.random.default_rng(4)
    d0 = date(2021, 1, 4)
    days = [date.fromordinal(d0.toordinal() + i) for i in range(90)]
    rows = []
    for d in days:
        for t in [f"T{i}" for i in range(8)]:
            rows.append({
                "date": d, "ticker": t, "next_ret": float(rng.normal(0, 0.01)),
                "proba_c0_p0": float(rng.uniform()), "proba_c0_p1": float(rng.uniform()),
            })
    pl.DataFrame(rows).write_parquet(tmp_path / "tech_oos_proba.parquet")
    (tmp_path / "tech_candidate.json").write_text("{}")
    cfg = SimpleNamespace(long_short=SimpleNamespace(
        enabled=True, quantile=0.25, cost_bps=5.0, min_names_per_day=6,
        sector_neutral=False, null_iterations=2, null_quantile=0.95,
        rebalance_days=5, score_smoothing_days=1, vol_target_annual=0.0,
        vol_lookback_days=20, rebalance_band=0.5, regime_gate_enabled=False,
        regime_experts_enabled=False, eval_start=None, structure_variants=False,
        calm_cost_variants=True, calm_rebalance_band=1.5, calm_rebalance_days=10,
        short_borrow_bps=50.0, hedge_cost_bps=2.0,
    ))
    entry = run_universe_long_short(
        {"Tech": {"candidate_path": str(tmp_path / "tech_candidate.json")}}, tmp_path, cfg
    )
    assert set(entry["diagnostics"]["structure_trials"]) == {
        "ls|combo0", "ls_calmband|combo0", "ls_calmslow|combo0", "ls_calmboth|combo0"
    }
    assert entry["diagnostics"]["construction"] in (
        "ls", "ls_calmband", "ls_calmslow", "ls_calmboth"
    )
    assert entry["best_params"]["construction"] == entry["diagnostics"]["construction"]
    assert entry["diagnostics"]["calm_rebalance_days"] == 10
    matrix = pl.read_parquet(tmp_path / "universe_long_short_returns_matrix.parquet")
    assert matrix.width == 4
