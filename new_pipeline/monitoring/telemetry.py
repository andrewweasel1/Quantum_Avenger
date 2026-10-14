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


def runtime_metrics(cfg=None) -> dict[str, float]:
    """The ``/metrics`` payload: process counters + ledger KPIs + champion DSR.

    Counters come from the process-wide collector (decisions/executions/vetoes,
    API run launches); the KPI gauges (veto_rate, total_pnl, sharpe,
    max_drawdown, win_rate, profit_factor, …) are computed from the ledgers at
    scrape time so any process serving this — the API or a standalone exporter —
    reports the same book state; ``dsr_value`` is the weakest active champion's
    promoted DSR (the alert-relevant one), omitted until something promotes.
    """
    from new_pipeline.config import get_config
    from new_pipeline.monitoring.dashboard.realtime import RealtimeDataManager
    from new_pipeline.monitoring.metrics import get_metrics

    cfg = cfg or get_config()
    manager = RealtimeDataManager(cfg.dashboard.veto_ledger_path, cfg.dashboard.trade_log_path)
    payload: dict[str, float] = dict(get_metrics().counters)
    payload.update(manager.kpis())
    dsr = _min_promoted_dsr(cfg.evaluation.registry_path)
    if dsr is not None:
        payload["dsr_value"] = dsr
    return payload


def _min_promoted_dsr(registry_path) -> float | None:
    """Min over each sector's most recent promoted DSR (append-only registry)."""
    import json
    from pathlib import Path

    file = Path(registry_path)
    if not file.exists():
        return None
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    latest: dict[str, float] = {}
    for entry in data.get("promotions", []):
        if entry.get("promoted") and isinstance(entry.get("dsr"), (int, float)):
            latest[entry.get("sector", "?")] = float(entry["dsr"])
    return min(latest.values()) if latest else None


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
