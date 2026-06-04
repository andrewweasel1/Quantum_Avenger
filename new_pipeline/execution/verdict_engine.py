"""Verdict generation: turn a signal + retrieved context into a stance.

Delegates entirely to an ``LLMClient`` (the offline ``FakeLLMClient`` in dev and
tests). The LLM only produces a narrative stance — it performs no math (G1);
all quantities flow through deterministic tools / the Shield.
"""

from dataclasses import dataclass

from new_pipeline.adapters.base import LLMClient, Verdict


@dataclass
class VerdictEngine:
    llm: LLMClient

    def generate(self, signal: str, symbol: str, context: list[str]) -> Verdict:
        return self.llm.verdict(self._build_prompt(signal, symbol, context))

    @staticmethod
    def _build_prompt(signal: str, symbol: str, context: list[str]) -> str:
        joined = "\n".join(f"- {item}" for item in context)
        return (
            f"Signal: {signal}\nSymbol: {symbol}\nContext:\n{joined}\n"
            "Generate a BULLISH/BEARISH/NEUTRAL verdict with a one-line rationale."
        )
