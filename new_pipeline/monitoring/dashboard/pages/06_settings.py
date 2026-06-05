"""Settings page — current configuration and alert thresholds (read-only)."""

import streamlit as st
from new_pipeline.config import get_config

st.title("Settings")

cfg = get_config()
st.subheader("Risk & execution")
st.json(cfg.execution.model_dump())
st.subheader("Alert thresholds")
st.json(cfg.dashboard.model_dump())
st.caption("Edit via config overlays / QA_ env vars. Auth: DASHBOARD_USER / DASHBOARD_PASS.")
