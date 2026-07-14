"""GDELT adapter (egress-bound, coverage-omitted). The JSON -> NewsItem mapping
and query building are validated with an injected ``fetch`` (no network)."""

from datetime import UTC, date, datetime

from new_pipeline.adapters.news_gdelt import GdeltNewsSource


def _fake_payload(_url):
    return {
        "articles": [
            {"seendate": "20210108T143000Z", "title": "Apple rallies on earnings"},
            {"seendate": "not-a-date", "title": "dropped: bad timestamp"},
            {"seendate": "20210108T160000Z", "title": ""},
        ]
    }


def test_maps_articles_and_drops_malformed():
    src = GdeltNewsSource({"AAPL": ["Apple", "Apple Inc"]}, fetch=_fake_payload)
    items = src.fetch("AAPL", date(2021, 1, 8), date(2021, 1, 8))
    assert len(items) == 1  # bad seendate + empty title are dropped
    assert items[0].symbol == "AAPL"
    assert items[0].headline == "Apple rallies on earnings"
    assert items[0].timestamp == datetime(2021, 1, 8, 14, 30, tzinfo=UTC)


def test_query_url_uses_gazetteer_aliases_and_dates():
    src = GdeltNewsSource({"AAPL": ["Apple", "Apple Inc"]}, fetch=_fake_payload)
    url = src.query_url("AAPL", date(2021, 1, 1), date(2021, 1, 31))
    assert "Apple" in url and "Apple+Inc" in url
    assert "%28%22Apple%22" in url  # OR'd terms must be parenthesized (live API rule)
    single = src.query_url("ZZZ", date(2021, 1, 1), date(2021, 1, 2))
    assert "%28" not in single  # single-term queries stay bare
    assert "20210101000000" in url and "20210131235959" in url


def test_attach_sentiment_uses_one_range_fetch_per_symbol():
    """Regression: the per-(symbol, day) loop would be ~500k HTTP calls at index
    scale; sentiment attachment must issue exactly one range fetch per symbol."""
    from datetime import date

    from new_pipeline.adapters.fakes import FakeNewsSource, FakeSentimentEngine
    from new_pipeline.config import reload_config
    from new_pipeline.execution.entity_anonymizer import EntityAnonymizer
    from new_pipeline.tournament.pipeline import build_training_frame

    calls = []

    class _CountingNews(FakeNewsSource):
        def fetch(self, symbol, start, end, as_of=None):
            calls.append((symbol, start, end))
            return super().fetch(symbol, start, end, as_of)

    cfg = reload_config()
    frame = build_training_frame(
        ["AAPL", "MSFT"], {"AAPL": "Information Technology", "MSFT": "Information Technology"},
        date(2021, 1, 1), date(2021, 3, 31), None, cfg,
        news_source=_CountingNews(), sentiment_engine=FakeSentimentEngine(),
        anonymizer=EntityAnonymizer(),
    )
    assert [c[0] for c in calls] == ["AAPL", "MSFT"]  # one range call each, whole window
    assert calls[0][1] == date(2021, 1, 1) and calls[0][2] == date(2021, 3, 31)
    assert "sentiment_score" in frame.columns


def test_fetch_retries_through_a_429(monkeypatch):
    from datetime import date

    from new_pipeline.adapters.news_gdelt import GdeltNewsSource

    monkeypatch.setattr("new_pipeline.adapters.news_gdelt.time.sleep", lambda s: None)
    attempts = []

    def flaky_fetch(url):
        attempts.append(url)
        if len(attempts) == 1:
            raise RuntimeError("HTTP Error 429: Too Many Requests")
        return {"articles": [{"seendate": "20240102T120000Z", "title": "Recovered headline"}]}

    source = GdeltNewsSource({"AAPL": ["Apple"]}, fetch=flaky_fetch)
    items = source.fetch("AAPL", date(2024, 1, 1), date(2024, 1, 31))
    assert len(attempts) == 2  # one 429, one success
    assert items[0].headline == "Recovered headline"


def test_fetch_does_not_retry_non_retryable(monkeypatch):
    from datetime import date

    import pytest as _pytest
    from new_pipeline.adapters.news_gdelt import GdeltNewsSource

    calls = []

    def broken_fetch(url):
        calls.append(url)
        raise ValueError("bad json")

    source = GdeltNewsSource({}, fetch=broken_fetch)
    with _pytest.raises(ValueError):
        source.fetch("AAPL", date(2024, 1, 1), date(2024, 1, 2))
    assert len(calls) == 1
