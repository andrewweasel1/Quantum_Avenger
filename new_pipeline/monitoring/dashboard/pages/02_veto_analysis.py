"""Veto analysis page — rejection breakdown by gate."""

import streamlit as st
from new_pipeline.monitoring.dashboard.app import build_manager

st.title("Veto Analysis")

veto = build_manager().veto_summary()
st.metric("Veto rate", f"{veto.veto_rate:.0%}")
if veto.by_gate:
    st.bar_chart(veto.by_gate)
else:
    st.info("No vetoes recorded yet.")
