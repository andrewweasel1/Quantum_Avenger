"""Short-flow signal family: FINRA daily short-volume, fast per-ticker features.

The fundamentals experiment showed the causal screen selects FAST per-ticker
time-series signals (returns, overnight, microstructure) and rejects slow
cross-sectional levels. Short volume is daily, so these are built the same way —
per-ticker causal trailing transforms of the day's short fraction:

  short_ratio  : short_volume / total_volume (the day's short-marked fraction);
                 missing days (outside the CDN window / thin names) neutral-fill
                 to 0.5, the population median.
  short_z_21   : trailing 21d z-score of short_ratio — how UNUSUAL today's
                 shorting is for THIS name (warmup/degenerate -> 0.0).
  short_chg_5  : 5-day change in short_ratio — short-flow acceleration (0.0 on
                 warmup / missing).

Opt-in via ``features.short_flow_features``; consumes the ``short_volume`` /
``total_volume`` columns joined by :func:`data.short_volume.attach_short_volume`
and drops them.
"""

import polars as pl

SHORT_FLOW_COLS = ["short_ratio", "short_z_21", "short_chg_5"]
_MEDIAN_FILL = 0.5  # population median short fraction (neutral level for missing)


def add_short_flow_features(frame: pl.DataFrame) -> pl.DataFrame:
    """Per-ticker causal short-flow features from joined short/total volume."""
    out = frame.sort(["ticker", "date"]).with_columns(
        (pl.col("short_volume") / pl.col("total_volume")).alias("_sr")
    )
    sr = pl.col("_sr")
    mean = sr.rolling_mean(window_size=21, min_samples=15).over("ticker")
    std = sr.rolling_std(window_size=21, min_samples=15).over("ticker")
    z = pl.when(std > 0).then((sr - mean) / std).otherwise(0.0)
    chg = sr - sr.shift(5).over("ticker")
    out = out.with_columns([
        sr.fill_null(_MEDIAN_FILL).alias("short_ratio"),
        z.fill_null(0.0).alias("short_z_21"),
        chg.fill_null(0.0).alias("short_chg_5"),
    ])
    return out.drop("_sr", "short_volume", "total_volume")
