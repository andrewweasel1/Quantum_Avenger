import numpy as np
from new_pipeline.evaluation.minbtl import backtest_length_is_sufficient, min_backtest_length


def test_minbtl_increases_with_trials():
    few = min_backtest_length(5, target_sharpe=1.0)
    many = min_backtest_length(500, target_sharpe=1.0)
    assert many > few > 0.0


def test_minbtl_decreases_with_higher_target_sharpe():
    easy = min_backtest_length(100, target_sharpe=2.0)
    hard = min_backtest_length(100, target_sharpe=0.5)
    assert hard > easy


def test_minbtl_guards():
    assert min_backtest_length(100, target_sharpe=0.0) == float("inf")
    assert min_backtest_length(1, target_sharpe=1.0) == 0.0  # no multiplicity with < 2 trials


def test_periods_per_year_scales_to_observations():
    years = min_backtest_length(50, 1.0)
    observations = min_backtest_length(50, 1.0, periods_per_year=252)
    assert np.isclose(observations, years * 252)


def test_sufficiency_check():
    required = min_backtest_length(50, 1.0, periods_per_year=252)
    assert backtest_length_is_sufficient(int(required) + 1, 50, 1.0)
    assert not backtest_length_is_sufficient(int(required) - 1, 50, 1.0)
