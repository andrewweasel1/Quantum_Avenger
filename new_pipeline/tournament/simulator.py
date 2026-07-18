"""t+1 risk-managed return simulation (no look-ahead).

Enters at ``close[i]`` when ``signal[i] == 1``, places an ATR stop, and realizes
the trade on the *next* bar: a stop-out returns the (negative) risk distance,
otherwise the close-to-close move — both scaled by the risk-based position
fraction. Shares the Shield Agent's stop/sizing math (``features.shields``) so
backtest and live risk stay consistent (the roadmap "central invariant").

The ``_net`` variants additionally debit transaction costs using the SAME
hydrodynamic impact model the Shield Agent vetoes on (``features.slippage``):
cost = ``c·σ·sqrt(Q/V)`` bps charged on TURNOVER (the change in position between
bars), so a held position pays a full round-trip once across its enter→exit — not
a round-trip every bar it is held — while daily churn pays daily (matches the
long-short book's turnover costing). A fill is vetoed when the target position's
one-way estimate exceeds ``max_slippage_bps`` (backtest parity with Shield gate
#4). ``V`` is the name's *dollar* ADV so ``Q/V`` is a dimensionless participation
rate — the dimensionally-correct usage of the model (the live shield passes raw
share volume; see the audit note in the promotion pipeline). Gross behaviour is
left byte-for-byte intact so goldens and the default suite stay bit-stable.
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
    """:func:`simulate_t1_returns` net of dynamic slippage on TURNOVER.

    A persistent signal (fires on consecutive bars) is a *held* position, not a
    daily round-trip, so cost is charged only on the traded delta — mirroring the
    long-short book's turnover costing. Each bar targets position
    ``p = size_fraction`` (0 when unsignalled or liquidity-vetoed); the turnover
    ``|p_i − p_{i-1}|`` is executed at ``close[i]`` and charged
    ``impact(turnover·capital)/10000 · turnover`` (one-way hydrodynamic impact of
    the delta traded). Holding the same size costs nothing; a genuine enter→exit
    still pays a full round-trip (one-way at entry + one-way at exit). The gross
    leg is unchanged: hold ``p`` over ``[i, i+1]`` for the close-to-close move or
    the ATR stop. A stop-out flattens the book into the next bar (its re-entry is
    then real turnover). ``Q/V`` uses dollar ADV ⇒ dimensionless participation.
    """
    n = close.shape[0]
    out = np.zeros(n, dtype=np.float64)
    prev_pos = 0.0
    for i in range(n - 1):
        entry = close[i]
        want = 0.0
        risk_distance = 0.0
        if signals[i] == 1 and entry > 0.0 and atr[i] > 0.0:
            stop = entry - atr_multiplier * atr[i]
            risk_distance = (entry - stop) / entry
            if risk_distance > 0.0:
                size_fraction = max_risk_pct / risk_distance
                if size_fraction > 1.0:
                    size_fraction = 1.0
                target_bps = hydrodynamic_slippage_bps(
                    size_fraction * account_capital, volatility[i], adv_20[i],
                    slippage_constant, bps_scaler,
                )
                if target_bps <= max_slippage_bps:  # Shield gate #4 parity
                    want = size_fraction

        turnover = want - prev_pos
        if turnover < 0.0:
            turnover = -turnover
        cost = 0.0
        if turnover > 0.0:
            trade_bps = hydrodynamic_slippage_bps(
                turnover * account_capital, volatility[i], adv_20[i],
                slippage_constant, bps_scaler,
            )
            cost = trade_bps / 10000.0 * turnover

        stopped = False
        gross = 0.0
        if want > 0.0:
            stop = entry - atr_multiplier * atr[i]
            if low[i + 1] <= stop:
                gross = -risk_distance * want
                stopped = True
            else:
                gross = (close[i + 1] - entry) / entry * want
        out[i] = gross - cost
        prev_pos = 0.0 if stopped else want  # forced flat after a stop-out
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
