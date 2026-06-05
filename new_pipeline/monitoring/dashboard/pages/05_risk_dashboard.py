"""Risk dashboard page — exposure and concentration."""

import streamlit as st
from new_pipeline.config import get_config
from new_pipeline.monitoring.dashboard.views import risk_view

st.title("Risk Dashboard")

view = risk_view(get_config().dashboard.trade_log_path)
columns = st.columns(4)
columns[0].metric("Gross exposure", f"${view.gross_exposure:,.0f}")
columns[1].metric("Open positions", view.position_count)
columns[2].metric("Largest position", f"${view.largest_position:,.0f}")
columns[3].metric("Concentration", f"{view.concentration:.0%}")
