from new_pipeline.adapters.base import SentimentEngine, SentimentScore
from new_pipeline.adapters.fakes import FakeSentimentEngine


def test_one_score_per_text():
    scores = FakeSentimentEngine().score_headlines(["a", "b", "c"])
    assert len(scores) == 3
    assert all(isinstance(s, SentimentScore) for s in scores)


def test_signed_equals_p_pos_minus_p_neg_and_probs_sum_to_one():
    for s in FakeSentimentEngine().score_headlines(["Apple soars", "Banks crash", "flat text"]):
        assert s.signed == s.p_pos - s.p_neg
        assert abs(s.p_pos + s.p_neg + s.p_neutral - 1.0) < 1e-12
        assert -1.0 <= s.signed <= 1.0
        assert 0.0 <= s.confidence <= 1.0


def test_deterministic():
    eng = FakeSentimentEngine()
    assert eng.score_headlines(["same text"])[0] == eng.score_headlines(["same text"])[0]


def test_implements_the_abc():
    assert isinstance(FakeSentimentEngine(), SentimentEngine)
