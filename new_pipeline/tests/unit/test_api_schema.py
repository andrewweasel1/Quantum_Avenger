"""Control-panel schema introspection + config-override application."""

import json

import pytest
from new_pipeline.api.overrides import build_overridden_config, install_config
from new_pipeline.api.schema_introspect import config_schema
from new_pipeline.config import base, get_config
from pydantic import ValidationError


def _field(groups, group_key, field_name):
    group = next(g for g in groups if g["key"] == group_key)
    return next(f for f in group["fields"] if f["name"] == field_name)


def test_schema_groups_cover_every_appconfig_section():
    from new_pipeline.config.schema import AppConfig

    schema = config_schema()
    keys = {g["key"] for g in schema["groups"]}
    assert keys == set(AppConfig.model_fields)


def test_schema_is_json_serialisable():
    # Required fields (PydanticUndefined default) must serialise to null, not crash.
    json.dumps(config_schema())


def test_primary_groups_sort_first():
    groups = config_schema()["groups"]
    primary = [g["primary"] for g in groups]
    assert primary == sorted(primary, reverse=True)  # all True before any False


def test_list_knob_renders_as_multiselect_with_options():
    field = _field(config_schema()["groups"], "features", "factor_set")
    assert field["type"] == "list"
    assert field["control"] == "multiselect"
    assert "mom_12_1" in field["options"]
    assert field["tunable"] is True


def test_numeric_knob_with_range_renders_as_slider():
    field = _field(config_schema()["groups"], "tournament", "num_boost_round")
    assert field["control"] == "slider"
    assert field["min"] == 10
    assert field["max"] == 500


def test_required_field_default_is_none():
    # data.raw_vault_dir is required (value comes from defaults.yaml), so the
    # static schema default is null and GET /api/config serves the live value.
    field = _field(config_schema()["groups"], "data", "raw_vault_dir")
    assert field["default"] is None


def test_overrides_apply_list_and_scalar_knobs():
    cfg = build_overridden_config(
        {"features": {"factor_set": ["reversal_21", "low_vol"]},
         "tournament": {"num_boost_round": 25}}
    )
    assert cfg.features.factor_set == ["reversal_21", "low_vol"]
    assert cfg.tournament.num_boost_round == 25


def test_empty_overrides_reproduce_defaults():
    cfg = build_overridden_config({})
    assert cfg.tournament.num_boost_round == get_config().tournament.num_boost_round


def test_install_config_sets_the_singleton():
    cfg = build_overridden_config({"tournament": {"num_boost_round": 17}})
    install_config(cfg)
    assert base.get_config().tournament.num_boost_round == 17


def test_bad_override_value_raises_validation_error():
    with pytest.raises(ValidationError):
        build_overridden_config({"tournament": {"num_boost_round": "not-an-int"}})


def test_overrides_start_from_the_effective_env_config(monkeypatch):
    """Regression: dashboard-launched runs must keep QA_* env configuration.

    build_overridden_config used to merge onto raw defaults, silently stripping
    env-provided credentials/run_mode from every subprocess run.
    """
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "33")
    monkeypatch.setenv("QA_ALPACA__API_KEY", "env-key")
    from new_pipeline.config import reload_config

    reload_config()

    cfg = build_overridden_config({})
    assert cfg.tournament.num_boost_round == 33  # env survived
    assert cfg.alpaca.api_key == "env-key"

    cfg = build_overridden_config({"tournament": {"num_boost_round": 55}})
    assert cfg.tournament.num_boost_round == 55  # explicit override beats env
    assert cfg.alpaca.api_key == "env-key"  # untouched groups keep env values
