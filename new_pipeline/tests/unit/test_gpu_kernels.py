import numpy as np
import pytest
from new_pipeline.features.gpu_kernels import (
    compute_amihud,
    compute_spread_pct,
    cpu_amihud,
    cpu_spread_pct,
    duvol,
    gpu_available,
    ncskew,
)


def test_cpu_spread_pct_golden():
    high = np.array([2.0, 3.0])
    low = np.array([1.0, 1.0])
    np.testing.assert_allclose(cpu_spread_pct(high, low), [1.0 / 1.5, 2.0 / 2.0])


def test_cpu_amihud_golden():
    out = cpu_amihud(np.array([0.02]), np.array([100.0]), np.array([1000.0]))
    np.testing.assert_allclose(out, [0.02 / 100_000.0])


def test_amihud_zero_volume_is_zero():
    out = cpu_amihud(np.array([0.02]), np.array([100.0]), np.array([0.0]))
    assert out[0] == 0.0


def test_ncskew_symmetric_is_zero():
    assert abs(ncskew(np.array([1.0, -1.0, 2.0, -2.0, 3.0, -3.0]))) < 1e-9


def test_ncskew_positive_for_crashy_returns():
    crashy = np.array([0.01, 0.012, 0.009, 0.011, -0.10, 0.01, 0.008])
    assert ncskew(crashy) > 0.0  # left tail -> negative skew -> NCSKEW > 0


def test_duvol_positive_when_downside_more_volatile():
    returns = np.array([0.01, 0.01, 0.01, -0.05, -0.06, -0.04])
    assert duvol(returns) > 0.0


def test_dispatch_uses_cpu_when_gpu_not_requested():
    high = np.array([2.0, 3.0, 4.0])
    low = np.array([1.0, 1.5, 2.0])
    np.testing.assert_allclose(
        compute_spread_pct(high, low, use_gpu=False), cpu_spread_pct(high, low)
    )
    returns, close, volume = np.array([0.01]), np.array([100.0]), np.array([1e6])
    np.testing.assert_allclose(
        compute_amihud(returns, close, volume, use_gpu=False),
        cpu_amihud(returns, close, volume),
    )


def test_gpu_available_returns_bool():
    assert isinstance(gpu_available(), bool)


@pytest.mark.skipif(not gpu_available(), reason="no CUDA device")
def test_gpu_matches_cpu():  # pragma: no cover - runs only on a GPU box
    high, low = np.array([2.0, 3.0, 4.0]), np.array([1.0, 1.5, 2.0])
    np.testing.assert_allclose(
        compute_spread_pct(high, low, use_gpu=True), cpu_spread_pct(high, low)
    )
