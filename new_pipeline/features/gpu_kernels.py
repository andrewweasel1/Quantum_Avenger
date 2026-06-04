"""GPU-targeted microstructure kernels with correct CPU fallbacks.

The production target is CUDA (``@cuda.jit`` + CuPy); this module also provides
NumPy CPU implementations so the metrics are correct and testable on a machine
with no GPU (CI / this sandbox). Host dispatchers use the GPU when it is
available and requested, otherwise the CPU path.

Metrics: per-bar spread, Amihud illiquidity, and the crash-risk pair NCSKEW
(negative coefficient of skewness) and DUVOL (down-to-up volatility). The
elementwise pair ship with ``@cuda.jit`` kernels; the reduction pair are CPU
implementations (GPU reductions are a follow-up to be validated on a GPU box).
"""

import math

import numpy as np

try:
    from numba import cuda

    _CUDA_IMPORTABLE = True
except Exception:  # pragma: no cover - import guard for environments w/o numba.cuda
    cuda = None
    _CUDA_IMPORTABLE = False


def gpu_available() -> bool:
    """True only when numba.cuda is importable AND a CUDA device is present."""
    if not _CUDA_IMPORTABLE:
        return False
    try:
        return bool(cuda.is_available())
    except Exception:  # pragma: no cover - driver probing
        return False


# --- CPU implementations (correct, tested) --------------------------------
def cpu_spread_pct(high: np.ndarray, low: np.ndarray) -> np.ndarray:
    high = np.asarray(high, dtype=np.float64)
    low = np.asarray(low, dtype=np.float64)
    mid = (high + low) / 2.0
    result = np.zeros_like(mid)
    np.divide(high - low, mid, out=result, where=mid > 0.0)
    return result


def cpu_amihud(returns: np.ndarray, close: np.ndarray, volume: np.ndarray) -> np.ndarray:
    returns = np.asarray(returns, dtype=np.float64)
    close = np.asarray(close, dtype=np.float64)
    volume = np.asarray(volume, dtype=np.float64)
    dollar_volume = close * volume
    result = np.zeros_like(dollar_volume)
    np.divide(np.abs(returns), dollar_volume, out=result, where=dollar_volume > 0.0)
    return result


def ncskew(returns: np.ndarray) -> float:
    """Negative coefficient of skewness (Chen-Hong-Stein crash-risk measure)."""
    values = np.asarray(returns, dtype=np.float64)
    n = values.size
    if n < 3:
        return 0.0
    centered = values - values.mean()
    sum_sq = float(np.sum(centered**2))
    if sum_sq <= 0.0:
        return 0.0
    sum_cube = float(np.sum(centered**3))
    numerator = n * (n - 1) ** 1.5 * sum_cube
    denominator = (n - 1) * (n - 2) * sum_sq**1.5
    return -numerator / denominator


def duvol(returns: np.ndarray) -> float:
    """Down-to-up volatility: log ratio of down-day vs up-day return variance."""
    values = np.asarray(returns, dtype=np.float64)
    centered = values - values.mean()
    down = centered[centered < 0.0]
    up = centered[centered >= 0.0]
    if down.size < 2 or up.size < 2:
        return 0.0
    down_var = float(np.sum(down**2))
    up_var = float(np.sum(up**2))
    if down_var <= 0.0 or up_var <= 0.0:
        return 0.0
    return math.log(((up.size - 1) * down_var) / ((down.size - 1) * up_var))


# --- CUDA kernels (compiled lazily; exercised on a GPU box) ----------------
if _CUDA_IMPORTABLE:

    @cuda.jit
    def _spread_kernel(high, low, out):  # pragma: no cover - requires a GPU
        i = cuda.grid(1)
        if i < high.size:
            mid = (high[i] + low[i]) / 2.0
            out[i] = (high[i] - low[i]) / mid if mid > 0.0 else 0.0

    @cuda.jit
    def _amihud_kernel(returns, close, volume, out):  # pragma: no cover - requires a GPU
        i = cuda.grid(1)
        if i < returns.size:
            dollar_volume = close[i] * volume[i]
            out[i] = abs(returns[i]) / dollar_volume if dollar_volume > 0.0 else 0.0


def _launch(kernel, size, *arrays):  # pragma: no cover - requires a GPU
    out = np.empty(size, dtype=np.float64)
    threads = 256
    blocks = (size + threads - 1) // threads
    device_args = [cuda.to_device(np.ascontiguousarray(a, dtype=np.float64)) for a in arrays]
    device_out = cuda.to_device(out)
    kernel[blocks, threads](*device_args, device_out)
    return device_out.copy_to_host()


def compute_spread_pct(high: np.ndarray, low: np.ndarray, use_gpu: bool = False) -> np.ndarray:
    if use_gpu and gpu_available():  # pragma: no cover - requires a GPU
        return _launch(_spread_kernel, high.size, high, low)
    return cpu_spread_pct(high, low)


def compute_amihud(
    returns: np.ndarray, close: np.ndarray, volume: np.ndarray, use_gpu: bool = False
) -> np.ndarray:
    if use_gpu and gpu_available():  # pragma: no cover - requires a GPU
        return _launch(_amihud_kernel, returns.size, returns, close, volume)
    return cpu_amihud(returns, close, volume)
