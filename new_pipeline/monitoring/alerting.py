"""Push-side alerting: compute threshold alerts from the ledgers and deliver them.

The dashboard's alert *engine* (``dashboard/alerts.py::check_alerts``) is pull —
the UI polls it. This module is the push half: the trading runner calls
:func:`dispatch_current_alerts` at session end, which evaluates the same
thresholds over the same ledgers and delivers any breaches through the channels
named in ``dashboard.alert_channels`` (``console`` and/or ``webhook``; empty —
the default — means compute-but-don't-deliver). The webhook transport is
injectable so tests never touch the network.
"""

import json
import urllib.request

from new_pipeline.config import get_config
from new_pipeline.monitoring.dashboard.alerts import Alert, check_alerts
from new_pipeline.monitoring.dashboard.notifications import (
    ConsoleChannel,
    WebhookChannel,
    dispatch,
)
from new_pipeline.monitoring.dashboard.realtime import RealtimeDataManager


def _post_json(url: str, payload: dict) -> None:  # pragma: no cover - egress
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url, data=body, headers={"Content-Type": "application/json"}
    )
    urllib.request.urlopen(request, timeout=10).read()


def build_channels(cfg=None, webhook_transport=_post_json) -> list:
    cfg = cfg or get_config()
    channels = []
    for name in cfg.dashboard.alert_channels:
        if name == "console":
            channels.append(ConsoleChannel())
        elif name == "webhook" and cfg.dashboard.alert_webhook_url:
            channels.append(WebhookChannel(cfg.dashboard.alert_webhook_url, webhook_transport))
    return channels


def dispatch_current_alerts(cfg=None, channels=None) -> list[Alert]:
    """Evaluate the dashboard thresholds over the live ledgers and deliver breaches."""
    cfg = cfg or get_config()
    manager = RealtimeDataManager(cfg.dashboard.veto_ledger_path, cfg.dashboard.trade_log_path)
    alerts = check_alerts(
        manager.performance(),
        manager.veto_summary(),
        max_drawdown=cfg.dashboard.max_drawdown_alert,
        min_sharpe=cfg.dashboard.min_sharpe_alert,
        max_veto_rate=cfg.dashboard.max_veto_rate_alert,
    )
    if alerts:
        dispatch(alerts, build_channels(cfg) if channels is None else channels)
    return alerts
