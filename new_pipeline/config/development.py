from .base import build_config
from .schema import AppConfig


def development_config() -> AppConfig:
    return build_config(env="development")
