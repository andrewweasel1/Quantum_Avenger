"""Config endpoints: the control-panel knob schema + the current effective values.

``GET /api/config/schema`` drives the React control panel (group/field/control
metadata, derived from ``AppConfig`` — never hard-coded). ``GET /api/config`` returns
the current effective config so the panel can seed its inputs with live defaults.
"""

from fastapi import APIRouter

from new_pipeline.api.schema_introspect import config_schema
from new_pipeline.config import get_config

router = APIRouter(prefix="/api/config", tags=["config"])


@router.get("/schema")
def get_schema() -> dict:
    """Group/field metadata that the control panel renders itself from."""
    return config_schema()


@router.get("")
def get_current() -> dict:
    """Current effective config as a nested JSON dict (the panel's seed values)."""
    return get_config().model_dump(mode="json")
