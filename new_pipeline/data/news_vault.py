"""Point-in-time news vault: fetch news over a universe + date range and persist
it to Parquet, then replay it reproducibly via
:class:`new_pipeline.adapters.news_static.VaultNewsSource`.

Survivorship-safe: only tickers whose membership window overlaps ``[start, end]``
are fetched (via ``universe.members``), so a backtest never sees news for a name
that was not in the index. Persistence mirrors
``data/ingestion.py::DataIngestion.stage_dataframe`` (pandas -> Parquet).
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import pandas as pd

_NEWS_COLUMNS = ["timestamp", "ticker", "headline"]


def _active_symbols(universe, start: date, end: date) -> list[str]:
    """Tickers whose ``[start_date, end_date)`` membership overlaps ``[start, end]``."""
    symbols: list[str] = []
    for member in universe.members():
        if member.start_date <= end and (member.end_date is None or member.end_date >= start):
            symbols.append(member.ticker)
    return symbols


def ingest_news_vault(
    news_source,
    universe,
    start: date,
    end: date,
    out_path,
    as_of: datetime | None = None,
) -> dict:
    """Fetch PIT news for the active universe over ``[start, end]`` and write a
    Parquet vault (``timestamp, ticker, headline``). Returns a small summary."""
    symbols = _active_symbols(universe, start, end)
    records = [
        {"timestamp": item.timestamp, "ticker": item.symbol, "headline": item.headline}
        for symbol in symbols
        for item in news_source.fetch(symbol, start, end, as_of=as_of)
    ]
    frame = pd.DataFrame(records, columns=_NEWS_COLUMNS)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.to_parquet(out, index=False)
    return {
        "rows": int(frame.shape[0]),
        "symbols": len(symbols),
        "path": str(out),
        "start": start.isoformat(),
        "end": end.isoformat(),
    }


def load_news_vault(path) -> pd.DataFrame:
    return pd.read_parquet(path)
