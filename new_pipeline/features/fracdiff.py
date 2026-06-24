"""Fractional differentiation (offense roadmap P1, §A).

López de Prado Ch.5: integer differencing (returns) makes a price series stationary
but erases its memory; fractional differencing with the *minimum* ``d`` that achieves
stationarity keeps as much long memory as possible — the sweet spot raw price (memory,
non-stationary) and returns (stationary, memoryless) both miss. Fixed-width window
implementation: binomial weights ``wₖ = -wₖ₋₁·(d-k+1)/k`` truncated where |wₖ| falls
below a threshold, applied to the log-price.

Per-ticker (no cross-symbol bleed); leading rows are null until the weight window
fills. See ``docs/quantitative_math.md`` Part II §A.
"""

import numpy as np
import polars as pl

FRACDIFF_FEATURE_NAMES = ("fracdiff",)


def frac_diff_weights(d, threshold=1e-4, max_width=1000) -> np.ndarray:
    """Binomial fractional-difference weights ``[w₀=1, w₁, …]`` (w₀ multiplies the
    current observation), truncated where |wₖ| < ``threshold``."""
    weights = [1.0]
    for k in range(1, max_width):
        w = -weights[-1] * (d - k + 1) / k
        if abs(w) < threshold:
            break
        weights.append(w)
    return np.array(weights, dtype=np.float64)


def fractional_difference(series, d=0.4, threshold=1e-3) -> np.ndarray:
    """Fixed-width fractional difference of ``series``; ``out[t] = Σₖ wₖ·x[t-k]``.

    The first ``len(weights)-1`` entries are NaN (window not yet full)."""
    values = np.asarray(series, dtype=np.float64)
    weights = frac_diff_weights(d, threshold)
    width = weights.size
    out = np.full(values.size, np.nan)
    if width > values.size:
        return out
    reversed_weights = weights[::-1]  # align so the dot gives Σ wₖ·x[t-k]
    for t in range(width - 1, values.size):
        out[t] = float(reversed_weights @ values[t - width + 1 : t + 1])
    return out


def add_fracdiff(ticker_frame: pl.DataFrame, d=0.4, threshold=1e-3) -> pl.DataFrame:
    """Append ``fracdiff`` (fractional difference of log-close) to one ticker's
    date-sorted frame."""
    log_close = np.log(ticker_frame["close"].to_numpy())
    return ticker_frame.with_columns(
        pl.Series("fracdiff", fractional_difference(log_close, d, threshold))
    )
