"""Unit tests for the P1 extended feature families (offense roadmap P1).

Fractional differentiation (stationary-with-memory), range-based vol estimators
(Parkinson/GK/RS/YZ), microstructure proxies (Roll/Corwin-Schultz/Kyle), and the
per-ticker orchestration. Golden numbers live in tests/golden/test_extended_golden.py.
"""

import math
from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest
from new_pipeline.core.exceptions import SchemaValidationError
from new_pipeline.features.extended import (
    add_extended_features,
    extended_feature_names,
)
from new_pipeline.features.fracdiff import (
    add_fracdiff,
    frac_diff_weights,
    fractional_difference,
)
from new_pipeline.features.microstructure import corwin_schultz, kyle_lambda, roll_measure
from new_pipeline.features.vol_estimators import add_vol_estimators
from new_pipeline.tournament.stat_arb import adf_tstat


def _ohlc(n, seed=7, ticker="AAA") -> pl.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    high = close + np.abs(rng.normal(0, 0.5, n))
    low = close - np.abs(rng.normal(0, 0.5, n))
    openp = close + rng.normal(0, 0.3, n)
    volume = (1e6 + rng.integers(0, 5e5, n)).astype(float)
    days = [date(2021, 1, 4) + timedelta(days=i) for i in range(n)]
    return pl.DataFrame(
        {"date": days, "ticker": [ticker] * n, "open": openp, "high": high,
         "low": low, "close": close, "volume": volume}
    )


# --- fractional differentiation ---


def test_frac_diff_weights_recurrence():
    w = frac_diff_weights(0.4, threshold=1e-3)
    assert w[0] == 1.0
    assert w[1] == pytest.approx(-0.4)
    assert w[2] == pytest.approx(-0.12)  # -w[1]*(d-1)/2
    assert w.size == 55  # known fixed width at d=0.4, threshold=1e-3
    assert abs(w[-1]) >= 1e-3  # last kept weight is above the truncation threshold


def test_fractional_difference_warmup():
    width = frac_diff_weights(0.4, 1e-3).size
    out = fractional_difference(np.log(100 + np.arange(200.0)), 0.4, 1e-3)
    assert np.isnan(out[: width - 1]).all() and np.isfinite(out[width - 1 :]).all()


def test_fracdiff_makes_random_walk_more_stationary():
    log_price = np.log(100 + np.cumsum(np.random.default_rng(1).normal(0, 1, 400)))
    fd = fractional_difference(log_price, 0.4, 1e-3)
    assert adf_tstat(fd[np.isfinite(fd)]) < adf_tstat(log_price)  # closer to stationary


def test_fractional_difference_series_shorter_than_window():
    out = fractional_difference(np.arange(5.0), 0.4, 1e-3)  # width (55) > series
    assert np.isnan(out).all()


def test_add_fracdiff_adds_column():
    assert "fracdiff" in add_fracdiff(_ohlc(80)).columns


# --- volatility estimators ---


def test_vol_estimators_positive_and_named():
    out = add_vol_estimators(_ohlc(120), window=20)
    for column in ("parkinson_vol", "garman_klass_vol", "rogers_satchell_vol", "yang_zhang_vol"):
        series = out[column].drop_nulls().to_numpy()
        assert series.size > 0 and (series >= 0).all()


def test_parkinson_matches_closed_form():
    # constant high/low ratio -> constant Parkinson variance -> known annualized vol.
    n = 40
    frame = pl.DataFrame(
        {"date": [date(2021, 1, 4) + timedelta(days=i) for i in range(n)], "ticker": ["A"] * n,
         "open": [101.0] * n, "high": [102.0] * n, "low": [100.0] * n,
         "close": [101.0] * n, "volume": [1e6] * n}
    )
    expected = math.sqrt((math.log(102 / 100) ** 2 / (4 * math.log(2))) * 252)
    assert add_vol_estimators(frame, 20)["parkinson_vol"][30] == pytest.approx(expected, rel=1e-9)


# --- microstructure ---


def test_roll_measure_positive_on_bid_ask_bounce():
    prices = np.array([100.0, 100.5] * 30)  # alternating -> negative serial covariance
    roll = roll_measure(prices, window=10)
    finite = roll[np.isfinite(roll)]
    assert (finite >= 0).all() and finite.max() > 0


def test_corwin_schultz_nonnegative():
    frame = _ohlc(80)
    cs = corwin_schultz(frame["high"].to_numpy(), frame["low"].to_numpy(), 20)
    assert (cs[np.isfinite(cs)] >= 0).all()


def test_kyle_lambda_nonnegative_price_impact():
    rng = np.random.default_rng(2)
    close = 100 + np.cumsum(rng.normal(0, 0.5, 200))
    volume = 1e6 + rng.integers(0, 5e5, 200).astype(float)
    lam = kyle_lambda(close, volume, 20)
    assert np.isfinite(lam[np.isfinite(lam)]).all()
    assert np.nanmean(lam) >= 0  # price moves with signed flow


# --- orchestration ---


def test_extended_feature_names():
    assert extended_feature_names(["fracdiff", "microstructure"]) == [
        "fracdiff", "roll_measure", "corwin_schultz", "kyle_lambda",
    ]


def test_add_extended_features_empty_is_identity():
    frame = _ohlc(50)
    assert add_extended_features(frame, []).equals(frame)


def test_add_extended_features_unknown_raises():
    with pytest.raises(SchemaValidationError):
        add_extended_features(_ohlc(50), ["not_a_family"])


def test_add_extended_features_all_families_per_ticker():
    frame = pl.concat([_ohlc(120, 7, "AAA"), _ohlc(120, 9, "BBB")])
    out = add_extended_features(frame, ["fracdiff", "vol_estimators", "microstructure"])
    assert out.height == 240  # rows preserved
    for column in extended_feature_names(["fracdiff", "vol_estimators", "microstructure"]):
        assert column in out.columns
    # per-ticker grouping: each ticker independently has populated values
    for ticker in ("AAA", "BBB"):
        assert out.filter(pl.col("ticker") == ticker)["parkinson_vol"].drop_nulls().len() > 0
