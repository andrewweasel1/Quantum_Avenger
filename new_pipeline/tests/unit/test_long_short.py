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
