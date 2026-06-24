"""Golden values for statistical arbitrage (offense roadmap P5).

Pins the Engle-Granger hedge ratio, ADF t-stat, and OU half-life on a fixed seeded
cointegrated pair so a refactor of the OLS / ADF / OU math is caught. See
docs/quantitative_math.md Part II §C.
"""

import numpy as np
import pytest
from new_pipeline.tournament.stat_arb import engle_granger


def _cointegrated_pair():
    rng = np.random.default_rng(0)
    t = 400
    x = np.cumsum(rng.normal(0, 1, t))
    spread = np.zeros(t)
    for k in range(1, t):
        spread[k] = 0.9 * spread[k - 1] + rng.normal(0, 1)
    return 2.0 * x + spread, x


def test_stat_arb_golden():
    result, _ = engle_granger(*_cointegrated_pair())
    assert result.hedge_ratio == pytest.approx(2.019268213378379, rel=1e-9)
    assert result.adf_tstat == pytest.approx(-4.647441132396602, rel=1e-9)
    assert result.half_life == pytest.approx(6.137269372371761, rel=1e-9)
    assert result.cointegrated is True
