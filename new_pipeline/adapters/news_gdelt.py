"""Live GDELT 2.0 DOC news adapter (``NewsSource``).

Free, keyless, point-in-time global news. Queried by company name using the
universe gazetteer aliases (``{ticker: [name, ...]}``) and mapped to the internal
:class:`NewsItem`. Uses only stdlib ``urllib`` (no new dependency). Egress-bound,
so it is coverage-omitted; an injected ``fetch`` callable lets the
JSON -> NewsItem mapping + query building be tested with no network.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import UTC, date, datetime

from new_pipeline.adapters.base import NewsItem, NewsSource

_DEFAULT_ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"


_USER_AGENT = "QuantumAvenger-research/1.0 (contact: repo operator)"


def _http_get_json(url: str, timeout: float = 15.0) -> dict:  # pragma: no cover - live egress
    # GDELT throttles anonymous default-UA clients hard; identify ourselves.
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout) as response:  # noqa: S310 - trusted
        body = response.read().decode("utf-8")
    try:
        return json.loads(body)
    except ValueError as exc:
        # GDELT reports query/rate errors as plain text with HTTP 200 — surface
        # the message instead of an opaque JSONDecodeError.
        raise ValueError(f"GDELT non-JSON reply: {body[:200]!r}") from exc


def _gdelt_stamp(day: date, end_of_day: bool) -> str:
    return day.strftime("%Y%m%d") + ("235959" if end_of_day else "000000")


def _parse_seendate(value: str) -> datetime | None:
    try:
        return datetime.strptime(value, "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    except (ValueError, TypeError):
        return None


class GdeltNewsSource(NewsSource):
    def __init__(
        self,
        aliases,
        endpoint: str = _DEFAULT_ENDPOINT,
        limit: int = 20,
        fetch=None,
        min_interval: float = 5.0,  # GDELT's informal per-IP tolerance is ~1 req/5s
        source_lang: str = "english",
        retry_attempts: int = 3,
        retry_backoff: float = 60.0,
    ):
        self._aliases = {ticker: list(names) for ticker, names in aliases.items()}
        self._endpoint = endpoint
        self._limit = limit
        self._fetch = fetch or _http_get_json
        # Politeness throttle for the free keyless API: space real HTTP calls by
        # min_interval seconds so an index-scale sweep (~500 queries) can't look
        # like abuse. Injected-fetch tests are unaffected (throttle wraps HTTP only).
        self._min_interval = min_interval if fetch is None else 0.0
        self._last_call = 0.0
        self._source_lang = source_lang
        self._retry_attempts = retry_attempts
        self._retry_backoff = retry_backoff

    def query_url(self, symbol: str, start: date, end: date) -> str:
        names = self._aliases.get(symbol) or [symbol]
        query = " OR ".join(f'"{name}"' for name in names)
        if len(names) > 1:
            # GDELT rejects bare OR'd terms: "Queries containing OR'd terms must
            # be surrounded by ()." (learned from the live API, not the docs).
            query = f"({query})"
        if self._source_lang:
            # GDELT is a global index; restrict to a language the sentiment
            # engine can actually score (mixed-language results dilute signal).
            query = f"{query} sourcelang:{self._source_lang}"
        params = {
            "query": query,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": str(self._limit),
            "startdatetime": _gdelt_stamp(start, end_of_day=False),
            "enddatetime": _gdelt_stamp(end, end_of_day=True),
        }
        return f"{self._endpoint}?{urllib.parse.urlencode(params)}"

    def _throttle(self) -> None:
        if self._min_interval <= 0.0:
            return
        wait = self._min_interval - (time.monotonic() - self._last_call)
        if wait > 0:  # pragma: no cover - timing-dependent
            time.sleep(wait)
        self._last_call = time.monotonic()

    def _fetch_with_retry(self, url: str, attempts: int = 0, backoff: float = 0.0) -> dict:
        """The free API 429s bursts; back off and retry instead of losing the symbol."""
        attempts = attempts or self._retry_attempts
        backoff = backoff or self._retry_backoff
        for attempt in range(attempts):
            self._throttle()
            try:
                return self._fetch(url)
            except Exception as exc:
                retryable = "429" in str(exc) or isinstance(exc, TimeoutError)
                if attempt == attempts - 1 or not retryable:
                    raise
                time.sleep(backoff * (attempt + 1))
        raise RuntimeError("unreachable")  # pragma: no cover

    def fetch(self, symbol, start, end, as_of=None) -> list[NewsItem]:
        payload = self._fetch_with_retry(self.query_url(symbol, start, end))
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
