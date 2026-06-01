from typing import Any


class FeatureRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, dict[str, Any]] = {}

    def register(self, feature_name: str, metadata: dict[str, Any]) -> None:
        self._registry[feature_name] = metadata

    def get(self, feature_name: str) -> dict[str, Any] | None:
        return self._registry.get(feature_name)

    def list_features(self) -> list[str]:
        return list(self._registry.keys())
