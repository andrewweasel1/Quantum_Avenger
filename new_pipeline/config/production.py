from .base import build_config
from .schema import AppConfig


def production_config() -> AppConfig:
    return build_config(env="production")
