from abc import ABC, abstractmethod
from pathlib import Path


class BaseDataHandler(ABC):
    @abstractmethod
    def load(self, path: Path):
        raise NotImplementedError

    @abstractmethod
    def save(self, path: Path):
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> bool:
        raise NotImplementedError
