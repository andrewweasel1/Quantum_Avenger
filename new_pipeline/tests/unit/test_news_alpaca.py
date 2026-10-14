"""AlpacaNewsSource: month-windowed range fetch + pagination + as_of (fake client)."""

from datetime import UTC, date, datetime

import pytest

pytest.importorskip("alpaca")

from new_pipeline.adapters.news_alpaca import AlpacaNewsSource, _month_starts  # noqa: E402


class _Article:
    def __init__(self, created_at, headline):
        self.created_at = created_at
        self.headline = headline


class _NewsSet:
    def __init__(self, articles, next_page_token=None):
        self.data = {"news": articles}
        self.next_page_token = next_page_token


class _MonthlyClient:
    """One article per request, dated at the request's start; no pagination
    (mirrors Alpaca's free-tier 50-cap-no-token behavior)."""

    def __init__(self):
        self.calls = []

    def get_news(self, request):
        self.calls.append((request.start.date(), request.end.date()))
        # Real Alpaca articles carry tz-aware timestamps.
        stamp = request.start.replace(tzinfo=UTC)
        return _NewsSet([_Article(stamp, f"news {request.start:%Y-%m}")])


def test_month_starts_spans_range():
    months = _month_starts(date(2024, 1, 15), date(2024, 4, 2))
    assert months == [date(2024, 1, 1), date(2024, 2, 1), date(2024, 3, 1), date(2024, 4, 1)]


def test_fetch_windows_by_month():
    client = _MonthlyClient()
    source = AlpacaNewsSource("k", "s", client=client)
    items = source.fetch("AAPL", date(2024, 1, 1), date(2024, 3, 31))
    # one call per calendar month -> three distinct monthly headlines
    assert len(client.calls) == 3
    assert [i.headline for i in items] == ["news 2024-01", "news 2024-02", "news 2024-03"]


def test_pagination_within_a_window():
    class _PagingClient:
        def __init__(self):
            self.tokens = []

        def get_news(self, request):
            self.tokens.append(request.page_token)
            if request.page_token is None:
                return _NewsSet([_Article(datetime(2024, 1, 2, tzinfo=UTC), "p1")], "tok")
            return _NewsSet([_Article(datetime(2024, 1, 20, tzinfo=UTC), "p2")])

    client = _PagingClient()
    items = AlpacaNewsSource("k", "s", client=client).fetch(
        "AAPL", date(2024, 1, 1), date(2024, 1, 31)
    )
    assert [i.headline for i in items] == ["p1", "p2"]
    assert client.tokens == [None, "tok"]  # followed the token inside the window


def test_as_of_cutoff():
    client = _MonthlyClient()
    source = AlpacaNewsSource("k", "s", client=client)
    items = source.fetch("AAPL", date(2024, 1, 1), date(2024, 3, 31),
                         as_of=datetime(2024, 2, 15, tzinfo=UTC))
    assert [i.headline for i in items] == ["news 2024-01", "news 2024-02"]  # March dropped
