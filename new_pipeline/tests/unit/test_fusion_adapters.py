"""Fusion adapters (FinBERT + spaCy). The modules are coverage-omitted (heavy
deps), so the bug-prone *pure* logic is checked without torch/spaCy, and the
model-backed paths are gated behind ``pytest.importorskip`` + dependency
injection (mirroring tests/unit/test_alpaca_adapters.py)."""

from types import SimpleNamespace

import numpy as np
import pytest
from new_pipeline.adapters.sentiment_finbert import _probs_to_scores, _resolve_label_indices


def test_resolve_label_indices_handles_permutations():
    assert _resolve_label_indices({0: "positive", 1: "negative", 2: "neutral"}) == (0, 1, 2)
    assert _resolve_label_indices({0: "Neutral", 1: "Positive", 2: "Negative"}) == (1, 2, 0)


def test_probs_to_scores_signed_is_pos_minus_neg():
    probs = np.array([[0.7, 0.1, 0.2], [0.1, 0.8, 0.1]])
    scores = _probs_to_scores(probs, pos_i=0, neg_i=1, neu_i=2)
    assert abs(scores[0].signed - 0.6) < 1e-9
    assert abs(scores[1].signed - (-0.7)) < 1e-9
    assert abs(scores[0].confidence - 0.7) < 1e-9


def test_finbert_engine_scores_with_injected_model():
    torch = pytest.importorskip("torch")  # skipped in the offline CI image
    from new_pipeline.adapters.sentiment_finbert import FinBERTSentimentEngine

    class _Enc(dict):
        def to(self, _device):
            return self

    class _Tokenizer:
        def __call__(self, batch, **_kw):
            n = len(batch)
            return _Enc(
                input_ids=torch.zeros((n, 4), dtype=torch.long),
                attention_mask=torch.ones((n, 4), dtype=torch.long),
            )

    class _Model:
        config = SimpleNamespace(id2label={0: "positive", 1: "negative", 2: "neutral"})

        def __call__(self, **enc):
            n = enc["input_ids"].shape[0]
            return SimpleNamespace(logits=torch.tensor([[5.0, 0.0, 0.0]] * n))

    engine = FinBERTSentimentEngine(model=_Model(), tokenizer=_Tokenizer(), device="cpu")
    scores = engine.score_headlines(["AAPL beats", "MSFT beats"], batch_size=8)
    assert len(scores) == 2
    assert scores[0].signed > 0.9  # strong-positive logits -> bullish


def test_spacy_anonymizer_gazetteer_path():
    spacy = pytest.importorskip("spacy")  # skipped in the offline CI image
    from new_pipeline.execution.anonymizer_spacy import SpacyNewsAnonymizer

    # spacy.blank has no NER, so this exercises the gazetteer path without a model download.
    anon = SpacyNewsAnonymizer({"AAPL": ["Apple"]}, nlp=spacy.blank("en"))
    result = anon.anonymize("Apple rose 5% today")
    assert result.ticker_to_token["AAPL"] in result.text
    assert "Apple" not in result.text
    assert "[PERCENT]" in result.text
