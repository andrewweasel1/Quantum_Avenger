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


def _month_starts(start: date, end: date) -> list[date]:
    """First-of-month dates spanning [start, end] (the windowing boundaries)."""
    months, y, m = [], start.year, start.month
    while (y, m) <= (end.year, end.month):
        months.append(date(y, m, 1))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return months


class AlpacaNewsSource(NewsSource):
    """Alpaca's free/paper news tier caps a range request at ~50 articles with no
    pagination, so a multi-year range would return only 50 headlines. ``fetch``
    therefore windows the range into calendar months (each capturing its own 50),
    which yields dense per-day coverage; ``next_page_token`` is still followed
    within a window for tiers that do paginate."""

    def __init__(self, api_key, secret_key, limit: int = 50, per_window: int = 200, client=None):
        self._client = client or NewsClient(api_key, secret_key)
        self._limit = min(limit, 50)
        self._per_window = per_window  # cap per monthly window (paginating tiers)

    def _fetch_window(self, symbol, start: date, end: date, as_of) -> list[NewsItem]:
        items: list[NewsItem] = []
        page_token = None
        while True:
            newsset = self._client.get_news(NewsRequest(
                symbols=symbol, start=datetime.combine(start, time.min),
                end=datetime.combine(end, time.max), limit=self._limit,
                sort="asc", page_token=page_token,
            ))
            for article in _articles(newsset):
                if as_of is None or article.created_at <= as_of:
                    items.append(NewsItem(article.created_at, symbol, article.headline))
            page_token = getattr(newsset, "next_page_token", None)
            if not page_token or len(items) >= self._per_window:
                return items

    def fetch(self, symbol, start: date, end: date, as_of=None) -> list[NewsItem]:
        months = _month_starts(start, end)
        collected: list[NewsItem] = []
        seen: set = set()
        for i, month_start in enumerate(months):
            window_end = months[i + 1] if i + 1 < len(months) else end
            for item in self._fetch_window(symbol, month_start, window_end, as_of):
                key = (item.timestamp, item.headline)
                if key not in seen:  # month windows can overlap on the boundary day
                    seen.add(key)
                    collected.append(item)
        return collected

    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        return self._fetch_window(symbol, on, on, None)
