from datetime import date, datetime

from new_pipeline.adapters.base import NewsItem, NewsSource
from new_pipeline.adapters.news_composite import CompositeNewsSource


class _TaggedNews(NewsSource):
    def __init__(self, tag: str) -> None:
        self._tag = tag

    def headlines(self, symbol, on):
        return [
            NewsItem(
                timestamp=datetime(on.year, on.month, on.day),
                symbol=symbol,
                headline=f"{self._tag}:{symbol}",
            )
        ]


def test_composite_merges_headlines():
    items = CompositeNewsSource([_TaggedNews("a"), _TaggedNews("b")]).headlines(
        "AAPL", date(2021, 1, 8)
    )
    assert {it.headline for it in items} == {"a:AAPL", "b:AAPL"}


def test_composite_merges_fetch_ranges():
    items = CompositeNewsSource([_TaggedNews("a"), _TaggedNews("b")]).fetch(
        "AAPL", date(2021, 1, 4), date(2021, 1, 5)
    )
    assert len(items) == 4  # 2 sources x 2 days
