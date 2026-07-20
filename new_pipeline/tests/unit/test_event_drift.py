"""Event-drift family: 52w-high anchor, lottery MAX, vol-shock drift (causal)."""

from datetime import date, timedelta

import numpy as np
import polars as pl
from new_pipeline.features.event_drift import EVENT_DRIFT_COLS, add_event_drift_features


def _frame(n=300, seed=0, shock_days=(), tickers=("A",)):
    days, d = [], date(2020, 1, 6)
    while len(days) < n:
        if d.weekday() < 5:
            days.append(d)
        d += timedelta(days=1)
    rng = np.random.default_rng(seed)
    rows = []
    for t in tickers:
        ret = rng.normal(0.0005, 0.012, n)
        close = 100.0 * np.exp(np.cumsum(ret))
        vol = np.full(n, 1.0e6)
        for s in shock_days:
            vol[s] = 6.0e6
        rows.append(pl.DataFrame({
            "date": days, "ticker": [t] * n, "close": close,
            "returns": ret, "volume": vol,
        }))
    return pl.concat(rows)


def test_dist_52w_high_exact_and_bounded():
    frame = _frame()
    out = add_event_drift_features(frame).sort("date")
    close = frame.sort("date")["close"].to_numpy()
    i = 280  # full 252d window available
    np.testing.assert_allclose(
        out["dist_52w_high"][i], close[i] / close[i - 251 : i + 1].max(), rtol=1e-12
    )
    vals = out["dist_52w_high"].drop_nulls().to_numpy()
    assert (vals <= 1.0 + 1e-12).all() and (vals > 0).all()
    assert out["dist_52w_high"][:99].null_count() == 99  # min_samples=100 warmup


def test_max_ret_21_exact():
    frame = _frame()
    out = add_event_drift_features(frame).sort("date")
    ret = frame.sort("date")["returns"].to_numpy()
    i = 60
    np.testing.assert_allclose(out["max_ret_21"][i], ret[i - 20 : i + 1].max(), rtol=1e-12)


def test_ret_since_vol_shock_anchors_and_neutral():
    frame = _frame(shock_days=(100, 200))
    out = add_event_drift_features(frame).sort("date")
    ret = frame.sort("date")["returns"].to_numpy()
    # before any shock: neutral 0.0 (not null -> survives drop_nulls)
    assert (out["ret_since_vol_shock"][:100].to_numpy() == 0.0).all()
    np.testing.assert_allclose(out["ret_since_vol_shock"][100], 0.0, atol=1e-12)  # shock day
    i = 150  # anchored to shock at 100: compounded product of post-shock returns
    np.testing.assert_allclose(
        out["ret_since_vol_shock"][i], np.prod(1.0 + ret[101 : i + 1]) - 1.0, rtol=1e-9
    )
    j = 240  # re-anchored to the LATEST shock at 200
    np.testing.assert_allclose(
        out["ret_since_vol_shock"][j], np.prod(1.0 + ret[201 : j + 1]) - 1.0, rtol=1e-9
    )


def test_per_ticker_isolation_and_truncation_invariance():
    frame = _frame(n=200, tickers=("A", "B"), shock_days=(50,))
    full = add_event_drift_features(frame).sort(["ticker", "date"])
    # truncation: first 150 rows per ticker computed alone == full's first 150
    trunc_in = frame.sort(["ticker", "date"]).group_by("ticker", maintain_order=True).head(150)
    trunc = add_event_drift_features(trunc_in).sort(["ticker", "date"])
    for col in EVENT_DRIFT_COLS:
        a = trunc.group_by("ticker", maintain_order=True).head(150)[col].to_numpy()
        b = full.group_by("ticker", maintain_order=True).head(150)[col].to_numpy()
        np.testing.assert_array_equal(a, b)


def test_family_registered():
    from new_pipeline.features.extended import (
        SUPPORTED_FAMILIES,
        add_extended_features,
        extended_feature_names,
    )

    assert "event_drift" in SUPPORTED_FAMILIES
    assert extended_feature_names(["event_drift"]) == EVENT_DRIFT_COLS
    out = add_extended_features(_frame(n=120), ["event_drift"])
    assert all(c in out.columns for c in EVENT_DRIFT_COLS)
