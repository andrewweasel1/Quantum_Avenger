"""t+1 risk-managed return simulation (no look-ahead).

Enters at ``close[i]`` when ``signal[i] == 1``, places an ATR stop, and realizes
the trade on the *next* bar: a stop-out returns the (negative) risk distance,
otherwise the close-to-close move — both scaled by the risk-based position
fraction. Shares the Shield Agent's stop/sizing math (``features.shields``) so
backtest and live risk stay consistent (the roadmap "central invariant").

The ``_net`` variants additionally debit round-trip transaction costs from each
realized trade using the SAME hydrodynamic impact model the Shield Agent vetoes
on (``features.slippage``): one-way cost = ``c·σ·sqrt(Q/V)`` in bps, charged at
both entry and exit, and the trade is skipped entirely when the one-way estimate
exceeds ``max_slippage_bps`` (backtest parity with Shield gate #4). ``V`` is the
name's *dollar* ADV so ``Q/V`` is a dimensionless participation rate — the
dimensionally-correct usage of the model (the live shield passes raw share
volume; see the audit note in the promotion pipeline). Gross behaviour is left
byte-for-byte intact so goldens and the default suite stay bit-stable.
"""

import numpy as np
from numba import njit

from new_pipeline.features.slippage import hydrodynamic_slippage_bps


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


@njit(fastmath=True, cache=True)
def simulate_t1_returns_net(
    signals, close, low, atr, adv_20, volatility, atr_multiplier, max_risk_pct,
    account_capital, slippage_constant, bps_scaler, max_slippage_bps,
):
    """:func:`simulate_t1_returns` net of dynamic round-trip slippage.

    Order notional ``Q = size_fraction · account_capital``; one-way impact is
    ``hydrodynamic_slippage_bps(Q, volatility[i], adv_20[i])`` (dollar ADV ⇒
    participation rate). A one-way estimate above ``max_slippage_bps`` vetoes the
    trade (0.0, like the live Shield). Otherwise the round-trip cost
    ``2·bps/10000`` is subtracted from the per-share return before position
    scaling, so cost scales with participation exactly as the impact model does.
    """
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
        order_notional = size_fraction * account_capital
        one_way_bps = hydrodynamic_slippage_bps(
            order_notional, volatility[i], adv_20[i], slippage_constant, bps_scaler
        )
        if one_way_bps > max_slippage_bps:
            continue  # illiquid: no fill (Shield gate #4 parity)
        cost = 2.0 * one_way_bps / 10000.0  # round trip, bps -> return fraction
        if low[i + 1] <= stop:
            out[i] = (-risk_distance - cost) * size_fraction
        else:
            out[i] = ((close[i + 1] - entry) / entry - cost) * size_fraction
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


def simulate_t1_returns_blockwise_net(
    signals, close, low, atr, adv_20, volatility, block_ids, atr_multiplier,
    max_risk_pct, account_capital, slippage_constant, bps_scaler, max_slippage_bps,
):
    """:func:`simulate_t1_returns_net` applied per contiguous ``block_ids`` block
    (mirrors :func:`simulate_t1_returns_blockwise`, net of dynamic slippage)."""
    n = np.asarray(close).shape[0]
    out = np.zeros(n, dtype=np.float64)
    if n == 0:
        return out
    ids = np.asarray(block_ids)
    starts = np.concatenate([[0], np.flatnonzero(ids[1:] != ids[:-1]) + 1])
    ends = np.concatenate([starts[1:], [n]])  # exclusive
    for a, b in zip(starts, ends, strict=True):
        out[a:b] = simulate_t1_returns_net(
            signals[a:b], close[a:b], low[a:b], atr[a:b], adv_20[a:b], volatility[a:b],
            atr_multiplier, max_risk_pct, account_capital, slippage_constant,
            bps_scaler, max_slippage_bps,
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
