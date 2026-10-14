"""Config loader: environment-override parsing."""


def test_env_override_parses_json_list_and_object_values(monkeypatch):
    """Every LIST field was un-overridable from the environment: the raw string
    reached pydantic and failed validation, forcing YAML edits for run bodies."""
    from new_pipeline.config import base, reload_config

    monkeypatch.setenv("QA_INTRADAY__SCANNER_VARIANTS", '["attention","tradable"]')
    monkeypatch.setenv("QA_FEATURES__FACTOR_SET", '["reversal_21"]')
    reload_config()
    cfg = base.get_config()
    assert cfg.intraday.scanner_variants == ["attention", "tradable"]
    assert cfg.features.factor_set == ["reversal_21"]
    # scalars and non-JSON strings are untouched
    monkeypatch.setenv("QA_INTRADAY__SCANNER_TOP_N", "7")
    monkeypatch.setenv("QA_INTRADAY__STRATEGY", "meanrev")
    monkeypatch.setenv("QA_LOGGING__FORMAT", "[weird] %(message)s")
    reload_config()
    cfg = base.get_config()
    assert cfg.intraday.scanner_top_n == 7 and cfg.intraday.strategy == "meanrev"
    assert cfg.logging.format == "[weird] %(message)s"  # malformed JSON stays a string
