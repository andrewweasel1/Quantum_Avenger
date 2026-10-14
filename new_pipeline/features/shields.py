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

# Asymmetric sentiment-volatility gate defaults (beta > alpha: downside steeper).
DEFAULT_SENTIMENT_ALPHA = 0.25   # upside size sensitivity
DEFAULT_SENTIMENT_BETA = 1.0     # downside size sensitivity
DEFAULT_SENTIMENT_GAMMA = 0.40   # stop tightening on negative sentiment
DEFAULT_MIN_STOP_FRAC = 0.25     # floor on the effective ATR multiple


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


@njit(fastmath=True, cache=True)
def sentiment_volatility_gate(
    entry_price,
    atr,
    atr_multiplier,
    account_capital,
    max_risk_pct,
    sentiment,
    alpha=DEFAULT_SENTIMENT_ALPHA,
    beta=DEFAULT_SENTIMENT_BETA,
    gamma=DEFAULT_SENTIMENT_GAMMA,
    min_stop_frac=DEFAULT_MIN_STOP_FRAC,
):
    """Asymmetric sentiment-volatility veto — a scalar, branch-light, Numba
    extension of the Shield's asymmetric-loss philosophy: downside is penalized
    harder than upside is rewarded. Returns ``(approved, position_size)``.

    Negative sentiment shrinks size steeply *and* tightens the ATR stop; positive
    sentiment relaxes size mildly (capped). Size gain ``g(s)=1+alpha*s`` for
    ``s>=0`` and ``1+beta*s`` for ``s<0`` (``beta>alpha``); a hard veto fires when
    ``g<=0``. The effective ATR multiple is tightened by ``gamma*max(0,-s)`` and
    floored at ``min_stop_frac`` of the base multiple. Single-threaded by design:
    inputs are scalars, so a thread-spawn would cost more than the arithmetic.
    """
    if entry_price <= 0.0 or atr <= 0.0 or atr_multiplier <= 0.0:
        return False, 0.0
    if account_capital <= 0.0 or max_risk_pct <= 0.0:
        return False, 0.0

    # Asymmetric size gain g(s).
    if sentiment >= 0.0:
        g = 1.0 + alpha * sentiment
    else:
        g = 1.0 + beta * sentiment
    if g <= 0.0:
        return False, 0.0  # sentiment sufficiently negative -> hard veto

    # Asymmetric stop tightening: only negative sentiment pulls the stop in.
    downside = -sentiment if sentiment < 0.0 else 0.0
    atr_mult_eff = atr_multiplier * (1.0 - gamma * downside)
    floor = atr_multiplier * min_stop_frac
    if atr_mult_eff < floor:
        atr_mult_eff = floor

    stop_distance = atr_mult_eff * atr
    if stop_distance <= 0.0:
        return False, 0.0
    if entry_price - stop_distance <= 0.0:  # stop must sit below entry for a long
        return False, 0.0

    position_size = (account_capital * max_risk_pct / stop_distance) * g
    return True, position_size
