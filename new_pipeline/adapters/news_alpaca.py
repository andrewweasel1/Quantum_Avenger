"""Live Alpaca news adapter (``NewsSource``).

Wraps alpaca-py's ``NewsClient`` behind the project's ABC, mapping Alpaca news
articles to the internal :class:`NewsItem` (timestamp + headline). Loaded lazily
by the adapter factory for a live ``run_mode``; requires egress to
``data.alpaca.markets``.
"""

from datetime import date, datetime, time

from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest

from new_pipeline.adapters.base import NewsItem, NewsSource


class AlpacaNewsSource(NewsSource):
    def __init__(self, api_key, secret_key, limit: int = 10, client=None):
        self._client = client or NewsClient(api_key, secret_key)
        self._limit = limit

    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        request = NewsRequest(
            symbols=symbol,
            start=datetime.combine(on, time.min),
            end=datetime.combine(on, time.max),
            limit=self._limit,
            sort="desc",
        )
        newsset = self._client.get_news(request)
        articles = newsset.data.get("news", []) if hasattr(newsset, "data") else list(newsset)
        return [
            NewsItem(timestamp=article.created_at, symbol=symbol, headline=article.headline)
            for article in articles
        ]
