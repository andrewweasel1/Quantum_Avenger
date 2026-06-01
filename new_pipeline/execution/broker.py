from abc import ABC, abstractmethod


class BrokerAdapter(ABC):
    @abstractmethod
    def submit_order(self, order: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_positions(self) -> dict[str, float]:
        raise NotImplementedError
