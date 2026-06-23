"""t+1 risk-managed return simulation (no look-ahead).

Enters at ``close[i]`` when ``signal[i] == 1``, places an ATR stop, and realizes
the trade on the *next* bar: a stop-out returns the (negative) risk distance,
otherwise the close-to-close move — both scaled by the risk-based position
fraction. Shares the Shield Agent's stop/sizing math (``features.shields``) so
backtest and live risk stay consistent (the roadmap "central invariant").
"""

import numpy as np
from numba import njit


@njit(fastmath=True, cache=True)
def simulate_t1_returns(signals, close, low, atr, atr_multiplier, max_risk_pct):
    """Per-bar strategy returns; 0.0 on bars with no (or vetoed) entry."""
    n = close.shape[0]
    out = np.zeros(n, dtype=np.float64)
    for i in range(n - 1):
        if signals[i] != 1:
            continue
        entry = close[i]
        if entry <= 0.0 or atr[i] <= 0.0:
            continue
        stop = entry - atr_multiplier * atr[i]
        risk_distance = (entry - stop) / entry
        if risk_distance <= 0.0:
            continue
        size_fraction = max_risk_pct / risk_distance
        if size_fraction > 1.0:
            size_fraction = 1.0
        if low[i + 1] <= stop:
            out[i] = -risk_distance * size_fraction
        else:
            out[i] = (close[i + 1] - entry) / entry * size_fraction
    return out


def simulate_t1_returns_blockwise(
    signals, close, low, atr, block_ids, atr_multiplier, max_risk_pct
):
    """:func:`simulate_t1_returns` applied independently within each contiguous
    block (e.g. ticker run) of ``block_ids``, so a trade's t+1 exit never crosses
    a block boundary into another ticker. With a single block this is identical to
    :func:`simulate_t1_returns`."""
    n = np.asarray(close).shape[0]
    out = np.zeros(n, dtype=np.float64)
    if n == 0:
        return out
    ids = np.asarray(block_ids)
    starts = np.concatenate([[0], np.flatnonzero(ids[1:] != ids[:-1]) + 1])
    ends = np.concatenate([starts[1:], [n]])  # exclusive
    for a, b in zip(starts, ends, strict=True):
        out[a:b] = simulate_t1_returns(
            signals[a:b], close[a:b], low[a:b], atr[a:b], atr_multiplier, max_risk_pct
        )
    return out


def sharpe_ratio(returns: np.ndarray, periods: int = 252) -> float:
    """Annualized Sharpe of a per-bar return series (0 risk-free)."""
    series = np.asarray(returns, dtype=np.float64)
    if series.size < 2:
        return 0.0
    std = series.std(ddof=1)
    if std <= 0.0:
        return 0.0
    return float(series.mean() / std * np.sqrt(periods))
