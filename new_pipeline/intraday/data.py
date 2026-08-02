"""Minute-vault readers: partitioned parquet tree -> tidy polars frames.

The vault stores RAW feed bars per (symbol, month) — including pre/post-market
minutes, because Alpaca minute bars carry extended hours and a future scanner
may want the pre-market tape. Session discipline is applied at READ time via
the exchange-calendar fixture: `filter_to_sessions` keeps only bars whose
open-timestamp falls inside [session open, session close).
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import polars as pl

from new_pipeline.intraday.calendar import Session

MINUTE_COLUMNS = ("ts", "open", "high", "low", "close", "volume", "vwap")


def vault_file(vault_dir: Path, symbol: str, year: int, month: int) -> Path:
    safe = symbol.replace("/", "_").replace(".", "_")
    return Path(vault_dir) / "by_symbol_month" / f"{safe}_{year:04d}{month:02d}.parquet"


def months_between(start: date, end: date) -> list[tuple[int, int]]:
    """Inclusive (year, month) range."""
    out, y, m = [], start.year, start.month
    while (y, m) <= (end.year, end.month):
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def load_minutes(vault_dir: Path, symbols: list[str], start: datetime,
                 end: datetime) -> pl.DataFrame:
    """Long frame (ticker, ts, o/h/l/c/volume/vwap) for [start, end], sorted.
    Missing files are simply absent rows — a symbol not yet listed in a month
    is not an error."""
    frames = []
    for symbol in symbols:
        for year, month in months_between(start.date(), end.date()):
            path = vault_file(vault_dir, symbol, year, month)
            if not path.exists():
                continue
            frame = pl.read_parquet(path)
            if frame.is_empty():
                continue
            frames.append(frame.with_columns(pl.lit(symbol).alias("ticker")))
    if not frames:
        dtypes = {c: (pl.Datetime("us", "UTC") if c == "ts"
                      else pl.Int64 if c == "volume" else pl.Float64)
                  for c in MINUTE_COLUMNS}
        return pl.DataFrame(schema={"ticker": pl.Utf8, **dtypes})
    out = pl.concat(frames)
    return (out.filter((pl.col("ts") >= start) & (pl.col("ts") < end))
            .sort(["ticker", "ts"]))


def session_daily(regular: pl.DataFrame) -> pl.DataFrame:
    """Daily OHLCV aggregated from SESSION-FILTERED minute bars — the single
    price source for liquidity floors and the scanner, so the intraday stack
    never mixes two feeds' views of the same day. Requires the
    ``session_date`` column that `filter_to_sessions` attaches."""
    if regular.is_empty():
        return pl.DataFrame(schema={"date": pl.Date, "ticker": pl.Utf8,
                                    "open": pl.Float64, "high": pl.Float64,
                                    "low": pl.Float64, "close": pl.Float64,
                                    "volume": pl.Int64, "dollar_vol": pl.Float64})
    return (regular.sort(["ticker", "ts"])
            .group_by(["ticker", "session_date"], maintain_order=True)
            .agg(pl.col("open").first(),
                 pl.col("high").max(),
                 pl.col("low").min(),
                 pl.col("close").last(),
                 pl.col("volume").sum(),
                 (pl.col("close") * pl.col("volume")).sum().alias("dollar_vol"))
            .rename({"session_date": "date"})
            .sort(["ticker", "date"]))


def filter_to_sessions(frame: pl.DataFrame, sessions: dict[date, Session]) -> pl.DataFrame:
    """Keep regular-hours bars only: session open <= ts < session close, per the
    exchange calendar (early closes included). Bars on non-session days drop."""
    if frame.is_empty():
        return frame
    bounds = pl.DataFrame({
        "session_date": list(sessions),
        "_open": [s.open_utc for s in sessions.values()],
        "_close": [s.close_utc for s in sessions.values()],
    }).with_columns(pl.col("session_date").cast(pl.Date),
                    pl.col("_open").dt.convert_time_zone("UTC"),
                    pl.col("_close").dt.convert_time_zone("UTC"))
    out = (frame.with_columns(
        pl.col("ts").dt.convert_time_zone("UTC").dt.date().alias("session_date"))
        .join(bounds, on="session_date", how="inner")
        .filter((pl.col("ts") >= pl.col("_open")) & (pl.col("ts") < pl.col("_close")))
        .drop(["_open", "_close"]))
    return out
