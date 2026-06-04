from .base import build_config
from .schema import AppConfig


def testing_config() -> AppConfig:
    return build_config(env="testing")
