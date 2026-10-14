import numpy as np
from new_pipeline.tournament.feature_selection import (
    cluster_features,
    select_orthogonal_features,
)


def test_cluster_groups_collinear_features():
    rng = np.random.default_rng(0)
    base = rng.normal(size=200)
    matrix = np.column_stack([base, base + rng.normal(0, 0.01, 200), rng.normal(size=200)])
    clusters = cluster_features(matrix, ["f0", "f1", "f2"], distance_threshold=0.5)
    assert sorted(len(c) for c in clusters) == [1, 2]  # f0+f1 together, f2 alone


def test_cluster_handles_exactly_two_features():
    # scipy.spearmanr returns a scalar for 2 columns; cluster_features must not crash.
    rng = np.random.default_rng(0)
    base = rng.normal(size=120)
    collinear = np.column_stack([base, base + rng.normal(0, 0.01, 120)])
    assert sorted(len(c) for c in cluster_features(collinear, ["f0", "f1"], 0.5)) == [2]
    independent = np.column_stack([rng.normal(size=120), rng.normal(size=120)])
    assert sorted(len(c) for c in cluster_features(independent, ["f0", "f1"], 0.5)) == [1, 1]


def test_select_prunes_unimportant_features():
    rng = np.random.default_rng(1)
    target = rng.normal(size=150)
    informative = target + rng.normal(0, 0.1, 150)
    matrix = np.column_stack([informative, rng.normal(size=150), rng.normal(size=150)])

    def score(candidate):
        return abs(float(np.corrcoef(candidate[:, 0], target)[0, 1]))

    kept = select_orthogonal_features(
        matrix, ["f0", "f1", "f2"], score, distance_threshold=0.5, min_importance=0.1, seed=0
    )
    assert kept == ["f0"]


def test_select_falls_back_to_all_when_nothing_clears_threshold():
    rng = np.random.default_rng(2)
    matrix = rng.normal(size=(80, 3))
    kept = select_orthogonal_features(
        matrix, ["a", "b", "c"], lambda _m: 1.0, min_importance=0.5, seed=0
    )
    assert kept == ["a", "b", "c"]  # constant score -> zero importance -> fallback
