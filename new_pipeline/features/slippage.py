"""Dynamic hydrodynamic slippage model:  S = c · σ · sqrt(Q / V).

Numba-compiled so the Shield Agent (also ``@njit``) can call it inside its veto
gates. ``Q`` is the order notional, ``V`` the traded volume over the same unit,
``σ`` the (annualized) volatility, and ``c`` a calibrated market-impact
constant. The result is scaled to basis points.
"""

import math

from numba import njit

DEFAULT_SLIPPAGE_CONSTANT = 0.5
DEFAULT_BPS_SCALER = 10000.0
HIGH_VOL_MULTIPLIER = 2.0
_NO_LIQUIDITY_BPS = 1.0e18  # forces a downstream veto when there is no volume


@njit(fastmath=True, cache=True)
def hydrodynamic_slippage_bps(
    order_notional,
    volatility,
    volume,
    constant=DEFAULT_SLIPPAGE_CONSTANT,
    bps_scaler=DEFAULT_BPS_SCALER,
):
    """Estimated slippage in basis points for an order of ``order_notional``."""
    if volume <= 0.0:
        return _NO_LIQUIDITY_BPS
    if order_notional <= 0.0 or volatility <= 0.0:
        return 0.0
    impact = constant * volatility * math.sqrt(order_notional / volume)
    return impact * bps_scaler


@njit(fastmath=True, cache=True)
def adjust_slippage_by_regime(
    base_bps,
    regime,
    normal_multiplier=1.0,
    high_vol_multiplier=HIGH_VOL_MULTIPLIER,
):
    """Scale slippage up in a high-volatility regime (``regime == 1``)."""
    if regime == 1:
        return base_bps * high_vol_multiplier
    return base_bps * normal_multiplier
