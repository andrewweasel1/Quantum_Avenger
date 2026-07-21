"""Causal market-state decoding for regime-conditional books.

State at date t uses ONLY information available at t: yesterday's-and-earlier
equal-weight market returns -> trailing realized vol -> EXPANDING-window
percentile rank -> n_states buckets (0 = calmest). Deterministic and leak-free
(no refits, no smoothed posteriors) — the evaluation gate's full-sample HMM
remains the (legitimately anticausal) judge; this is the tradable signal.
"""

import numpy as np
import polars as pl


def causal_market_regimes(panel: pl.DataFrame, vol_lookback: int = 20,
                          n_states: int = 3) -> dict:
    """{date: state} from a (date, ticker, next_ret) panel; warmup -> state 0."""
    daily = (
        panel.drop_nulls(["next_ret"]).group_by("date")
        .agg(pl.col("next_ret").mean().alias("mkt")).sort("date")
    )
    return causal_states_from_series(
        daily["date"].to_list(), daily["mkt"], vol_lookback, n_states
    )


def causal_states_from_series(days: list, market_returns, vol_lookback: int = 20,
                              n_states: int = 3) -> dict:
    """{date: state} from an already-daily market return series (same decoder;
    seam for callers that hold the equal-weight series rather than the panel,
    e.g. the registry's causal cross-check of the HMM regime verdict)."""
    vol = (
        pl.Series(market_returns).shift(1).rolling_std(window_size=vol_lookback)
        .to_numpy()
    )
    states, history = {}, []
    for day, v in zip(days, vol, strict=True):
        if v is None or np.isnan(v) or len(history) < vol_lookback:
            states[day] = 0
        else:
            rank = float(np.mean(np.asarray(history) <= v))
            states[day] = min(int(rank * n_states), n_states - 1)
        if v is not None and not np.isnan(v):
            history.append(float(v))
    return states
