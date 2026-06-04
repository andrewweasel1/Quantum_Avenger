import math

from new_pipeline.execution.risk import RiskManager
from new_pipeline.features.shields import (
    calculate_kelly_position_size,
    enforce_volatility_stop,
    evaluate_risk_veto_gates,
)

# A baseline trade that passes all five gates.
_APPROVE = {
    "entry_price": 100.0,
    "atr": 2.0,
    "atr_multiplier": 2.0,
    "account_capital": 100_000.0,
    "max_risk_pct": 0.02,
    "current_qty": 0.0,
    "adv_20": 10_000_000.0,
    "volume_today": 100_000_000.0,
    "volatility": 0.2,
}


def _call(**overrides):
    args = {**_APPROVE, **overrides}
    return evaluate_risk_veto_gates(
        args["entry_price"],
        args["atr"],
        args["atr_multiplier"],
        args["account_capital"],
        args["max_risk_pct"],
        args["current_qty"],
        args["adv_20"],
        args["volume_today"],
        args["volatility"],
    )


def test_baseline_trade_approved():
    approved, size = _call()
    assert approved is True
    assert size == 500.0


def test_gate1_invalid_atr_vetoes():
    assert _call(atr=0.0) == (False, 0.0)


def test_gate2_account_too_small_vetoes():
    assert _call(account_capital=10.0) == (False, 0.0)


def test_gate3_illiquid_vetoes():
    assert _call(adv_20=1_000.0) == (False, 0.0)


def test_gate4_high_slippage_vetoes():
    assert _call(volume_today=100_000.0, volatility=0.6) == (False, 0.0)


def test_gate5_already_at_target_vetoes():
    assert _call(current_qty=600.0) == (False, 0.0)


def test_invariant_veto_implies_zero_size():
    for override in ({"atr": 0.0}, {"adv_20": 1.0}, {"current_qty": 10_000.0}):
        approved, size = _call(**override)
        assert approved is False
        assert size == 0.0


def test_invariant_size_never_negative():
    for capital in (1.0, 100.0, 1_000.0, 1_000_000.0):
        _, size = _call(account_capital=capital)
        assert size >= 0.0


def test_kelly_matches_riskmanager_oracle():
    rm = RiskManager(max_risk_per_trade=0.02, atr_multiplier=2.0)
    kelly = calculate_kelly_position_size(100.0, 2.0, 2.0, 100_000.0, 0.02)
    assert kelly == math.floor(rm.compute_position_size(100_000.0, 100.0, 2.0))


def test_enforce_volatility_stop_uses_trailing_and_flags_trigger():
    stop, triggered = enforce_volatility_stop(100.0, 2.0, 2.0, 95.0, 110.0)
    assert stop == 106.0  # trailing: 110 - 2*2 beats hard stop 96
    assert triggered is True  # current 95 <= 106
    _, not_triggered = enforce_volatility_stop(100.0, 2.0, 2.0, 108.0, 110.0)
    assert not_triggered is False
