"""Apply a control-panel override payload onto the engine config.

The ``QA_*`` env mechanism can't carry lists (``config/base.py::_parse_env_value``
returns strings), so the API applies overrides *programmatically*: deep-merge the
nested payload onto the **effective** config — defaults + the ``QA_ENV`` overlay +
``QA_*`` env vars, i.e. exactly what ``GET /api/config`` shows the panel — and
validate via Pydantic. Merging onto raw defaults instead would silently strip the
environment's configuration (credentials, run_mode, paths) from every
dashboard-launched run. ``install_config`` then sets the singleton so
``run_offline_pipeline`` (which reads ``get_config()``) sees it.
"""

from new_pipeline.config import base
from new_pipeline.config.schema import AppConfig


def build_overridden_config(overrides: dict | None) -> AppConfig:
    """Validated ``AppConfig`` = the effective config deep-merged with ``overrides``.

    Raises ``pydantic.ValidationError`` on a bad value/type — the caller maps that to
    an HTTP 422.
    """
    effective = base.get_config().model_dump()
    merged = base._deep_merge(effective, overrides or {})
    return AppConfig.model_validate(merged)


def install_config(cfg: AppConfig) -> None:
    """Make ``cfg`` the process-wide singleton (used inside a run subprocess)."""
    base._CONFIG_INSTANCE = cfg
