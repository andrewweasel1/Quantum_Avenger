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


def sharpe_ratio(returns: np.ndarray, periods: int = 252) -> float:
    """Annualized Sharpe of a per-bar return series (0 risk-free)."""
    series = np.asarray(returns, dtype=np.float64)
    if series.size < 2:
        return 0.0
    std = series.std(ddof=1)
    if std <= 0.0:
        return 0.0
    return float(series.mean() / std * np.sqrt(periods))
