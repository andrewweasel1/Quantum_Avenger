"""Phase 5 offline integration: news -> anonymize -> RAG context -> decision -> ledger.

The Milestone M4 capstone — the full live-execution graph driven by fakes, no
network, deterministic.
"""

from datetime import date

from new_pipeline.adapters import FakeBroker, FakeNewsSource, StaticUniverseProvider
from new_pipeline.adapters.base import LLMClient, SentimentResult, Verdict
from new_pipeline.execution.entity_anonymizer import EntityAnonymizer
from new_pipeline.execution.orchestrator import TradeOrchestrator, TradeRequest
from new_pipeline.execution.rag_engine import RagEngine
from new_pipeline.execution.veto_ledger import VetoLedger


class _BullLLM(LLMClient):
    def sentiment(self, text):
        return SentimentResult(1.0, "bullish")

    def verdict(self, prompt):
        return Verdict("BULLISH", "supported by context")


def test_offline_execution_flow(tmp_path):
    # 1) news -> anonymized against the universe vocabulary (no tradable names leak)
    universe = StaticUniverseProvider()
    anonymizer = EntityAnonymizer(vocabulary=universe.symbols(date(2020, 1, 1)))
    headlines = FakeNewsSource().headlines("AAPL", date(2022, 6, 1))
    masked = [anonymizer.anonymize(item.headline).text for item in headlines]
    assert all("AAPL" not in text for text in masked)

    # 2) RAG context from the masked corpus
    rag = RagEngine(top_k=2)
    rag.index([*masked, "Market sentiment steady amid macro data."])
    context = [hit.text for hit in rag.retrieve("company outlook")]
    assert context

    # 3) orchestrate -> ledger
    ledger = VetoLedger(tmp_path / "veto.parquet")
    request = TradeRequest(
        "BUY", "AAPL", 100.0, 1.0, 2.0, 100000.0, 0.02, 0.0, 5e6, 5e6, 0.02, context
    )
    out = TradeOrchestrator(_BullLLM(), FakeBroker(), ledger).run(request)

    assert out["outcome"] in {"executed", "vetoed"}
    assert ledger.read().num_rows == 1
