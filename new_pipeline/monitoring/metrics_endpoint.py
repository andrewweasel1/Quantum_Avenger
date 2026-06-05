"""Prometheus ``/metrics`` HTTP exposition (Phase 7 observability).

Frameworkless: :func:`render_metrics_response` returns ``(status, content_type,
body)`` so it is unit-testable, and :func:`serve_metrics` binds a tiny
``http.server`` for real use (Prometheus scrapes the body the exporter renders).
"""

from new_pipeline.monitoring.metrics import MetricsCollector
from new_pipeline.monitoring.telemetry import TelemetryExporter

CONTENT_TYPE = "text/plain; version=0.0.4"


def render_metrics_response(collector: MetricsCollector) -> tuple[int, str, str]:
    return 200, CONTENT_TYPE, TelemetryExporter().from_collector(collector)


def serve_metrics(collector, host="0.0.0.0", port=9090):  # pragma: no cover - binds a socket
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            status, content_type, body = render_metrics_response(collector)
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        def log_message(self, *args):
            pass

    HTTPServer((host, port), _Handler).serve_forever()
