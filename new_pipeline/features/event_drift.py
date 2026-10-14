"""Event-drift signal family: self-contained price/volume drift anomalies.

The causal screen keeps price-derived drift/reaction signals (overnight,
residual-reversal, ret_since_filing) and rejects slow or noise-dominated data.
These three are documented cross-sectional anomalies of exactly that shape,
built from OHLCV alone (no external data), so they ride EVERY run:

  dist_52w_high      : close / trailing 252d max close — George-Hwang (2004)
                       52-week-high anchoring: names near their high drift up.
                       Distinct from momentum (a level ratio, not a return).
  max_ret_21         : max single-day return over the trailing 21 days —
                       Bali-Cakici-Whitelaw lottery demand: high-MAX names
                       systematically underperform.
  ret_since_vol_shock: compounded return since the last abnormal-volume day
                       (volume z-score > 2) — drift following an unattributed
                       information/attention shock; 0.0 before the first shock.

All per-ticker causal (trailing windows only); enter via
``features.extended_features`` family name "event_drift".
"""

import polars as pl

EVENT_DRIFT_COLS = ["dist_52w_high", "max_ret_21", "ret_since_vol_shock"]
_VOL_SHOCK_Z = 2.0


def add_event_drift_features(frame: pl.DataFrame) -> pl.DataFrame:
    """Append the event-drift columns, computed per ticker (trailing/causal)."""
    out = frame.sort(["ticker", "date"])
    close, ret, vol = pl.col("close"), pl.col("returns"), pl.col("volume").cast(pl.Float64)

    high_252 = close.rolling_max(window_size=252, min_samples=100).over("ticker")
    out = out.with_columns((close / high_252).alias("dist_52w_high"))
    out = out.with_columns(
        ret.rolling_max(window_size=21, min_samples=15).over("ticker").alias("max_ret_21")
    )

    v_mean = vol.rolling_mean(window_size=21, min_samples=15).over("ticker")
    v_std = vol.rolling_std(window_size=21, min_samples=15).over("ticker")
    vol_z = pl.when(v_std > 0).then((vol - v_mean) / v_std).otherwise(0.0)
    cumlog = ret.fill_null(0.0).log1p().cum_sum().over("ticker")
    out = out.with_columns(cumlog.alias("_cumlog"), (vol_z > _VOL_SHOCK_Z).alias("_shock"))
    # anchor = cumlog at the most recent shock day (carried forward per ticker)
    shock_cumlog = (
        pl.when(pl.col("_shock")).then(pl.col("_cumlog")).otherwise(None)
        .forward_fill().over("ticker")
    )
    out = out.with_columns(shock_cumlog.alias("_shock_cumlog"))
    return out.with_columns(
        ((pl.col("_cumlog") - pl.col("_shock_cumlog")).exp() - 1.0)
        .fill_null(0.0).alias("ret_since_vol_shock")
    ).drop("_cumlog", "_shock", "_shock_cumlog")
