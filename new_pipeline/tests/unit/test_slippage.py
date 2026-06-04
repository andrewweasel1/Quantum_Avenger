import math

from new_pipeline.features.slippage import (
    adjust_slippage_by_regime,
    hydrodynamic_slippage_bps,
)


def test_slippage_matches_formula():
    bps = hydrodynamic_slippage_bps(50_000.0, 0.2, 100_000_000.0, 0.5, 10_000.0)
    expected = 0.5 * 0.2 * math.sqrt(50_000.0 / 100_000_000.0) * 10_000.0
    assert math.isclose(bps, expected, rel_tol=1e-9)


def test_no_volume_forces_veto_value():
    assert hydrodynamic_slippage_bps(50_000.0, 0.2, 0.0) > 1e17


def test_zero_volatility_is_zero_slippage():
    assert hydrodynamic_slippage_bps(50_000.0, 0.0, 1_000.0) == 0.0


def test_regime_doubles_slippage_in_high_vol():
    assert adjust_slippage_by_regime(30.0, 1) == 60.0
    assert adjust_slippage_by_regime(30.0, 0) == 30.0
