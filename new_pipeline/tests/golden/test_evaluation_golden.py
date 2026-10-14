"""Golden numbers for the statistical-evaluation formulas (DSR family + haircut).

Pins exact outputs on fixed inputs so the Bailey/López de Prado and Harvey/Liu
math can't silently drift. Part of the tests/golden/ harness.
"""

import numpy as np
import pytest
from new_pipeline.evaluation.dsr import (
    compute_deflated_sharpe_ratio,
    expected_max_sharpe,
    min_track_record_length,
    probabilistic_sharpe_ratio,
)
from new_pipeline.evaluation.haircut import haircut_sharpe_ratio
from new_pipeline.evaluation.hmm_gauntlet import run_hmm_synthetic_gauntlet


def _returns() -> np.ndarray:
    return np.random.default_rng(3).normal(0.001, 0.02, 300)


def test_dsr_family_golden():
    returns = _returns()
    assert expected_max_sharpe(0.5, 10) == pytest.approx(1.1134091365258485, rel=1e-9)
    assert probabilistic_sharpe_ratio(returns, 0.0) == pytest.approx(0.9546271186467692, rel=1e-9)
    assert min_track_record_length(returns, 0.0, 0.95) == pytest.approx(283.7441171345737, rel=1e-9)
    assert compute_deflated_sharpe_ratio(
        returns, [0.05, 0.1, 0.08, 0.12, 0.03]
    ) == pytest.approx(0.8269386744349638, rel=1e-9)


def test_haircut_sharpe_golden():
    haircut = haircut_sharpe_ratio(2.5, 1260, 10, "bhy")
    assert haircut.adjusted_sharpe == pytest.approx(2.2233145042990574, rel=1e-9)
    assert haircut.haircut_fraction == pytest.approx(0.11067419828037706, rel=1e-9)


def test_hmm_gauntlet_golden():
    rng = np.random.default_rng(0)
    benchmark = rng.normal(0.0, 0.01, 200)
    features = rng.normal(size=(200, 3))
    value = run_hmm_synthetic_gauntlet(
        benchmark, features, lambda f: 1.0 / (1.0 + np.exp(-f[:, 0])),
        n_iter=20, seed=7, block_size=10,
    )
    assert value == pytest.approx(-0.9420801852345936, rel=1e-9)
