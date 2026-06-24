"""Unit tests for meta-labeling (offense roadmap P3).

The pure scoring layer (precision/recall/F1, primary vs. meta-filtered, improvement
criteria) and the ``run_meta_labeling`` orchestration with an injected stub model
(happy path, thin/single-class guards, weight subsetting). Golden pins live in
tests/golden/test_meta_labeling_golden.py.
"""

import numpy as np
import pytest
from new_pipeline.tournament.meta_labeling import (
    evaluate_meta_labeling,
    meta_filtered_signal,
    precision_recall_f1,
    primary_signal,
    run_meta_labeling,
)

# primary fires on the first 4 bars; outcomes have 3 wins.
_OUT = [1, 1, 0, 0, 1, 0]
_SIG = [1, 1, 1, 1, 0, 0]
_PROBA = [0.9, 0.8, 0.2, 0.1, 0.5, 0.5]


def _stub_fit(x, y, w):
    """Deterministic 'model': P(win) = first feature column (clipped)."""
    return lambda tx: np.clip(np.asarray(tx, dtype=float)[:, 0], 0.0, 1.0)


def test_primary_signal_threshold():
    sig = primary_signal([0.2, 0.7, 0.65, 0.66], 0.65)
    assert sig.tolist() == [0, 1, 0, 1]  # strictly greater than


def test_precision_recall_f1_hand_case():
    p, r, f = precision_recall_f1(_OUT, _SIG)
    assert p == pytest.approx(0.5)
    assert r == pytest.approx(2 / 3)
    assert f == pytest.approx(0.5714285714285715)


def test_precision_recall_f1_no_positives_is_zero():
    assert precision_recall_f1([1, 0, 1], [0, 0, 0]) == (0.0, 0.0, 0.0)


def test_meta_filtered_signal_requires_fire_and_confidence():
    out = meta_filtered_signal([1, 1, 0, 0], [0.9, 0.2, 0.9, 0.1], 0.5)
    assert out.tolist() == [1, 0, 0, 0]  # bar 2 not fired; bar 1 not confident


def test_evaluate_meta_improves_precision():
    verdict = evaluate_meta_labeling(_OUT, _SIG, _PROBA, meta_threshold=0.5, criterion="f1")
    assert verdict.precision_primary == pytest.approx(0.5)
    assert verdict.precision_meta == pytest.approx(1.0)  # meta kills the 2 false positives
    assert verdict.f1_meta == pytest.approx(0.8)
    assert verdict.improved is True


def test_evaluate_meta_precision_criterion():
    verdict = evaluate_meta_labeling(_OUT, _SIG, _PROBA, meta_threshold=0.5, criterion="precision")
    assert verdict.improved is True  # precision 0.5 -> 1.0 with recall still > 0


def test_evaluate_meta_no_improvement_when_filter_empties():
    # every meta proba below threshold -> meta acts never -> f1 0 < primary.
    verdict = evaluate_meta_labeling(_OUT, _SIG, [0.1] * 6, meta_threshold=0.5)
    assert verdict.f1_meta == 0.0
    assert verdict.improved is False


def test_run_meta_labeling_happy_path():
    train_x = np.array([[0.9], [0.8], [0.2], [0.1], [0.7], [0.3], [0.95], [0.05], [0.6], [0.4]])
    train_y = np.array([1, 1, 0, 0, 1, 0, 1, 0, 1, 0])
    test_x = np.array([[0.9], [0.1], [0.8], [0.2]])
    test_y = np.array([1, 0, 1, 0])
    result = run_meta_labeling(
        train_x, train_y, test_x, test_y,
        np.ones(10, int), np.ones(4, int), _stub_fit, min_fired_test=3,
    )
    assert result is not None
    verdict, predict = result
    assert verdict.improved is True
    assert verdict.precision_meta == pytest.approx(1.0)
    assert callable(predict)


def test_run_meta_labeling_thin_test_returns_none():
    x, y = np.ones((10, 1)), np.array([1, 0] * 5)
    assert (
        run_meta_labeling(x, y, x[:4], y[:4], np.ones(10, int), np.array([1, 0, 0, 0]), _stub_fit)
        is None
    )


def test_run_meta_labeling_single_class_returns_none():
    x = np.ones((10, 1))
    assert (
        run_meta_labeling(
            x, np.ones(10, int), x[:4], np.array([1, 0, 1, 0]),
            np.ones(10, int), np.ones(4, int), _stub_fit, min_fired_test=3,
        )
        is None
    )


def test_run_meta_labeling_weights_subset_to_fired():
    captured = {}

    def fit(x, y, w):
        captured["w_len"] = None if w is None else len(w)
        return lambda tx: np.full(len(tx), 0.9)

    train_x = np.arange(20, dtype=float).reshape(10, 2)
    train_y = np.array([1, 0, 1, 0, 1, 0, 1, 0, 1, 0])
    signal = np.array([1, 1, 1, 1, 1, 1, 1, 1, 0, 0])  # 8 fired
    run_meta_labeling(
        train_x, train_y, train_x[:4], train_y[:4], signal, np.ones(4, int),
        fit, weights=np.linspace(0.5, 1.0, 10), min_fired_test=3,
    )
    assert captured["w_len"] == 8  # weights subset to the fired training bars
