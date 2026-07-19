"""Offline FINRA short-volume from the ingested vault CSV.

Loads ``sp500_short_volume.csv`` (``date,ticker,short_volume,total_volume``,
produced by ``scripts.ingest_short_volume_vault``) once and serves date-windowed
panels to :func:`new_pipeline.data.short_volume.attach_short_volume`.
"""

from datetime import date
from pathlib import Path

import polars as pl


class StaticShortVolumeSource:
    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._panel = self._load()

    def _load(self) -> pl.DataFrame:
        schema = {
            "date": pl.Date, "ticker": pl.Utf8,
            "short_volume": pl.Int64, "total_volume": pl.Int64,
        }
        if not self._path.exists():
            return pl.DataFrame(schema=schema)
        return pl.read_csv(self._path, schema_overrides={
            "short_volume": pl.Int64, "total_volume": pl.Int64,
        }).with_columns(pl.col("date").cast(pl.Date))

    def panel(self, start: date, end: date) -> pl.DataFrame:
        if self._panel.is_empty():
            return self._panel
        return self._panel.filter(
            (pl.col("date") >= start) & (pl.col("date") <= end)
        )
