"""Nested Clustered Optimization (offense roadmap §H).

López de Prado's NCO tames the instability of direct mean-variance optimization on a
noisy covariance: cluster the assets, find minimum-variance weights *within* each
cluster (inverting only the small, well-conditioned cluster sub-covariances), reduce
each cluster to one synthetic asset, find minimum-variance weights *across* the
reduced clusters, and multiply. Far more stable than inverting the full covariance.

Minimum-variance is unconstrained, so NCO weights can be negative (a short sleeve);
they still sum to 1. See ``docs/quantitative_math.md`` Part II §H.
"""

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform

from new_pipeline.portfolio.covariance import cov_to_corr


def _min_variance_weights(cov) -> np.ndarray:
    """Unconstrained minimum-variance weights ``inv(Σ)·1 / (1ᵀ·inv(Σ)·1)`` (pinv for
    stability); falls back to equal weight if the system is degenerate."""
    cov = np.asarray(cov, dtype=np.float64)
    raw = np.linalg.pinv(cov) @ np.ones(cov.shape[0])
    total = raw.sum()
    return raw / total if abs(total) > 1e-12 else np.full(cov.shape[0], 1.0 / cov.shape[0])


def _cluster_labels(cov) -> np.ndarray:
    """Single-linkage clusters on the correlation distance, cut at the largest gap in
    the merge heights (a dependency-free elbow)."""
    n = cov.shape[0]
    corr, _ = cov_to_corr(cov)
    distance = np.sqrt(np.clip((1.0 - corr) / 2.0, 0.0, None))
    link = linkage(squareform(distance, checks=False), method="single")
    gaps = np.diff(link[:, 2])
    k = int(n - 1 - np.argmax(gaps)) if gaps.size else 1
    return fcluster(link, t=max(1, min(k, n)), criterion="maxclust")


def nco_weights(cov) -> np.ndarray:
    """NCO minimum-variance weights for assets of covariance ``cov`` (sums to 1)."""
    cov = np.asarray(cov, dtype=np.float64)
    n = cov.shape[0]
    if n <= 1:
        return np.ones(n)
    labels = _cluster_labels(cov)
    clusters = [np.where(labels == c)[0] for c in np.unique(labels)]
    intra = np.zeros(n)
    cluster_weights = []
    for items in clusters:
        w = _min_variance_weights(cov[np.ix_(items, items)])
        intra[items] = w
        cluster_weights.append(w)
    # reduce each cluster to one synthetic asset, then optimize across clusters.
    reduced = np.zeros((len(clusters), len(clusters)))
    for i, (ci, wi) in enumerate(zip(clusters, cluster_weights, strict=True)):
        for j, (cj, wj) in enumerate(zip(clusters, cluster_weights, strict=True)):
            reduced[i, j] = wi @ cov[np.ix_(ci, cj)] @ wj
    inter = _min_variance_weights(reduced)
    weights = np.zeros(n)
    for cluster_idx, items in enumerate(clusters):
        weights[items] = intra[items] * inter[cluster_idx]
    return weights
