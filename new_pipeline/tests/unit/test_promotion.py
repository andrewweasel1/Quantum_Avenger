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
