# Phase 2: Vectorized Quant Engine & Numba Shields - Detailed Specification

> **Implementation status: ✅ DONE (grew past spec).** The Polars feature engine, Numba `@njit` Shield (5 veto gates) and hydrodynamic slippage are implemented in `new_pipeline/features/`. **Beyond the spec:** an asymmetric `sentiment_volatility_gate` was added beside the 5 gates, and triple‑barrier labels replaced the original target. The `@cuda.jit` kernels exist but the **CPU fallback is the CI default** (GPU‑box validation deferred — see IMPLEMENTATION_STATUS §6). *Original build spec; current state in `ARCHITECTURE_ROADMAP.md` + `quantitative_math.md`.*

**Duration**: 2 weeks  
**Target Date**: Complete by mid-June (after Phase 1)  
**Success Criteria**: All features vectorized; GPU kernels passing benchmarks; Shield Agent <100µs latency; 85%+ test coverage

---

## 1. Phase 2 Architecture Overview

### 1.1 System Context (Integration with Phase 1)

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1 (Complete): Config, Logging, Exceptions, Testing  │
├─────────────────────────────────────────────────────────────┤
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PHASE 2: VECTORIZED QUANT ENGINE & SHIELDS        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                      │   │
│  │  LAYER 1: POLARS LAZY-FRAME VECTORIZATION          │   │
│  │  ├─ Rolling window calculations                     │   │
│  │  ├─ Volatility regime tagging                       │   │
│  │  ├─ Log return transforms                           │   │
│  │  └─ Factor normalization                            │   │
│  │                                                      │   │
│  │  LAYER 2: CUDA/NUMBA GPU KERNELS                    │   │
│  │  ├─ Spread calculations (high-low)                  │   │
│  │  ├─ Amihud illiquidity metric                       │   │
│  │  ├─ Non-cash skewness (NCSKEW)                      │   │
│  │  ├─ Down/Up volume asymmetry (DUVOL)               │   │
│  │  └─ Correlation matrices                            │   │
│  │                                                      │   │
│  │  LAYER 3: THE SHIELD AGENT (NUMBA JIT)             │   │
│  │  ├─ Position sizing logic (Kelly-like)              │   │
│  │  ├─ Stop loss validation (2×ATR)                    │   │
│  │  ├─ Dynamic slippage calculation                    │   │
│  │  ├─ Liquidity checks (ADV coverage)                 │   │
│  │  ├─ Portfolio reconciliation                        │   │
│  │  └─ Microsecond latency execution                   │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│         Uses Phase 1: Config, Logger, Exceptions             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

```
/new_pipeline/features/
├── __init__.py
├── base.py                    # Abstract FeatureEngine
├── registry.py                # Feature metadata tracking
├── polars_engine.py           # ✨ NEW: Polars vectorized ops
├── gpu_kernels.py             # ✨ NEW: CUDA @cuda.jit functions
├── shields.py                 # ✨ NEW: Shield Agent (Numba JIT)
├── slippage.py                # ✨ NEW: Dynamic slippage model
└── tests/
    ├── test_polars_features.py
    ├── test_gpu_kernels.py
    ├── test_shield_agent.py
    ├── test_slippage.py
    └── benchmarks/
        ├── bench_polars_vs_pandas.py
        ├── bench_gpu_kernels.py
        └── bench_shield_agent_latency.py
```

---

## 2. Polars Vectorized Feature Engine

### 2.1 Architecture & Principle

**Principle**: Replace all pandas `.apply()` loops with Polars lazy-frame expressions. Defer computation until `.collect()`.

```python
# ❌ PANDAS (Slow - row-by-row):
for idx, row in df.iterrows():
    atr[idx] = calculate_atr(row)

# ✅ POLARS (Fast - vectorized):
df = df.with_columns(
    pl.col('close').rolling_mean(14).alias('atr')
)
```

### 2.2 Module: `features/polars_engine.py`

**File Structure**:
```
PolarsFeatureEngine
├── __init__()
├── load_raw_vault() → LazyFrame
├── compute_returns() → LazyFrame
├── compute_rolling_indicators() → LazyFrame
├── compute_microstructure() → LazyFrame
├── compute_volatility_regimes() → LazyFrame
├── normalize_features() → LazyFrame
├── execute_pipeline() → DataFrame (collected)
└── to_parquet() → Path
```

### 2.3 Feature Functions (Detailed Signatures)

#### 2.3.1 Basic Technical Indicators

**Function: `compute_returns()`**
```python
def compute_returns(
    df: pl.LazyFrame,
    price_col: str = "close",
    log_returns: bool = True
) -> pl.LazyFrame:
    """Compute returns (arithmetic or log).
    
    Args:
        df: Lazy DataFrame with OHLCV data.
        price_col: Column name to compute returns from.
        log_returns: If True, use log returns; else simple.
    
    Returns:
        DataFrame with 'returns' column appended.
    
    Formula:
        - Arithmetic: returns[t] = (price[t] - price[t-1]) / price[t-1]
        - Log: returns[t] = ln(price[t] / price[t-1])
    
    Notes:
        - First row is NaN (no prior price).
        - Shift by -1 to align signal at t+1 (no look-ahead).
    """
    if log_returns:
        return df.with_columns(
            pl.col(price_col).log().diff().alias('returns')
        )
    else:
        return df.with_columns(
            (pl.col(price_col).pct_change()).alias('returns')
        )
```

**Function: `compute_atr()`**
```python
def compute_atr(
    df: pl.LazyFrame,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    period: int = 14
) -> pl.LazyFrame:
    """Compute Average True Range (Wilder's smoothing).
    
    Args:
        df: Lazy DataFrame with OHLCV data.
        period: Lookback window (default 14).
    
    Returns:
        DataFrame with 'atr' column.
    
    Formula:
        TR[t] = max(high[t] - low[t], |high[t] - close[t-1]|, |low[t] - close[t-1]|)
        ATR[t] = SMA(TR, period) using Wilder's smoothing (cumsum / n)
    
    Internal:
        - Use Polars' rolling_mean with window=period
        - First period-1 rows are NaN
    """
    # True Range calculation
    tr = pl.max_horizontal(
        pl.col(high_col) - pl.col(low_col),
        (pl.col(high_col) - pl.col(close_col).shift(1)).abs(),
        (pl.col(low_col) - pl.col(close_col).shift(1)).abs()
    )
    
    return df.with_columns(
        tr.rolling_mean(period).alias('atr')
    )
```

**Function: `compute_adv()`**
```python
def compute_adv(
    df: pl.LazyFrame,
    volume_col: str = "volume",
    high_col: str = "high",
    low_col: str = "low",
    period: int = 20
) -> pl.LazyFrame:
    """Compute Average Dollar Volume (ADV).
    
    Args:
        period: Lookback window (default 20).
    
    Returns:
        DataFrame with 'adv_20' column.
    
    Formula:
        ADV[t] = SMA((high[t] + low[t]) / 2 * volume[t], period)
    
    Notes:
        - Used for liquidity checks in Shield Agent
        - First period-1 rows are NaN
    """
    avg_price = (pl.col(high_col) + pl.col(low_col)) / 2
    dollar_volume = avg_price * pl.col(volume_col)
    
    return df.with_columns(
        dollar_volume.rolling_mean(period).alias('adv_20')
    )
```

#### 2.3.2 Volatility & Regime Detection

**Function: `compute_rolling_volatility()`**
```python
def compute_rolling_volatility(
    df: pl.LazyFrame,
    returns_col: str = "returns",
    window: int = 15,
    annualize: bool = True
) -> pl.LazyFrame:
    """Compute rolling volatility (standard deviation).
    
    Args:
        window: Lookback period (default 15 = 15-minute bars).
        annualize: If True, scale by √252 (trading days).
    
    Returns:
        DataFrame with 'volatility' column.
    
    Formula:
        vol[t] = std(returns[t-window:t])
        vol_annual[t] = vol[t] * √252 (if annualize)
    
    Usage:
        - Determine volatility regime (low, normal, high)
        - Scale position size in high-vol environments
    """
    scale = np.sqrt(252) if annualize else 1.0
    
    return df.with_columns(
        pl.col(returns_col).rolling_std(window).mul(scale).alias('volatility')
    )
```

**Function: `tag_volatility_regimes()`**
```python
def tag_volatility_regimes(
    df: pl.LazyFrame,
    volatility_col: str = "volatility",
    percentile_threshold: float = 0.80
) -> pl.LazyFrame:
    """Tag high/normal volatility regimes.
    
    Args:
        volatility_col: Column containing rolling volatility.
        percentile_threshold: If vol > this percentile, tag as 'high'.
    
    Returns:
        DataFrame with 'regime' column: 0 (normal) or 1 (high).
    
    Formula:
        threshold = percentile(volatility, 80)
        regime[t] = 1 if volatility[t] > threshold else 0
    
    Notes:
        - Used to dynamically adjust lookback windows
        - High vol → shorter windows (recent > history)
    """
    # Compute 80th percentile of volatility
    threshold = df.select(pl.col(volatility_col).quantile(percentile_threshold))
    
    return df.with_columns(
        (pl.col(volatility_col) > threshold).cast(pl.Int8).alias('regime')
    )
```

#### 2.3.3 Microstructure Features

**Function: `compute_spreads()`**
```python
def compute_spreads(
    df: pl.LazyFrame,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close"
) -> pl.LazyFrame:
    """Compute bid-ask spread as percent of mid-price.
    
    Args:
        high_col, low_col, close_col: OHLC columns.
    
    Returns:
        DataFrame with 'spread_pct' column.
    
    Formula:
        mid = (high + low) / 2
        spread = (high - low) / mid * 100  [basis points]
    
    Notes:
        - High spread → illiquid, larger slippage
        - Used in Shield Agent slippage calculation
    """
    mid = (pl.col(high_col) + pl.col(low_col)) / 2
    spread = (pl.col(high_col) - pl.col(low_col)) / mid * 100
    
    return df.with_columns(spread.alias('spread_pct'))
```

**Function: `compute_amihud_illiquidity()`**
```python
def compute_amihud_illiquidity(
    df: pl.LazyFrame,
    returns_col: str = "returns",
    volume_col: str = "volume",
    high_col: str = "high",
    low_col: str = "low"
) -> pl.LazyFrame:
    """Compute Amihud illiquidity measure.
    
    Args:
        returns_col: Log returns column.
        volume_col: Trading volume.
    
    Returns:
        DataFrame with 'amihud' column.
    
    Formula:
        amihud[t] = |returns[t]| / (volume[t] * price[t])
        Higher value → more illiquid
    
    Interpretation:
        - amihud < 0.001: Highly liquid
        - 0.001 - 0.01: Normal liquidity
        - > 0.01: Illiquid, large slippage expected
    
    GPU Implementation:
        - Computed in @cuda.jit kernel for speed
    """
    mid_price = (pl.col(high_col) + pl.col(low_col)) / 2
    
    return df.with_columns(
        (pl.col(returns_col).abs() / (pl.col(volume_col) * mid_price))
        .alias('amihud')
    )
```

### 2.4 Pipeline Orchestration

**Function: `execute_feature_pipeline()`**
```python
def execute_feature_pipeline(
    raw_vault_path: str,
    sector: str,
    target_vault_path: str,
    config: AppConfig
) -> None:
    """End-to-end feature compilation pipeline.
    
    Args:
        raw_vault_path: Path to RAW_VAULT_DIR/sector={sector}/
        sector: Sector name (e.g., "Technology").
        target_vault_path: Output PROCESSED_VAULT_DIR/sector={sector}/
        config: AppConfig for feature settings.
    
    Flow:
        1. Load all Parquet files as LazyFrame (lazy evaluation)
        2. Compute returns (log & arithmetic)
        3. Compute rolling indicators (ATR, ADV, volatility)
        4. Tag volatility regimes
        5. Compute microstructure (spreads, Amihud)
        6. Normalize features (z-score, min-max as needed)
        7. Collect → persist to Parquet
    
    Notes:
        - All operations are lazy until .collect()
        - GPU kernels triggered during collection
        - Memory efficient: processes in row groups
    """
    logger = get_logger(__name__)
    
    # Load raw vault
    df = pl.scan_parquet(f"{raw_vault_path}/*.parquet")
    
    # Apply transformations (all lazy)
    df = compute_returns(df)
    df = compute_atr(df)
    df = compute_adv(df)
    df = compute_rolling_volatility(df)
    df = tag_volatility_regimes(df)
    df = compute_spreads(df)
    df = compute_amihud_illiquidity(df)
    
    # Collect & persist
    logger.info(f"Collecting features for {sector}...")
    result = df.collect()
    
    result.write_parquet(
        f"{target_vault_path}/{sector}_features.parquet",
        row_group_size=config.data.row_group_size
    )
    
    logger.info(f"Features written to {target_vault_path}")
```

---

## 3. GPU Kernels via CUDA & Numba

### 3.1 Architecture: From CPU to GPU

```
CPU (Polars)          GPU (CUDA Kernels)
─────────────────────────────────────────
OHLCV data       ──→  Copy to VRAM
(Parquet)            ↓
                  Execute @cuda.jit kernels
                  ├─ Spread calc
                  ├─ Amihud illiquidity
                  ├─ NCSKEW (skewness)
                  ├─ DUVOL (asymmetry)
                  └─ Correlations
                     ↓
Result (GPU mem) ───← Copy back to CPU
(np.ndarray)         ↓
                  Convert to Polars
                  Append to DataFrame
```

### 3.2 Module: `features/gpu_kernels.py`

**Header & Imports**:
```python
import numpy as np
from numba import cuda, jit, prange
import logging

logger = get_logger(__name__)

# CUDA configuration
THREADS_PER_BLOCK = 256
BLOCKS_PER_GRID = 128
```

#### 3.2.1 GPU Kernel: Spread Calculation

**Function: `kernel_spreads()`**
```python
@cuda.jit
def kernel_spreads(highs, lows, closes, out_spreads):
    """CUDA kernel: Compute bid-ask spreads (high-low normalized).
    
    Args:
        highs: [n] array of high prices
        lows: [n] array of low prices
        closes: [n] array of close prices (for NaN checking)
        out_spreads: [n] output array (preallocated on GPU)
    
    Formula (per thread):
        mid = (high + low) / 2
        spread_pct = (high - low) / mid * 100
        If any input is NaN: output NaN
    
    Thread Config:
        - 1 thread per element
        - Grid-stride loop for large arrays
    
    Memory:
        - Read-only: highs, lows, closes
        - Write: out_spreads
    """
    i = cuda.grid(1)
    
    if i < highs.shape[0]:
        high = highs[i]
        low = lows[i]
        
        if np.isnan(high) or np.isnan(low):
            out_spreads[i] = np.nan
        else:
            mid = (high + low) / 2.0
            if mid > 0:
                out_spreads[i] = (high - low) / mid * 100.0
            else:
                out_spreads[i] = np.nan
```

**Wrapper: `compute_spreads_gpu()`**
```python
def compute_spreads_gpu(
    highs: np.ndarray,
    lows: np.ndarray,
    closes: np.ndarray,
    fallback_to_cpu: bool = True
) -> np.ndarray:
    """Compute spreads on GPU; fallback to CPU if needed.
    
    Args:
        highs, lows, closes: CPU numpy arrays
        fallback_to_cpu: If True, use CPU if GPU fails
    
    Returns:
        Spreads array on CPU
    
    Memory Management:
        - Check VRAM availability
        - Copy arrays to GPU
        - Execute kernel
        - Copy results back to CPU
        - Free GPU memory
    """
    try:
        # Check VRAM
        free_vram = cuda.current_context().get_memory_info()[0]
        required = highs.nbytes * 4  # 4 arrays
        
        if free_vram < required:
            if fallback_to_cpu:
                logger.warning(f"Insufficient VRAM ({free_vram/1e9:.1f}GB); using CPU")
                return compute_spreads_cpu(highs, lows, closes)
            else:
                raise CUDAOutOfMemoryError(...)
        
        # Allocate GPU memory
        d_highs = cuda.to_device(highs)
        d_lows = cuda.to_device(lows)
        d_closes = cuda.to_device(closes)
        d_spreads = cuda.device_array_like(highs)
        
        # Configure grid/block
        threads_per_block = 256
        blocks_per_grid = (highs.shape[0] + threads_per_block - 1) // threads_per_block
        
        # Execute
        kernel_spreads[blocks_per_grid, threads_per_block](
            d_highs, d_lows, d_closes, d_spreads
        )
        
        # Copy back
        result = d_spreads.copy_to_host()
        
        # Free GPU memory
        d_highs.free()
        d_lows.free()
        d_closes.free()
        d_spreads.free()
        
        return result
        
    except CudaAPIError as e:
        if fallback_to_cpu:
            logger.warning(f"CUDA error: {e}; falling back to CPU")
            return compute_spreads_cpu(highs, lows, closes)
        else:
            raise
```

#### 3.2.2 GPU Kernel: Amihud Illiquidity

**Function: `kernel_amihud()`**
```python
@cuda.jit
def kernel_amihud(returns, volumes, highs, lows, out_amihud):
    """CUDA kernel: Compute Amihud illiquidity measure.
    
    Args:
        returns: [n] log returns
        volumes: [n] daily volumes
        highs, lows: [n] OHLC prices for mid calculation
        out_amihud: [n] output
    
    Formula (per thread):
        mid = (high + low) / 2
        amihud[i] = |returns[i]| / (volume[i] * mid[i])
    
    Performance:
        - Single pass, O(n) complexity
        - Suitable for large arrays (millions of rows)
    """
    i = cuda.grid(1)
    
    if i < returns.shape[0]:
        ret = returns[i]
        vol = volumes[i]
        high = highs[i]
        low = lows[i]
        
        if np.isnan(ret) or vol <= 0:
            out_amihud[i] = np.nan
        else:
            mid = (high + low) / 2.0
            if mid > 0:
                out_amihud[i] = np.abs(ret) / (vol * mid)
            else:
                out_amihud[i] = np.nan
```

#### 3.2.3 GPU Kernel: Non-Cash Skewness (NCSKEW)

**Function: `kernel_ncskew()`**
```python
@cuda.jit
def kernel_ncskew(returns, window, out_ncskew):
    """CUDA kernel: Compute non-cash skewness (downside asymmetry).
    
    Args:
        returns: [n] log returns
        window: lookback period (e.g., 20 days)
        out_ncskew: [n] output
    
    Formula (per thread i, for i >= window):
        mean = avg(returns[i-window:i])
        std = stddev(returns[i-window:i])
        downside_sq = sum(min(returns[j] - mean, 0)^2 for j in window)
        upside_sq = sum(max(returns[j] - mean, 0)^2 for j in window)
        NCSKEW[i] = -(downside_sq^(3/2) - upside_sq^(3/2)) / (std^3 * n)
    
    Interpretation:
        - NCSKEW < 0: Negative skew, downside tail risk (bad)
        - NCSKEW > 0: Positive skew, upside potential (good)
    
    Implementation Note:
        - Expensive: requires rolling window statistics
        - Offload to GPU for speed
    """
    i = cuda.grid(1)
    
    if i >= window and i < returns.shape[0]:
        # Extract window
        window_start = i - window
        window_returns = returns[window_start:i]
        
        # Compute mean, std
        mean = 0.0
        for j in range(window):
            mean += window_returns[j]
        mean /= window
        
        # Compute variance
        var = 0.0
        for j in range(window):
            diff = window_returns[j] - mean
            var += diff * diff
        var /= window
        std = np.sqrt(var)
        
        # Compute skewness (downside vs upside)
        down_sum = 0.0
        up_sum = 0.0
        for j in range(window):
            diff = window_returns[j] - mean
            if diff < 0:
                down_sum += diff * diff
            else:
                up_sum += diff * diff
        
        down_sum = np.power(down_sum, 1.5)
        up_sum = np.power(up_sum, 1.5)
        
        denom = np.power(std, 3.0) * window
        if denom > 0:
            out_ncskew[i] = -(down_sum - up_sum) / denom
        else:
            out_ncskew[i] = np.nan
    else:
        out_ncskew[i] = np.nan
```

#### 3.2.4 GPU Kernel: Down/Up Volume Asymmetry (DUVOL)

**Function: `kernel_duvol()`**
```python
@cuda.jit
def kernel_duvol(returns, volumes, window, out_duvol):
    """CUDA kernel: Compute down/up volume asymmetry.
    
    Args:
        returns: [n] log returns
        volumes: [n] volumes
        window: lookback period
        out_duvol: [n] output
    
    Formula (per thread i):
        down_vol = sum(volume[j] for j if returns[j] < 0)
        up_vol = sum(volume[j] for j if returns[j] > 0)
        DUVOL[i] = log(down_vol / up_vol)
    
    Interpretation:
        - DUVOL > 0: More volume on down days (sell pressure)
        - DUVOL < 0: More volume on up days (buy pressure)
    
    Notes:
        - Used to detect selling pressure (bearish signal)
    """
    i = cuda.grid(1)
    
    if i >= window and i < returns.shape[0]:
        window_start = i - window
        
        down_vol = 0.0
        up_vol = 0.0
        
        for j in range(window_start, i):
            if returns[j] < 0:
                down_vol += volumes[j]
            elif returns[j] > 0:
                up_vol += volumes[j]
        
        if up_vol > 0:
            out_duvol[i] = np.log(down_vol / up_vol)
        else:
            out_duvol[i] = np.nan
    else:
        out_duvol[i] = np.nan
```

### 3.3 GPU Kernel Testing & Benchmarking

**File: `tests/benchmarks/bench_gpu_kernels.py`**

```python
import pytest
import numpy as np
import time
from features.gpu_kernels import (
    compute_spreads_gpu,
    compute_amihud_gpu,
    compute_ncskew_gpu,
    compute_duvol_gpu
)
from features.polars_engine import (  # CPU equivalents
    compute_spreads_cpu,
    compute_amihud_cpu,
    compute_ncskew_cpu,
    compute_duvol_cpu
)

@pytest.mark.benchmark
def test_spreads_gpu_vs_cpu(benchmark):
    """Benchmark GPU vs CPU spread calculation."""
    n = 10_000_000
    highs = np.random.randn(n).cumsum() + 100
    lows = highs - np.abs(np.random.randn(n))
    closes = (highs + lows) / 2
    
    # GPU
    gpu_time = benchmark(
        compute_spreads_gpu,
        highs, lows, closes
    )
    
    # CPU (for comparison)
    cpu_start = time.time()
    cpu_result = compute_spreads_cpu(highs, lows, closes)
    cpu_time = time.time() - cpu_start
    
    # GPU should be 10-50x faster
    speedup = cpu_time / gpu_time
    print(f"Speedup: {speedup:.1f}x")
    assert speedup > 10, f"GPU speedup too low: {speedup:.1f}x"

@pytest.mark.benchmark
def test_amihud_gpu_vs_cpu(benchmark):
    """Benchmark GPU Amihud calculation."""
    n = 1_000_000
    returns = np.random.randn(n) * 0.02
    volumes = np.random.randint(1e6, 1e7, n)
    highs = np.random.randn(n).cumsum() + 100
    lows = highs - np.abs(np.random.randn(n))
    
    gpu_time = benchmark(
        compute_amihud_gpu,
        returns, volumes, highs, lows
    )
    
    cpu_start = time.time()
    cpu_result = compute_amihud_cpu(returns, volumes, highs, lows)
    cpu_time = time.time() - cpu_start
    
    speedup = cpu_time / gpu_time
    assert speedup > 5, f"GPU speedup too low: {speedup:.1f}x"
```

---

## 4. The Shield Agent: Numba JIT Risk Manager

### 4.1 Architecture

**Principle**: Deterministic risk veto gates executed in microseconds using Numba JIT compilation.

```
ML Signal (probability > threshold)
         │
         ▼
    ┌──────────────────────────────────┐
    │  SHIELD AGENT (Numba @njit)     │
    ├──────────────────────────────────┤
    │                                  │
    │  GATE 1: Stop Loss Validity      │
    │  ├─ stop > 0                     │
    │  ├─ entry > stop                 │
    │  └─ return (VETO if fail)        │
    │                                  │
    │  GATE 2: Position Sizing (Kelly) │
    │  ├─ risk_dist = entry - stop     │
    │  ├─ size = (cap × max_risk) / risk │
    │  ├─ size = min(size, max_qty)    │
    │  └─ return (VETO if size < 1)    │
    │                                  │
    │  GATE 3: Liquidity Check         │
    │  ├─ order_size ≤ 25% ADV         │
    │  └─ return (VETO if fail)        │
    │                                  │
    │  GATE 4: Slippage Estimate       │
    │  ├─ s = c·σ·√(Q/V)               │
    │  ├─ s ≤ 50 bps limit             │
    │  └─ return (VETO if fail)        │
    │                                  │
    │  GATE 5: Portfolio Sync          │
    │  ├─ new_qty = size - current     │
    │  ├─ new_qty > 0 (don't overallocate) │
    │  └─ return (VETO if fail)        │
    │                                  │
    └──────────────────────────────────┘
         │
         ├─ ALL GATES PASS → (True, size)
         └─ ANY GATE FAILS → (False, 0)
```

### 4.2 Module: `features/shields.py`

**File: `features/shields.py`**

```python
from numba import njit
import numpy as np
import logging

logger = get_logger(__name__)

# Configuration constants
DEFAULT_ATR_MULTIPLIER = 2.0
DEFAULT_MAX_RISK_PCT = 0.02
DEFAULT_MAX_ORDER_COVERAGE = 0.25
DEFAULT_MAX_SLIPPAGE_BPS = 50.0
SLIPPAGE_CONSTANT = 0.5  # Empirically calibrated
```

#### 4.2.1 Core Shield Agent Function

**Function: `evaluate_risk_veto_gates()`**
```python
@njit(fastmath=True)
def evaluate_risk_veto_gates(
    entry_price: float,
    atr: float,
    atr_multiplier: float,
    account_capital: float,
    max_risk_pct: float,
    current_qty: float,
    adv_20: float,
    volume_today: float,
    volatility: float
) -> tuple:
    """Evaluate all risk gates and return (approved, position_size).
    
    Args:
        entry_price: Entry price for the trade.
        atr: Current ATR (volatility measure).
        atr_multiplier: How many ATRs for stop loss (typically 2.0).
        account_capital: Total available capital.
        max_risk_pct: Max capital at risk per trade (typically 0.02).
        current_qty: Current position size in this ticker (for delta).
        adv_20: 20-day average dollar volume.
        volume_today: Today's observed volume so far.
        volatility: Current volatility (for slippage adjustment).
    
    Returns:
        (approved: bool, position_size: float)
        - If approved: position_size is recommended qty
        - If veto: position_size is 0
    
    Execution Time:
        - Target: < 100 microseconds (all gates)
        - fastmath=True enables CPU optimizations
    
    Veto Reasons (logged separately):
        - "invalid_stop_loss"
        - "insufficient_capital"
        - "order_too_large"
        - "slippage_exceeded"
        - "liquidity_insufficient"
    
    Notes:
        - Deterministic: no random, no external calls
        - GPU-safe: can be launched from CUDA kernels
    """
    
    # GATE 1: Stop Loss Validity
    # ─────────────────────────
    stop_loss = entry_price - (atr_multiplier * atr)
    risk_per_share = entry_price - stop_loss
    
    if risk_per_share <= 0 or entry_price <= 0:
        return (False, 0.0)
    
    if stop_loss <= 0:
        # Veto: stop would be negative
        return (False, 0.0)
    
    # GATE 2: Position Sizing (Kelly-like)
    # ──────────────────────────────────
    capital_at_risk = account_capital * max_risk_pct
    position_size = capital_at_risk / risk_per_share
    
    # Cap by available capital
    max_allowable_qty = account_capital / entry_price
    position_size = min(position_size, max_allowable_qty)
    
    # Floor to avoid fractional shares
    position_size = int(position_size)
    
    if position_size < 1:
        return (False, 0.0)
    
    # GATE 3: Liquidity Check (ADV Coverage)
    # ───────────────────────────────────
    order_size_usd = position_size * entry_price
    max_order_coverage = 0.25  # Don't exceed 25% of ADV
    max_order_usd = adv_20 * max_order_coverage
    
    if order_size_usd > max_order_usd:
        # Veto: order too large relative to liquidity
        return (False, 0.0)
    
    # GATE 4: Dynamic Slippage Estimate
    # ──────────────────────────────────
    # s = c·σ·√(Q/V)
    # where c ≈ 0.5, σ = volatility, Q = order size, V = volume
    
    if volume_today <= 0:
        # Can't estimate slippage without volume data
        slippage_bps = 50.0  # Conservative default
    else:
        ratio = (position_size * entry_price) / volume_today
        slippage_bps = SLIPPAGE_CONSTANT * volatility * np.sqrt(ratio) * 10000
    
    max_slippage_bps = 50.0
    
    if slippage_bps > max_slippage_bps:
        # Veto: estimated slippage exceeds limit
        return (False, 0.0)
    
    # GATE 5: Portfolio Reconciliation
    # ────────────────────────────────
    delta_qty = position_size - current_qty
    
    if delta_qty <= 0:
        # Not adding to position (could be reducing), reject
        return (False, 0.0)
    
    # All gates passed
    return (True, float(position_size))
```

#### 4.2.2 Position Sizing Logic (Kelly-like)

**Function: `calculate_kelly_position_size()`**
```python
@njit(fastmath=True)
def calculate_kelly_position_size(
    win_rate: float,
    win_loss_ratio: float,
    capital: float,
    entry_price: float,
    atr: float,
    atr_multiplier: float
) -> float:
    """Calculate position size using Kelly criterion (modified).
    
    Args:
        win_rate: Probability of trade being profitable.
        win_loss_ratio: Avg win size / avg loss size.
        capital: Total capital.
        entry_price, atr, atr_multiplier: Risk calculation.
    
    Returns:
        Fraction of capital to risk (typically 0.01-0.05).
    
    Formula (Kelly):
        f = (p × b - q) / b
        where p = win_rate, q = 1 - p, b = ratio
        
        Risk fraction = min(f, 0.05)  [cap at 5% for safety]
    
    Notes:
        - Kelly fraction balances growth vs drawdown
        - Often underestimate by 25% for safety (0.75 × Kelly)
    """
    if win_rate <= 0 or win_rate >= 1:
        return 0.01  # Default to 1% risk
    
    q = 1.0 - win_rate
    b = win_loss_ratio
    
    if b <= 0:
        return 0.01
    
    kelly_fraction = (win_rate * b - q) / b
    kelly_fraction = max(kelly_fraction, 0.01)  # Min 1%
    kelly_fraction = min(kelly_fraction, 0.05)  # Max 5%
    
    # Conservative: use 75% of Kelly
    return kelly_fraction * 0.75
```

#### 4.2.3 Volatility Stop Enforcement

**Function: `enforce_volatility_stop()`**
```python
@njit(fastmath=True)
def enforce_volatility_stop(
    entry_price: float,
    current_price: float,
    atr: float,
    atr_multiplier: float,
    trailing_high: float
) -> tuple:
    """Determine if position should be stopped out.
    
    Args:
        entry_price: Entry price of position.
        current_price: Current market price.
        atr: Current ATR.
        atr_multiplier: ATR multiplier for stops (typically 2.0).
        trailing_high: Highest price since entry.
    
    Returns:
        (stopped_out: bool, stop_price: float)
    
    Logic:
        1. Hard stop: If current < entry - 2×ATR → STOP
        2. Trailing stop: If trailed > entry by 1.5×ATR
           AND current < trailing - 0.5×ATR → STOP
    
    Notes:
        - Prevents holding large losses
        - Locks in gains with trailing logic
    """
    hard_stop = entry_price - (atr_multiplier * atr)
    
    # Hard stop hit
    if current_price <= hard_stop:
        return (True, hard_stop)
    
    # Trailing stop logic
    profit_threshold = entry_price + (1.5 * atr)
    trailing_stop = trailing_high - (0.5 * atr)
    
    if trailing_high >= profit_threshold and current_price <= trailing_stop:
        return (True, trailing_stop)
    
    return (False, 0.0)
```

### 4.3 Shield Agent Integration with Live Trader

**Integration Pattern** (in `live_trader.py`):

```python
from features.shields import evaluate_risk_veto_gates, enforce_volatility_stop

def execute_trade_with_shield(
    ticker: str,
    signal_probability: float,
    entry_price: float,
    atr: float,
    current_inventory: dict,
    account_capital: float,
    adv_20: float,
    volume_today: float,
    volatility: float,
    config: AppConfig
):
    """Execute trade only if Shield Agent approves."""
    
    logger = get_logger(__name__)
    current_qty = current_inventory.get(ticker, 0.0)
    
    # Query Shield Agent
    approved, position_size = evaluate_risk_veto_gates(
        entry_price=entry_price,
        atr=atr,
        atr_multiplier=config.execution.atr_stop_multiplier,
        account_capital=account_capital,
        max_risk_pct=config.execution.max_risk_per_trade,
        current_qty=current_qty,
        adv_20=adv_20,
        volume_today=volume_today,
        volatility=volatility
    )
    
    if not approved:
        logger.warning(
            f"[{ticker}] Shield Agent VETO",
            extra={
                "signal_prob": signal_probability,
                "entry": entry_price,
                "reason": "veto_reason_logged_separately"
            }
        )
        # Log to veto ledger
        return False
    
    # Approved: submit order to Alpaca
    logger.info(f"[{ticker}] Shield Agent APPROVED: {position_size} shares")
    
    limit_price = entry_price + (0.1 * atr)
    submit_order_to_alpaca(ticker, position_size, limit_price)
    
    return True
```

---

## 5. Dynamic Slippage Modeling

### 5.1 Module: `features/slippage.py`

**File: `features/slippage.py`**

```python
import numpy as np
from numba import njit
import logging

logger = get_logger(__name__)

# Calibration constants
SLIPPAGE_CONSTANT = 0.5  # Market impact multiplier
BPS_SCALER = 10000.0  # Convert decimal to basis points
```

#### 5.1.1 Hydrodynamic Slippage Model

**Function: `calculate_hydrodynamic_slippage()`**
```python
def calculate_hydrodynamic_slippage(
    order_size_usd: float,
    volatility: float,
    adv_20: float,
    volume_today: float,
    constant: float = SLIPPAGE_CONSTANT
) -> float:
    """Calculate estimated market impact/slippage using hydrodynamic model.
    
    Args:
        order_size_usd: Order size in dollars.
        volatility: Current volatility (σ) as decimal (e.g., 0.02 = 2%).
        adv_20: 20-day average dollar volume.
        volume_today: Volume observed so far today.
        constant: Calibration factor (typically 0.4-0.6).
    
    Returns:
        Slippage in basis points (bps).
    
    Formula:
        S = c · σ · √(Q/V)
        where:
        - Q = order size / ADV (as ratio)
        - V = volume_today / ADV (as ratio, or use 1.0 for default)
        - c = market impact constant
        - σ = volatility
        
        Result in bps = S * 10000
    
    Interpretation:
        - < 10 bps: Highly liquid, minimal slippage
        - 10-25 bps: Normal slippage
        - 25-50 bps: Elevated, reduce size
        - > 50 bps: Illiquid, VETO trade
    
    Calibration Notes:
        - Constant 'c' depends on market microstructure
        - Typically calibrated on historical fill data
        - Higher for illiquid assets, lower for liquid
    """
    if adv_20 <= 0 or volatility <= 0:
        return 50.0  # Conservative default (veto threshold)
    
    # Normalize volume
    volume_ratio = volume_today / adv_20 if volume_today > 0 else 1.0
    
    # Order size ratio
    order_ratio = order_size_usd / adv_20
    
    # Slippage formula
    if volume_ratio <= 0:
        return 50.0
    
    slippage = constant * volatility * np.sqrt(order_ratio / volume_ratio)
    slippage_bps = slippage * BPS_SCALER
    
    return slippage_bps
```

#### 5.1.2 Regime-Specific Slippage Adjustment

**Function: `adjust_slippage_by_regime()`**
```python
@njit(fastmath=True)
def adjust_slippage_by_regime(
    base_slippage_bps: float,
    regime: int,
    regime_multiplier_normal: float = 1.0,
    regime_multiplier_high_vol: float = 2.0
) -> float:
    """Adjust base slippage by volatility regime.
    
    Args:
        base_slippage_bps: Baseline slippage from hydrodynamic model.
        regime: 0 = normal, 1 = high volatility.
        regime_multiplier_normal: Multiplier for normal regime (typically 1.0).
        regime_multiplier_high_vol: Multiplier for high vol (typically 1.5-2.0).
    
    Returns:
        Regime-adjusted slippage in bps.
    
    Logic:
        - In low-volatility regimes, slippage is predictable
        - In high-volatility regimes, slippage spikes
        - Adjust multiplier based on regime tag
    
    Notes:
        - Used in Shield Agent to tighten veto threshold in high-vol
    """
    if regime == 0:
        # Normal regime
        adjusted = base_slippage_bps * regime_multiplier_normal
    else:
        # High volatility regime
        adjusted = base_slippage_bps * regime_multiplier_high_vol
    
    return adjusted
```

#### 5.1.3 Slippage Testing

**File: `tests/test_slippage.py`**

```python
import pytest
from features.slippage import (
    calculate_hydrodynamic_slippage,
    adjust_slippage_by_regime
)

def test_slippage_calculation_baseline():
    """Test slippage under normal conditions."""
    # Baseline: $1M order, 2% volatility, $100M ADV
    slippage = calculate_hydrodynamic_slippage(
        order_size_usd=1e6,
        volatility=0.02,
        adv_20=100e6,
        volume_today=50e6,
        constant=0.5
    )
    
    # Expected: 0.5 * 0.02 * sqrt(1e6 / 100e6 / (50e6 / 100e6))
    #         = 0.5 * 0.02 * sqrt(0.01 / 0.5)
    #         = 0.5 * 0.02 * sqrt(0.02)
    #         = 0.5 * 0.02 * 0.1414 ≈ 0.14 bp
    assert 10 < slippage < 30, f"Unexpected slippage: {slippage}"

def test_slippage_scaling_with_order_size():
    """Verify slippage scales with order size."""
    base_slippage = calculate_hydrodynamic_slippage(
        order_size_usd=1e6,
        volatility=0.02,
        adv_20=100e6,
        volume_today=100e6,
        constant=0.5
    )
    
    # Double order size → slippage should √2 increase
    double_slippage = calculate_hydrodynamic_slippage(
        order_size_usd=2e6,
        volatility=0.02,
        adv_20=100e6,
        volume_today=100e6,
        constant=0.5
    )
    
    ratio = double_slippage / base_slippage
    expected_ratio = np.sqrt(2)
    assert abs(ratio - expected_ratio) < 0.1, f"Ratio {ratio} != {expected_ratio}"

def test_slippage_regime_adjustment():
    """Test regime multipliers."""
    base = 20.0  # 20 bps
    
    normal = adjust_slippage_by_regime(base, regime=0, regime_multiplier_normal=1.0)
    high_vol = adjust_slippage_by_regime(base, regime=1, regime_multiplier_high_vol=2.0)
    
    assert normal == 20.0
    assert high_vol == 40.0
```

---

## 6. Implementation Checklist - Phase 2

### Week 1: Polars & GPU Foundations

- [ ] **Day 1-2**: Polars engine basics
  - [ ] Implement `polars_engine.py` with basic indicators (returns, ATR, ADV)
  - [ ] Unit tests: `test_polars_features.py`
  - [ ] Benchmark Polars vs Pandas (at least 2x speedup)

- [ ] **Day 2-3**: Advanced Polars features
  - [ ] Implement rolling volatility, regime tagging
  - [ ] Implement microstructure (spreads, Amihud)
  - [ ] Integration test: full pipeline

- [ ] **Day 3-4**: GPU kernel setup
  - [ ] Implement `gpu_kernels.py` header & infrastructure
  - [ ] Implement kernel_spreads() + wrapper
  - [ ] Test on GPU with sample data

- [ ] **Day 4-5**: GPU kernel expansion
  - [ ] Implement kernel_amihud()
  - [ ] Implement kernel_ncskew() (expensive)
  - [ ] Implement kernel_duvol()
  - [ ] Unit tests + fallback to CPU handling

### Week 2: Shield Agent & Slippage

- [ ] **Day 6-7**: Shield Agent implementation
  - [ ] Implement `shields.py` core function
  - [ ] Implement all 5 veto gates
  - [ ] Unit tests: `test_shield_agent.py`

- [ ] **Day 7-8**: Shield Agent advanced
  - [ ] Implement Kelly-like position sizing
  - [ ] Implement volatility stop enforcement
  - [ ] Integration tests with mock Alpaca

- [ ] **Day 8-9**: Slippage modeling
  - [ ] Implement `slippage.py` hydrodynamic model
  - [ ] Implement regime adjustments
  - [ ] Unit tests: `test_slippage.py`

- [ ] **Day 9-10**: Performance optimization
  - [ ] GPU kernel benchmarking
  - [ ] Profile Shield Agent latency (target < 100µs)
  - [ ] Fix bottlenecks, add caching

---

## 7. Success Criteria & Benchmarks

### 7.1 Performance Targets

| Component | Metric | Target | Test |
|-----------|--------|--------|------|
| Polars Pipeline | Full feature compilation | 10-50 stocks/sec | `bench_polars_vs_pandas.py` |
| GPU Spreads | Throughput | > 10M ops/sec | `bench_gpu_kernels.py` |
| GPU Amihud | Throughput | > 5M ops/sec | `bench_gpu_kernels.py` |
| GPU NCSKEW | Throughput | > 1M ops/sec | `bench_gpu_kernels.py` |
| Shield Agent | Latency per eval | < 100µs | Numba profiler |
| Slippage Calc | Latency | < 10µs | Numba profiler |

### 7.2 Functional Acceptance

| Criterion | Test | Expected |
|-----------|------|----------|
| Polars lazy evaluation | Feature pipeline test | ✓ All lazy until .collect() |
| GPU kernels fallback | CUDA OOM scenario | ✓ Fallback to CPU works |
| Shield Agent all gates | 5-gate evaluation | ✓ All gates tested + veto'd correctly |
| Slippage matches formula | Unit test | ✓ Within 1% of expected |
| Position sizing Kelly | Unit test | ✓ Correct kelly fraction |
| Volatility stops | Unit test | ✓ Hard & trailing stops work |

### 7.3 Code Quality

| Criterion | Target |
|-----------|--------|
| Test coverage (features/) | ≥ 85% |
| GPU kernel tests | All pass + benchmarked |
| Type hints | 100% (mypy clean) |
| Linting errors | 0 |

---

## 8. Integration Points with Phase 1 & 3

### 8.1 Phase 1 Dependencies

- **Config system**: All feature params read from `AppConfig`
- **Logging**: All operations logged via Phase 1 logger
- **Exceptions**: Use Phase 1 exception hierarchy
- **Retry logic**: Use @retry for API calls
- **Testing framework**: Pytest fixtures from Phase 1

### 8.2 Handoff to Phase 3 (Tournament)

- Feature outputs → ParquetDataIter (zero-copy)
- Shield Agent veto gates → Live execution layer
- Slippage model → Risk simulator in backtest
- GPU kernels available for model training

---

## 9. Quick Reference Commands

```bash
# Run Polars pipeline
python -c "
from features.polars_engine import execute_feature_pipeline
from config import get_config
config = get_config()
execute_feature_pipeline(
    config.data.raw_vault_dir,
    'Technology',
    config.data.processed_vault_dir,
    config
)
"

# Benchmark GPU kernels
pytest tests/benchmarks/bench_gpu_kernels.py -v --benchmark-only

# Profile Shield Agent latency
python -m cProfile -s cumtime -c "
from features.shields import evaluate_risk_veto_gates
import numpy as np
for _ in range(10000):
    evaluate_risk_veto_gates(100.0, 2.5, 2.0, 50000.0, 0.02, 0.0, 5e6, 2e6, 0.02)
"

# Test slippage model
pytest tests/test_slippage.py -v --tb=short

# Run all Phase 2 tests
pytest tests/unit/features/ tests/integration/features/ --cov=features --cov-report=html
```

---

## 10. Deliverables Summary - Phase 2

### Codebase
- [ ] `/new_pipeline/features/polars_engine.py` (500+ lines)
- [ ] `/new_pipeline/features/gpu_kernels.py` (600+ lines CUDA)
- [ ] `/new_pipeline/features/shields.py` (400+ lines Numba)
- [ ] `/new_pipeline/features/slippage.py` (200+ lines)
- [ ] 100+ unit tests + benchmarks

### Performance
- [ ] Polars 5-10x faster than pandas
- [ ] GPU kernels 10-50x faster than CPU
- [ ] Shield Agent < 100µs per eval
- [ ] Memory efficient: out-of-core processing

### Documentation
- [ ] Feature engineering guide
- [ ] GPU kernel optimization tips
- [ ] Shield Agent decision tree
- [ ] Slippage calibration guide

---

**Next**: After Phase 2 completion, proceed to [Phase 3: Tournament Backtesting & Model Selection](PHASE_3_SPECIFICATION.md) (to be created).
