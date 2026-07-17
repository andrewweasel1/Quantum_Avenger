"""Point-in-time join of fundamentals onto a per-(ticker, date) feature frame.

A backward as-of join attaches, for each (ticker, date) row, the most recent
fundamental snapshot whose filing date (``as_of``) is on or before that date —
strictly causal, no look-ahead. Feeds the value/quality cross-sectional factors.
"""

import warnings

import polars as pl

FUNDAMENTAL_COLUMNS = ("book_value_per_share", "earnings_per_share", "return_on_equity")


def attach_fundamentals(frame: pl.DataFrame, source, keep_as_of: bool = False) -> pl.DataFrame:
    """Join the latest-known fundamentals as-of each (ticker, date) row.

    Requires ``ticker`` and ``date`` columns. Always returns the three fundamental
    columns (null where no snapshot is yet knowable, so downstream factors drop
    those rows rather than raising). ``keep_as_of`` retains the joined filing
    date column for the event-time features (default drop keeps the frame
    schema bit-stable for existing consumers)."""
    symbols = frame["ticker"].unique().to_list()
    start, end = frame["date"].min(), frame["date"].max()
    rows = [
        {
            "ticker": symbol, "as_of": snap.as_of,
            "book_value_per_share": snap.book_value_per_share,
            "earnings_per_share": snap.earnings_per_share,
            "return_on_equity": snap.return_on_equity,
        }
        for symbol in symbols
        for snap in source.history(symbol, start, end)
    ]
    if not rows:
        out = frame.with_columns(
            [pl.lit(None, dtype=pl.Float64).alias(column) for column in FUNDAMENTAL_COLUMNS]
        )
        if keep_as_of:
            out = out.with_columns(pl.lit(None, dtype=pl.Date).alias("as_of"))
        return out
    fundamentals = (
        pl.DataFrame(rows).with_columns(pl.col("as_of").cast(pl.Date)).sort(["ticker", "as_of"])
    )
    with warnings.catch_warnings():  # both frames are sorted; polars can't verify with `by`
        warnings.filterwarnings("ignore", message="Sortedness of columns")
        joined = frame.sort(["ticker", "date"]).join_asof(
            fundamentals, left_on="date", right_on="as_of", by="ticker", strategy="backward"
        )
    return joined if keep_as_of else joined.drop("as_of")
