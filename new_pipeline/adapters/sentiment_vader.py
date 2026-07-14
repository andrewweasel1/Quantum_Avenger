"""Lexicon-based sentiment engine (VADER + a financial-term augmentation).

A lightweight, fully deterministic ``SentimentEngine`` for hosts that cannot
run FinBERT (no torch / no HuggingFace egress). VADER's general lexicon is
famously blind to market phrasing ("beats", "soars", "downgrade" all score
neutral), so a compact Loughran-McDonald-style financial lexicon is merged in —
curated unigrams with VADER-scale valences in [-4, 4]. Pure Python, ~130KB dep,
installed with the base requirements and fully unit-tested offline.

Select with ``fusion.sentiment_backend: "vader"`` (default stays ``finbert``).
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from new_pipeline.adapters.base import SentimentEngine, SentimentScore

# Financial unigrams VADER's general lexicon misses or underweights.
FINANCIAL_LEXICON: dict[str, float] = {
    # bullish
    "beat": 2.0, "beats": 2.2, "tops": 1.8, "exceeds": 1.8, "outperform": 2.0,
    "soar": 3.0, "soars": 3.0, "soared": 3.0, "surge": 2.8, "surges": 2.8,
    "surged": 2.8, "rally": 2.4, "rallies": 2.4, "rallied": 2.4,
    "upgrade": 2.3, "upgraded": 2.3, "bullish": 2.5, "breakout": 1.8,
    "buyback": 1.5, "profitable": 1.8, "momentum": 1.2, "dividend": 1.0,
    # bearish
    "miss": -1.8, "misses": -1.8, "missed": -1.8, "shortfall": -2.0,
    "plunge": -2.9, "plunges": -2.9, "plunged": -2.9, "tumble": -2.5,
    "tumbles": -2.5, "tumbled": -2.5, "slump": -2.3, "slumps": -2.3,
    "sinks": -2.2, "selloff": -2.4, "downgrade": -2.3, "downgraded": -2.3,
    "bearish": -2.5, "underperform": -2.0, "layoffs": -2.0, "recall": -1.7,
    "probe": -1.4, "investigation": -1.5, "lawsuit": -1.8, "writedown": -2.2,
    "impairment": -2.0, "delisting": -2.5, "insolvency": -3.0,
}


class VaderSentimentEngine(SentimentEngine):
    """Deterministic sensor: VADER ``compound`` as the signed scalar plus the
    pos/neg/neu mass as the class distribution. ``signed`` is VADER's normalized
    compound score (not literally p_pos - p_neg, but the same [-1, 1] semantic
    the fusion/decay consumers expect)."""

    def __init__(self, extra_lexicon: dict[str, float] | None = None):
        self._analyzer = SentimentIntensityAnalyzer()
        self._analyzer.lexicon.update(FINANCIAL_LEXICON)
        if extra_lexicon:
            self._analyzer.lexicon.update(extra_lexicon)

    def score_headlines(self, texts, batch_size: int = 64) -> list[SentimentScore]:
        scores: list[SentimentScore] = []
        for text in texts:
            polarity = self._analyzer.polarity_scores(str(text))
            scores.append(
                SentimentScore(
                    signed=float(polarity["compound"]),
                    confidence=float(max(polarity["pos"], polarity["neg"], polarity["neu"])),
                    p_pos=float(polarity["pos"]),
                    p_neg=float(polarity["neg"]),
                    p_neutral=float(polarity["neu"]),
                )
            )
        return scores
