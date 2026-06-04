import json
import logging

from new_pipeline.core.logging import (
    JsonFormatter,
    TraceIdFilter,
    configure_logging,
    get_trace_id,
    trace_context,
)


def _record(msg: str = "hello") -> logging.LogRecord:
    return logging.LogRecord("quantum_avenger", logging.INFO, __file__, 1, msg, None, None)


def test_json_formatter_emits_valid_json_with_trace_id():
    formatter = JsonFormatter()
    with trace_context("abc123"):
        payload = json.loads(formatter.format(_record("hi")))
    assert payload["message"] == "hi"
    assert payload["level"] == "INFO"
    assert payload["trace_id"] == "abc123"


def test_trace_context_sets_and_resets():
    assert get_trace_id() is None
    with trace_context("xyz") as tid:
        assert tid == "xyz"
        assert get_trace_id() == "xyz"
    assert get_trace_id() is None


def test_trace_filter_injects_default_dash():
    record = _record()
    assert TraceIdFilter().filter(record) is True
    assert record.trace_id == "-"


def test_configure_logging_returns_logger():
    assert isinstance(configure_logging(), logging.Logger)
