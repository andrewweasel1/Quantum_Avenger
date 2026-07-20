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
filing_reaction: the market's return over the ~3 trading days immediately
after the filing — with no analyst estimates, the market's OWN verdict is
the earnings-surprise proxy. Exposed only once the window has fully elapsed
(``days_since_filing >= FILING_REACTION_VISIBLE_DAYS``) so it is strictly
causal; 0.0 before that / no filing.
pead_drift: ``ret_since_filing * sign(filing_reaction)`` — post-earnings
drift IN THE DIRECTION of the initial reaction (the textbook PEAD
refinement of the already-selected ret_since_filing).
news_burst_21: today's headline count vs its own trailing 21d distribution
(z-score; 0.0 in warmup/degenerate windows) — coverage volume, not
polarity; bursts mark event days the filing calendar cannot see.
"""

import warnings

import polars as pl

FILING_EVENT_COLS = ["days_since_filing", "ret_since_filing", "filing_reaction", "pead_drift"]
NEWS_EVENT_COLS = ["news_burst_21"]

# One saturation constant for "stale filing" and "no filing knowable": past a
# year the filing clock carries no post-announcement information either way.
FILING_CLOCK_CAP_DAYS = 365.0
# Calendar-day lag after which the 3-trading-day filing reaction is fully in the
# past (a conservative bound covering long weekends/holidays -> no look-ahead).
FILING_REACTION_VISIBLE_DAYS = 7.0
_REACTION_TRADING_DAYS = 3


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
    # cumlog 3 trading rows ahead: at a filing row this is the cumulative return
    # through the close of the 3rd post-filing day (the reaction window's end).
    out = out.with_columns(
        pl.col("_cumlog").shift(-_REACTION_TRADING_DAYS).over("ticker").alias("_cumlog_fwd")
    )
    anchors = out.select(
        pl.col("ticker"),
        pl.col("date").alias("as_of"),
        pl.col("_cumlog").alias("_cumlog_filing"),
        pl.col("_cumlog_fwd").alias("_cumlog_reaction"),
    )
    with warnings.catch_warnings():  # both sorted within ticker; polars can't verify with `by`
        warnings.filterwarnings("ignore", message="Sortedness of columns")
        out = out.join_asof(
            anchors, left_on="as_of", right_on="as_of", by="ticker", strategy="backward"
        )
    reaction = (pl.col("_cumlog_reaction") - pl.col("_cumlog_filing")).exp() - 1.0
    ret_since = ((pl.col("_cumlog") - pl.col("_cumlog_filing")).exp() - 1.0).fill_null(0.0)
    # visible only once the whole 3-day window is in the past -> strictly causal.
    filing_reaction = (
        pl.when(pl.col("days_since_filing") >= FILING_REACTION_VISIBLE_DAYS)
        .then(reaction).otherwise(0.0).fill_null(0.0)
    )
    return out.with_columns(
        pl.col("days_since_filing").fill_null(FILING_CLOCK_CAP_DAYS),
        ret_since.alias("ret_since_filing"),
        filing_reaction.alias("filing_reaction"),
    ).with_columns(
        (pl.col("ret_since_filing") * pl.col("filing_reaction").sign()).alias("pead_drift")
    ).drop("as_of", "_cumlog", "_cumlog_fwd", "_cumlog_filing", "_cumlog_reaction")


def add_news_burst(frame: pl.DataFrame) -> pl.DataFrame:
    """Consume the joined ``news_count`` -> trailing 21d burst z; drops the count."""
    out = frame.sort(["ticker", "date"])
    count = pl.col("news_count").fill_null(0.0).cast(pl.Float64)
    mean = count.rolling_mean(window_size=21, min_samples=21).over("ticker")
    std = count.rolling_std(window_size=21, min_samples=21).over("ticker")
    return out.with_columns(
        pl.when(std > 0).then((count - mean) / std).otherwise(0.0).alias("news_burst_21")
    ).drop("news_count")
