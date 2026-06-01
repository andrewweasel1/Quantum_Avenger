import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, RootModel

from .schema import AppConfig

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_DEFAULTS_PATH = _PROJECT_ROOT / "config" / "defaults.yaml"

_CONFIG_INSTANCE: AppConfig | None = None


def load_defaults() -> dict[str, Any]:
    with open(_DEFAULTS_PATH, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


class ConfigManager:
    def __init__(self) -> None:
        self._defaults = load_defaults()
        self._config = self._build_config()

    def _build_config(self) -> AppConfig:
        merged = self._defaults.copy()

        for key, value in os.environ.items():
            if key.startswith("QA_"):
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
