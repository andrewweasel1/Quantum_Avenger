import numpy as np
import pytest
from new_pipeline.evaluation.cscv import cscv_partition_indices, cscv_splits, n_cscv_splits
from new_pipeline.evaluation.pbo import evaluate_cscv, probability_of_backtest_overfitting


def test_partition_count_and_coverage():
    assert n_cscv_splits(10) == 252  # C(10, 5)
    blocks = cscv_partition_indices(100, 10)
    assert len(blocks) == 10
    assert sum(b.size for b in blocks) == 100


def test_odd_partitions_rejected():
    with pytest.raises(ValueError):
        cscv_partition_indices(100, 5)


def test_splits_partition_the_axis():
    for is_idx, oos_idx in cscv_splits(60, 6):
        assert set(is_idx.tolist()).isdisjoint(oos_idx.tolist())
        assert np.array_equal(np.sort(np.concatenate([is_idx, oos_idx])), np.arange(60))


def test_pbo_low_for_genuine_skill():
    rng = np.random.default_rng(0)
    matrix = rng.normal(0.0, 0.01, size=(500, 12))
    matrix[:, 0] += 0.01  # one trial carries a persistent edge across every row
    assert probability_of_backtest_overfitting(matrix, n_partitions=10) < 0.2


def test_pbo_high_for_overfit_matrix():
    rng = np.random.default_rng(1)
    matrix = rng.normal(0.0, 0.01, size=(500, 40))
    matrix -= matrix.mean(axis=0, keepdims=True)  # zero true edge -> IS gains revert OOS
    result = evaluate_cscv(matrix, n_partitions=10)
    assert result.pbo > 0.8
    assert result.performance_degradation < 0.0
    assert result.n_splits == 252


def test_degenerate_matrices_are_safe():
    assert probability_of_backtest_overfitting(np.zeros((4, 1))) == 0.0  # single trial
    assert probability_of_backtest_overfitting(np.zeros((1, 5))) == 0.0  # too few observations
