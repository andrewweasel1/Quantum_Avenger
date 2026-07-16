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
