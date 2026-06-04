from new_pipeline.monitoring.metrics import MetricsCollector
from new_pipeline.monitoring.telemetry import TelemetryExporter, render_prometheus


def test_render_prometheus_format():
    text = render_prometheus({"veto_rate": 0.25, "dsr_value": 0.96})
    assert "# TYPE quantum_avenger_veto_rate gauge" in text
    assert "quantum_avenger_veto_rate 0.25" in text
    assert "quantum_avenger_dsr_value 0.96" in text


def test_render_empty():
    assert render_prometheus({}) == ""


def test_exporter_filters_non_numeric_and_bool():
    text = TelemetryExporter().export(
        {"trades": 3, "ok": True, "label": "x", "latency_ms": 12.5}
    )
    assert "quantum_avenger_trades 3.0" in text
    assert "quantum_avenger_latency_ms 12.5" in text
    assert "ok" not in text
    assert "label" not in text


def test_from_collector():
    collector = MetricsCollector()
    collector.increment("orders", 2)
    collector.increment("vetoes")
    text = TelemetryExporter().from_collector(collector)
    assert "quantum_avenger_orders 2.0" in text
    assert "quantum_avenger_vetoes 1.0" in text
