"""spaCy + gazetteer news anonymizer (live; heavy dep, lazy-imported).

Open-vocabulary NER (spaCy) fused with the universe gazetteer -- the gazetteer
wins ties because tradable entities (the ones we can trade) matter most for
look-ahead, and it resolves them to a ticker. Same ``Anonymizer`` interface as
the offline ``EntityAnonymizer``. NOT in the offline CI image: spaCy is imported
lazily and the module is coverage-omitted. An ``nlp`` pipeline may be injected
(e.g. ``spacy.blank("en")``) to exercise the gazetteer path without a model
download.

Ordering note: entity spans are computed and replaced on the *original* text
(gazetteer + NER offsets stay consistent), and structural masking
(URL/email/cashtag/money/percent, which is offset-independent) runs afterward.
"""

from __future__ import annotations

import re

from new_pipeline.execution.entity_anonymizer import (
    AnonymizationResult,
    Anonymizer,
    _mask_structural,
)

# Entity types worth masking (open-vocabulary, via spaCy NER).
_MASKABLE = {"ORG", "PERSON", "GPE", "PRODUCT", "FAC", "NORP"}


class SpacyNewsAnonymizer(Anonymizer):
    def __init__(
        self,
        universe_aliases,
        spacy_model: str = "en_core_web_lg",
        mask_money: bool = True,
        use_gpu: bool = False,
        nlp=None,
    ) -> None:
        self.mask_money = mask_money
        self._alias_to_ticker: dict[str, str] = {}
        for ticker, aliases in universe_aliases.items():
            self._alias_to_ticker[ticker.lower()] = ticker
            for alias in aliases:
                self._alias_to_ticker[alias.lower()] = ticker
        self._gazetteer_re = self._compile_gazetteer(self._alias_to_ticker.keys())

        if nlp is not None:
            self.nlp = nlp
        else:  # pragma: no cover - needs the spaCy model download / egress
            import spacy

            if use_gpu:
                try:
                    spacy.require_gpu()
                except Exception as exc:
                    import logging

                    logging.getLogger(__name__).warning("spaCy GPU unavailable: %s", exc)
            self.nlp = spacy.load(spacy_model, disable=["lemmatizer", "tagger"])

    @staticmethod
    def _compile_gazetteer(aliases) -> re.Pattern | None:
        terms = sorted({a for a in aliases if a.strip()}, key=len, reverse=True)
        if not terms:
            return None
        body = "|".join(re.escape(t) for t in terms)
        return re.compile(rf"\b({body})\b", re.IGNORECASE)

    # ------------------------------------------------------------------ public
    def anonymize_batch(self, texts: list[str]) -> list[AnonymizationResult]:
        return [self._anonymize_doc(doc.text, doc) for doc in self.nlp.pipe(texts, batch_size=64)]

    def anonymize(self, text: str) -> AnonymizationResult:
        return self.anonymize_batch([text])[0]

    # ----------------------------------------------------------------- private
    def _anonymize_doc(self, text: str, doc) -> AnonymizationResult:
        spans: list[tuple[int, int, str, str | None]] = []
        if self._gazetteer_re is not None:
            for m in self._gazetteer_re.finditer(text):
                spans.append((m.start(), m.end(), "ORG", self._alias_to_ticker[m.group(1).lower()]))
        for ent in getattr(doc, "ents", ()):
            if ent.label_ in _MASKABLE:
                spans.append((ent.start_char, ent.end_char, ent.label_, None))
        spans = self._dedupe_overlaps(spans)

        counters: dict[str, int] = {}
        token_of_key: dict[str, str] = {}
        mapping: dict[str, str] = {}
        ticker_to_token: dict[str, str] = {}
        result = text
        # Replace right-to-left so earlier offsets stay valid.
        for start, end, label, ticker in sorted(spans, key=lambda s: s[0], reverse=True):
            surface = text[start:end]
            key = ticker if ticker else surface.lower()
            family = "COMPANY" if label == "ORG" else label
            if key not in token_of_key:
                idx = counters.get(family, 0)
                suffix = chr(ord("A") + idx) if family == "COMPANY" else str(idx + 1)
                token = f"[{family}_{suffix}]"
                counters[family] = idx + 1
                token_of_key[key] = token
                mapping[token] = surface
                if ticker:
                    ticker_to_token[ticker] = token
            result = result[:start] + token_of_key[key] + result[end:]

        if self.mask_money:
            result = _mask_structural(result)
        return AnonymizationResult(text=result, mapping=mapping, ticker_to_token=ticker_to_token)

    @staticmethod
    def _dedupe_overlaps(spans):
        # Longest first; gazetteer hit (ticker not None) wins ties.
        spans.sort(key=lambda s: (s[1] - s[0], s[3] is not None), reverse=True)
        kept: list = []
        for s in spans:
            if not any(not (s[1] <= k[0] or s[0] >= k[1]) for k in kept):
                kept.append(s)
        return kept
