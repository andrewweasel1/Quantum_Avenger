"""Clustered Feature Selection (CFS) — keep orthogonal alpha, drop redundancy.

Restores the legacy pruning step: Spearman correlation -> correlation distance
-> Ward hierarchical clustering groups collinear features; within each cluster we
keep the single feature whose permutation drops the out-of-sample score the most,
provided that drop clears ``min_importance``. This removes redundant inputs while
preserving genuinely independent signal.
"""

from collections.abc import Callable

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from scipy.stats import spearmanr


def cluster_features(
    feature_matrix: np.ndarray, feature_names: list[str], distance_threshold: float = 0.5
) -> list[list[str]]:
    """Group features into clusters by Ward linkage on correlation distance."""
    matrix = np.asarray(feature_matrix, dtype=np.float64)
    if matrix.shape[1] <= 1:
        return [list(feature_names)]
    corr = np.atleast_2d(spearmanr(matrix).statistic)
    corr = np.nan_to_num(corr, nan=0.0)
    distance = np.sqrt(np.clip(0.5 * (1.0 - corr), 0.0, None))
    np.fill_diagonal(distance, 0.0)
    linkage_matrix = linkage(squareform(distance, checks=False), method="ward")
    cluster_ids = fcluster(linkage_matrix, t=distance_threshold, criterion="distance")
    clusters: dict[int, list[str]] = {}
    for name, cluster_id in zip(feature_names, cluster_ids, strict=True):
        clusters.setdefault(int(cluster_id), []).append(name)
    return list(clusters.values())


def select_orthogonal_features(
    feature_matrix: np.ndarray,
    feature_names: list[str],
    score_fn: Callable[[np.ndarray], float],
    distance_threshold: float = 0.5,
    min_importance: float = 0.0,
    seed: int = 0,
) -> list[str]:
    """Return surviving feature names: best per cluster by permutation importance.

    ``score_fn`` maps a feature matrix to an out-of-sample score (e.g. Sharpe);
    a feature's importance is the score drop when its column is shuffled.
    Falls back to all features if nothing clears ``min_importance``.
    """
    matrix = np.asarray(feature_matrix, dtype=np.float64)
    names = list(feature_names)
    base_score = score_fn(matrix)
    rng = np.random.default_rng(seed)

    survivors: list[str] = []
    for cluster in cluster_features(matrix, names, distance_threshold):
        best_name, best_importance = None, -np.inf
        for name in cluster:
            column = names.index(name)
            permuted = matrix.copy()
            permuted[:, column] = rng.permutation(permuted[:, column])
            importance = base_score - score_fn(permuted)
            if importance > best_importance:
                best_name, best_importance = name, importance
        if best_name is not None and best_importance >= min_importance:
            survivors.append(best_name)

    return survivors or names
