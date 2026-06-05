"""Model registry page — active champions and promotion history."""

import streamlit as st
from new_pipeline.config import get_config
from new_pipeline.monitoring.dashboard.views import model_registry_view

st.title("Model Registry")

view = model_registry_view(get_config().evaluation.registry_path)
st.subheader("Active champions")
st.json(view["active_champions"])
st.subheader("Promotion history")
if view["promotions"]:
    st.dataframe(view["promotions"])
else:
    st.info("No promotions recorded yet.")
