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


def test_min_promoted_dsr_uses_latest_entry_per_sector(tmp_path):
    from new_pipeline.monitoring.telemetry import _min_promoted_dsr

    registry = tmp_path / "registry.json"
    registry.write_text(
        '{"promotions": ['
        '{"sector": "Tech", "dsr": 0.99, "promoted": true},'
        '{"sector": "Energy", "dsr": 0.955, "promoted": true},'
        '{"sector": "Tech", "dsr": 0.97, "promoted": true},'      # latest Tech wins
        '{"sector": "Utilities", "dsr": 0.40, "promoted": false}'  # rejected: ignored
        ']}'
    )
    assert _min_promoted_dsr(registry) == 0.955

    assert _min_promoted_dsr(tmp_path / "missing.json") is None
    corrupt = tmp_path / "corrupt.json"
    corrupt.write_text("{nope")
    assert _min_promoted_dsr(corrupt) is None


def test_runtime_metrics_combines_counters_kpis_and_dsr(tmp_path, monkeypatch):
    from new_pipeline.config import reload_config
    from new_pipeline.monitoring.metrics import get_metrics
    from new_pipeline.monitoring.telemetry import runtime_metrics

    monkeypatch.setenv("QA_DASHBOARD__VETO_LEDGER_PATH", str(tmp_path / "v.parquet"))
    monkeypatch.setenv("QA_DASHBOARD__TRADE_LOG_PATH", str(tmp_path / "t.parquet"))
    monkeypatch.setenv("QA_EVALUATION__REGISTRY_PATH", str(tmp_path / "r.json"))
    cfg = reload_config()
    (tmp_path / "r.json").write_text(
        '{"promotions": [{"sector": "Tech", "dsr": 0.96, "promoted": true}]}'
    )
    get_metrics().increment("decisions_total", 3)

    payload = runtime_metrics(cfg)

    assert payload["decisions_total"] == 3       # process counter
    assert payload["veto_rate"] == 0.0           # ledger KPI (absent ledgers -> zeros)
    assert payload["dsr_value"] == 0.96          # registry-derived gauge
