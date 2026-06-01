from dataclasses import dataclass


@dataclass
class MetricsCollector:
    counters: dict[str, int] = None

    def __post_init__(self) -> None:
        self.counters = self.counters or {}

    def increment(self, name: str, amount: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + amount

    def get(self, name: str) -> int:
        return self.counters.get(name, 0)
