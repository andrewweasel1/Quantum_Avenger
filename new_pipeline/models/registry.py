
from .metadata import ModelMetadata


class ModelRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, ModelMetadata] = {}

    def register(self, model_name: str, metadata: ModelMetadata) -> None:
        self._registry[model_name] = metadata

    def get(self, model_name: str) -> ModelMetadata | None:
        return self._registry.get(model_name)

    def list_models(self) -> list[str]:
        return list(self._registry.keys())
