from new_pipeline.adapters.base import LLMClient, SentimentResult, Verdict
from new_pipeline.execution.grader import Grader
from new_pipeline.execution.verdict_engine import VerdictEngine


class _StubLLM(LLMClient):
    def __init__(self, stance: str):
        self._stance = stance

    def sentiment(self, text):
        return SentimentResult(0.0, "neutral")

    def verdict(self, prompt):
        return Verdict(self._stance, "because")


def test_verdict_engine_returns_stance():
    verdict = VerdictEngine(_StubLLM("BULLISH")).generate("BUY", "AAPL", ["ctx"])
    assert verdict.stance == "BULLISH"


def test_grader_approves_decisive_stance():
    result = Grader(_StubLLM("BULLISH")).grade(Verdict("BULLISH", ""), ["ctx"])
    assert result.approved is True


def test_grader_rejects_neutral():
    result = Grader(_StubLLM("NEUTRAL")).grade(Verdict("BULLISH", ""), ["ctx"])
    assert result.approved is False
