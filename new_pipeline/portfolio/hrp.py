"""Hierarchical Risk Parity weights (offense roadmap P4, §H).

López de Prado's HRP allocates risk down a correlation-clustered tree instead of
inverting a noisy covariance: (1) single-linkage cluster on the correlation
distance ``√((1-ρ)/2)``, (2) quasi-diagonalize (seriate so similar assets sit
adjacent), (3) recursively bisect, splitting capital between the two halves in
inverse proportion to each half's inverse-variance cluster variance. No matrix
inversion ⇒ robust to the ill-conditioned covariances that wreck mean-variance.

See ``docs/quantitative_math.md`` Part II §H.
"""

import numpy as np
from scipy.cluster.hierarchy import linkage
from scipy.spatial.distance import squareform

from new_pipeline.portfolio.covariance import cov_to_corr


def inverse_variance_weights(cov):
    """Inverse-variance portfolio weights (diagonal only — no correlation).

    Zero-variance sleeves (a flat return stream) get zero weight rather than
    poisoning the book with ``1/0 = inf`` → NaN; an all-flat set falls back to equal.
    """
    diag = np.diag(np.asarray(cov, dtype=np.float64))
    ivp = np.where(diag > 0.0, 1.0 / np.where(diag > 0.0, diag, 1.0), 0.0)
    total = ivp.sum()
    return ivp / total if total > 0.0 else np.full(ivp.size, 1.0 / ivp.size)


def _quasi_diag(link, n_items):
    """Leaf order from a linkage tree: expand each merged cluster into its children
    until only original items (< ``n_items``) remain."""
    order = [int(link[-1, 0]), int(link[-1, 1])]
    while max(order) >= n_items:
        expanded = []
        for node in order:
            if node < n_items:
                expanded.append(node)
            else:
                merge = link[node - n_items]
                expanded.extend((int(merge[0]), int(merge[1])))
        order = expanded
    return order


def _cluster_variance(cov, items):
    """Variance of the inverse-variance portfolio over a sub-cluster of ``items``."""
    sub = cov[np.ix_(items, items)]
    weights = inverse_variance_weights(sub)
    return float(weights @ sub @ weights)


def _recursive_bisection(cov, order):
    weights = np.ones(cov.shape[0])
    clusters = [list(order)]
    while clusters:
        nxt = []
        for cluster in clusters:
            if len(cluster) <= 1:
                continue
            half = len(cluster) // 2
            left, right = cluster[:half], cluster[half:]
            var_left, var_right = _cluster_variance(cov, left), _cluster_variance(cov, right)
            alpha = 1.0 - var_left / (var_left + var_right)  # less variance -> more weight
            for i in left:
                weights[i] *= alpha
            for i in right:
                weights[i] *= 1.0 - alpha
            nxt.extend((left, right))
        clusters = nxt
    return weights


def hrp_weights(cov):
    """Hierarchical Risk Parity weights for the assets of covariance ``cov`` (in its
    own row/column order). Sums to 1; degenerate sizes handled (0 -> empty, 1 -> [1])."""
    cov = np.asarray(cov, dtype=np.float64)
    n = cov.shape[0]
    if n == 0:
        return np.zeros(0)
    if n == 1:
        return np.ones(1)
    corr, _ = cov_to_corr(cov)
    distance = np.sqrt(np.clip((1.0 - corr) / 2.0, 0.0, None))
    link = linkage(squareform(distance, checks=False), method="single")
    order = _quasi_diag(link, n)
    return _recursive_bisection(cov, order)
