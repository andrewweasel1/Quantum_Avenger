"""The process-wide metrics collector and its production increment sites."""

from new_pipeline.adapters import FakeBroker
from new_pipeline.adapters.base import LLMClient, SentimentResult, Verdict
from new_pipeline.execution.orchestrator import TradeOrchestrator, TradeRequest
from new_pipeline.execution.veto_ledger import VetoLedger
from new_pipeline.monitoring.metrics import get_metrics, reset_metrics


class _ScriptedLLM(LLMClient):
    def __init__(self, stance: str):
        self._stance = stance

    def sentiment(self, text):
        return SentimentResult(0.0, "neutral")

    def verdict(self, prompt):
        return Verdict(self._stance, "rationale")


def _request(capital=100000.0):
    return TradeRequest(
        "BUY", "AAPL", 100.0, 1.0, 2.0, capital, 0.02, 0.0, 5e6, 5e6, 0.02, ["ctx"]
    )


def test_singleton_identity_and_reset():
    collector = get_metrics()
    collector.increment("x")
    assert get_metrics() is collector
    assert get_metrics().get("x") == 1
    reset_metrics()
    assert get_metrics().get("x") == 0


def test_executed_trade_increments_counters(tmp_path):
    ledger = VetoLedger(tmp_path / "v.parquet")
    TradeOrchestrator(_ScriptedLLM("BULLISH"), FakeBroker(), ledger).run(_request())
    metrics = get_metrics()
    assert metrics.get("decisions_total") == 1
    assert metrics.get("executed_total") == 1
    assert metrics.get("vetoed_total") == 0


def test_grader_veto_increments_gate_counter(tmp_path):
    ledger = VetoLedger(tmp_path / "v.parquet")
    TradeOrchestrator(_ScriptedLLM("NEUTRAL"), FakeBroker(), ledger).run(_request())
    metrics = get_metrics()
    assert metrics.get("decisions_total") == 1
    assert metrics.get("vetoed_total") == 1
    assert metrics.get("vetoed_grader_total") == 1


def test_shield_veto_increments_gate_counter(tmp_path):
    ledger = VetoLedger(tmp_path / "v.parquet")
    orchestrator = TradeOrchestrator(_ScriptedLLM("BULLISH"), FakeBroker(), ledger)
    orchestrator.run(_request(capital=50.0))  # account too small -> Shield veto
    assert get_metrics().get("vetoed_shield_total") == 1
