from new_pipeline.adapters import FakeBroker
from new_pipeline.adapters.base import LLMClient, SentimentResult, Verdict
from new_pipeline.execution.orchestrator import TradeOrchestrator, TradeRequest
from new_pipeline.execution.veto_ledger import VetoLedger


class _ScriptedLLM(LLMClient):
    def __init__(self, stance: str):
        self._stance = stance

    def sentiment(self, text):
        return SentimentResult(0.0, "neutral")

    def verdict(self, prompt):
        return Verdict(self._stance, "rationale")


def _executable_request():
    return TradeRequest(
        "BUY", "AAPL", 100.0, 1.0, 2.0, 100000.0, 0.02, 0.0, 5e6, 5e6, 0.02, ["ctx"]
    )


def test_happy_path_executes(tmp_path):
    ledger = VetoLedger(tmp_path / "v.parquet")
    out = TradeOrchestrator(_ScriptedLLM("BULLISH"), FakeBroker(), ledger).run(
        _executable_request()
    )
    assert out["outcome"] == "executed"
    assert out["position_size"] == 1000.0
    assert out["execution_id"]
    assert ledger.read().column("veto_gate").to_pylist() == ["none"]


def test_grader_veto_after_retries(tmp_path):
    ledger = VetoLedger(tmp_path / "v.parquet")
    out = TradeOrchestrator(_ScriptedLLM("NEUTRAL"), FakeBroker(), ledger, max_retries=3).run(
        _executable_request()
    )
    assert out["outcome"] == "vetoed"
    assert out["attempts"] == 3  # retried up to the limit before falling back
    assert ledger.read().column("veto_gate").to_pylist() == ["grader"]


def test_shield_veto_when_account_too_small(tmp_path):
    ledger = VetoLedger(tmp_path / "v.parquet")
    tiny = TradeRequest("BUY", "AAPL", 100.0, 1.0, 2.0, 50.0, 0.02, 0.0, 5e6, 5e6, 0.02, ["ctx"])
    out = TradeOrchestrator(_ScriptedLLM("BULLISH"), FakeBroker(), ledger).run(tiny)
    assert out["outcome"] == "vetoed"
    assert ledger.read().column("veto_gate").to_pylist() == ["shield"]


def test_broker_records_executed_order(tmp_path):
    broker = FakeBroker()
    TradeOrchestrator(_ScriptedLLM("BULLISH"), broker, VetoLedger(tmp_path / "v.parquet")).run(
        _executable_request()
    )
    assert broker.get_positions()["AAPL"] == 1000.0
    assert broker.orders[0]["tif"] == "day"
