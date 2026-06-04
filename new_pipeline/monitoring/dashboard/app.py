"""Quantum Avenger — Streamlit monitoring dashboard (Phase 6).

Run: ``streamlit run new_pipeline/monitoring/dashboard/app.py``
Reads the veto ledger + trade log via RealtimeDataManager (offline, no network).
When ``dashboard.auth_enabled`` is set, a login gate guards the app
(credentials from DASHBOARD_USER / DASHBOARD_PASS).
"""

import streamlit as st

from new_pipeline.config import get_config
from new_pipeline.monitoring.dashboard.alerts import check_alerts
from new_pipeline.monitoring.dashboard.auth import require_login
from new_pipeline.monitoring.dashboard.realtime import RealtimeDataManager


def build_manager() -> RealtimeDataManager:
    cfg = get_config().dashboard
    return RealtimeDataManager(cfg.veto_ledger_path, cfg.trade_log_path)


def main() -> None:
    cfg = get_config().dashboard
    st.set_page_config(page_title="Quantum Avenger", layout="wide", page_icon="🛡️")
    if cfg.auth_enabled and not require_login(st):
        return
    st.title("🛡️ Quantum Avenger — Monitoring")

    manager = build_manager()
    kpis = manager.kpis()
    performance = manager.performance()
    veto = manager.veto_summary()

    columns = st.columns(4)
    columns[0].metric("Total P&L", f"{kpis['total_pnl']:.2%}")
    columns[1].metric("Sharpe", f"{kpis['sharpe']:.2f}")
    columns[2].metric("Max Drawdown", f"{kpis['max_drawdown']:.1%}")
    columns[3].metric("Veto Rate", f"{kpis['veto_rate']:.0%}")

    for alert in check_alerts(
        performance,
        veto,
        max_drawdown=cfg.max_drawdown_alert,
        min_sharpe=cfg.min_sharpe_alert,
        max_veto_rate=cfg.max_veto_rate_alert,
    ):
        (st.error if alert.severity == "critical" else st.warning)(alert.message)

    if performance.equity_curve:
        st.subheader("Equity curve")
        st.line_chart(performance.equity_curve)

    if veto.by_gate:
        st.subheader("Vetoes by gate")
        st.bar_chart(veto.by_gate)


if __name__ == "__main__":
    main()
