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


@pytest.fixture(autouse=True)
def _isolate_feature_registry(tmp_path):
    """Redirect the feature-registry singleton to a throwaway path so no test
    mutates the tracked data/metadata/feature_registry.yaml artifact."""
    from new_pipeline.features.registry import feature_registry

    original_path = feature_registry._metadata_path
    feature_registry._metadata_path = tmp_path / "feature_registry.yaml"
    feature_registry.clear()
    yield
    feature_registry._metadata_path = original_path
