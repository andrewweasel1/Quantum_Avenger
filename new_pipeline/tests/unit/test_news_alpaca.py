"""AlpacaNewsSource: paginated range fetch + as_of cutoff (fake client, no egress)."""

from datetime import UTC, date, datetime

import pytest

pytest.importorskip("alpaca")

from new_pipeline.adapters.news_alpaca import AlpacaNewsSource  # noqa: E402


class _Article:
    def __init__(self, created_at, headline):
        self.created_at = created_at
        self.headline = headline


class _NewsSet:
    def __init__(self, articles, next_page_token=None):
        self.data = {"news": articles}
        self.next_page_token = next_page_token


class _PaginatingClient:
    """Serves two pages then stops; records each requested page_token."""

    def __init__(self):
        self.tokens_seen = []

    def get_news(self, request):
        self.tokens_seen.append(request.page_token)
        if request.page_token is None:
            return _NewsSet(
                [_Article(datetime(2024, 1, 2, tzinfo=UTC), "Page one headline")],
                next_page_token="tok2",
            )
        return _NewsSet([_Article(datetime(2024, 1, 9, tzinfo=UTC), "Page two headline")])


def test_range_fetch_paginates():
    client = _PaginatingClient()
    source = AlpacaNewsSource("k", "s", client=client)
    items = source.fetch("AAPL", date(2024, 1, 1), date(2024, 1, 31))
    assert [i.headline for i in items] == ["Page one headline", "Page two headline"]
    assert client.tokens_seen == [None, "tok2"]  # followed the next_page_token


def test_as_of_cutoff_drops_future_articles():
    client = _PaginatingClient()
    source = AlpacaNewsSource("k", "s", client=client)
    items = source.fetch("AAPL", date(2024, 1, 1), date(2024, 1, 31),
                         as_of=datetime(2024, 1, 5, tzinfo=UTC))
    assert [i.headline for i in items] == ["Page one headline"]  # Jan 9 dropped


def test_max_articles_caps_pagination():
    client = _PaginatingClient()
    source = AlpacaNewsSource("k", "s", max_articles=1, client=client)
    items = source.fetch("AAPL", date(2024, 1, 1), date(2024, 1, 31))
    assert len(items) == 1  # stopped after page one hit the cap
    assert client.tokens_seen == [None]
