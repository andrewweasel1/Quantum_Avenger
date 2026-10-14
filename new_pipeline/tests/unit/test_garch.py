"""Unit tests for GARCH(1,1) conditional volatility (offense roadmap §D)."""

from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest
from new_pipeline.features.extended import add_extended_features
from new_pipeline.features.garch import add_garch, fit_garch, garch_conditional_volatility


def _simulate_garch(omega, alpha, beta, n, seed):
    rng = np.random.default_rng(seed)
    sig2 = np.empty(n)
    eps = np.empty(n)
    sig2[0] = omega / (1.0 - alpha - beta)
    for t in range(n):
        if t > 0:
            sig2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sig2[t - 1]
        eps[t] = np.sqrt(sig2[t]) * rng.normal()
    return eps, np.sqrt(sig2)


def test_fit_garch_recovers_parameters():
    eps, _ = _simulate_garch(1e-5, 0.08, 0.90, 1500, 0)
    omega, alpha, beta, _mu = fit_garch(eps)
    assert omega > 0.0
    assert alpha == pytest.approx(0.08, abs=0.05)
    assert beta == pytest.approx(0.90, abs=0.05)
    assert 0.0 < alpha + beta < 1.0  # covariance-stationary


def test_conditional_vol_is_causal_and_tracks_true_vol():
    eps, true_vol = _simulate_garch(1e-5, 0.08, 0.90, 1500, 0)
    cv = garch_conditional_volatility(eps, fit_window=252, annualize=False)
    assert np.isnan(cv[:252]).all()  # warmup null (params fit there)
    assert np.isfinite(cv[252:]).all()  # causal forward
    mask = np.isfinite(cv)
    assert np.corrcoef(cv[mask], true_vol[mask])[0, 1] > 0.9  # tracks the true conditional vol


def test_conditional_vol_too_short_is_nan():
    assert np.isnan(garch_conditional_volatility(np.zeros(50), fit_window=252)).all()


def test_add_garch_and_extended_orchestration():
    n = 320
    rng = np.random.default_rng(1)
    frames = []
    for ticker in ("AAA", "BBB"):
        frames.append(
            pl.DataFrame(
                {
                    "ticker": [ticker] * n,
                    "date": [date(2021, 1, 4) + timedelta(days=i) for i in range(n)],
                    "returns": rng.normal(0, 0.01, n),
                }
            )
        )
    out = add_extended_features(pl.concat(frames), ["garch"], garch_fit_window=252)
    assert "garch_vol" in out.columns
    for ticker in ("AAA", "BBB"):
        assert out.filter(pl.col("ticker") == ticker)["garch_vol"].drop_nulls().len() > 0
    assert "garch_vol" in add_garch(frames[0], fit_window=252).columns
