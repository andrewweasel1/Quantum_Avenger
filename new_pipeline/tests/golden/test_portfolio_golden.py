"""Golden HRP weights for the portfolio layer (offense roadmap P4).

Pins HRP allocation on a fixed seeded two-cluster returns fixture so a refactor of
the clustering / recursive-bisection math is caught (scipy linkage is deterministic).
See docs/quantitative_math.md Part II §H.
"""

import numpy as np
import pytest
from new_pipeline.portfolio import hrp_weights, ic_weights, nco_weights


def _fixture_cov() -> np.ndarray:
    rng = np.random.default_rng(0)
    t = 500
    f1, f2 = rng.normal(0, 1, t), rng.normal(0, 1, t)
    returns = np.column_stack(
        [
            0.01 * (f1 + 0.3 * rng.normal(0, 1, t)),
            0.02 * (f1 + 0.6 * rng.normal(0, 1, t)),
            0.01 * (f2 + 0.3 * rng.normal(0, 1, t)),
            0.03 * (f2 + 0.6 * rng.normal(0, 1, t)),
        ]
    )
    return np.cov(returns, rowvar=False)


def test_hrp_weights_golden():
    weights = hrp_weights(_fixture_cov())
    assert weights == pytest.approx(
        [0.375586670488, 0.076663285049, 0.498880294326, 0.048869750138], rel=1e-9
    )


def test_nco_weights_golden():
    weights = nco_weights(_fixture_cov())
    assert weights == pytest.approx(
        [0.58382799943, -0.153628611421, 0.707510714554, -0.137710102562], rel=1e-9
    )


def test_ic_weights_golden():
    rng = np.random.default_rng(1)
    sleeves = np.column_stack(
        [rng.normal(0.005, 0.01, 300), rng.normal(0.0, 0.01, 300), rng.normal(-0.004, 0.01, 300)]
    )
    assert ic_weights(sleeves) == pytest.approx([0.965384390971, 0.034615609029, 0.0], rel=1e-9)
