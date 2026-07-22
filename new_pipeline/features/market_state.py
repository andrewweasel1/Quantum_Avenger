"""Per-date market-state features broadcast to every name.

The cheap alternative to per-ticker rolling-HMM machinery
(``fusion.markov_features``): the causal market trend/vol percentile ranks as
continuous per-date features. A per-date constant cannot rank names by itself
— its value is INTERACTION context (trees splitting on the macro state to use
cross-sectional features regime-conditionally) — so expect its contribution
through MDA and the gates, and a degenerate cross-sectional IC in alpha_eval.

Causality: the daily market series is the pinned ``market_next_ret`` shifted
one date, so at date t it is the equal-weight close(t-1)->close(t) return —
fully known at t's close. Trailing stats end at t; percentile windows rank
against STRICTLY PRIOR days (the decoder's discipline). Warmup rows carry the
neutral 0.5 so no training row is dropped (a null here would silently shift
the whole frame's usable start by ~15 months)."""

import polars as pl

from new_pipeline.tournament.regime_state import causal_percentiles

MARKET_STATE_COLS = ("mkt_vol_pctl_252", "mkt_trend_pctl_252")


def add_market_state_features(frame: pl.DataFrame, span: int = 252,
                              vol_window: int = 20,
                              trend_window: int = 63) -> pl.DataFrame:
    daily = (
        frame.select("date", "market_next_ret").drop_nulls()
        .unique(subset=["date"]).sort("date")
    )
    same_day = daily["market_next_ret"].shift(1)  # close(t-1)->close(t) at t
    vol = same_day.rolling_std(window_size=vol_window)
    trend = same_day.rolling_mean(window_size=trend_window)
    days = daily["date"].to_list()
    vol_pctl = causal_percentiles(days, vol.to_list(), span=span)
    trend_pctl = causal_percentiles(days, trend.to_list(), span=span)
    state = pl.DataFrame({
        "date": days,
        "mkt_vol_pctl_252": [vol_pctl[d] for d in days],
        "mkt_trend_pctl_252": [trend_pctl[d] for d in days],
    })
    return frame.join(state, on="date", how="left").with_columns(
        pl.col(list(MARKET_STATE_COLS)).fill_null(0.5)
    )
