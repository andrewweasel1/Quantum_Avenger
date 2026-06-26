"""Apply a control-panel override payload onto the engine config.

The ``QA_*`` env mechanism can't carry lists (``config/base.py::_parse_env_value``
returns strings), so the API applies overrides *programmatically*: deep-merge the
nested payload onto the defaults and validate via Pydantic. ``install_config`` then
sets the singleton so ``run_offline_pipeline`` (which reads ``get_config()``) sees it.
"""

from new_pipeline.config import base
from new_pipeline.config.schema import AppConfig


def build_overridden_config(overrides: dict | None) -> AppConfig:
    """Validated ``AppConfig`` = defaults deep-merged with the (nested) ``overrides``.

    Raises ``pydantic.ValidationError`` on a bad value/type — the caller maps that to
    an HTTP 422.
    """
    merged = base._deep_merge(base.load_defaults(), overrides or {})
    return AppConfig.model_validate(merged)


def install_config(cfg: AppConfig) -> None:
    """Make ``cfg`` the process-wide singleton (used inside a run subprocess)."""
    base._CONFIG_INSTANCE = cfg
