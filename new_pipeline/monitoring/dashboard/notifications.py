"""Alert delivery channels for the dashboard alert engine (Phase 6/7).

Dispatch ``Alert``s to one or more channels. Offline-friendly: ``ConsoleChannel``
writes to an injectable sink, ``WebhookChannel`` posts JSON via an injectable
transport (a fake in tests; a real HTTP client when wired live). No network in
dev/tests.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from new_pipeline.monitoring.dashboard.alerts import Alert


class Channel(Protocol):
    def send(self, alert: Alert) -> None: ...


@dataclass
class ConsoleChannel:
    sink: Callable[[str], None] = print

    def send(self, alert: Alert) -> None:
        self.sink(f"[{alert.severity.upper()}] {alert.message}")


@dataclass
class WebhookChannel:
    url: str
    transport: Callable[[str, dict], None]

    def send(self, alert: Alert) -> None:
        self.transport(self.url, {"severity": alert.severity, "message": alert.message})


@dataclass
class RecordingChannel:
    """In-memory channel for tests."""

    sent: list = field(default_factory=list)

    def send(self, alert: Alert) -> None:
        self.sent.append(alert)


def dispatch(alerts, channels) -> int:
    """Send every alert to every channel; returns the number of deliveries."""
    deliveries = 0
    for alert in alerts:
        for channel in channels:
            channel.send(alert)
            deliveries += 1
    return deliveries
