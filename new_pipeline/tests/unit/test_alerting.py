"""Push-side alert dispatch: thresholds over the ledgers -> configured channels."""

from new_pipeline.config import reload_config
from new_pipeline.execution.trade_log import TradeLog, TradeRecord
from new_pipeline.monitoring.alerting import build_channels, dispatch_current_alerts
from new_pipeline.monitoring.dashboard.notifications import RecordingChannel


def _seed_breaching_trades(path):
    log = TradeLog(path)
    for pnl, oid in [(0.02, "a"), (-0.30, "b"), (0.01, "c")]:  # -30% drawdown breach
        log.append(TradeRecord("AAPL", "buy", 10, 100.0, "filled", oid, pnl=pnl))


def _cfg(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_DASHBOARD__VETO_LEDGER_PATH", str(tmp_path / "veto.parquet"))
    monkeypatch.setenv("QA_DASHBOARD__TRADE_LOG_PATH", str(tmp_path / "trades.parquet"))
    return reload_config()


def test_breach_is_dispatched_to_injected_channel(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path, monkeypatch)
    _seed_breaching_trades(tmp_path / "trades.parquet")
    channel = RecordingChannel()

    alerts = dispatch_current_alerts(cfg, channels=[channel])

    assert any(a.severity == "critical" for a in alerts)  # the drawdown breach
    assert channel.sent == alerts


def test_no_breach_dispatches_nothing(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path, monkeypatch)  # no ledgers at all -> zero KPIs -> no alerts
    channel = RecordingChannel()
    assert dispatch_current_alerts(cfg, channels=[channel]) == []
    assert channel.sent == []


def test_channels_built_from_config(tmp_path, monkeypatch):
    cfg = _cfg(tmp_path, monkeypatch)
    cfg.dashboard.alert_channels = ["console", "webhook"]
    cfg.dashboard.alert_webhook_url = "https://hooks.example/qa"
    sent = []
    channels = build_channels(
        cfg, webhook_transport=lambda url, payload: sent.append((url, payload))
    )
    assert len(channels) == 2

    cfg.dashboard.alert_webhook_url = ""  # webhook without a URL is skipped
    assert len(build_channels(cfg)) == 1

    cfg.dashboard.alert_channels = []
    assert build_channels(cfg) == []


def test_console_channel_end_to_end(tmp_path, monkeypatch, capsys):
    cfg = _cfg(tmp_path, monkeypatch)
    cfg.dashboard.alert_channels = ["console"]
    _seed_breaching_trades(tmp_path / "trades.parquet")

    alerts = dispatch_current_alerts(cfg)  # channels resolved from config

    out = capsys.readouterr().out
    assert alerts and "[CRITICAL]" in out and "drawdown" in out.lower()
