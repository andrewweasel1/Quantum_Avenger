import copy
import json
import os
from pathlib import Path
from typing import Any

import yaml

from .schema import AppConfig

_CONFIG_DIR = Path(__file__).resolve().parent
_DEFAULTS_PATH = _CONFIG_DIR / "defaults.yaml"

# Recognized deployment environments and their overlay files (layered over
# defaults.yaml, then any QA_-prefixed env vars win).
_ENV_OVERLAYS = {
    "development": _CONFIG_DIR / "development.yaml",
    "testing": _CONFIG_DIR / "testing.yaml",
    "production": _CONFIG_DIR / "production.yaml",
}

_CONFIG_INSTANCE: AppConfig | None = None


def load_defaults() -> dict[str, Any]:
    with open(_DEFAULTS_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_overlay(env: str) -> dict[str, Any]:
    path = _ENV_OVERLAYS.get(env)
    if path is None or not path.exists():
        return {}
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigManager:
    def __init__(self, env: str | None = None) -> None:
        self._env = env if env is not None else os.environ.get("QA_ENV")
        self._defaults = load_defaults()
        self._config = self._build_config()

    def _build_config(self) -> AppConfig:
        merged = copy.deepcopy(self._defaults)
        if self._env:
            merged = _deep_merge(merged, _load_overlay(self._env))

        for key, value in os.environ.items():
            # QA_ENV selects the overlay; it is not a config key itself.
            if key.startswith("QA_") and key != "QA_ENV":
                parts = key[3:].lower().split("__")
                target = merged
                for part in parts[:-1]:
                    if part not in target or not isinstance(target[part], dict):
                        target[part] = {}
                    target = target[part]
                target[parts[-1]] = self._parse_env_value(value)

        return AppConfig.model_validate(merged)

    @staticmethod
    def _parse_env_value(value: str) -> Any:
        if value.lower() in {"true", "false"}:
            return value.lower() == "true"
        if value.isdigit():
            return int(value)
        # JSON list/object literals: without this every LIST field (factor_set,
        # extended_features, scanner_variants, the intraday axes) was
        # un-overridable from the environment — the string reached pydantic and
        # failed validation, so run bodies had to edit YAML instead.
        stripped = value.strip()
        if stripped[:1] in {"[", "{"}:
            try:
                return json.loads(stripped)
            except json.JSONDecodeError:
                return value
        try:
            return float(value)
        except ValueError:
            return value

    def get_config(self) -> AppConfig:
        return self._config


def get_config() -> AppConfig:
    global _CONFIG_INSTANCE
    if _CONFIG_INSTANCE is None:
        _CONFIG_INSTANCE = ConfigManager().get_config()
    return _CONFIG_INSTANCE


def reload_config() -> AppConfig:
    global _CONFIG_INSTANCE
    _CONFIG_INSTANCE = None
    return get_config()


def build_config(env: str | None = None) -> AppConfig:
    """Build a fresh (non-singleton) config for a specific environment overlay."""
    return ConfigManager(env=env).get_config()
