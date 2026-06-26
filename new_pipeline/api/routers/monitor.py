"""Live-monitor endpoints: thin JSON wrappers over the existing dashboard data layer.

Reuses the Streamlit-era accessors verbatim (``RealtimeDataManager``, ``views.py``,
``alerts.py``) so the React monitor reports exactly what the Streamlit dashboard does.
Every accessor returns empty/zero gracefully when the ledgers don't exist yet, so the
endpoints are safe to call before any live trading has happened.
"""

from dataclasses import asdict

import pyarrow.parquet as pq
from fastapi import APIRouter

from new_pipeline.config import get_config
from new_pipeline.monitoring.dashboard.alerts import check_alerts
from new_pipeline.monitoring.dashboard.realtime import RealtimeDataManager
from new_pipeline.monitoring.dashboard.views import model_registry_view, risk_view

router = APIRouter(prefix="/api/monitor", tags=["monitor"])

_MAX_TRADES = 500  # cap rows sent to the trade-log table


def _manager() -> RealtimeDataManager:
    cfg = get_config().dashboard
    return RealtimeDataManager(cfg.veto_ledger_path, cfg.trade_log_path)


@router.get("/kpis")
def kpis() -> dict:
    """Headline KPI cards: P&L, Sharpe, drawdown, veto rate, decision counts."""
    return _manager().kpis()


@router.get("/performance")
def performance() -> dict:
    """Equity curve + performance metrics from the trade log."""
    return asdict(_manager().performance())


@router.get("/vetoes")
def vetoes() -> dict:
    """Veto totals and a by-gate breakdown from the veto ledger."""
    return asdict(_manager().veto_summary())


@router.get("/risk")
def risk() -> dict:
    """Net per-symbol exposure and concentration from the trade log."""
    return asdict(risk_view(get_config().dashboard.trade_log_path))


@router.get("/registry")
def registry() -> dict:
    """Active champions + promotion history from the immutable registry JSON."""
    return model_registry_view(get_config().evaluation.registry_path)


@router.get("/alerts")
def alerts() -> list[dict]:
    """Threshold alerts (drawdown / Sharpe / veto-rate) over the current KPIs."""
    cfg = get_config().dashboard
    manager = _manager()
    fired = check_alerts(
        manager.performance(), manager.veto_summary(),
        max_drawdown=cfg.max_drawdown_alert,
        min_sharpe=cfg.min_sharpe_alert,
        max_veto_rate=cfg.max_veto_rate_alert,
    )
    return [asdict(alert) for alert in fired]


@router.get("/trades")
def trades() -> list[dict]:
    """The most recent trade-log rows (capped), newest last; empty if no log."""
    path = get_config().dashboard.trade_log_path
    from pathlib import Path

    if not Path(path).exists():
        return []
    table = pq.read_table(path)
    rows = table.to_pylist()
    return rows[-_MAX_TRADES:]
