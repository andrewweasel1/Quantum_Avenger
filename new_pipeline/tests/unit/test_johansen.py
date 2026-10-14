"""Unit tests for Johansen multivariate cointegration (offense roadmap §C)."""

import numpy as np
import pytest
from new_pipeline.tournament.johansen import johansen_basket, johansen_test
from new_pipeline.tournament.stat_arb import ADF_CRITICAL_5PCT, adf_tstat


def _cointegrated_basket(seed=0, t=500) -> np.ndarray:
    # two common trends; Y3 = Y1 + Y2 + stationary spread -> cointegrating vector ~ [1,1,-1].
    rng = np.random.default_rng(seed)
    w1, w2 = np.cumsum(rng.normal(0, 1, t)), np.cumsum(rng.normal(0, 1, t))
    spread = np.zeros(t)
    for k in range(1, t):
        spread[k] = 0.9 * spread[k - 1] + rng.normal(0, 1)
    return np.column_stack(
        [w1 + rng.normal(0, 0.5, t), w2 + rng.normal(0, 0.5, t), w1 + w2 + spread]
    )


def test_johansen_recovers_cointegrating_vector():
    prices = _cointegrated_basket()
    vector = johansen_basket(prices)
    assert vector[0] == 1.0  # normalized so the first weight is 1
    assert vector[1] == pytest.approx(1.0, abs=0.3)  # ~ Y1 + Y2 - Y3 stationary
    assert vector[2] == pytest.approx(-1.0, abs=0.3)
    assert adf_tstat(prices @ vector) < ADF_CRITICAL_5PCT  # the basket spread is stationary


def test_johansen_eigenvalues_descending_in_unit_interval():
    result = johansen_test(_cointegrated_basket())
    assert (np.diff(result.eigenvalues) <= 1e-12).all()  # descending
    positive = result.eigenvalues[result.eigenvalues > 0]
    assert (positive < 1.0).all()  # squared canonical correlations
    assert result.trace_statistic > 0.0


def test_johansen_basket_more_stationary_than_independent_walks():
    cointegrated = _cointegrated_basket()
    rng = np.random.default_rng(5)
    independent = np.column_stack([np.cumsum(rng.normal(0, 1, 500)) for _ in range(3)])
    assert adf_tstat(cointegrated @ johansen_basket(cointegrated)) < adf_tstat(
        independent @ johansen_basket(independent)
    )
