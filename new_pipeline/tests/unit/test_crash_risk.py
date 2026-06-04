import numpy as np
from new_pipeline.features.gpu_kernels import ncskew, rolling_duvol, rolling_ncskew


def test_rolling_ncskew_shape_and_leading_nan():
    returns = np.random.default_rng(0).normal(size=100)
    out = rolling_ncskew(returns, 60)
    assert out.shape == (100,)
    assert np.isnan(out[:59]).all()
    assert np.isfinite(out[59:]).all()


def test_rolling_duvol_shape_and_leading_nan():
    returns = np.random.default_rng(0).normal(size=100)
    out = rolling_duvol(returns, 60)
    assert out.shape == (100,)
    assert np.isnan(out[:59]).all()
    assert np.isfinite(out[59:]).all()


def test_rolling_ncskew_matches_scalar_on_full_window():
    returns = np.random.default_rng(2).normal(size=60)
    out = rolling_ncskew(returns, 60)
    assert abs(out[-1] - ncskew(returns)) < 1e-9


def test_rolling_too_short_is_all_nan():
    assert np.isnan(rolling_ncskew(np.zeros(10), 60)).all()
