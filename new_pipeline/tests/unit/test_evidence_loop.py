"""The agentic evidence loop: retrieve -> verdict -> grader, config-gated."""

from new_pipeline.adapters import FakeBroker
from new_pipeline.adapters.base import LLMClient, SentimentResult, Verdict
from new_pipeline.config import reload_config
from new_pipeline.execution.orchestrator import TradeOrchestrator, TradeRequest
from new_pipeline.execution.rag_engine import HashingEmbedder, RagEngine, build_rag_engine
from new_pipeline.execution.veto_ledger import VetoLedger

_CONTEXT = [
    "AAPL beats earnings expectations by a wide margin. Analysts raise targets.",
    "Weather in Cupertino is sunny this week with mild temperatures.",
    "AAPL supply chain constraints ease; BUY momentum builds among funds.",
]


class _CapturingLLM(LLMClient):
    """Scripted stance + captures every prompt so tests can inspect the flow."""

    def __init__(self, stance="BULLISH"):
        self.stance = stance
        self.prompts: list[str] = []

    def sentiment(self, text):
        return SentimentResult(0.0, "neutral")

    def verdict(self, prompt):
        self.prompts.append(prompt)
        return Verdict(self.stance, "scripted")


def _request():
    return TradeRequest(
        "BUY", "AAPL", 100.0, 1.0, 2.0, 100000.0, 0.02, 0.0, 5e6, 5e6, 0.02, list(_CONTEXT)
    )


def test_evidence_node_populates_state_and_prompts(tmp_path):
    llm = _CapturingLLM("BULLISH")
    rag = RagEngine(HashingEmbedder(), top_k=2)
    out = TradeOrchestrator(llm, FakeBroker(), VetoLedger(tmp_path / "v.parquet"), rag=rag).run(
        _request()
    )

    assert out["outcome"] == "executed"
    assert out["evidence"], "evidence should be retrieved from the request context"
    assert len(out["evidence"]) <= 2  # top_k respected
    # The relevant AAPL passages should outrank the weather noise.
    assert any("AAPL" in passage for passage in out["evidence"])

    verdict_prompt, grader_prompt = llm.prompts[0], llm.prompts[1]
    assert "Retrieved evidence" in verdict_prompt
    assert "FOR and AGAINST" in verdict_prompt
    assert "Retrieved evidence" in grader_prompt
    assert "MISSING" in grader_prompt  # the evidence_for/against/missing instruction


def test_no_rag_keeps_prompts_byte_identical_to_legacy(tmp_path):
    llm = _CapturingLLM("BULLISH")
    TradeOrchestrator(llm, FakeBroker(), VetoLedger(tmp_path / "v.parquet")).run(_request())

    assert "evidence" not in llm.prompts[0] and "evidence" not in llm.prompts[1].lower()
    assert llm.prompts[1].endswith("Is the verdict supported by the context? Answer YES or NO.")


def test_grader_retry_reuses_evidence_without_reindexing(tmp_path):
    class _RejectingThenApprovingLLM(_CapturingLLM):
        def verdict(self, prompt):
            self.prompts.append(prompt)
            # Grader prompts start with "Verdict:"; reject the first grade, approve later.
            grades = [p for p in self.prompts if p.startswith("Verdict:")]
            if prompt.startswith("Verdict:") and len(grades) == 1:
                return Verdict("NEUTRAL", "insufficient evidence")
            return Verdict("BULLISH", "ok")

    class _CountingRag(RagEngine):
        def __init__(self):
            super().__init__(HashingEmbedder(), top_k=2)
            self.index_calls = 0

        def index(self, documents):
            self.index_calls += 1
            super().index(documents)

    llm = _RejectingThenApprovingLLM()
    rag = _CountingRag()
    out = TradeOrchestrator(
        llm, FakeBroker(), VetoLedger(tmp_path / "v.parquet"), max_retries=3, rag=rag
    ).run(_request())

    assert out["outcome"] == "executed"
    assert out["attempts"] == 2  # one grader rejection -> one verdict retry
    assert rag.index_calls == 1  # evidence retrieved once, reused across the retry


def test_build_rag_engine_defaults_to_hashing():
    cfg = reload_config()
    engine = build_rag_engine(cfg)
    assert isinstance(engine.embedder, HashingEmbedder)
    assert engine.top_k == cfg.rag.top_k
