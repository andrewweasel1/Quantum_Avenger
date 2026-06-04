"""Live monitor page — execution counts, win rate, and the equity curve."""

import streamlit as st
from new_pipeline.monitoring.dashboard.app import build_manager

st.title("Live Monitor")

manager = build_manager()
kpis = manager.kpis()
columns = st.columns(3)
columns[0].metric("Executed", kpis["executed"])
columns[1].metric("Vetoed", kpis["vetoed"])
columns[2].metric("Win Rate", f"{kpis['win_rate']:.0%}")

performance = manager.performance()
if performance.equity_curve:
    st.line_chart(performance.equity_curve)
else:
    st.info("No trades logged yet.")
