"""Unit tests for statistical arbitrage (offense roadmap P5, §C).

ADF stationarity, Engle-Granger cointegration (recovers the hedge ratio, detects a
cointegrated pair, rejects independent walks), OU half-life, the causal
mean-reversion rule, and pair discovery. Golden values live in
tests/golden/test_stat_arb_golden.py.
"""

import numpy as np
import pytest
from new_pipeline.tournament.simulator import sharpe_ratio
from new_pipeline.tournament.stat_arb import (
    ADF_CRITICAL_5PCT,
    adf_tstat,
    engle_granger,
    find_cointegrated_pairs,
    mean_reversion_returns,
    ou_half_life,
)


def _ar1(phi, n, seed, scale=1.0):
    rng = np.random.default_rng(seed)
    s = np.zeros(n)
    for t in range(1, n):
        s[t] = phi * s[t - 1] + rng.normal(0, scale)
    return s


def _cointegrated_pair(seed=0, t=400, hedge=2.0):
    rng = np.random.default_rng(seed)
    x = np.cumsum(rng.normal(0, 1, t))  # random-walk common factor
    spread = np.zeros(t)
    for k in range(1, t):
        spread[k] = 0.9 * spread[k - 1] + rng.normal(0, 1)  # stationary AR(1)
    return hedge * x + spread, x


def test_adf_flags_stationary_below_random_walk():
    white = adf_tstat(_ar1(0.0, 400, 1))  # i.i.d. -> strongly stationary
    walk = adf_tstat(np.cumsum(np.random.default_rng(2).normal(0, 1, 400)))
    assert white < ADF_CRITICAL_5PCT  # stationary detected
    assert walk > white  # a random walk is "less stationary" than white noise


def test_adf_too_short_returns_zero():
    assert adf_tstat([1.0, 2.0, 3.0]) == 0.0


def test_adf_constant_series_returns_zero():
    assert adf_tstat(np.ones(50)) == 0.0  # rank-deficient design -> guarded


def test_ou_half_life_too_short_is_inf():
    assert ou_half_life([1.0, 2.0]) == float("inf")


def test_engle_granger_recovers_hedge_and_detects_cointegration():
    y, x = _cointegrated_pair()
    result, spread = engle_granger(y, x)
    assert result.hedge_ratio == pytest.approx(2.0, abs=0.1)
    assert result.cointegrated is True
    assert result.adf_tstat < ADF_CRITICAL_5PCT
    assert np.isfinite(result.half_life) and result.half_life > 0
    assert spread.shape == y.shape


def test_engle_granger_independent_walks_not_cointegrated():
    rng = np.random.default_rng(42)
    y = np.cumsum(rng.normal(0, 1, 400))
    x = np.cumsum(rng.normal(0, 1, 400))
    assert engle_granger(y, x)[0].cointegrated is False


def test_ou_half_life_reverting_vs_random_walk():
    half_revert = ou_half_life(_ar1(0.8, 500, 3))  # mean-reverting -> short, finite
    assert np.isfinite(half_revert) and half_revert > 0
    half_walk = ou_half_life(np.cumsum(np.random.default_rng(4).normal(0, 1, 500)))
    assert half_walk > half_revert  # a random walk reverts far slower (often inf)


def test_mean_reversion_profitable_on_reverting_spread():
    _, _ = _cointegrated_pair()
    _, spread = engle_granger(*_cointegrated_pair())
    assert sharpe_ratio(mean_reversion_returns(spread)) > 0.5


def test_mean_reversion_no_lookahead():
    returns = mean_reversion_returns(np.sin(np.linspace(0, 12, 100)) * 3.0, window=10)
    assert returns[0] == 0.0  # first bar can carry no position-from-yesterday P&L


def test_find_cointegrated_pairs_isolates_the_true_pair():
    y, x = _cointegrated_pair()
    noise = np.cumsum(np.random.default_rng(99).normal(0, 1, 400))  # independent of the pair
    pairs = find_cointegrated_pairs(np.column_stack([y, x, noise]), ["Y", "X", "Z"])
    # the strongest (most stationary) pair is the genuinely-cointegrated one — it ranks
    # first by a wide margin (ADF ~-4.6) over any 5%-level spurious noise pair (~-2.9).
    assert pairs
    assert pairs[0]["y"] == "Y" and pairs[0]["x"] == "X"
    assert pairs[0]["adf_tstat"] < ADF_CRITICAL_5PCT
