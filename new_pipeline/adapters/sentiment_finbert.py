"""FinBERT sentiment engine (live sensor; heavy deps, lazy-imported).

``ProsusAI/finbert`` in eval mode -> a deterministic signed score, which keeps it
on the deterministic side of the ML/LLM isolation boundary (G1): it produces a
number, not a generative verdict. NOT in the offline CI image -- torch and
transformers are imported lazily in ``__init__`` (blueprint:
``core/seeding.py::_seed_torch``) and this module is coverage-omitted. The
bug-prone pure logic (label-index resolution and softmax-probs -> SentimentScore)
is factored into module functions so it is checkable without GPU weights.

Long documents (10-K / 10-Q): FinBERT is a 512-token encoder; ``score_document``
sliding-windows with overflow and aggregates chunk scores by confidence-weighted
mean (chunk-then-aggregate, not late chunking).
"""

from __future__ import annotations

import numpy as np

from new_pipeline.adapters.base import SentimentEngine, SentimentScore

_MODEL = "ProsusAI/finbert"  # label order: [positive, negative, neutral]


def _resolve_label_indices(id2label) -> tuple[int, int, int]:
    """Map (pos, neg, neu) class indices robustly to label permutations."""
    lower = {int(i): str(label).lower() for i, label in id2label.items()}
    pos = next(i for i, label in lower.items() if "pos" in label)
    neg = next(i for i, label in lower.items() if "neg" in label)
    neu = next(i for i, label in lower.items() if "neu" in label)
    return pos, neg, neu


def _probs_to_scores(probs, pos_i: int, neg_i: int, neu_i: int) -> list[SentimentScore]:
    """(B, 3) softmax probabilities -> SentimentScore list (signed = p_pos - p_neg)."""
    return [
        SentimentScore(
            signed=float(p[pos_i] - p[neg_i]),
            confidence=float(p.max()),
            p_pos=float(p[pos_i]),
            p_neg=float(p[neg_i]),
            p_neutral=float(p[neu_i]),
        )
        for p in np.asarray(probs, dtype=np.float64)
    ]


class FinBERTSentimentEngine(SentimentEngine):
    def __init__(
        self,
        model_name: str = _MODEL,
        device: str | None = None,
        max_length: int = 512,
        fp16: bool = True,
        model=None,
        tokenizer=None,
    ) -> None:
        import torch
        import torch.nn.functional as F

        self._torch = torch
        self._F = F
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.max_length = max_length
        if model is None or tokenizer is None:  # pragma: no cover - needs weights/egress
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            if fp16 and self.device.type == "cuda":
                model = model.half()
            model.to(self.device).eval()
        self.tokenizer = tokenizer
        self.model = model
        self._pos_i, self._neg_i, self._neu_i = _resolve_label_indices(model.config.id2label)

    def score_headlines(self, texts, batch_size: int = 64) -> list[SentimentScore]:
        out: list[SentimentScore] = []
        with self._torch.no_grad():
            for start in range(0, len(texts), batch_size):
                probs = self._forward(list(texts[start : start + batch_size]))
                out.extend(_probs_to_scores(probs, self._pos_i, self._neg_i, self._neu_i))
        return out

    def score_document(self, text: str, stride: int = 64) -> SentimentScore:
        with self._torch.no_grad():
            enc = self.tokenizer(
                text,
                return_overflowing_tokens=True,
                max_length=self.max_length,
                stride=stride,
                truncation=True,
                padding="max_length",
                return_tensors="pt",
            )
            ids = enc["input_ids"].to(self.device)
            mask = enc["attention_mask"].to(self.device)
            logits = self.model(input_ids=ids, attention_mask=mask).logits
            probs = self._F.softmax(logits.float(), dim=-1).cpu().numpy()
        chunks = _probs_to_scores(probs, self._pos_i, self._neg_i, self._neu_i)
        conf = np.array([c.confidence for c in chunks], dtype=np.float64)
        w = conf / conf.sum() if conf.sum() > 0 else np.full(len(chunks), 1.0 / len(chunks))
        return SentimentScore(
            signed=float(sum(c.signed * wi for c, wi in zip(chunks, w, strict=True))),
            confidence=float(conf.mean()),
            p_pos=float(sum(c.p_pos * wi for c, wi in zip(chunks, w, strict=True))),
            p_neg=float(sum(c.p_neg * wi for c, wi in zip(chunks, w, strict=True))),
            p_neutral=float(sum(c.p_neutral * wi for c, wi in zip(chunks, w, strict=True))),
        )

    def _forward(self, batch):
        enc = self.tokenizer(
            batch, padding=True, truncation=True, max_length=self.max_length, return_tensors="pt"
        ).to(self.device)
        logits = self.model(**enc).logits
        return self._F.softmax(logits.float(), dim=-1).cpu().numpy()
