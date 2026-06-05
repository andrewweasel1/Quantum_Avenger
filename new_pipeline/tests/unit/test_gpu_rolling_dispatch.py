import numpy as np
from new_pipeline.features.gpu_kernels import (
    compute_rolling_duvol,
    compute_rolling_ncskew,
    rolling_duvol,
    rolling_ncskew,
)


def test_rolling_ncskew_cpu_dispatch_matches():
    returns = np.random.default_rng(0).normal(size=100)
    np.testing.assert_allclose(
        compute_rolling_ncskew(returns, 60, use_gpu=False),
        rolling_ncskew(returns, 60),
        equal_nan=True,
    )


def test_rolling_duvol_cpu_dispatch_matches():
    returns = np.random.default_rng(1).normal(size=100)
    np.testing.assert_allclose(
        compute_rolling_duvol(returns, 60, use_gpu=False),
        rolling_duvol(returns, 60),
        equal_nan=True,
    )
