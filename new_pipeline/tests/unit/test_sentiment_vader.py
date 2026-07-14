"""VADER sentiment engine: financial-lexicon augmentation + score contract."""

from new_pipeline.adapters.sentiment_vader import VaderSentimentEngine


def test_financial_phrases_discriminate():
    engine = VaderSentimentEngine()
    bullish, bearish, neutral = engine.score_headlines([
        "Company beats earnings expectations, stock soars",
        "Analyst downgrade sends shares lower after guidance miss",
        "Quarterly results in line with estimates",
    ])
    assert bullish.signed > 0.5      # stock VADER scores this 0.0 — the augmentation matters
    assert bearish.signed < -0.5
    assert neutral.signed == 0.0


def test_score_contract():
    engine = VaderSentimentEngine()
    (score,) = engine.score_headlines(["Shares surge after record buyback"])
    assert -1.0 <= score.signed <= 1.0
    assert abs(score.p_pos + score.p_neg + score.p_neutral - 1.0) < 1e-6
    assert score.confidence == max(score.p_pos, score.p_neg, score.p_neutral)


def test_deterministic_and_extendable():
    base = VaderSentimentEngine()
    assert base.score_headlines(["stock soars"]) == base.score_headlines(["stock soars"])
    custom = VaderSentimentEngine(extra_lexicon={"quantumavenger": 3.5})
    (score,) = custom.score_headlines(["quantumavenger announced today"])
    assert score.signed > 0.5


def test_factory_selects_vader_backend(monkeypatch):
    from new_pipeline.adapters.factory import _build_fusion, _build_universe
    from new_pipeline.adapters.sentiment_vader import VaderSentimentEngine as V
    from new_pipeline.config import reload_config

    monkeypatch.setenv("QA_FUSION__ENABLED", "true")
    monkeypatch.setenv("QA_FUSION__SENTIMENT_BACKEND", "vader")
    cfg = reload_config()
    engine, anonymizer = _build_fusion(cfg, _build_universe(cfg))
    assert isinstance(engine, V)
    # spaCy isn't installed here -> the anonymizer degrades to the gazetteer.
    assert type(anonymizer).__name__ == "EntityAnonymizer"
