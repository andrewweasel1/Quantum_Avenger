import numpy as np
from new_pipeline.evaluation.dsr import (
    compute_deflated_sharpe_ratio,
    expected_max_sharpe,
    interpret_dsr,
)


def _series(mean: float, n: int = 1000, seed: int = 0):
    return np.random.default_rng(seed).normal(mean, 0.01, n)


def test_dsr_is_a_probability():
    dsr = compute_deflated_sharpe_ratio(_series(0.002), [0.1, 0.12, 0.09, 0.11])
    assert 0.0 <= dsr <= 1.0


def test_strong_alpha_promotes():
    # champion Sharpe well above a low-variance trial cluster -> DSR ~ 1
    dsr = compute_deflated_sharpe_ratio(_series(0.005), list(np.linspace(0.0, 0.1, 9)))
    assert dsr > 0.95
    assert interpret_dsr(dsr) == "promote"


def test_flat_returns_not_significant():
    dsr = compute_deflated_sharpe_ratio(_series(0.0), list(np.linspace(0.0, 0.1, 9)))
    assert dsr < 0.5


def test_dsr_monotonic_in_sharpe():
    trials = list(np.linspace(0.0, 0.1, 9))
    low = compute_deflated_sharpe_ratio(_series(0.001, seed=1), trials)
    high = compute_deflated_sharpe_ratio(_series(0.004, seed=1), trials)
    assert high >= low


def test_expected_max_sharpe_increases_with_trials():
    assert expected_max_sharpe(0.01, 50) > expected_max_sharpe(0.01, 5)


def test_interpret_thresholds():
    assert interpret_dsr(0.3) == "overfit"
    assert interpret_dsr(0.8) == "insignificant"
    assert interpret_dsr(0.96) == "promote"
