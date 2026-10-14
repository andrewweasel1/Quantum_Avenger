"""Golden numbers for Johansen multivariate cointegration (offense roadmap §C).

Pins the eigenvalues + leading cointegrating vector on a fixed seeded cointegrated
basket so a refactor of the VECM eigenproblem is caught. See
docs/quantitative_math.md Part II §C.
"""

import numpy as np
import pytest
from new_pipeline.tournament.johansen import johansen_basket, johansen_test


def _cointegrated_basket() -> np.ndarray:
    rng = np.random.default_rng(0)
    t = 500
    w1, w2 = np.cumsum(rng.normal(0, 1, t)), np.cumsum(rng.normal(0, 1, t))
    spread = np.zeros(t)
    for k in range(1, t):
        spread[k] = 0.9 * spread[k - 1] + rng.normal(0, 1)
    return np.column_stack(
        [w1 + rng.normal(0, 0.5, t), w2 + rng.normal(0, 0.5, t), w1 + w2 + spread]
    )


def test_johansen_golden():
    result = johansen_test(_cointegrated_basket())
    assert result.eigenvalues == pytest.approx(
        [0.0561342026, 0.0080168622, 0.0009610493], rel=1e-6
    )
    assert johansen_basket(_cointegrated_basket()) == pytest.approx(
        [1.0, 1.1350080383, -1.0795238821], rel=1e-6
    )
