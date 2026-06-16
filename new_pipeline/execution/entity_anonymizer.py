"""Entity anonymization for the LLM/sentiment pipeline (G1 defense).

Tradable entities (tickers and company names) are masked to opaque placeholders
("[COMPANY_A]") before text reaches a generative LLM, defeating name
memorization / look-ahead. Offline by default: deterministic regex over a
supplied vocabulary — no spaCy model download needed.

Two optional upgrades keep the same interface:
  * a **gazetteer** ``{ticker: [alias, ...]}`` so every surface form of one
    tradable entity ("Apple", "AAPL", "Apple Inc.") collapses to the *same*
    placeholder and resolves to a ticker via ``ticker_to_token`` — which lets a
    downstream sentiment score re-attach to the right ticker;
  * **structural masking** of URLs/emails/cashtags/money/percent, stripping
    numeric anchors a model could memorize against.

A spaCy NER pass for open-vocabulary entities layers on behind the same
``Anonymizer`` interface (``execution/anonymizer_spacy.py``).
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_CASHTAG_RE = re.compile(r"\$[A-Za-z]{1,5}\b")
_MONEY_RE = re.compile(r"[\$€£]\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:million|billion|bn|m|k))?", re.I)
_PERCENT_RE = re.compile(r"\b\d+(?:\.\d+)?\s?%")


@dataclass
class AnonymizationResult:
    text: str
    mapping: dict[str, str]  # placeholder -> original surface form
    # ticker -> placeholder, so a caller can re-attach a score to the right ticker
    ticker_to_token: dict[str, str] = field(default_factory=dict)


def _placeholder(index: int) -> str:
    suffix = chr(ord("A") + index) if index < 26 else str(index)
    return f"[COMPANY_{suffix}]"


def _mask_structural(text: str) -> str:
    """Strip numeric/identifier anchors (order matters: cashtag before money)."""
    text = _URL_RE.sub("[URL]", text)
    text = _EMAIL_RE.sub("[EMAIL]", text)
    text = _CASHTAG_RE.sub("[TICKER]", text)
    text = _MONEY_RE.sub("[MONEY]", text)
    text = _PERCENT_RE.sub("[PERCENT]", text)
    return text


class Anonymizer(ABC):
    """Mask tradable entities in financial text. ``anonymize_batch`` defaults to a
    per-document loop; model-backed implementations override it for batching."""

    @abstractmethod
    def anonymize(self, text: str) -> AnonymizationResult:
        raise NotImplementedError

    def anonymize_batch(self, texts: list[str]) -> list[AnonymizationResult]:
        return [self.anonymize(text) for text in texts]


@dataclass
class EntityAnonymizer(Anonymizer):
    """Deterministic vocabulary/gazetteer anonymizer (offline, no model download)."""

    vocabulary: list[str] = field(default_factory=list)
    # {ticker: [alias, ...]}; aliases of one ticker collapse to a single token.
    gazetteer: dict[str, list[str]] = field(default_factory=dict)
    mask_structural: bool = False

    def __post_init__(self) -> None:
        # alias/ticker (lowercased) -> canonical ticker
        self._alias_to_ticker: dict[str, str] = {}
        for ticker, aliases in self.gazetteer.items():
            self._alias_to_ticker[ticker.lower()] = ticker
            for alias in aliases:
                self._alias_to_ticker[alias.lower()] = ticker
        terms: set[str] = {t for t in self.vocabulary if t}
        terms.update(self.gazetteer.keys())
        for aliases in self.gazetteer.values():
            terms.update(aliases)
        # Longest term first so "Apple Inc" is masked before "Apple".
        self._terms: list[str] = sorted({t for t in terms if t}, key=len, reverse=True)

    def anonymize(self, text: str) -> AnonymizationResult:
        result = _mask_structural(text) if self.mask_structural else text
        mapping: dict[str, str] = {}
        ticker_to_token: dict[str, str] = {}
        token_of_key: dict[str, str] = {}  # ticker | lowered surface -> placeholder
        for term in self._terms:
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            if not pattern.search(result):
                continue
            ticker = self._alias_to_ticker.get(term.lower())
            key = ticker if ticker else term.lower()
            if key not in token_of_key:
                placeholder = _placeholder(len(token_of_key))
                token_of_key[key] = placeholder
                mapping[placeholder] = term
                if ticker:
                    ticker_to_token[ticker] = placeholder
            result = pattern.sub(token_of_key[key], result)
        return AnonymizationResult(text=result, mapping=mapping, ticker_to_token=ticker_to_token)

    @staticmethod
    def deanonymize(text: str, mapping: dict[str, str]) -> str:
        result = text
        for placeholder, original in mapping.items():
            result = result.replace(placeholder, original)
        return result
