"""Offline point-in-time fundamentals from a CSV fixture.

Implements :class:`FundamentalsSource` over
``data/fundamentals/snapshots.csv`` (``ticker, as_of, book_value_per_share,
earnings_per_share, return_on_equity``). A licensed point-in-time fundamentals
dataset replaces the fixture with no code change. Mirrors
:mod:`new_pipeline.adapters.universe_static`.
"""

import csv
from datetime import date
from pathlib import Path

from new_pipeline.adapters.base import FundamentalSnapshot, FundamentalsSource
from new_pipeline.core.paths import data_dir

DEFAULT_FUNDAMENTALS_PATH = data_dir() / "fundamentals" / "snapshots.csv"


class StaticFundamentalsSource(FundamentalsSource):
    def __init__(self, path: Path | str | None = None) -> None:
        self._path = Path(path) if path else DEFAULT_FUNDAMENTALS_PATH
        self._by_symbol = self._load()

    def _load(self) -> dict[str, list[FundamentalSnapshot]]:
        by_symbol: dict[str, list[FundamentalSnapshot]] = {}
        if not self._path.exists():
            return by_symbol
        with open(self._path, encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                by_symbol.setdefault(row["ticker"].strip(), []).append(
                    FundamentalSnapshot(
                        as_of=date.fromisoformat(row["as_of"].strip()),
                        book_value_per_share=float(row["book_value_per_share"]),
                        earnings_per_share=float(row["earnings_per_share"]),
                        return_on_equity=float(row["return_on_equity"]),
                    )
                )
        for snapshots in by_symbol.values():
            snapshots.sort(key=lambda snap: snap.as_of)
        return by_symbol

    def history(self, symbol: str, start: date, end: date) -> list[FundamentalSnapshot]:
        # Everything knowable by ``end`` (incl. the latest pre-``start`` snapshot, so a
        # point-in-time join has a value for the earliest dates).
        return [snap for snap in self._by_symbol.get(symbol, []) if snap.as_of <= end]
