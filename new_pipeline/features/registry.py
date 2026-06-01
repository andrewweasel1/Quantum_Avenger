from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from new_pipeline.config import get_config


@dataclass
class FeatureMetadata:
    name: str
    description: str
    source: str
    window: str | None = None
    dtype: str = "float"


class FeatureRegistry:
    METADATA_FILENAME = "feature_registry.yaml"

    def __init__(self) -> None:
        self._registry: dict[str, FeatureMetadata] = {}
        self._metadata_path = self._resolve_metadata_path()
        self._load_persistent_registry()

    def _resolve_metadata_path(self) -> Path:
        config = get_config()
        metadata_dir = Path(config.features.metadata_dir)
        metadata_dir.mkdir(parents=True, exist_ok=True)
        return metadata_dir / self.METADATA_FILENAME

    def _load_persistent_registry(self) -> None:
        if not self._metadata_path.exists():
            return

        with self._metadata_path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}

        for feature_name, metadata in payload.items():
            self.register(feature_name, metadata, persist=False)

    def register(
        self,
        feature_name: str,
        metadata: FeatureMetadata | dict[str, Any],
        persist: bool = True,
    ) -> None:
        if isinstance(metadata, dict):
            metadata = FeatureMetadata(**metadata)
        self._registry[feature_name] = metadata
        if persist:
            self.save()

    def get(self, feature_name: str) -> dict[str, Any] | None:
        metadata = self._registry.get(feature_name)
        return asdict(metadata) if metadata is not None else None

    def list_features(self) -> list[str]:
        return list(self._registry.keys())

    def clear(self) -> None:
        self._registry.clear()

    def save(self, path: Path | None = None) -> None:
        destination = path or self._metadata_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {name: asdict(metadata) for name, metadata in self._registry.items()}

        with destination.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(payload, handle)

    def load(self, path: Path | None = None) -> None:
        source = path or self._metadata_path
        if not source.exists():
            return

        with source.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}

        self.clear()
        for feature_name, metadata in payload.items():
            self.register(feature_name, metadata, persist=False)


feature_registry = FeatureRegistry()
