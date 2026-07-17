"""Overnight/intraday decomposition, beta-residual momentum, volume/flow (causal windows)."""

from datetime import date, timedelta

import numpy as np
import polars as pl
from new_pipeline.features.signals_v2 import (
    add_flow_features,
    add_overnight_features,
    add_residual_features,
)


def _frame(n_days, tickers, ret_fn, vol_fn=lambda t, d: 100.0):
    rows, price = [], {t: 100.0 for t in tickers}
    for d in range(n_days):
        day = date(2021, 1, 4) + timedelta(days=d)
        for t in tickers:
            r = ret_fn(t, d)
            close = price[t] * (1 + r)
            rows.append({"date": day, "ticker": t, "open": price[t] * (1 + r / 2),
                         "close": close, "returns": r, "volume": vol_fn(t, d)})
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

    assert {"overnight", "residual", "flow"} <= set(SUPPORTED_FAMILIES)
    names = extended_feature_names(["overnight", "residual"])
    assert "overnight_bias_21" in names and "resid_mom_21" in names
    assert extended_feature_names(["flow"]) == [
        "turnover_z_21", "vol_price_div_21", "amihud_chg_21"
    ]


def test_flow_turnover_z_exact_and_neutral_fill():
    frame = _frame(30, ["A"], lambda t, d: 0.01, vol_fn=lambda t, d: 100.0 + 7.0 * d)
    out = add_flow_features(frame).sort("date")
    v = np.array([100.0 + 7.0 * d for d in range(30)])
    i = 25  # trailing 21d window = v[5..25], sample std (ddof=1) as polars rolling_std
    win = v[i - 20 : i + 1]
    np.testing.assert_allclose(
        out["turnover_z_21"][i], (v[i] - win.mean()) / win.std(ddof=1), rtol=1e-12
    )
    assert out["turnover_z_21"][:20].to_list() == [0.0] * 20  # warmup neutral-fills to 0

    flat = add_flow_features(_frame(30, ["A"], lambda t, d: 0.01)).sort("date")
    assert (flat["turnover_z_21"].to_numpy() == 0.0).all()  # zero-variance volume => 0


def test_flow_divergence_accumulation_and_sign():
    # Volume spikes land exclusively on down days -> divergence must be negative.
    frame = _frame(
        40, ["A"],
        lambda t, d: -0.02 if d % 5 == 0 else 0.001,
        vol_fn=lambda t, d: 500.0 if d % 5 == 0 else 100.0,
    )
    out = add_flow_features(frame).sort("date")
    z = out["turnover_z_21"].to_numpy()
    signed = np.sign(out["returns"].to_numpy()) * z
    i = 28
    np.testing.assert_allclose(
        out["vol_price_div_21"][i], signed[i - 20 : i + 1].mean(), rtol=1e-12
    )
    assert (out["vol_price_div_21"].to_numpy()[25:] < 0).all()


def test_flow_amihud_change_exact_and_warmup():
    frame = _frame(
        50, ["A"],
        lambda t, d: 0.01 if d % 2 == 0 else -0.005,
        vol_fn=lambda t, d: 100.0 + 3.0 * d,
    )
    out = add_flow_features(frame).sort("date")
    r = out["returns"].to_numpy()
    daily = np.abs(r) / (out["volume"].to_numpy() * out["close"].to_numpy())
    a21 = np.array(
        [daily[i - 20 : i + 1].mean() if i >= 20 else np.nan for i in range(50)]
    )
    i = 45  # change = trailing 21d Amihud minus its own value 21 days earlier
    np.testing.assert_allclose(out["amihud_chg_21"][i], a21[i] - a21[i - 21], rtol=1e-12)
    assert out["amihud_chg_21"][40] is None  # needs 21 (mean) + 21 (lag) = 42 rows
    assert out["amihud_chg_21"][41] is not None


def test_flow_per_ticker_isolation_via_extended():
    from new_pipeline.features.extended import add_extended_features

    frame = _frame(
        30, ["A", "B"],
        lambda t, d: 0.01 if d % 2 else -0.01,
        vol_fn=lambda t, d: (200.0 if d % 7 == 0 else 100.0) if t == "A" else 100.0,
    )
    out = add_extended_features(frame, ["flow"])
    b = out.filter(pl.col("ticker") == "B").sort("date")
    assert (b["turnover_z_21"].to_numpy() == 0.0).all()  # blind to A's spikes
    assert (out.filter(pl.col("ticker") == "A")["turnover_z_21"].to_numpy() != 0.0).any()


def test_flow_truncation_invariance():
    # Trailing windows only: first 45 rows of the full result == result on 45 rows.
    frame = _frame(
        60, ["A"],
        lambda t, d: 0.01 if d % 3 else -0.02,
        vol_fn=lambda t, d: 100.0 + float((d * 37) % 11),
    )
    full = add_flow_features(frame.sort("date")).sort("date")
    trunc = add_flow_features(frame.sort("date").head(45)).sort("date")
    for col in ["turnover_z_21", "vol_price_div_21", "amihud_chg_21"]:
        np.testing.assert_array_equal(
            trunc[col].to_numpy(), full[col].to_numpy()[:45]
        )
