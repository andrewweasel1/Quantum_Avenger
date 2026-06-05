"""Trade log page — recent fills and realized P&L."""

import streamlit as st
from new_pipeline.config import get_config
from new_pipeline.execution.trade_log import TradeLog

st.title("Trade Log")

table = TradeLog(get_config().dashboard.trade_log_path).read()
if table.num_rows:
    st.dataframe(table.to_pandas())
else:
    st.info("No trades logged yet.")
