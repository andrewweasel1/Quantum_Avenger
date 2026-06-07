import numpy as np
import pytest
from new_pipeline.evaluation.haircut import (
    haircut_sharpe_ratio,
    minimum_profit_hurdle,
    multiple_testing_adjust,
)


def test_bonferroni_scales_by_count():
    assert np.allclose(multiple_testing_adjust([0.01, 0.02], "bonferroni"), [0.02, 0.04])


def test_adjusted_pvalues_stay_in_range_and_never_shrink():
    p = np.array([0.001, 0.02, 0.03, 0.04])
    for method in ("holm", "bhy"):
        adj = multiple_testing_adjust(p, method)
        assert np.all(adj >= p - 1e-12)  # adjustment only inflates p-values
        assert np.all((adj >= 0.0) & (adj <= 1.0))


def test_haircut_never_exceeds_observed_and_decays_with_trials():
    base = haircut_sharpe_ratio(1.5, n_obs=2520, n_trials=1)
    few = haircut_sharpe_ratio(1.5, n_obs=2520, n_trials=10)
    many = haircut_sharpe_ratio(1.5, n_obs=2520, n_trials=200)
    assert base.adjusted_sharpe <= 1.5 + 1e-9
    assert many.adjusted_sharpe < few.adjusted_sharpe < base.adjusted_sharpe
    assert 0.0 <= many.haircut_fraction <= 1.0


def test_haircut_handles_nonpositive_sharpe():
    res = haircut_sharpe_ratio(-0.5, n_obs=2520, n_trials=10)
    assert res.adjusted_sharpe == 0.0
    assert res.haircut_fraction == 0.0


def test_minimum_hurdle_rises_with_trials():
    one = minimum_profit_hurdle(2520, n_trials=1)
    many = minimum_profit_hurdle(2520, n_trials=100)
    assert many > one > 0.0


def test_unknown_method_raises():
    with pytest.raises(ValueError):
        multiple_testing_adjust([0.1], "bogus")
