import numpy as np
import pytest
from new_pipeline.tournament.sample_weights import (
    average_uniqueness,
    get_concurrency,
    sequential_bootstrap,
    uniqueness_sample_weights,
)


def test_non_overlapping_labels_are_fully_unique():
    t1 = np.arange(8)  # each label spans only its own bar
    assert get_concurrency(t1).tolist() == [1.0] * 8
    assert average_uniqueness(t1).tolist() == [1.0] * 8
    assert uniqueness_sample_weights(t1).tolist() == [1.0] * 8


def test_concurrency_counts_live_labels():
    # All four labels run to the last bar -> concurrency ramps 1,2,3,4.
    t1 = np.array([3, 3, 3, 3])
    assert get_concurrency(t1).tolist() == [1.0, 2.0, 3.0, 4.0]


def test_overlap_downweights_crowded_later_labels():
    t1 = np.array([3, 3, 3, 3])
    weights = uniqueness_sample_weights(t1)
    assert weights.mean() == pytest.approx(1.0)  # normalized
    # Earlier label spans the lightly-concurrent bars -> strictly higher weight.
    assert weights[0] > weights[1] > weights[2] > weights[3]


def test_average_uniqueness_golden():
    t1 = np.array([3, 3, 3, 3])
    np.testing.assert_allclose(
        average_uniqueness(t1),
        [0.52083333333333, 0.36111111111111, 0.29166666666667, 0.25],
        atol=1e-11,
    )


def test_sequential_bootstrap_is_deterministic_and_favours_unique():
    # obs 0 is isolated (very unique); obs 1..5 heavily overlap on [1,5].
    t1 = np.array([0, 5, 5, 5, 5, 5])
    first = sequential_bootstrap(t1, size=600, seed=0)
    second = sequential_bootstrap(t1, size=600, seed=0)
    assert np.array_equal(first, second)  # determinism
    assert first.shape == (600,)
    assert set(first.tolist()) <= set(range(6))
    # the isolated observation is drawn more than its uniform 1/6 share
    assert np.mean(first == 0) > 1.0 / 6.0
