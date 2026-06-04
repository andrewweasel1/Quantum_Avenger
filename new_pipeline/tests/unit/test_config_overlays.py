from new_pipeline.config import reload_config
from new_pipeline.config.development import development_config
from new_pipeline.config.production import production_config
from new_pipeline.config.testing import testing_config as load_testing_config


def test_development_overlay():
    cfg = development_config()
    assert cfg.logging.level == "DEBUG"
    assert cfg.gpu.cuda_enabled is False


def test_testing_overlay_isolates_vaults():
    cfg = load_testing_config()
    assert cfg.data.raw_vault_dir == "./data/test/raw"
    assert cfg.logging.level == "WARNING"
    assert cfg.features.cache_enabled is False


def test_production_overlay_enables_gpu_and_json():
    cfg = production_config()
    assert cfg.gpu.device == "cuda"
    assert cfg.gpu.cuda_enabled is True
    assert cfg.logging.json_logs is True
    assert cfg.system.run_mode == "live"


def test_defaults_have_no_overlay_applied():
    cfg = reload_config()
    assert cfg.system.run_mode == "backtest"
    assert cfg.gpu.device == "cpu"


def test_qa_env_selects_overlay(monkeypatch):
    monkeypatch.setenv("QA_ENV", "production")
    cfg = reload_config()
    assert cfg.logging.json_logs is True
    assert cfg.gpu.device == "cuda"


def test_env_var_overrides_overlay(monkeypatch):
    monkeypatch.setenv("QA_ENV", "development")
    monkeypatch.setenv("QA_LOGGING__LEVEL", "ERROR")
    cfg = reload_config()
    assert cfg.logging.level == "ERROR"  # QA_ var beats the development overlay's DEBUG
