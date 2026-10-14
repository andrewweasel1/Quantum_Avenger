"""New signal families v2: overnight/intraday, beta-residual momentum, volume/flow.

Motivation (10-year audit): every existing signal is close-to-close and
raw-return based; the regime fragility lives in market-beta exposure of the
learned ranking. (1) The overnight anomaly — returns earned close->open differ
systematically from open->close — is absent from the stack. (2) Residualizing
returns against a trailing causal beta yields the regime-robust variants of
momentum/reversal. (3) Volume/flow innovations — turnover z-score, signed
volume-price divergence, Amihud change — capture flow shocks orthogonal to the
price path. All columns are per-ticker causal (trailing windows only) and enter
the tournament via features.extended_features family names "overnight",
"residual", and "flow"; the causal feature screen judges them.
"""

import polars as pl

OVERNIGHT_COLS = ["overnight_ret", "intraday_ret", "overnight_bias_21", "intraday_bias_21"]
FLOW_COLS = ["turnover_z_21", "vol_price_div_21", "amihud_chg_21"]
RESIDUAL_COLS = ["beta_60", "resid_mom_21", "resid_rev_5"]


def add_overnight_features(frame: pl.DataFrame) -> pl.DataFrame:
    """close->open vs open->close decomposition + trailing 21d biases."""
    out = frame.sort(["ticker", "date"]).with_columns([
        (pl.col("open") / pl.col("close").shift(1).over("ticker") - 1.0).alias("overnight_ret"),
        (pl.col("close") / pl.col("open") - 1.0).alias("intraday_ret"),
    ])
    return out.with_columns([
        pl.col("overnight_ret").rolling_mean(window_size=21, min_samples=21)
        .over("ticker").alias("overnight_bias_21"),
        pl.col("intraday_ret").rolling_mean(window_size=21, min_samples=21)
        .over("ticker").alias("intraday_bias_21"),
    ])


def add_residual_features(frame: pl.DataFrame, beta_window: int = 60) -> pl.DataFrame:
    """Trailing-beta residual returns -> residual momentum (21d) and reversal (5d).

    Beta is the causal rolling cov(ret, mkt)/var(mkt) over ``beta_window`` days
    against the equal-weight market return of the frame's own universe; the
    residual is ret - beta*mkt. Signals are sums of trailing residuals
    (momentum EXCLUDES the most recent 5 days; reversal is their negative sum).
    """
    mkt = frame.group_by("date").agg(pl.col("returns").mean().alias("_mkt"))
    out = frame.join(mkt, on="date", how="left").sort(["ticker", "date"])
    # rolling cov via E[xy] - E[x]E[y] with per-ticker trailing means
    r, m = pl.col("returns"), pl.col("_mkt")
    ex = r.rolling_mean(window_size=beta_window, min_samples=beta_window).over("ticker")
    em = m.rolling_mean(window_size=beta_window, min_samples=beta_window).over("ticker")
    exy = (r * m).rolling_mean(window_size=beta_window, min_samples=beta_window).over("ticker")
    emm = (m * m).rolling_mean(window_size=beta_window, min_samples=beta_window).over("ticker")
    var = emm - em * em
    beta = pl.when(var > 0).then((exy - ex * em) / var).otherwise(None).alias("beta_60")
    out = out.with_columns(beta)
    resid = (r - pl.col("beta_60") * m).alias("_resid")
    out = out.with_columns(resid)
    mom = (
        pl.col("_resid").rolling_sum(window_size=21, min_samples=21).over("ticker")
        - pl.col("_resid").rolling_sum(window_size=5, min_samples=5).over("ticker")
    ).alias("resid_mom_21")
    rev = (-pl.col("_resid").rolling_sum(window_size=5, min_samples=5).over("ticker")).alias(
        "resid_rev_5"
    )
    return out.with_columns([mom, rev]).drop("_mkt", "_resid")


def add_flow_features(frame: pl.DataFrame) -> pl.DataFrame:
    """Volume/flow family: turnover z-score, volume-price divergence, Amihud change.

    All trailing per-ticker windows. turnover_z_21: today's volume vs its own
    trailing 21d distribution. vol_price_div_21: correlation-style divergence —
    sign(ret)*volume_z accumulated 21d (rising volume on down moves reads
    negative). amihud_chg_21: 21d change in trailing 21d Amihud illiquidity —
    the INNOVATION in liquidity, not its level (the level is already a feature).
    """
    out = frame.sort(["ticker", "date"])
    vol = pl.col("volume").cast(pl.Float64)
    v_mean = vol.rolling_mean(window_size=21, min_samples=21).over("ticker")
    v_std = vol.rolling_std(window_size=21, min_samples=21).over("ticker")
    turnover_z = pl.when(v_std > 0).then((vol - v_mean) / v_std).otherwise(0.0)
    out = out.with_columns(turnover_z.alias("turnover_z_21"))
    signed = (
        pl.when(pl.col("returns") > 0).then(1.0)
        .when(pl.col("returns") < 0).then(-1.0).otherwise(0.0)
        * pl.col("turnover_z_21")
    )
    out = out.with_columns(
        signed.rolling_mean(window_size=21, min_samples=21).over("ticker")
        .alias("vol_price_div_21")
    )
    dollar = vol * pl.col("close")
    amihud_21 = (
        (pl.col("returns").abs() / pl.when(dollar > 0).then(dollar).otherwise(None))
        .rolling_mean(window_size=21, min_samples=21).over("ticker")
    )
    out = out.with_columns(
        (amihud_21 - amihud_21.shift(21).over("ticker")).alias("amihud_chg_21")
    )
    return out
