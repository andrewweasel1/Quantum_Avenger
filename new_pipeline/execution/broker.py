from abc import ABC, abstractmethod


class BrokerAdapter(ABC):
    @abstractmethod
    def submit_order(self, order: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_positions(self) -> dict[str, float]:
        raise NotImplementedError

    def order_status(self, order_id: str) -> str:
        """Current status of a submitted order.

        Concrete rather than abstract so existing adapters keep working; the
        default reports "unknown", which callers must treat as "cannot confirm
        a fill" rather than as success."""
        return "unknown"
