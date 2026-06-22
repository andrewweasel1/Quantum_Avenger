import pytest
from new_pipeline.core.exceptions import PromotionError
from new_pipeline.evaluation.promotion import PromotionRegistry, assess_promotion


def test_promote_when_both_gates_pass():
    decision = assess_promotion("Energy", 0.97, 0.2)
    assert decision.promoted is True
    assert decision.reason == "true alpha"


def test_reject_low_dsr():
    decision = assess_promotion("Energy", 0.80, 0.5)
    assert decision.promoted is False
    assert decision.reason == "low DSR"


def test_reject_failed_gauntlet():
    decision = assess_promotion("Energy", 0.97, -0.1)
    assert decision.promoted is False
    assert decision.reason == "failed synthetic gauntlet"


def test_registry_records_persists_and_is_append_only(tmp_path):
    path = tmp_path / "reg.json"
    registry = PromotionRegistry(path)
    registry.record(assess_promotion("Energy", 0.97, 0.2), model_path="/m/energy.json")
    registry.record(assess_promotion("Tech", 0.80, 0.1))  # rejected, still recorded
    assert registry.is_champion("Energy")
    assert not registry.is_champion("Tech")
    assert len(registry.promotions) == 2
    # reload from disk -> persisted active champions
    reloaded = PromotionRegistry(path)
    assert reloaded.active_champions() == {"Energy": "/m/energy.json"}


def test_promoted_without_model_path_raises(tmp_path):
    registry = PromotionRegistry(tmp_path / "reg.json")
    with pytest.raises(PromotionError):
        registry.record(assess_promotion("Energy", 0.97, 0.2))


def test_pbo_gate_blocks_overfit_candidate():
    decision = assess_promotion("Energy", 0.97, 0.2, pbo=0.8, pbo_threshold=0.5)
    assert decision.promoted is False
    assert decision.reason == "overfit (high PBO)"


def test_pbo_within_threshold_still_promotes():
    decision = assess_promotion("Energy", 0.97, 0.2, pbo=0.3, pbo_threshold=0.5)
    assert decision.promoted is True
    assert decision.pbo == 0.3


def test_omitted_pbo_leaves_gate_disabled():
    # Back-compat: callers that pass no PBO are gated on DSR + synthetic only.
    assert assess_promotion("Energy", 0.97, 0.2).promoted is True


def test_minbtl_gate_blocks_short_backtest():
    decision = assess_promotion("Energy", 0.97, 0.2, minbtl_satisfied=False)
    assert decision.promoted is False
    assert decision.reason == "backtest shorter than MinBTL"


def test_minbtl_gate_disabled_by_default():
    # minbtl_satisfied=None (the default) must not gate.
    assert assess_promotion("Energy", 0.97, 0.2, minbtl_satisfied=True).promoted is True
    assert assess_promotion("Energy", 0.97, 0.2).promoted is True


def test_diagnostics_are_recorded(tmp_path):
    registry = PromotionRegistry(tmp_path / "reg.json")
    decision = assess_promotion("Energy", 0.97, 0.2, pbo=0.1, psr=0.99, haircut_sharpe=1.1)
    entry = registry.record(decision, model_path="/m/e.json")
    assert entry["pbo"] == 0.1
    assert entry["psr"] == 0.99
    assert entry["haircut_sharpe"] == 1.1


def test_cpcv_path_gate_blocks_unstable_paths():
    decision = assess_promotion(
        "Energy", 0.97, 0.2,
        path_pass_fraction=0.2, path_fraction_threshold=0.5, path_gate_enabled=True,
    )
    assert decision.promoted is False
    assert decision.reason == "unstable across CPCV paths"
    assert decision.cpcv_path_pass_fraction == 0.2


def test_cpcv_path_gate_passes_when_enough_paths_clear():
    decision = assess_promotion(
        "Energy", 0.97, 0.2,
        path_pass_fraction=0.8, path_fraction_threshold=0.5, path_gate_enabled=True,
    )
    assert decision.promoted is True


def test_cpcv_path_gate_inert_when_disabled():
    # Default path_gate_enabled=False: the fraction is recorded but never gates.
    decision = assess_promotion("Energy", 0.97, 0.2, path_pass_fraction=0.0)
    assert decision.promoted is True
    assert decision.cpcv_path_pass_fraction == 0.0


def test_cpcv_path_diagnostics_recorded(tmp_path):
    registry = PromotionRegistry(tmp_path / "reg.json")
    decision = assess_promotion("Energy", 0.97, 0.2, path_pass_fraction=0.6, path_dsr_median=0.93)
    entry = registry.record(decision, model_path="/m/e.json")
    assert entry["cpcv_path_pass_fraction"] == 0.6
    assert entry["cpcv_path_dsr_median"] == 0.93
