"""Hybrid intraday universe: liquidity-filtered static base + daily scanner.

The static base is the membership question (which small/mid names exist and
are liquid enough to touch at all); the scanner is the attention question
(where today's intraday liquidity actually concentrates). Both are causal:
eligibility for session T uses data strictly through T-1, and the scanner's
only same-day input is the session OPEN price — known at 09:30, before any
ORB entry (earliest range is 5 minutes).
"""

from __future__ import annotations

from pathlib import Path

import polars as pl


def segment_symbols(cfg) -> list[str]:
    """Tickers of the configured extended-cap segments from the universe
    fixture (`data.universe_path`), sorted for determinism."""
    from new_pipeline.adapters import StaticUniverseProvider

    path = Path(cfg.data.universe_path) if cfg.data.universe_path else None
    universe = StaticUniverseProvider(path)
    segments = set(cfg.intraday.universe_segments)
    return sorted(t for t, sector in universe.sectors().items() if sector in segments)


def eligibility(daily: pl.DataFrame, min_adv_dollars: float,
                min_price: float, window: int = 20) -> pl.DataFrame:
    """(date, ticker, eligible) — session-T eligibility from STRICTLY PRIOR
    data: trailing ``window``-day median dollar volume and the prior close,
    both shifted one session, so a name's first eligible day never leans on
    its own same-day tape."""
    return (daily.sort(["ticker", "date"])
            .with_columns(
                pl.col("dollar_vol").rolling_median(window_size=window)
                .shift(1).over("ticker").alias("_adv_med"),
                pl.col("close").shift(1).over("ticker").alias("_prev_close"))
            .with_columns(
                ((pl.col("_adv_med") >= min_adv_dollars)
                 & (pl.col("_prev_close") >= min_price))
                .fill_null(False).alias("eligible"))
            .select("date", "ticker", "eligible", "_adv_med", "_prev_close"))


def scan_day(daily: pl.DataFrame, day, top_n: int,
             min_adv_dollars: float, min_price: float) -> list[str]:
    """Session-``day`` ORB candidates: the eligible set ranked by a causal
    attention score and cut to ``top_n``.

    Score = mean of cross-sectional percentiles of |gap| (session open vs
    prior close — the one same-day input, known at 09:30), prior-day relative
    volume (vs its own trailing median), and prior-day dollar volume. Ties
    break by ticker for determinism."""
    elig = eligibility(daily, min_adv_dollars, min_price)
    frame = (daily.join(elig, on=["date", "ticker"], how="left")
             .sort(["ticker", "date"])
             .with_columns(
                 pl.col("dollar_vol").shift(1).over("ticker").alias("_prev_dv"))
             .filter((pl.col("date") == day) & pl.col("eligible")))
    if frame.is_empty():
        return []
    frame = frame.with_columns(
        (pl.col("open") / pl.col("_prev_close") - 1.0).abs().alias("_gap"),
        (pl.col("_prev_dv") / pl.col("_adv_med")).alias("_rvol"),
    ).drop_nulls(["_gap", "_rvol", "_adv_med"])
    if frame.is_empty():
        return []
    ranked = frame.with_columns(
        (pl.col("_gap").rank("average") / pl.len()).alias("_p_gap"),
        (pl.col("_rvol").rank("average") / pl.len()).alias("_p_rvol"),
        (pl.col("_adv_med").rank("average") / pl.len()).alias("_p_adv"),
    ).with_columns(
        ((pl.col("_p_gap") + pl.col("_p_rvol") + pl.col("_p_adv")) / 3.0).alias("score")
    ).sort(["score", "ticker"], descending=[True, False])
    return ranked["ticker"].head(top_n).to_list()
