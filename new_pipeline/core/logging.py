"""Structured logging with trace-id propagation.

:func:`configure_logging` honours ``logging.json_logs`` (emit one JSON object
per line) and ``logging.trace_enabled`` (attach the current trace id to every
record). Wrap a unit of work in :func:`trace_context` so every log line it
emits shares one correlating ``trace_id``.
"""

import json
import logging
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from new_pipeline.config import get_config

_LOGGER_NAME = "quantum_avenger"
_TRACE_ID: ContextVar[str | None] = ContextVar("qa_trace_id", default=None)


def new_trace_id() -> str:
    return uuid.uuid4().hex


def get_trace_id() -> str | None:
    return _TRACE_ID.get()


def set_trace_id(trace_id: str | None) -> Token:
    return _TRACE_ID.set(trace_id)


@contextmanager
def trace_context(trace_id: str | None = None) -> Iterator[str]:
    """Bind a trace id for the duration of the block (auto-generated if None)."""
    resolved = trace_id or new_trace_id()
    token = _TRACE_ID.set(resolved)
    try:
        yield resolved
    finally:
        _TRACE_ID.reset(token)


class TraceIdFilter(logging.Filter):
    """Inject the current trace id onto every record as ``trace_id``."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = _TRACE_ID.get() or "-"
        return True


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON, including the trace id."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None) or _TRACE_ID.get() or "-",
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging() -> logging.Logger:
    config = get_config()
    log_file_path = Path(config.logging.log_file).resolve()
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(getattr(logging, config.logging.level.upper(), logging.INFO))

    if not logger.handlers:
        if config.logging.json_logs:
            formatter: logging.Formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(config.logging.format)

        handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=config.logging.max_bytes,
            backupCount=5,
            encoding="utf-8",
        )
        handler.setFormatter(formatter)
        if config.logging.trace_enabled:
            handler.addFilter(TraceIdFilter())
        logger.addHandler(handler)

    return logger
