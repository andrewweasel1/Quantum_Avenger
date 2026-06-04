"""Telemetry export in Prometheus text exposition format (Phase 7).

No ``prometheus_client`` dependency — the scrape payload is rendered as plain
text so a ``/metrics`` endpoint works anywhere and stays unit-testable offline.
Numeric values become gauges; the metric names the roadmap calls out
(``trade_rate``, ``veto_rate``, ``execution_latency_ms``, ``dsr_value``, …) are
simply keys in the payload.
"""

from typing import Any

from new_pipeline.monitoring.metrics import MetricsCollector

DEFAULT_PREFIX = "quantum_avenger"


def render_prometheus(metrics: dict[str, float], prefix: str = DEFAULT_PREFIX) -> str:
    """Render a ``{name: value}`` mapping as Prometheus text exposition format."""
    lines: list[str] = []
    for name in sorted(metrics):
        metric_name = f"{prefix}_{name}"
        lines.append(f"# TYPE {metric_name} gauge")
        lines.append(f"{metric_name} {float(metrics[name])}")
    return "\n".join(lines) + "\n" if lines else ""


class TelemetryExporter:
    def __init__(self, prefix: str = DEFAULT_PREFIX) -> None:
        self._prefix = prefix
        self._last_render = ""

    def export(self, payload: dict[str, Any]) -> str:
        numeric = {
            key: float(value)
            for key, value in payload.items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        }
        self._last_render = render_prometheus(numeric, self._prefix)
        return self._last_render

    def from_collector(self, collector: MetricsCollector) -> str:
        return self.export(dict(collector.counters))

    @property
    def last_render(self) -> str:
        return self._last_render
