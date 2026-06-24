"""Per-signal alpha evaluation — the "finding" lens (offense roadmap P2).

Measures each signal's cross-sectional predictive power against forward returns:
the **Information Coefficient** (per-date Spearman rank correlation between the
signal and the forward return, across names), its stability (**ICIR** =
mean(IC)/std(IC)), significance (t-stat), breadth, hit-rate, and horizon decay.

Universe-wide, *not* per-sector: cross-sectional IC needs a broad cross-section and
our sectors are thin (a handful of names). Pure/offline (polars + numpy) — no model,
no network; recorded as a run diagnostic (``alpha_eval.json``) so signal edge is
*measured*, not assumed.

See ``docs/OFFENSE_ROADMAP.md`` (P2) and ``docs/quantitative_math.md`` Part II §H.
"""

import math
from dataclasses import asdict, dataclass

import polars as pl

DEFAULT_MIN_NAMES = 5  # minimum cross-sectional breadth for a usable IC observation
DEFAULT_DECAY_HORIZONS = (1, 5, 10, 20)


@dataclass(frozen=True)
class ICReport:
    """Cross-sectional IC summary for one signal (all stats reporting-only)."""

    signal: str
    mean_ic: float
    icir: float
    ic_t_stat: float
    n_periods: int
    breadth: float  # mean names per usable date
    hit_rate: float  # fraction of periods with IC > 0


def _ic_per_date(frame, signal, fwd_ret_col, date_col, min_names) -> pl.DataFrame:
    """Per-date Spearman rank-IC across names; drops thin (< ``min_names``) and
    zero-dispersion (NaN) dates so the IC series is well-defined."""
    sub = frame.select([date_col, signal, fwd_ret_col]).drop_nulls()
    return (
        sub.group_by(date_col)
        .agg(
            pl.corr(pl.col(signal), pl.col(fwd_ret_col), method="spearman").alias("ic"),
            pl.len().alias("n"),
        )
        .filter(pl.col("n") >= min_names)
        .with_columns(pl.col("ic").fill_nan(None))
        .drop_nulls("ic")
        .sort(date_col)
    )


def information_coefficient(
    frame, signal, fwd_ret_col="fwd_ret", date_col="date", min_names=DEFAULT_MIN_NAMES
) -> ICReport:
    """Cross-sectional IC report for one signal vs. ``fwd_ret_col``.

    Empty (no usable date has >= ``min_names`` names) ⇒ an all-zero report rather
    than NaN, so thin universes degrade gracefully.
    """
    per_date = _ic_per_date(frame, signal, fwd_ret_col, date_col, min_names)
    ic = per_date["ic"].to_numpy()
    n = int(ic.size)
    if n == 0:
        return ICReport(signal, 0.0, 0.0, 0.0, 0, 0.0, 0.0)
    mean_ic = float(ic.mean())
    std_ic = float(ic.std(ddof=1)) if n > 1 else 0.0
    icir = mean_ic / std_ic if std_ic > 0.0 else 0.0
    t_stat = icir * math.sqrt(n) if std_ic > 0.0 else 0.0
    return ICReport(
        signal, mean_ic, icir, t_stat, n, float(per_date["n"].mean()), float((ic > 0).mean())
    )


def evaluate_signals(
    frame, signals, fwd_ret_col="fwd_ret", date_col="date", min_names=DEFAULT_MIN_NAMES
) -> dict[str, dict]:
    """``{signal -> ICReport-as-dict}`` for each present column, ranked by |mean_ic| desc."""
    reports = [
        information_coefficient(frame, s, fwd_ret_col, date_col, min_names)
        for s in signals
        if s in frame.columns
    ]
    reports.sort(key=lambda report: abs(report.mean_ic), reverse=True)
    return {report.signal: asdict(report) for report in reports}


def _forward_return_expr(horizon, close_col, ticker_col) -> pl.Expr:
    return pl.col(close_col).shift(-horizon).over(ticker_col) / pl.col(close_col) - 1.0


def ic_decay(
    frame,
    signal,
    horizons=DEFAULT_DECAY_HORIZONS,
    close_col="close",
    ticker_col="ticker",
    date_col="date",
    min_names=DEFAULT_MIN_NAMES,
) -> dict[int, float]:
    """Mean IC of ``signal`` against forward returns at each horizon — how fast edge
    fades. Recomputes forward returns per ticker from ``close_col`` (causal: shift(-h))."""
    ordered = frame.sort([ticker_col, date_col])
    decay = {}
    for horizon in horizons:
        with_fwd = ordered.with_columns(
            _forward_return_expr(horizon, close_col, ticker_col).alias("_ae_fwd")
        )
        decay[int(horizon)] = information_coefficient(
            with_fwd, signal, "_ae_fwd", date_col, min_names
        ).mean_ic
    return decay


def alpha_eval_report(
    frame,
    signals,
    factor_signals=(),
    fwd_ret_col="fwd_ret",
    date_col="date",
    min_names=DEFAULT_MIN_NAMES,
    decay_horizons=DEFAULT_DECAY_HORIZONS,
) -> dict:
    """Run-level diagnostic: per-signal IC/ICIR for every ``signal``, plus horizon
    decay for the (cheaper) ``factor_signals`` subset when ``close``/``ticker`` exist."""
    ic = evaluate_signals(frame, signals, fwd_ret_col, date_col, min_names)
    decay = {}
    if "close" in frame.columns and "ticker" in frame.columns:
        decay = {
            signal: ic_decay(
                frame, signal, decay_horizons, date_col=date_col, min_names=min_names
            )
            for signal in factor_signals
            if signal in frame.columns
        }
    return {"ic": ic, "decay": decay, "min_names": min_names, "n_signals": len(ic)}
