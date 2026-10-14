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
                          n_states: int = 3, span: int | None = None) -> dict:
    """{date: state} from a (date, ticker, next_ret) panel; warmup -> state 0."""
    daily = (
        panel.drop_nulls(["next_ret"]).group_by("date")
        .agg(pl.col("next_ret").mean().alias("mkt")).sort("date")
    )
    return causal_states_from_series(
        daily["date"].to_list(), daily["mkt"], vol_lookback, n_states, span
    )


def causal_states_from_series(days: list, market_returns, vol_lookback: int = 20,
                              n_states: int = 3, span: int | None = None) -> dict:
    """{date: state} from an already-daily market return series (same decoder;
    seam for callers that hold the equal-weight series rather than the panel,
    e.g. the registry's causal cross-check of the HMM regime verdict).

    ``span`` bounds the percentile-ranking history to the trailing ``span``
    observations (rolling window). ``None`` keeps the legacy EXPANDING window,
    which is prevalence-unstable under secular vol shifts: 2016-17's ultra-calm
    era permanently occupies the low percentiles, so post-2018 only ~9%% of
    census-window days ranked "calm" vs the ~46%% the evaluation HMM assigns —
    the decoder-prevalence mismatch that neutered the calm-cost policy (run
    711bdbd6845a). A trailing-year window (252) re-anchors each era: ~37%%
    calm, ~19-day state runs, and the calm set actually carries the weak edge
    (control book +0.41 in-calm vs +1.24 out) — an evidence-informed,
    pre-registered spec choice, disclosed rather than scanned."""
    vol = (
        pl.Series(market_returns).shift(1).rolling_std(window_size=vol_lookback)
        .to_numpy()
    )
    states, history = {}, []
    for day, v in zip(days, vol, strict=True):
        if v is None or np.isnan(v) or len(history) < vol_lookback:
            states[day] = 0
        else:
            window = np.asarray(history if span is None else history[-span:])
            rank = float(np.mean(window <= v))
            states[day] = min(int(rank * n_states), n_states - 1)
        if v is not None and not np.isnan(v):
            history.append(float(v))
    return states


def causal_percentiles(days: list, values, span: int | None = 252,
                       min_history: int = 20, fill: float = 0.5) -> dict:
    """{date: percentile in [0, 1]} of each value against STRICTLY PRIOR values
    over a trailing ``span`` window — the continuous form of the tercile
    decoder, sharing its discipline (today's value never ranks against itself).
    Warmup and NaN days carry the neutral ``fill``."""
    arr = np.asarray([np.nan if v is None else float(v) for v in values])
    out, history = {}, []
    for day, v in zip(days, arr, strict=True):
        if np.isnan(v) or len(history) < min_history:
            out[day] = fill
        else:
            window = np.asarray(history[-span:] if span else history)
            out[day] = float(np.mean(window <= v))
        if not np.isnan(v):
            history.append(float(v))
    return out
