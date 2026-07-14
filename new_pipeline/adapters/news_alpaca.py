"""Live Alpaca news adapter (``NewsSource``).

Wraps alpaca-py's ``NewsClient`` behind the project's ABC, mapping Alpaca news
articles to the internal :class:`NewsItem` (timestamp + headline). Loaded lazily
by the adapter factory for a live ``run_mode``; requires egress to
``data.alpaca.markets``. Authenticated with the Alpaca keys, so — unlike the
free GDELT tier — it is not per-IP rate-limited, which makes it the practical
news source for an index-scale vault ingest.
"""

from datetime import date, datetime, time

from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest

from new_pipeline.adapters.base import NewsItem, NewsSource


def _articles(newsset) -> list:
    return newsset.data.get("news", []) if hasattr(newsset, "data") else list(newsset)


class AlpacaNewsSource(NewsSource):
    def __init__(self, api_key, secret_key, limit: int = 50, max_articles: int = 1000, client=None):
        # limit is the per-page size (Alpaca caps at 50); max_articles bounds a
        # single symbol's range fetch so a very newsy name can't run away.
        self._client = client or NewsClient(api_key, secret_key)
        self._limit = min(limit, 50)
        self._max_articles = max_articles

    def fetch(self, symbol, start: date, end: date, as_of=None) -> list[NewsItem]:
        """One paginated range request per symbol (not the per-day base loop)."""
        collected: list[NewsItem] = []
        page_token = None
        while True:
            request = NewsRequest(
                symbols=symbol,
                start=datetime.combine(start, time.min),
                end=datetime.combine(end, time.max),
                limit=self._limit,
                sort="asc",
                page_token=page_token,
            )
            newsset = self._client.get_news(request)
            for article in _articles(newsset):
                if as_of is not None and article.created_at > as_of:
                    continue
                collected.append(
                    NewsItem(timestamp=article.created_at, symbol=symbol, headline=article.headline)
                )
            page_token = getattr(newsset, "next_page_token", None)
            if not page_token or len(collected) >= self._max_articles:
                break
        return collected

    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        return self.fetch(symbol, on, on)
