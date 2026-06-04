"""Friction-aware target-label generation (Phase 2/3).

``label[t] = 1`` if the forward return from ``t`` to ``t+horizon`` exceeds the
round-trip trading cost (in bps), else ``0``. The final ``horizon`` rows have no
forward window and are returned as NaN for the caller to drop.

The label is the supervised *target* (forward-looking by definition); feature
look-ahead hygiene is handled separately in the feature engine, and signal-side
look-ahead is handled by the t+1 backtest simulator.
"""

import numpy as np
import polars as pl


def friction_aware_labels(close, horizon: int = 1, cost_bps: float = 10.0) -> np.ndarray:
    """Binary label array: forward return over ``horizon`` beats round-trip cost."""
    prices = np.asarray(close, dtype=np.float64)
    n = prices.size
    labels = np.full(n, np.nan, dtype=np.float64)
    if horizon < 1 or n <= horizon:
        return labels
    forward_return = prices[horizon:] / prices[:-horizon] - 1.0
    labels[:-horizon] = (forward_return > cost_bps / 10000.0).astype(np.float64)
    return labels


def add_labels(frame: pl.DataFrame, horizon: int = 1, cost_bps: float = 10.0) -> pl.DataFrame:
    """Add a ``target_label`` column per ticker (sorted by date)."""
    groups = []
    for _, group in frame.sort("date").group_by("ticker", maintain_order=True):
        labels = friction_aware_labels(group["close"].to_numpy(), horizon, cost_bps)
        groups.append(group.with_columns(pl.Series("target_label", labels)))
    return pl.concat(groups) if groups else frame
