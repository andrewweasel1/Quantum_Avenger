"""Unit tests for the multiple-strategy reality checks (offense roadmap P4, §J).

White's RC and Hansen's SPA must flag a genuinely skilled best-of-K strategy (low
p) and stay agnostic on pure noise (high p), accept a single strategy, guard short
inputs, and be deterministic under a fixed seed. Golden p-values live in
tests/golden/test_reality_check_golden.py.
"""

import numpy as np
from new_pipeline.evaluation.reality_check import hansens_spa, whites_reality_check


def _skilled_and_noise():
    rng = np.random.default_rng(7)
    noise = rng.normal(0, 0.01, (252, 20))
    skilled = rng.normal(0, 0.01, (252, 20))
    skilled[:, 0] += 0.004  # one genuine ~0.4%/day edge among 19 noise strategies
    return skilled, noise


def test_skilled_best_strategy_low_pvalue():
    skilled, _ = _skilled_and_noise()
    assert whites_reality_check(skilled, n_bootstrap=500, seed=1) < 0.05
    assert hansens_spa(skilled, n_bootstrap=500, seed=1) < 0.05


def test_pure_noise_high_pvalue():
    _, noise = _skilled_and_noise()
    assert whites_reality_check(noise, n_bootstrap=500, seed=1) > 0.4
    assert hansens_spa(noise, n_bootstrap=500, seed=1) > 0.4


def test_accepts_single_strategy():
    skilled, _ = _skilled_and_noise()
    p = whites_reality_check(skilled[:, 0], n_bootstrap=200, seed=1)
    assert 0.0 < p < 0.05  # 1-D input reshaped to a single column


def test_short_input_guards_return_one():
    assert whites_reality_check(np.zeros((1, 3))) == 1.0  # T < 2
    assert hansens_spa(np.zeros((2, 3))) == 1.0  # T < 3


def test_deterministic_under_seed():
    skilled, _ = _skilled_and_noise()
    a = whites_reality_check(skilled, n_bootstrap=200, seed=3)
    b = whites_reality_check(skilled, n_bootstrap=200, seed=3)
    assert a == b


def test_pvalue_in_unit_interval():
    skilled, noise = _skilled_and_noise()
    for matrix in (skilled, noise):
        for fn in (whites_reality_check, hansens_spa):
            assert 0.0 < fn(matrix, n_bootstrap=100, seed=5) <= 1.0
