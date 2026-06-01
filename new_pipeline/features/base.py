from abc import ABC, abstractmethod
from pathlib import Path


class FeatureEngine(ABC):
    @abstractmethod
    def compile(self, raw_path: Path, processed_path: Path) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_available_features(self) -> list[str]:
        raise NotImplementedError
