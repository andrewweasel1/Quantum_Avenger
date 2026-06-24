"""Golden HRP weights for the portfolio layer (offense roadmap P4).

Pins HRP allocation on a fixed seeded two-cluster returns fixture so a refactor of
the clustering / recursive-bisection math is caught (scipy linkage is deterministic).
See docs/quantitative_math.md Part II §H.
"""

import numpy as np
import pytest
from new_pipeline.portfolio import hrp_weights


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
