from new_pipeline.execution.trade_log import TRADE_LOG_SCHEMA, TradeLog, TradeRecord


def _record(pnl=0.05, exec_id="o1"):
    return TradeRecord("AAPL", "buy", 10, 100.0, "filled", exec_id, fill_price=100.1, pnl=pnl)


def test_append_and_read(tmp_path):
    log = TradeLog(tmp_path / "trades.parquet")
    log.append(_record())
    table = log.read()
    assert table.num_rows == 1
    assert table.schema.names == TRADE_LOG_SCHEMA.names
    assert table.column("pnl").to_pylist() == [0.05]


def test_append_only_accumulates(tmp_path):
    log = TradeLog(tmp_path / "trades.parquet")
    log.append(_record(exec_id="a"))
    log.append(_record(pnl=-0.02, exec_id="b"))
    assert len(log) == 2


def test_read_empty(tmp_path):
    assert TradeLog(tmp_path / "missing.parquet").read().num_rows == 0
