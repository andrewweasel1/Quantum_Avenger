from new_pipeline.monitoring.metrics import MetricsCollector
from new_pipeline.monitoring.metrics_endpoint import CONTENT_TYPE, render_metrics_response


def test_render_metrics_response():
    collector = MetricsCollector()
    collector.increment("orders", 3)
    status, content_type, body = render_metrics_response(collector)
    assert status == 200
    assert content_type == CONTENT_TYPE
    assert "quantum_avenger_orders 3.0" in body
