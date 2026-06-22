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
    assert "20210101000000" in url and "20210131235959" in url
