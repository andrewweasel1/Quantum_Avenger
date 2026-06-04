"""Grader node: does the verdict hold up against the retrieved context?

A second LLM pass returning approve/reject. The orchestrator retries the verdict
up to ``max_retries`` on rejection. Offline, the ``FakeLLMClient`` makes the
decision deterministic; tests inject scripted clients to drive the retry path.
"""

from dataclasses import dataclass

from new_pipeline.adapters.base import LLMClient, Verdict


@dataclass
class GraderResult:
    approved: bool
    feedback: str


@dataclass
class Grader:
    llm: LLMClient

    def grade(self, verdict: Verdict, context: list[str]) -> GraderResult:
        joined = "\n".join(f"- {item}" for item in context)
        prompt = (
            f"Verdict: {verdict.stance} ({verdict.rationale})\nContext:\n{joined}\n"
            "Is the verdict supported by the context? Answer YES or NO."
        )
        response = self.llm.verdict(prompt)
        # A decisive (non-neutral) grader stance counts as support.
        return GraderResult(approved=response.stance != "NEUTRAL", feedback=response.rationale)
