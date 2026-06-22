import numpy as np
import polars as pl
import pytest
from new_pipeline.features.labels import (
    add_labels,
    friction_aware_labels,
    triple_barrier_labels,
)


def test_label_beats_cost():
    close = np.array([100.0, 100.05, 102.0, 101.0])  # cost 10bps = 0.001
    labels = friction_aware_labels(close, horizon=1, cost_bps=10.0)
    assert labels[0] == 0.0  # +0.05% < 0.1% cost
    assert labels[1] == 1.0  # +1.95% > cost
    assert labels[2] == 0.0  # negative
    assert np.isnan(labels[3])  # no forward window


def test_horizon_window_is_nan_at_tail():
    close = np.arange(1, 11, dtype=float)  # strictly increasing
    labels = friction_aware_labels(close, horizon=3, cost_bps=0.0)
    assert np.isnan(labels[-3:]).all()
    assert (labels[:-3] == 1.0).all()


def test_add_labels_per_ticker():
    frame = pl.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "ticker": ["AAA", "AAA", "AAA"],
            "close": [100.0, 110.0, 90.0],
        }
    )
    out = add_labels(frame, horizon=1, cost_bps=0.0)
    assert "target_label" in out.columns
    assert out["target_label"][0] == 1.0  # 100 -> 110 up
    assert out["target_label"][1] == 0.0  # 110 -> 90 down


# --- triple-barrier ---------------------------------------------------------
# atr=1, pt_mult=sl_mult=2 -> entry=100 gives upper=102, lower=98. horizon=2.
_TB_HIGH = np.array([100.0, 102.5, 100.5, 100.5, 100.5])
_TB_LOW = np.array([100.0, 99.0, 97.0, 99.5, 99.5])
_TB_CLOSE = np.array([100.0, 100.0, 100.0, 100.0, 100.0])
_TB_ATR = np.array([1.0, 1.0, 1.0, 1.0, 1.0])


def test_triple_barrier_first_touch_outcomes():
    res = triple_barrier_labels(
        _TB_HIGH, _TB_LOW, _TB_CLOSE, _TB_ATR, horizon=2, pt_mult=2.0, sl_mult=2.0, cost_bps=10.0
    )
    # i=0: high[1]=102.5 hits the +2*ATR profit-take at s=1 -> label 1.
    assert res.label[0] == 1.0
    assert res.t1_offset[0] == 1.0
    assert res.fwd_ret[0] == pytest.approx(0.02)
    # i=1: low[2]=97 hits the -2*ATR stop at s=2 -> label 0.
    assert res.label[1] == 0.0
    assert res.t1_offset[1] == 1.0
    assert res.fwd_ret[1] == pytest.approx(-0.02)
    # i=2: neither barrier touched -> vertical at s=4, flat return < cost -> label 0.
    assert res.label[2] == 0.0
    assert res.t1_offset[2] == 2.0
    # last `horizon` rows have no vertical window.
    assert np.isnan(res.label[-2:]).all()


def test_triple_barrier_same_bar_tie_resolves_to_stop():
    # A single bar straddles both barriers; the conservative resolution is the stop.
    high = np.array([100.0, 103.0, 100.0])
    low = np.array([100.0, 97.0, 100.0])
    close = np.array([100.0, 100.0, 100.0])
    atr = np.array([1.0, 1.0, 1.0])
    res = triple_barrier_labels(high, low, close, atr, horizon=1, pt_mult=2.0, sl_mult=2.0)
    assert res.label[0] == 0.0
    assert res.fwd_ret[0] == pytest.approx(-0.02)


def test_add_labels_triple_barrier_emits_span_columns():
    frame = pl.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04", "2024-01-05"],
            "ticker": ["AAA"] * 5,
            "high": _TB_HIGH,
            "low": _TB_LOW,
            "close": _TB_CLOSE,
            "atr": _TB_ATR,
        }
    )
    out = add_labels(frame, horizon=2, cost_bps=10.0, pt_mult=2.0, sl_mult=2.0)
    assert {"target_label", "fwd_ret", "label_t1_offset"} <= set(out.columns)
    assert out["target_label"][0] == 1.0
    assert out["label_t1_offset"][0] == 1.0
    assert out["target_label"][1] == 0.0
