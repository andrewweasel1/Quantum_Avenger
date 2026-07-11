"""Process-wide operational counters.

``MetricsCollector`` is a plain counter bag; :func:`get_metrics` returns the
process singleton that the orchestrator, trading runner, and API increment and
that the ``/metrics`` route renders (via ``telemetry.render_prometheus``).
Counters are per-process — a backtest subprocess keeps its own, the API server
its own — which is exactly what Prometheus expects from each scrape target.
"""

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


_METRICS = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """The process-wide collector (what production call sites increment)."""
    return _METRICS


def reset_metrics() -> None:
    """Zero the process collector (test isolation)."""
    _METRICS.counters.clear()
