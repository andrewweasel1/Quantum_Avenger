import numpy as np
from new_pipeline.evaluation.dsr import (
    compute_deflated_sharpe_ratio,
    expected_max_sharpe,
    min_track_record_length,
    probabilistic_sharpe_ratio,
)


def _series(mean: float, n: int = 1000, seed: int = 0):
    return np.random.default_rng(seed).normal(mean, 0.01, n)


def test_psr_is_a_probability():
    assert 0.0 <= probabilistic_sharpe_ratio(_series(0.002)) <= 1.0


def test_psr_rises_with_sample_length():
    short = probabilistic_sharpe_ratio(_series(0.0015, n=120))
    long = probabilistic_sharpe_ratio(_series(0.0015, n=1500))
    assert long > short


def test_psr_drops_as_benchmark_rises():
    returns = _series(0.003)
    assert probabilistic_sharpe_ratio(returns, 0.0) > probabilistic_sharpe_ratio(returns, 0.2)


def test_dsr_equals_psr_at_expected_max_benchmark():
    # The plan's golden identity: DSR is PSR with the benchmark set to E[max SR].
    returns = _series(0.002)
    trials = list(np.linspace(0.0, 0.1, 9))
    sr0 = expected_max_sharpe(float(np.var(trials, ddof=1)), len(trials))
    psr_at_max = probabilistic_sharpe_ratio(returns, sr0)
    assert psr_at_max == compute_deflated_sharpe_ratio(returns, trials)


def test_mintrl_infinite_when_sharpe_below_benchmark():
    returns = _series(0.001)
    sharpe = returns.mean() / returns.std(ddof=1)
    assert min_track_record_length(returns, benchmark_sr=sharpe + 0.5) == float("inf")


def test_mintrl_finite_and_grows_with_confidence():
    returns = _series(0.003)
    lo = min_track_record_length(returns, 0.0, prob=0.90)
    hi = min_track_record_length(returns, 0.0, prob=0.99)
    assert 0.0 < lo < hi < float("inf")


def test_degenerate_inputs_are_safe():
    assert probabilistic_sharpe_ratio([0.01, 0.01]) == 0.0  # < 3 observations
    assert min_track_record_length([0.01, 0.01]) == float("inf")
