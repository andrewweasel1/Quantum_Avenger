"""Unit tests for cross-sectional alpha factors (offense roadmap P0).

Correctness + mechanics: cross-sectional z-score, sector neutralization, the
degenerate/null guards, and the per-(ticker) raw signals (momentum, reversal,
low-vol, causal same-month seasonality). Golden number pins live in
tests/golden/test_factor_golden.py.
"""

from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest
from new_pipeline.core.exceptions import SchemaValidationError
from new_pipeline.features.factors import (
    _raw_signal,
    add_cross_sectional_factors,
    factor_feature_names,
)


def test_quality_growth_factors_zscore_and_accruals_sign():
    from new_pipeline.features.factors import FUNDAMENTAL_FACTORS, SUPPORTED_FACTORS

    new = ["roa", "gross_margin", "accruals", "fcf_yield", "revenue_growth", "earnings_growth"]
    assert set(new) <= set(SUPPORTED_FACTORS) and set(new) <= FUNDAMENTAL_FACTORS
    frame = pl.DataFrame({
        "date": [date(2021, 6, 1)] * 3,
        "ticker": ["A", "B", "C"], "sector": ["S"] * 3, "close": [100.0, 100.0, 100.0],
        "return_on_assets": [0.02, 0.08, 0.14], "gross_margin": [0.3, 0.5, 0.7],
        "accruals": [-0.04, 0.0, 0.04],  # LOW accruals = high quality -> sign flips
        "ocf_per_share": [2.0, 5.0, 8.0], "revenue_growth": [0.0, 0.1, 0.2],
        "earnings_growth": [-0.1, 0.05, 0.2],
    })
    out = add_cross_sectional_factors(frame, new, sector_neutral=True, null_policy="neutral")
    # accruals raw is negated: the LOW-accrual name (A, -0.04) must score HIGHEST.
    z = out.sort("ticker")["xf_accruals"].to_numpy()
    assert z[0] > z[1] > z[2]  # A > B > C after negation
    # roa is monotone increasing -> highest-roa name scores highest.
    assert out.sort("ticker")["xf_roa"].to_numpy()[2] > out.sort("ticker")["xf_roa"].to_numpy()[0]


def test_quality_factors_neutral_fill_on_missing_fundamentals():
    # A name with null quality inputs (uncovered issuer) must neutral-fill to 0.0
    # under null_policy="neutral" so it survives the tournament drop_nulls.
    frame = pl.DataFrame({
        "date": [date(2021, 6, 1)] * 2, "ticker": ["A", "B"], "sector": ["S"] * 2,
        "close": [100.0, 100.0], "return_on_assets": [0.05, None],
        "gross_margin": [0.4, None], "accruals": [0.0, None], "ocf_per_share": [3.0, None],
        "revenue_growth": [0.1, None], "earnings_growth": [0.05, None],
    })
    out = add_cross_sectional_factors(
        frame, ["roa", "revenue_growth"], sector_neutral=True, null_policy="neutral"
    )
    assert out["xf_roa"].null_count() == 0  # null input -> filled 0.0, row survives
    assert out["xf_revenue_growth"].null_count() == 0


def _single_date_frame(vols, sectors=None) -> pl.DataFrame:
    """One date, one row per ticker, with explicit ``volatility`` (drives low_vol)."""
    n = len(vols)
    return pl.DataFrame(
        {
            "date": [date(2021, 6, 1)] * n,
            "ticker": [f"T{i}" for i in range(n)],
            "close": [100.0] * n,
            "returns": [0.0] * n,
            "volatility": list(vols),
            "sector": list(sectors) if sectors else ["S"] * n,
        }
    )


def _series_frame(close, ticker="Z") -> pl.DataFrame:
    n = len(close)
    return pl.DataFrame(
        {
            "ticker": [ticker] * n,
            "date": [date(2021, 1, 4) + timedelta(days=i) for i in range(n)],
            "close": list(close),
        }
    ).sort(["ticker", "date"])


def test_empty_factor_set_is_identity():
    frame = _single_date_frame([0.1, 0.2, 0.3])
    out = add_cross_sectional_factors(frame, [])
    assert out.columns == frame.columns
    assert out.equals(frame)


def test_unknown_factor_raises():
    with pytest.raises(SchemaValidationError):
        add_cross_sectional_factors(_single_date_frame([0.1, 0.2]), ["not_a_factor"])


def test_raw_signal_unknown_raises():
    # defensive guard inside the builder (the public API validates names first).
    with pytest.raises(SchemaValidationError):
        _raw_signal("bogus")


def test_factor_feature_names():
    assert factor_feature_names(["mom_12_1", "low_vol"]) == ["xf_mom_12_1", "xf_low_vol"]


def test_low_vol_cross_sectional_zscore():
    vols = [0.10, 0.20, 0.30, 0.40]
    out = add_cross_sectional_factors(
        _single_date_frame(vols), ["low_vol"], sector_neutral=False
    ).sort("ticker")
    raw = -np.array(vols)
    expected = (raw - raw.mean()) / raw.std(ddof=1)  # polars std defaults to ddof=1
    assert out["xf_low_vol"].to_numpy() == pytest.approx(expected, rel=1e-12)
    assert out["xf_low_vol"][0] > out["xf_low_vol"][3]  # lower vol -> higher factor


def test_degenerate_date_is_neutral_zero():
    # zero cross-sectional dispersion (all-equal) -> neutral 0.0, never NaN/inf.
    out = add_cross_sectional_factors(
        _single_date_frame([0.2, 0.2, 0.2]), ["low_vol"], sector_neutral=False
    )
    assert out["xf_low_vol"].to_list() == [0.0, 0.0, 0.0]


def test_single_name_date_is_zero():
    out = add_cross_sectional_factors(
        _single_date_frame([0.2]), ["low_vol"], sector_neutral=False
    )
    assert out["xf_low_vol"].to_list() == [0.0]


def test_null_history_stays_null():
    frame = _single_date_frame([0.1, 0.2, 0.3]).with_columns(
        pl.when(pl.col("ticker") == "T0")
        .then(None)
        .otherwise(pl.col("volatility"))
        .alias("volatility")
    )
    out = add_cross_sectional_factors(frame, ["low_vol"], sector_neutral=False).sort("ticker")
    assert out["xf_low_vol"][0] is None  # null raw -> null factor (row drops in the tournament)
    assert out["xf_low_vol"].drop_nulls().len() == 2


def test_sector_neutralization_demeans_within_sector():
    # within a 2-name sector the demeaned bases are equal & opposite -> z equal & opposite.
    frame = _single_date_frame([0.10, 0.40, 0.20, 0.60], sectors=["A", "A", "B", "B"])
    z = add_cross_sectional_factors(frame, ["low_vol"], sector_neutral=True).sort("ticker")[
        "xf_low_vol"
    ].to_numpy()
    assert z[0] == pytest.approx(-z[1], rel=1e-9)
    assert z[2] == pytest.approx(-z[3], rel=1e-9)


def test_reversal_raw_matches_numpy():
    rng = np.random.default_rng(3)
    close = 100.0 + np.cumsum(rng.normal(0, 1.0, 40))
    raw = _series_frame(close).with_columns(_raw_signal("reversal_21").alias("r"))["r"].to_numpy()
    assert raw[35] == pytest.approx(-(close[35] / close[35 - 21] - 1.0), rel=1e-12)


def test_momentum_raw_matches_numpy():
    rng = np.random.default_rng(5)
    close = 100.0 + np.cumsum(rng.normal(0, 1.0, 300))
    raw = _series_frame(close).with_columns(_raw_signal("mom_12_1").alias("m"))["m"].to_numpy()
    assert raw[280] == pytest.approx(close[280 - 21] / close[280 - 252] - 1.0, rel=1e-12)
    assert np.isnan(raw[250])  # null before 252 days of history exist (12-1 warmup)


def _fundamental_frame():
    return pl.DataFrame(
        {
            "date": [date(2021, 6, 1)] * 3,
            "ticker": ["A", "B", "C"],
            "close": [100.0, 50.0, 200.0],
            "book_value_per_share": [10.0, 10.0, 10.0],
            "earnings_per_share": [5.0, 5.0, 5.0],
            "return_on_equity": [0.10, 0.20, 0.30],
            "sector": ["S"] * 3,
        }
    )


def test_value_quality_raw_signals():
    frame = _fundamental_frame()
    bm = frame.with_columns(_raw_signal("book_to_market").alias("r")).sort("ticker")["r"].to_numpy()
    assert bm == pytest.approx([0.10, 0.20, 0.05])  # bvps/close
    ey = frame.with_columns(_raw_signal("earnings_yield").alias("r")).sort("ticker")["r"].to_numpy()
    assert ey == pytest.approx([0.05, 0.10, 0.025])  # eps/close
    roe = frame.with_columns(_raw_signal("roe").alias("r")).sort("ticker")["r"].to_numpy()
    assert roe == pytest.approx([0.10, 0.20, 0.30])  # return_on_equity directly


def test_value_factor_cross_sectional_zscore_ranks_cheap_higher():
    out = add_cross_sectional_factors(
        _fundamental_frame(), ["book_to_market"], sector_neutral=False
    ).sort("ticker")
    z = out["xf_book_to_market"].to_numpy()
    assert z[1] > z[0] > z[2]  # B (B/M .20) > A (.10) > C (.05)


def test_low_vol_raw_is_negative_volatility():
    frame = _single_date_frame([0.1, 0.2, 0.3])
    raw = frame.with_columns(_raw_signal("low_vol").alias("r")).sort("ticker")["r"].to_numpy()
    assert raw == pytest.approx([-0.1, -0.2, -0.3], rel=1e-12)


def test_seasonality_is_causal_same_month():
    frame = (
        pl.DataFrame(
            {
                "ticker": ["X"] * 6,
                "date": [
                    date(2021, 1, 5), date(2021, 2, 5), date(2022, 1, 5),
                    date(2022, 2, 5), date(2023, 1, 5), date(2023, 1, 6),
                ],
                "returns": [0.10, 0.20, 0.30, 0.40, 0.50, 0.60],
            }
        )
        .with_columns(pl.col("date").dt.month().alias("_xf_month"))
        .sort(["ticker", "date"])
    )
    seas = frame.with_columns(_raw_signal("seasonality").alias("s"))["s"].to_list()
    assert seas[0] is None and seas[1] is None  # no prior same-month observation
    assert seas[2] == pytest.approx(0.10)  # prior Jan: mean([0.10])
    assert seas[3] == pytest.approx(0.20)  # prior Feb: mean([0.20])
    assert seas[4] == pytest.approx(0.20)  # prior Jan: mean([0.10, 0.30])
    assert seas[5] == pytest.approx(0.30)  # prior Jan: mean([0.10, 0.30, 0.50])


def test_no_scratch_columns_leak():
    out = add_cross_sectional_factors(
        _single_date_frame([0.1, 0.2, 0.3]), ["low_vol", "seasonality"], sector_neutral=False
    )
    assert "xf_low_vol" in out.columns and "xf_seasonality" in out.columns
    assert not [c for c in out.columns if c.startswith("_xf_")]


def test_row_order_independent():
    # the stage sorts internally, so a shuffled input yields the same factor values.
    frame = _single_date_frame([0.10, 0.20, 0.30, 0.40], sectors=["A", "A", "B", "B"])
    a = add_cross_sectional_factors(frame, ["low_vol"]).sort("ticker")["xf_low_vol"].to_list()
    b = (
        add_cross_sectional_factors(frame.reverse(), ["low_vol"])
        .sort("ticker")["xf_low_vol"]
        .to_list()
    )
    assert a == pytest.approx(b, rel=1e-12)
