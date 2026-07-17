"""Overnight/intraday decomposition + beta-residual momentum (causal windows)."""

from datetime import date, timedelta

import numpy as np
import polars as pl
from new_pipeline.features.signals_v2 import add_overnight_features, add_residual_features


def _frame(n_days, tickers, ret_fn):
    rows, price = [], {t: 100.0 for t in tickers}
    for d in range(n_days):
        day = date(2021, 1, 4) + timedelta(days=d)
        for t in tickers:
            r = ret_fn(t, d)
            close = price[t] * (1 + r)
            rows.append({"date": day, "ticker": t, "open": price[t] * (1 + r / 2),
                         "close": close, "returns": r})
            price[t] = close
    return pl.DataFrame(rows)


def test_overnight_decomposition_exact_and_warmup():
    frame = _frame(30, ["A"], lambda t, d: 0.01)
    out = add_overnight_features(frame).sort("date")
    # overnight = open_t/close_{t-1}-1; intraday = close_t/open_t-1; row0 null
    assert out["overnight_ret"][0] is None
    o1 = out["open"][1] / out["close"][0] - 1.0
    np.testing.assert_allclose(out["overnight_ret"][1], o1, rtol=1e-12)
    np.testing.assert_allclose(out["intraday_ret"][3],
                               out["close"][3] / out["open"][3] - 1.0, rtol=1e-12)
    assert out["overnight_bias_21"][19] is None  # 21d warmup
    assert out["overnight_bias_21"][25] is not None


def test_residual_beta_one_for_market_clone_and_zero_resid_mom():
    # Two tickers moving identically -> market == each -> beta ~ 1, residual ~ 0.
    rng = np.random.default_rng(4)
    rets = rng.normal(0, 0.01, 120)
    frame = _frame(120, ["A", "B"], lambda t, d: float(rets[d]))
    out = add_residual_features(frame).filter(pl.col("ticker") == "A").sort("date")
    beta = out["beta_60"].to_numpy()
    assert np.isnan(beta[:59]).all() or out["beta_60"][:59].null_count() == 59  # warmup
    np.testing.assert_allclose(beta[70:], 1.0, atol=1e-6)
    np.testing.assert_allclose(out["resid_mom_21"].to_numpy()[90:], 0.0, atol=1e-9)
    np.testing.assert_allclose(out["resid_rev_5"].to_numpy()[90:], 0.0, atol=1e-9)


def test_families_registered():
    from new_pipeline.features.extended import SUPPORTED_FAMILIES, extended_feature_names

    assert {"overnight", "residual"} <= set(SUPPORTED_FAMILIES)
    names = extended_feature_names(["overnight", "residual"])
    assert "overnight_bias_21" in names and "resid_mom_21" in names
