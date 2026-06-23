import numpy as np
import pytest
from new_pipeline.tournament.causal_selection import (
    granger_pvalue,
    granger_screen,
    purged_cpcv_mda,
    select_causal_features,
)
from new_pipeline.tournament.cpcv import CPCVSplitGenerator


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


# --- Stage B: purged-CPCV MDA ------------------------------------------------
def _label_corr_predictor(train_x, train_y):
    """Stub: pick the train-most-correlated column, predict its sign on test."""
    corrs = [abs(np.corrcoef(train_x[:, j], train_y)[0, 1]) for j in range(train_x.shape[1])]
    best = int(np.nanargmax(corrs))
    return lambda test_x: (test_x[:, best] > 0.0).astype(np.float64)


def test_purged_mda_is_deterministic_and_ranks_the_cause_top():
    rng = np.random.default_rng(3)
    n = 240
    x_true = rng.normal(size=n)
    x_decoy = rng.normal(size=n)
    labels = (x_true > 0.0).astype(np.float64)  # label depends on x_true contemporaneously
    matrix = np.column_stack([x_true, x_decoy])
    splitter = CPCVSplitGenerator(n_groups=4, test_groups=2, purge=0, embargo=0)

    names = ["x_true", "x_decoy"]
    first = purged_cpcv_mda(matrix, names, labels, _label_corr_predictor, splitter, seed=7)
    second = purged_cpcv_mda(matrix, names, labels, _label_corr_predictor, splitter, seed=7)
    assert first == second  # determinism under a fixed seed
    assert first["x_true"] > first["x_decoy"]  # permuting the genuine driver hurts accuracy most
    assert first["x_decoy"] == pytest.approx(0.0, abs=1e-9)  # predictor ignores the decoy column


# --- end-to-end select_causal_features ---------------------------------------
def _splitter():
    return CPCVSplitGenerator(n_groups=4, test_groups=2, purge=0, embargo=0)


def test_select_causal_keeps_cause_drops_decoy_collapses_redundant():
    rng = np.random.default_rng(5)
    n = 300
    x_true = rng.normal(size=n)
    x_redundant = x_true + rng.normal(0.0, 0.01, n)  # collinear with x_true
    x_decoy = rng.normal(size=n)
    fwd = np.zeros(n)
    fwd[1:] = 0.9 * x_true[:-1] + rng.normal(0.0, 0.4, n)[1:]  # Granger target (lagged)
    labels = (x_true > 0.0).astype(np.float64)  # MDA target (contemporaneous)
    matrix = np.column_stack([x_true, x_redundant, x_decoy])

    selected = select_causal_features(
        matrix, ["x_true", "x_redundant", "x_decoy"], fwd, labels,
        _label_corr_predictor, _splitter(), lags=2, horizon=1, causal_alpha=0.10,
    )
    assert "x_decoy" not in selected  # non-causal -> dropped by the Granger screen
    assert "x_true" in selected or "x_redundant" in selected  # the causal cluster survives
    assert not ("x_true" in selected and "x_redundant" in selected)  # collinear -> one kept


def test_select_causal_never_crashes_on_degenerate_input():
    rng = np.random.default_rng(6)
    n = 120
    const_col = np.ones(n)  # rank-deficient feature: must be dropped, never crash
    x = rng.normal(size=n)
    fwd = np.zeros(n)
    fwd[1:] = x[:-1] + rng.normal(0.0, 0.3, n - 1)  # x leads fwd (with noise, not collinear)
    labels = (x > 0.0).astype(np.float64)
    matrix = np.column_stack([const_col, x])

    selected = select_causal_features(
        matrix, ["const", "x"], fwd, labels, _label_corr_predictor, _splitter(),
        lags=2, horizon=1,
    )
    assert selected  # never empty
    assert "const" not in selected  # rank-deficient constant -> Granger p=1.0 -> dropped


def test_select_causal_falls_back_when_nothing_is_causal():
    rng = np.random.default_rng(8)
    n = 150
    matrix = rng.normal(size=(n, 3))
    target = rng.normal(size=n)  # nothing leads it
    labels = (rng.normal(size=n) > 0.0).astype(np.float64)

    selected = select_causal_features(
        matrix, ["a", "b", "c"], target, labels, _label_corr_predictor, _splitter(),
        lags=2, horizon=1,
    )
    assert selected  # empty screen -> fall back to all, never empty
    assert set(selected) <= {"a", "b", "c"}
