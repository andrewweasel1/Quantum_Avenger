"""Golden p-values for the multiple-strategy reality checks (offense roadmap P4).

Pins White's RC / Hansen's SPA on a fixed seeded set of strategy returns (fixed
bootstrap seed) so a refactor of the bootstrap/centering math is caught. See
docs/quantitative_math.md Part II §J.
"""

import numpy as np
import pytest
from new_pipeline.evaluation.reality_check import hansens_spa, whites_reality_check


def _strategies():
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 0.01, (252, 20))
    skilled = rng.normal(0, 0.01, (252, 20))
    skilled[:, 0] += 0.004
    return skilled, noise


def test_reality_check_golden():
    skilled, noise = _strategies()
    assert whites_reality_check(noise, n_bootstrap=300, seed=42) == pytest.approx(
        0.7109634551495017, rel=1e-9
    )
    assert whites_reality_check(skilled, n_bootstrap=300, seed=42) == pytest.approx(
        0.0033222591362126247, rel=1e-9
    )
    assert hansens_spa(skilled, n_bootstrap=300, seed=42) == pytest.approx(
        0.0033222591362126247, rel=1e-9
    )
