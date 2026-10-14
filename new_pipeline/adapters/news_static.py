"""Offline / vault-backed point-in-time news sources (deterministic).

``StaticNewsSource`` mirrors :class:`StaticUniverseProvider`: it loads a
checked-in ``data/news/headlines.csv`` fixture (columns ``timestamp, ticker,
headline``) once and serves :class:`NewsItem`s by ``(ticker, date)`` or date
range. Intraday timestamps + multi-headline days make the causal session
assignment / decay / dispersion meaningfully exercised offline (``FakeNewsSource``
emits one bland midnight headline/day). A missing fixture yields no news.

``VaultNewsSource`` serves the same interface from a materialized news vault
(Parquet written by :func:`new_pipeline.data.news_vault.ingest_news_vault`), so a
bounded one-time fetch can be replayed reproducibly with no network.
"""

from __future__ import annotations

import csv
from datetime import date, datetime
from pathlib import Path

from new_pipeline.adapters.base import NewsItem, NewsSource
from new_pipeline.core.paths import data_dir

DEFAULT_HEADLINES_PATH = data_dir() / "news" / "headlines.csv"


class _DictNewsSource(NewsSource):
    """Serves NewsItems from an in-memory ``{ticker: [NewsItem, ...]}`` map."""

    _by_symbol: dict[str, list[NewsItem]]

    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        return [it for it in self._by_symbol.get(symbol, ()) if it.timestamp.date() == on]

    def fetch(self, symbol, start, end, as_of=None) -> list[NewsItem]:
        out = [it for it in self._by_symbol.get(symbol, ()) if start <= it.timestamp.date() <= end]
        if as_of is not None:
            out = [it for it in out if it.timestamp <= as_of]
        return out


class StaticNewsSource(_DictNewsSource):
    def __init__(self, fixture_path: str | Path | None = None) -> None:
        self._path = Path(fixture_path) if fixture_path else DEFAULT_HEADLINES_PATH
        self._by_symbol = self._load()

    def _load(self) -> dict[str, list[NewsItem]]:
        items: dict[str, list[NewsItem]] = {}
        if not self._path.exists():
            return items
        with open(self._path, encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                ticker = row["ticker"].strip()
                headline = row["headline"].strip()
                if not ticker or not headline:
                    continue
                ts = datetime.fromisoformat(row["timestamp"].strip())
                items.setdefault(ticker, []).append(
                    NewsItem(timestamp=ts, symbol=ticker, headline=headline)
                )
        for series in items.values():
            series.sort(key=lambda it: it.timestamp)
        return items


class VaultNewsSource(_DictNewsSource):
    def __init__(self, parquet_path: str | Path) -> None:
        from new_pipeline.data.news_vault import load_news_vault

        items: dict[str, list[NewsItem]] = {}
        frame = load_news_vault(parquet_path)
        for ticker, ts, headline in zip(
            frame["ticker"], frame["timestamp"], frame["headline"], strict=True
        ):
            stamp = ts.to_pydatetime() if hasattr(ts, "to_pydatetime") else ts
            items.setdefault(str(ticker), []).append(
                NewsItem(timestamp=stamp, symbol=str(ticker), headline=str(headline))
            )
        for series in items.values():
            series.sort(key=lambda it: it.timestamp)
        self._by_symbol = items
