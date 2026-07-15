"""Whole-engine offline dry run: train+promote -> trade graph -> ledgers -> dashboard.

The capstone that proves the engine is operational end to end with no network:
the offline pipeline produces champions, the runner drives them through the real
LangGraph trade graph, and the resulting veto ledger + trade log feed the
dashboard's KPI layer.
"""

from datetime import date

from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.execution.runner import run_trading_session
from new_pipeline.monitoring.dashboard.realtime import RealtimeDataManager
from new_pipeline.tournament.pipeline import run_offline_pipeline


def test_engine_runs_end_to_end(tmp_path, monkeypatch):
    ledger_dir = tmp_path / "ledger"
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    monkeypatch.setenv("QA_EXECUTION__CONFIDENCE_THRESHOLD", "0.3")  # ensure signals fire
    monkeypatch.setenv("QA_EXECUTION__LEDGER_DIR", str(ledger_dir))
    monkeypatch.setenv("QA_SYSTEM__RUN_MODE", "backtest")
    # Synthetic noise (correctly) clears no gate; relax them so the trade path runs.
    monkeypatch.setenv("QA_EVALUATION__DSR_PROMOTION_THRESHOLD", "0.0")
    monkeypatch.setenv("QA_EVALUATION__SYNTHETIC_SR_MIN", "-1000.0")
    monkeypatch.setenv("QA_EVALUATION__PBO_THRESHOLD", "1.0")
    # This capstone needs a promotion to exercise the trade path; its ~124-day
    # run can't seat 60-obs regimes, so the (default-on) regime gate is opted out.
    monkeypatch.setenv("QA_EVALUATION__REGIME_GATE_ENABLED", "false")
    reload_config()
    seed_everything(0)

    candidates = tmp_path / "candidates"
    run_offline_pipeline(candidates, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=3)

    summary = run_trading_session(
        candidates, start=date(2021, 1, 1), end=date(2021, 6, 30)
    )

    assert summary.sectors  # at least one champion traded
    assert summary.decisions > 0
    assert summary.executed + summary.vetoed == summary.decisions

    # Both parquet artifacts the dashboard reads were produced.
    assert (ledger_dir / "veto_ledger.parquet").exists()
    manager = RealtimeDataManager(
        ledger_dir / "veto_ledger.parquet", ledger_dir / "trade_log.parquet"
    )
    kpis = manager.kpis()
    assert kpis["total_decisions"] == summary.decisions
    assert kpis["executed"] == summary.executed


def test_session_is_empty_without_champions(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_EXECUTION__LEDGER_DIR", str(tmp_path / "ledger"))
    reload_config()
    summary = run_trading_session(tmp_path / "no_candidates")
    assert summary.sectors == []
    assert summary.decisions == 0
