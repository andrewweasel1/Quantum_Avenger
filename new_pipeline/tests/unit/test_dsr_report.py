import numpy as np
import pytest
from new_pipeline.evaluation.dsr import (
    compute_deflated_sharpe_ratio,
    deflated_sharpe_report,
    effective_number_of_trials,
)


def _series(mean: float, n: int = 1000, seed: int = 0):
    return np.random.default_rng(seed).normal(mean, 0.01, n)


def test_report_dsr_matches_compute_when_trials_supplied():
    # Golden consistency: the rich report must agree with the scalar function.
    returns = _series(0.002)
    trials = list(np.linspace(0.0, 0.1, 9))
    report = deflated_sharpe_report(returns, len(trials), trials)
    assert report.dsr == compute_deflated_sharpe_ratio(returns, trials)
    assert report.used_fallback_variance is False
    assert report.n_obs == returns.size
    assert 0.0 <= report.dsr <= 1.0


def test_report_falls_back_to_lo_variance_without_trials():
    report = deflated_sharpe_report(_series(0.003), n_trials=20, trial_sharpes=None)
    assert report.used_fallback_variance is True
    assert report.var_trial_sr > 0.0
    assert 0.0 <= report.dsr <= 1.0


def test_report_zero_dsr_below_min_obs():
    report = deflated_sharpe_report(_series(0.005, n=10), n_trials=5, min_obs=30)
    assert report.dsr == 0.0
    assert report.n_obs == 10


def test_report_sr_annual_is_reporting_only():
    report = deflated_sharpe_report(_series(0.002), n_trials=10, trial_sharpes=[0.1, 0.2, 0.05])
    assert report.sr_annual == pytest.approx(report.sr_period * np.sqrt(252))


def test_more_trials_means_more_deflation():
    returns = _series(0.002)
    trials = list(np.linspace(0.0, 0.1, 9))
    few = deflated_sharpe_report(returns, 2, trials).dsr
    many = deflated_sharpe_report(returns, 500, trials).dsr
    assert few >= many


def test_effective_trials_identical_streams_collapse_to_one():
    base = np.random.default_rng(0).normal(size=200)
    assert effective_number_of_trials(np.tile(base, (8, 1))) == pytest.approx(1.0)


def test_effective_trials_independent_streams_near_n():
    matrix = np.random.default_rng(1).normal(size=(8, 400))
    assert effective_number_of_trials(matrix) > 6.0


def test_effective_trials_degenerate_inputs_are_safe():
    assert effective_number_of_trials(np.zeros((1, 50))) == 1.0
    assert effective_number_of_trials(np.zeros((0, 0))) == 1.0
