"""Entity anonymization for the LLM verdict pipeline (G1 defense).

Tradable entities (tickers and company names) are masked to opaque placeholders
("[COMPANY_A]") before any text reaches the LLM, defeating name memorization /
look-ahead. Offline by default: it masks a supplied vocabulary (e.g. the
universe's tickers and names) with deterministic regex — no spaCy model download
needed. A spaCy NER pass for open-vocabulary entities can layer on later behind
the same interface.
"""

import re
from dataclasses import dataclass, field


@dataclass
class AnonymizationResult:
    text: str
    mapping: dict[str, str]  # placeholder -> original


def _placeholder(index: int) -> str:
    suffix = chr(ord("A") + index) if index < 26 else str(index)
    return f"[COMPANY_{suffix}]"


@dataclass
class EntityAnonymizer:
    vocabulary: list[str] = field(default_factory=list)

    def anonymize(self, text: str) -> AnonymizationResult:
        mapping: dict[str, str] = {}
        assigned: dict[str, str] = {}  # original -> placeholder
        result = text
        # Longest term first so "Apple Inc" is masked before "Apple".
        for term in sorted({t for t in self.vocabulary if t}, key=len, reverse=True):
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            if not pattern.search(result):
                continue
            if term not in assigned:
                placeholder = _placeholder(len(assigned))
                assigned[term] = placeholder
                mapping[placeholder] = term
            result = pattern.sub(assigned[term], result)
        return AnonymizationResult(text=result, mapping=mapping)

    @staticmethod
    def deanonymize(text: str, mapping: dict[str, str]) -> str:
        result = text
        for placeholder, original in mapping.items():
            result = result.replace(placeholder, original)
        return result
