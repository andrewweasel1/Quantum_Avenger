"""Range-based realized-volatility estimators (offense roadmap P1, §D).

Close-to-close volatility throws away the intraday path; OHLC range estimators use
the high/low/open/close and are far more efficient per bar:

* **Parkinson** — high–low range only.
* **Garman–Klass** — range + open–close.
* **Rogers–Satchell** — drift-independent (valid with a trending price).
* **Yang–Zhang** — combines overnight + open-close + Rogers–Satchell; handles gaps.

Each per-bar variance is rolling-averaged over ``window`` and annualized (×√252).
Per-ticker; closed-form (no iteration). See ``docs/quantitative_math.md`` Part II §D.
"""

import math

import polars as pl

TRADING_DAYS = 252
LN2 = math.log(2.0)
VOL_FEATURE_NAMES = (
    "parkinson_vol",
    "garman_klass_vol",
    "rogers_satchell_vol",
    "yang_zhang_vol",
)


def _annualized(variance_expr) -> pl.Expr:
    return (variance_expr.clip(lower_bound=0.0) * TRADING_DAYS).sqrt()


def add_vol_estimators(ticker_frame: pl.DataFrame, window: int = 20) -> pl.DataFrame:
    """Append the four range-based annualized vol columns to one ticker's date-sorted
    frame. Leading rows are null until the rolling window fills."""
    log_hl = (pl.col("high") / pl.col("low")).log()
    log_co = (pl.col("close") / pl.col("open")).log()
    rogers_satchell = (pl.col("high") / pl.col("close")).log() * (
        pl.col("high") / pl.col("open")
    ).log() + (pl.col("low") / pl.col("close")).log() * (pl.col("low") / pl.col("open")).log()
    overnight = (pl.col("open") / pl.col("close").shift(1)).log()

    staged = ticker_frame.with_columns(
        (log_hl.pow(2) / (4.0 * LN2)).alias("_pk"),
        (0.5 * log_hl.pow(2) - (2.0 * LN2 - 1.0) * log_co.pow(2)).alias("_gk"),
        rogers_satchell.alias("_rs"),
        overnight.alias("_on"),
        log_co.alias("_oc"),
    )
    k = 0.34 / (1.34 + (window + 1) / (window - 1))  # Yang–Zhang weighting
    return staged.with_columns(
        _annualized(pl.col("_pk").rolling_mean(window_size=window)).alias("parkinson_vol"),
        _annualized(pl.col("_gk").rolling_mean(window_size=window)).alias("garman_klass_vol"),
        _annualized(pl.col("_rs").rolling_mean(window_size=window)).alias("rogers_satchell_vol"),
        _annualized(
            pl.col("_on").rolling_var(window_size=window)
            + k * pl.col("_oc").rolling_var(window_size=window)
            + (1.0 - k) * pl.col("_rs").rolling_mean(window_size=window)
        ).alias("yang_zhang_vol"),
    ).drop("_pk", "_gk", "_rs", "_on", "_oc")
