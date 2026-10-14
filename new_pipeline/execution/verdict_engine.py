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

    def generate(
        self, signal: str, symbol: str, context: list[str], evidence: list[str] | None = None
    ) -> Verdict:
        return self.llm.verdict(self._build_prompt(signal, symbol, context, evidence))

    @staticmethod
    def _build_prompt(
        signal: str, symbol: str, context: list[str], evidence: list[str] | None = None
    ) -> str:
        joined = "\n".join(f"- {item}" for item in context)
        prompt = f"Signal: {signal}\nSymbol: {symbol}\nContext:\n{joined}\n"
        if evidence:
            passages = "\n".join(f"- {item}" for item in evidence)
            prompt += (
                f"Retrieved evidence (most relevant first):\n{passages}\n"
                "Weigh the evidence FOR and AGAINST the signal before deciding.\n"
            )
        return prompt + "Generate a BULLISH/BEARISH/NEUTRAL verdict with a one-line rationale."
