from pathlib import Path

import pytest

from new_pipeline.config import base


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _reset_config_singleton():
    """Keep the cached config from leaking between tests (env overlays / QA_ vars)."""
    base._CONFIG_INSTANCE = None
    yield
    base._CONFIG_INSTANCE = None
