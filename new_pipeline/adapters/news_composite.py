"""Merge several news sources behind one ``NewsSource`` (e.g. GDELT headlines +
EDGAR filings). Pure composition — concatenates results, no network — so it is
fully offline-testable with fakes."""

from __future__ import annotations

from datetime import date, datetime

from new_pipeline.adapters.base import NewsItem, NewsSource


class CompositeNewsSource(NewsSource):
    def __init__(self, sources) -> None:
        self._sources = list(sources)

    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        items: list[NewsItem] = []
        for source in self._sources:
            items.extend(source.headlines(symbol, on))
        return items

    def fetch(self, symbol, start, end, as_of: datetime | None = None) -> list[NewsItem]:
        items: list[NewsItem] = []
        for source in self._sources:
            items.extend(source.fetch(symbol, start, end, as_of=as_of))
        return items
