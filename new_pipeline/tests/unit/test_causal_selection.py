import numpy as np
import pytest
from new_pipeline.tournament.causal_selection import (
    granger_pvalue,
    granger_screen,
)


def _causal_dataset(n=400, seed=0):
    """fwd_ret[t] = 0.8*x_true[t-1] + noise; x_decoy independent; x_redundant ~ x_true."""
    rng = np.random.default_rng(seed)
    x_true = rng.normal(size=n)
    noise = rng.normal(0.0, 0.5, n)
    fwd = np.zeros(n)
    fwd[1:] = 0.8 * x_true[:-1] + noise[1:]
    x_decoy = rng.normal(size=n)
    x_redundant = x_true + rng.normal(0.0, 0.01, n)
    return x_true, x_decoy, x_redundant, fwd


# --- Stage A: Granger screen -------------------------------------------------
def test_granger_detects_true_cause_rejects_decoy():
    x_true, x_decoy, _, fwd = _causal_dataset()
    p_true = granger_pvalue(x_true, fwd, lags=2, horizon=1)
    p_decoy = granger_pvalue(x_decoy, fwd, lags=2, horizon=1)
    assert p_true < 0.01
    assert p_decoy > 0.05
    assert p_true < p_decoy


def test_granger_pvalue_is_golden():
    x_true, x_decoy, _, fwd = _causal_dataset()
    # The decoy's p-value is a stable mid-range number we pin exactly (golden).
    assert granger_pvalue(x_decoy, fwd, lags=2, horizon=1) == pytest.approx(
        0.26715394646380813, abs=1e-9
    )
    # The true cause is astronomically significant; overlap deflation only weakens it.
    p_true_h1 = granger_pvalue(x_true, fwd, lags=2, horizon=1)
    p_true_h5 = granger_pvalue(x_true, fwd, lags=2, horizon=5)
    assert p_true_h1 < 1e-50
    assert p_true_h5 > p_true_h1


def test_singular_design_returns_pvalue_one():
    rng = np.random.default_rng(1)
    y = rng.normal(size=120)
    x = np.zeros_like(y)
    x[1:] = y[:-1]  # x[t] == y[t-1] exactly -> feature lag collinear with target lag
    assert granger_pvalue(x, y, lags=2, horizon=1) == 1.0


def test_granger_too_few_samples_returns_one():
    assert granger_pvalue(np.arange(4.0), np.arange(4.0), lags=2) == 1.0


def test_granger_screen_keeps_cause_drops_decoy():
    x_true, x_decoy, _, fwd = _causal_dataset()
    matrix = np.column_stack([x_true, x_decoy])
    survivors, adjusted = granger_screen(
        matrix, ["x_true", "x_decoy"], fwd, lags=2, horizon=1, alpha=0.10
    )
    assert survivors == ["x_true"]
    assert adjusted["x_true"] < adjusted["x_decoy"]
