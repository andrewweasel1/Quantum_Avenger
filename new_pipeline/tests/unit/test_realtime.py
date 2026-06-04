from new_pipeline.execution.trade_log import TradeLog, TradeRecord
from new_pipeline.execution.veto_ledger import VetoLedger, VetoRecord
from new_pipeline.monitoring.dashboard.realtime import RealtimeDataManager


def _seed_veto(path):
    ledger = VetoLedger(path)
    ledger.append(VetoRecord("AAPL", "BUY", 100.0, "executed", "none", 0.96, 10, "o1"))
    ledger.append(VetoRecord("MSFT", "BUY", 100.0, "risk veto", "shield", 0.96, 0, ""))
    ledger.append(VetoRecord("NVDA", "BUY", 100.0, "grader rejected", "grader", 0.96, 0, ""))


def _seed_trades(path):
    log = TradeLog(path)
    for pnl, order_id in [(0.10, "a"), (-0.05, "b"), (0.08, "c")]:
        log.append(TradeRecord("AAPL", "buy", 10, 100.0, "filled", order_id, pnl=pnl))


def test_veto_summary(tmp_path):
    veto_path = tmp_path / "v.parquet"
    _seed_veto(veto_path)
    summary = RealtimeDataManager(veto_path, tmp_path / "t.parquet").veto_summary()
    assert summary.total == 3
    assert summary.executed == 1
    assert summary.vetoed == 2
    assert abs(summary.veto_rate - 2 / 3) < 1e-9
    assert summary.by_gate == {"shield": 1, "grader": 1}


def test_performance(tmp_path):
    trade_path = tmp_path / "t.parquet"
    _seed_trades(trade_path)
    perf = RealtimeDataManager(tmp_path / "v.parquet", trade_path).performance()
    assert abs(perf.total_pnl - 0.13) < 1e-9
    assert perf.win_rate == 2 / 3
    assert len(perf.equity_curve) == 3
    assert perf.max_drawdown <= 0.0


def test_kpis_combines_both(tmp_path):
    veto_path = tmp_path / "v.parquet"
    trade_path = tmp_path / "t.parquet"
    _seed_veto(veto_path)
    _seed_trades(trade_path)
    kpis = RealtimeDataManager(veto_path, trade_path).kpis()
    assert kpis["executed"] == 1
    assert kpis["vetoed"] == 2
    assert "sharpe" in kpis
    assert "total_pnl" in kpis


def test_missing_files_return_zeros(tmp_path):
    manager = RealtimeDataManager(tmp_path / "nope_v.parquet", tmp_path / "nope_t.parquet")
    assert manager.veto_summary().total == 0
    assert manager.performance().total_pnl == 0.0
    assert manager.kpis()["veto_rate"] == 0.0
