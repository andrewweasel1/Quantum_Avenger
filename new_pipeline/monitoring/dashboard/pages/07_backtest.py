"""Backtest page — run the pooled S&P 500 backtest with fusion toggles.

Wraps :func:`new_pipeline.analysis.sp500_backtest.run_sp500_backtest`. The
toggles map 1:1 to the feature families: GDELT news sentiment, expanded
(crash-risk + regime) families, and SEC point-in-time fundamentals. When
"Write snapshot" is on, the run is persisted under ``data/backtests/``.
"""

from datetime import date, timedelta

import streamlit as st

from new_pipeline.analysis.sp500_backtest import (
    SP500BacktestOptions,
    run_sp500_backtest,
)

st.title("S&P 500 Backtest")

with st.form("sp500_backtest"):
    col1, col2 = st.columns(2)
    start = col1.date_input("Start", value=date.today() - timedelta(days=730))
    end = col2.date_input("End", value=date.today() - timedelta(days=3))
    news = st.toggle("News sentiment (GDELT sector tone)", value=True)
    expanded = st.toggle("Expanded feature families (crash risk + regime)", value=True)
    fundamentals = st.toggle("Fundamentals (SEC EDGAR, point-in-time)", value=True)
    snapshot = st.toggle("Write snapshot", value=True)
    max_symbols = st.number_input(
        "Max symbols (0 = full S&P 500)", min_value=0, max_value=503, value=0
    )
    submitted = st.form_submit_button("Run backtest")

if submitted:
    options = SP500BacktestOptions(
        start=start,
        end=end,
        use_news_sentiment=news,
        expanded_families=expanded,
        use_fundamentals=fundamentals,
        write_snapshot=snapshot,
        max_symbols=int(max_symbols) or None,
    )
    with st.spinner("Running S&P 500 backtest (bars → features → model → simulation)…"):
        st.session_state["sp500_report"] = run_sp500_backtest(options)

report = st.session_state.get("sp500_report")
if report is not None:
    columns = st.columns(4)
    columns[0].metric("Total return", f"{report.total_return:+.1%}")
    columns[1].metric("Sharpe", f"{report.sharpe:.2f}")
    columns[2].metric("Max drawdown", f"{report.max_drawdown:.1%}")
    columns[3].metric("Trades", f"{report.n_trades:,}")
    st.caption(
        f"{report.n_symbols} symbols · train {report.n_train_rows:,} rows / "
        f"test {report.n_test_rows:,} rows · split {report.split_date} · "
        f"features: {', '.join(report.feature_cols)}"
    )
    for note in report.degradations:
        st.warning(note)
    if report.test_dates:
        st.subheader("Portfolio equity (out-of-sample)")
        st.line_chart(
            {"equity": report.equity_curve.tolist()},
        )
    if not report.per_symbol.is_empty():
        st.subheader("Per-symbol results")
        st.dataframe(report.per_symbol.to_pandas(), width="stretch")
    if report.snapshot_path:
        st.success(f"Snapshot written to {report.snapshot_path}")
