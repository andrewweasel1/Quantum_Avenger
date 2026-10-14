"""Calendar-time accounting: collapse pooled per-(ticker, day) samples to daily means.

The tournament's OOS artifacts are pooled ticker-major sample series (~50-70
tickers x ~750 trading days stacked end to end). Every statistic that assumes a
time axis — Sharpe's sqrt(252) annualization, DSR/PSR's sqrt(n), PBO partitions,
haircut "years", the regime HMM's transition dynamics — is only meaningful on a
single chronologically-ordered daily series. This module is the one shared
pooled->daily transform used by trial scoring (grid search), the promotion
gates, the portfolio book, and the dashboard API, so all of them live on the
same axis. Kept dependency-light (polars/numpy only) because the API's artifact
parser imports it.
"""

import numpy as np
import polars as pl


def collapse_to_daily(dates, values) -> tuple[pl.Series, np.ndarray]:
    """Equal-weight per-date means of pooled per-(ticker, day) rows.

    ``dates`` is a length-n per-row date sequence (typically the persisted
    ``sample_dates``, non-monotonic ticker-major order); ``values`` is ``(n,)``
    or ``(n, k)``. The whole matrix is collapsed in ONE group_by so every column
    lands on the SAME sorted date axis — DSR deflation, PBO and the effective-
    trials estimate all require the trial columns to stay row-aligned.

    Returns ``(sorted_dates, collapsed)`` where ``collapsed`` matches the input
    dimensionality (``(d,)`` or ``(d, k)`` for d unique dates).
    """
    arr = np.asarray(values, dtype=np.float64)
    squeeze = arr.ndim == 1
    matrix = arr.reshape(-1, 1) if squeeze else arr
    if len(dates) != matrix.shape[0]:
        raise ValueError(
            f"dates length {len(dates)} != values rows {matrix.shape[0]}"
        )
    cols = [f"c{i}" for i in range(matrix.shape[1])]
    frame = pl.DataFrame({"date": dates}).with_columns(
        [pl.Series(name, matrix[:, i]) for i, name in enumerate(cols)]
    )
    daily = frame.group_by("date").agg([pl.col(c).mean() for c in cols]).sort("date")
    out = daily.select(cols).to_numpy()
    return daily["date"], (out[:, 0] if squeeze else out)
