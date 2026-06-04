import numpy as np
import polars as pl
from new_pipeline.features.labels import add_labels, friction_aware_labels


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
