
from new_pipeline.config import reload_config


def test_config_loads_defaults():
    config = reload_config()
    assert config.data.raw_vault_dir == "./data/raw"
    assert config.execution.max_risk_per_trade == 0.02
    assert config.logging.level == "INFO"


def test_feature_selection_defaults_are_backward_compatible():
    tournament = reload_config().tournament
    # Default stays the correlational selector; causal knobs round-trip from YAML.
    assert tournament.feature_selection_method == "clustered_permutation"
    assert tournament.causal_alpha == 0.10
    assert tournament.causal_granger_lags == 3


def test_config_environment_override(monkeypatch):
    monkeypatch.setenv("QA_DATA__RAW_VAULT_DIR", "/tmp/test_raw")
    monkeypatch.setenv("QA_EXECUTION__MAX_RISK_PER_TRADE", "0.05")
    config = reload_config()

    assert config.data.raw_vault_dir == "/tmp/test_raw"
    assert config.execution.max_risk_per_trade == 0.05
