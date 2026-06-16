import pandas as pd
from new_pipeline.adapters.fakes import FakeSentimentEngine
from new_pipeline.data.sentiment_feature_builder import (
    SentimentFeatureBuilder,
    SentimentStageConfig,
)
from new_pipeline.execution.entity_anonymizer import EntityAnonymizer

_COLUMNS = ["date", "ticker", "sentiment", "sent_confidence", "news_count", "sentiment_dispersion"]


def _builder(**cfg):
    return SentimentFeatureBuilder(
        anonymizer=EntityAnonymizer(),
        engine=FakeSentimentEngine(),
        config=SentimentStageConfig(**cfg),
    )


def test_empty_news_returns_typed_empty_frame():
    out = _builder().build_daily_sentiment(pd.DataFrame())
    assert list(out.columns) == _COLUMNS
    assert out.empty


def test_causal_session_assignment_preclose_postclose_weekend():
    # ET = UTC-5 in January. Fri 2021-01-08.
    news = pd.DataFrame(
        {
            "timestamp": [
                "2021-01-08T19:00:00Z",  # 14:00 ET Fri, pre-close  -> Fri 01-08
                "2021-01-09T02:00:00Z",  # 21:00 ET Fri, post-close -> Mon 01-11
                "2021-01-09T17:00:00Z",  # 12:00 ET Sat            -> Mon 01-11
            ],
            "text": ["AAPL up", "AAPL down", "AAPL flat"],
            "ticker": ["AAPL", "AAPL", "AAPL"],
        }
    )
    out = _builder().build_daily_sentiment(news).sort_values("date")
    dates = [d.date().isoformat() for d in pd.to_datetime(out["date"])]
    counts = dict(zip(dates, out["news_count"], strict=True))
    assert dates == ["2021-01-08", "2021-01-11"]
    assert counts == {"2021-01-08": 1, "2021-01-11": 2}


def test_multi_ticker_article_fans_out_with_one_document_score():
    news = pd.DataFrame(
        {
            "timestamp": ["2021-01-08T14:00:00Z"],
            "text": ["AAPL and MSFT rally"],
            "tickers": [["AAPL", "MSFT"]],
        }
    )
    out = _builder().build_daily_sentiment(news)
    assert set(out["ticker"]) == {"AAPL", "MSFT"}
    assert out["sentiment"].nunique() == 1  # same doc score fans out to both


def test_decayed_join_decays_toward_neutral_with_staleness():
    daily = pd.DataFrame(
        {
            "date": ["2021-01-04"], "ticker": ["AAPL"], "sentiment": [0.8],
            "sent_confidence": [1.0], "news_count": [1], "sentiment_dispersion": [0.0],
        }
    )
    bars = pd.DataFrame(
        {"date": pd.date_range("2021-01-04", periods=4, freq="D"), "ticker": "AAPL"}
    )
    out = _builder(halflife_days=1.0).attach_to_bars(bars, daily).sort_values("date")
    sent = out["sentiment"].tolist()
    assert sent[0] == 0.8
    assert abs(sent[1] - 0.4) < 1e-9  # 1 day stale, half-life 1
    assert abs(sent[2] - 0.2) < 1e-9  # 2 days stale
    assert out["sentiment_staleness"].tolist() == [0.0, 1.0, 2.0, 3.0]


def test_no_sentiment_leaks_onto_bars_before_first_news():
    daily = pd.DataFrame(
        {
            "date": ["2021-01-06"], "ticker": ["AAPL"], "sentiment": [0.9],
            "sent_confidence": [1.0], "news_count": [1], "sentiment_dispersion": [0.0],
        }
    )
    bars = pd.DataFrame(
        {"date": pd.date_range("2021-01-04", periods=4, freq="D"), "ticker": "AAPL"}
    )
    out = _builder().attach_to_bars(bars, daily).sort_values("date").reset_index(drop=True)
    assert out.loc[0, "sentiment"] == 0.0  # 01-04, before the news day -> neutral
    assert out.loc[1, "sentiment"] == 0.0  # 01-05, before the news day -> neutral
    assert out.loc[2, "sentiment"] == 0.9  # 01-06 news day
