"""Daily join of FINRA short-volume onto a per-(ticker, date) feature frame.

Unlike the quarterly fundamentals (a backward as-of join), short volume is a
DENSE DAILY panel, so this is a straight left-join on (ticker, date). Missing
cells — names/dates outside the CDN's rolling window, or thin names absent from
a day's file — stay null and are neutral-filled by the short-flow feature layer,
so coverage gaps never drop rows from the tournament.
"""

import polars as pl

SHORT_VOLUME_COLUMNS = ("short_volume", "total_volume")


def attach_short_volume(frame: pl.DataFrame, source) -> pl.DataFrame:
    """Left-join daily ``short_volume``/``total_volume`` onto (ticker, date).

    ``source`` exposes ``panel(start, end) -> DataFrame[date, ticker,
    short_volume, total_volume]``. Always returns both columns (null where no
    short-volume is known). The join key is normalized to Date (a Datetime
    ``date`` column — e.g. after the markov pandas round-trip — would otherwise
    break the key match, mirroring attach_fundamentals)."""
    if frame.schema["date"] != pl.Date:
        frame = frame.with_columns(pl.col("date").cast(pl.Date))
    start, end = frame["date"].min(), frame["date"].max()
    panel = source.panel(start, end) if source is not None else None
    if panel is None or panel.is_empty():
        return frame.with_columns(
            [pl.lit(None, dtype=pl.Int64).alias(column) for column in SHORT_VOLUME_COLUMNS]
        )
    panel = panel.with_columns(pl.col("date").cast(pl.Date)).select(
        "date", "ticker", *SHORT_VOLUME_COLUMNS
    )
    return frame.join(panel, on=["date", "ticker"], how="left")
