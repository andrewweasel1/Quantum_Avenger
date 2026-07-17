"""Event-time signal family: filing clock + news-flow burst (causal).

Fourth new family from the regime-fragility diagnosis. Unlike the OHLCV
families these depend on joined data sources, so they are computed inside
``build_training_frame`` right after the join they consume (fundamentals
as-of join; daily news table) — never in the per-ticker extended-family
loop. Opt-in via ``features.event_features``; each subset materializes only
when its source is active (fundamental factors / fusion news) and the
pipeline registers exactly the materialized names.

days_since_filing: calendar days since the most recent knowable filing
(the PIT ``as_of``), saturating at 365 — the position on the
post-announcement clock. Tickers with no knowable filing sit AT the
saturation value rather than nulling out: the tournament's drop_nulls
would otherwise silently delete every uncovered name, reintroducing the
survivorship the PIT universe removed.
ret_since_filing: compounded close-to-close return from the filing date to
today — the drift-so-far along that clock (PEAD-style state); 0.0 when no
filing is knowable.
news_burst_21: today's headline count vs its own trailing 21d distribution
(z-score; 0.0 in warmup/degenerate windows) — coverage volume, not
polarity; bursts mark event days the filing calendar cannot see.
"""

import warnings

import polars as pl

FILING_EVENT_COLS = ["days_since_filing", "ret_since_filing"]
NEWS_EVENT_COLS = ["news_burst_21"]

# One saturation constant for "stale filing" and "no filing knowable": past a
# year the filing clock carries no post-announcement information either way.
FILING_CLOCK_CAP_DAYS = 365.0


def add_filing_event_features(frame: pl.DataFrame) -> pl.DataFrame:
    """Consume the kept ``as_of`` column -> filing-clock features; drops it.

    The drift anchor is the close of the last trading day on or before the
    filing date (weekend/holiday filings roll back), matching the as-of join
    convention that a filing is usable from its ``filed`` date's close.
    """
    out = frame.sort(["ticker", "date"]).with_columns(
        (pl.col("date") - pl.col("as_of")).dt.total_days().cast(pl.Float64)
        .clip(upper_bound=FILING_CLOCK_CAP_DAYS).alias("days_since_filing"),
        pl.col("returns").fill_null(0.0).log1p().cum_sum().over("ticker").alias("_cumlog"),
    )
    anchors = out.select(
        pl.col("ticker"),
        pl.col("date").alias("as_of"),
        pl.col("_cumlog").alias("_cumlog_filing"),
    )
    with warnings.catch_warnings():  # both sorted within ticker; polars can't verify with `by`
        warnings.filterwarnings("ignore", message="Sortedness of columns")
        out = out.join_asof(
            anchors, left_on="as_of", right_on="as_of", by="ticker", strategy="backward"
        )
    return out.with_columns(
        pl.col("days_since_filing").fill_null(FILING_CLOCK_CAP_DAYS),
        ((pl.col("_cumlog") - pl.col("_cumlog_filing")).exp() - 1.0)
        .fill_null(0.0).alias("ret_since_filing"),
    ).drop("as_of", "_cumlog", "_cumlog_filing")


def add_news_burst(frame: pl.DataFrame) -> pl.DataFrame:
    """Consume the joined ``news_count`` -> trailing 21d burst z; drops the count."""
    out = frame.sort(["ticker", "date"])
    count = pl.col("news_count").fill_null(0.0).cast(pl.Float64)
    mean = count.rolling_mean(window_size=21, min_samples=21).over("ticker")
    std = count.rolling_std(window_size=21, min_samples=21).over("ticker")
    return out.with_columns(
        pl.when(std > 0).then((count - mean) / std).otherwise(0.0).alias("news_burst_21")
    ).drop("news_count")
