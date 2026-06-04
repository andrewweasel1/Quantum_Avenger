"""The Shield Agent: a deterministic, Numba-compiled risk veto.

``evaluate_risk_veto_gates`` is the project's risk gate *of record*. It is
imported unchanged by three call sites — the Phase 3 t+1 backtest simulator,
the Phase 5 LangGraph Risk-Veto node, and the Phase 5 MCP risk tool — so risk
logic can never drift between backtest and live (the roadmap "central
invariant").

Five gates, evaluated in order; any failure vetoes the trade and returns a
zero position size:

  1. Stop validity   — a positive ATR stop distance exists.
  2. Position sizing — risk-based size rounds down to >= 1 share (Kelly-style).
  3. Liquidity       — order notional <= ``max_adv_coverage`` * ADV20.
  4. Slippage        — hydrodynamic estimate <= ``max_slippage_bps``.
  5. Reconciliation  — the order strictly increases the position.
"""

import math

from numba import njit

from new_pipeline.features.slippage import hydrodynamic_slippage_bps

DEFAULT_MAX_ADV_COVERAGE = 0.25
DEFAULT_SLIPPAGE_CONSTANT = 0.5
DEFAULT_MAX_SLIPPAGE_BPS = 50.0
DEFAULT_BPS_SCALER = 10000.0


@njit(fastmath=True, cache=True)
def calculate_kelly_position_size(
    entry_price, atr, atr_multiplier, account_capital, max_risk_pct
):
    """Risk-based share count: capital_at_risk / risk_per_share, capped by the
    affordable share count and floored to a whole number. 0 means "no trade"."""
    if entry_price <= 0.0 or atr <= 0.0 or atr_multiplier <= 0.0:
        return 0.0
    if account_capital <= 0.0 or max_risk_pct <= 0.0:
        return 0.0
    risk_per_share = atr_multiplier * atr
    size = (account_capital * max_risk_pct) / risk_per_share
    max_allowable = account_capital / entry_price
    if size > max_allowable:
        size = max_allowable
    size = math.floor(size)
    return size if size >= 1.0 else 0.0


@njit(fastmath=True, cache=True)
def enforce_volatility_stop(
    entry_price, atr, atr_multiplier, current_price, highest_price
):
    """Effective stop = max(hard ATR stop, trailing ATR stop). Returns
    ``(stop_level, triggered)`` where ``triggered`` is current_price <= stop."""
    hard_stop = entry_price - atr_multiplier * atr
    trailing_stop = highest_price - atr_multiplier * atr
    stop = hard_stop if hard_stop > trailing_stop else trailing_stop
    return stop, current_price <= stop


@njit(fastmath=True, cache=True)
def evaluate_risk_veto_gates(
    entry_price,
    atr,
    atr_multiplier,
    account_capital,
    max_risk_pct,
    current_qty,
    adv_20,
    volume_today,
    volatility,
    max_adv_coverage=DEFAULT_MAX_ADV_COVERAGE,
    slippage_constant=DEFAULT_SLIPPAGE_CONSTANT,
    max_slippage_bps=DEFAULT_MAX_SLIPPAGE_BPS,
    bps_scaler=DEFAULT_BPS_SCALER,
):
    """Run the five veto gates. Returns ``(approved, position_size)``."""
    # Gate 1: stop-loss validity.
    if entry_price <= 0.0 or atr <= 0.0 or atr_multiplier <= 0.0:
        return False, 0.0
    risk_per_share = atr_multiplier * atr
    stop_price = entry_price - risk_per_share
    if stop_price <= 0.0:
        return False, 0.0

    # Gate 2: risk-based (Kelly-style) position sizing.
    position_size = calculate_kelly_position_size(
        entry_price, atr, atr_multiplier, account_capital, max_risk_pct
    )
    if position_size < 1.0:
        return False, 0.0

    # Gate 3: liquidity — cap order notional at a fraction of ADV.
    order_notional = position_size * entry_price
    if adv_20 <= 0.0 or order_notional > adv_20 * max_adv_coverage:
        return False, 0.0

    # Gate 4: dynamic (hydrodynamic) slippage ceiling.
    slippage_bps = hydrodynamic_slippage_bps(
        order_notional, volatility, volume_today, slippage_constant, bps_scaler
    )
    if slippage_bps > max_slippage_bps:
        return False, 0.0

    # Gate 5: portfolio reconciliation — only add to the position.
    if position_size - current_qty <= 0.0:
        return False, 0.0

    return True, position_size
