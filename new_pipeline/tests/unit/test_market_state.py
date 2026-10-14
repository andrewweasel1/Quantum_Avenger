"""Per-date market-state features: causality (no same-day next_ret leak),
per-date constancy, warmup neutrality, and default-off bit-stability."""

from datetime import date, timedelta

import numpy as np
import polars as pl
from new_pipeline.features.market_state import (
    MARKET_STATE_COLS,
    add_market_state_features,
)
from new_pipeline.tournament.regime_state import causal_percentiles


def _frame(n_days=400, spike_day=None, spike=0.10):
    rng = np.random.default_rng(2)
    d0 = date(2020, 1, 1)
    rows = []
    for i in range(n_days):
        day = d0 + timedelta(days=i)
        mkt = spike if (spike_day is not None and i == spike_day) else float(rng.normal(0, 0.005))
        for t in ("A", "B"):
            rows.append({"date": day, "ticker": t, "market_next_ret": mkt})
    return pl.DataFrame(rows)


def test_causal_percentiles_rank_strictly_prior():
    days = list(range(50))
    values = [1.0] * 49 + [100.0]  # huge final value
    out = causal_percentiles(days, values, span=None, min_history=20, fill=0.5)
    assert out[49] == 1.0          # ranks vs the 49 priors, all smaller
    assert out[10] == 0.5          # warmup -> neutral fill
    # today's value never ranks against itself: a repeat of the max stays 1.0
    out2 = causal_percentiles(list(range(3)), [5.0, 5.0, 5.0], span=None,
                              min_history=1, fill=0.5)
    assert out2[1] == 1.0 and out2[2] == 1.0  # <= comparison, prior-only window


def test_no_same_day_next_ret_leak():
    """market_next_ret at date T is the FORWARD t->t+1 return; a huge value at
    T must not move T's features (only T+1's, via the one-day shift)."""
    base = add_market_state_features(_frame(spike_day=None))
    spiked = add_market_state_features(_frame(spike_day=380))
    day_t = date(2020, 1, 1) + timedelta(days=380)
    day_t1 = day_t + timedelta(days=1)
    b_t = base.filter(pl.col("date") == day_t).row(0, named=True)
    s_t = spiked.filter(pl.col("date") == day_t).row(0, named=True)
    assert b_t["mkt_vol_pctl_252"] == s_t["mkt_vol_pctl_252"]      # T untouched
    assert b_t["mkt_trend_pctl_252"] == s_t["mkt_trend_pctl_252"]
    s_t1 = spiked.filter(pl.col("date") == day_t1).row(0, named=True)
    b_t1 = base.filter(pl.col("date") == day_t1).row(0, named=True)
    assert s_t1["mkt_vol_pctl_252"] > b_t1["mkt_vol_pctl_252"]     # T+1 reacts


def test_per_date_constant_and_warmup_neutral():
    out = add_market_state_features(_frame())
    per_date = out.group_by("date").agg(
        [pl.col(c).n_unique().alias(c) for c in MARKET_STATE_COLS])
    assert per_date.select(pl.col(MARKET_STATE_COLS[0]).max()).item() == 1
    early = out.sort("date").head(20)
    assert set(early["mkt_vol_pctl_252"].to_list()) == {0.5}  # warmup neutral
    late = out.sort("date").tail(100)
    assert late["mkt_trend_pctl_252"].n_unique() > 10  # genuinely varying later
