"""Live GDELT 2.0 DOC news adapter (``NewsSource``).

Free, keyless, point-in-time global news. Queried by company name using the
universe gazetteer aliases (``{ticker: [name, ...]}``) and mapped to the internal
:class:`NewsItem`. Uses only stdlib ``urllib`` (no new dependency). Egress-bound,
so it is coverage-omitted; an injected ``fetch`` callable lets the
JSON -> NewsItem mapping + query building be tested with no network.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request
from datetime import UTC, date, datetime

from new_pipeline.adapters.base import NewsItem, NewsSource

_DEFAULT_ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"


def _http_get_json(url: str, timeout: float = 15.0) -> dict:  # pragma: no cover - live egress
    with urllib.request.urlopen(url, timeout=timeout) as response:  # noqa: S310 - trusted endpoint
        return json.loads(response.read().decode("utf-8"))


def _gdelt_stamp(day: date, end_of_day: bool) -> str:
    return day.strftime("%Y%m%d") + ("235959" if end_of_day else "000000")


def _parse_seendate(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except (ValueError, TypeError):
        return None


class GdeltNewsSource(NewsSource):
    def __init__(self, aliases, endpoint: str = _DEFAULT_ENDPOINT, limit: int = 20, fetch=None):
        self._aliases = {ticker: list(names) for ticker, names in aliases.items()}
        self._endpoint = endpoint
        self._limit = limit
        self._fetch = fetch or _http_get_json

    def query_url(self, symbol: str, start: date, end: date) -> str:
        names = self._aliases.get(symbol) or [symbol]
        query = " OR ".join(f'"{name}"' for name in names)
        params = {
            "query": query,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": str(self._limit),
            "startdatetime": _gdelt_stamp(start, end_of_day=False),
            "enddatetime": _gdelt_stamp(end, end_of_day=True),
        }
        return f"{self._endpoint}?{urllib.parse.urlencode(params)}"

    def fetch(self, symbol, start, end, as_of=None) -> list[NewsItem]:
        payload = self._fetch(self.query_url(symbol, start, end))
        items: list[NewsItem] = []
        for article in payload.get("articles", []):
            timestamp = _parse_seendate(article.get("seendate", ""))
            title = (article.get("title") or "").strip()
            if timestamp is None or not title:
                continue
            if as_of is not None and timestamp > as_of:
                continue
            items.append(NewsItem(timestamp=timestamp, symbol=symbol, headline=title))
        return items

    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        return self.fetch(symbol, on, on)
