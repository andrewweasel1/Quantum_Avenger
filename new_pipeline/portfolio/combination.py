"""Combine many sleeve return streams into one book (offense roadmap P4, §H).

Each sleeve (a per-sector directional champion, a factor sleeve, a stat-arb book)
is a return stream; this layer cleans their covariance and allocates capital across
them — Hierarchical Risk Parity (default), inverse-variance, or equal-weight — then
returns the weights and the combined book series.

NOTE on alignment: a valid cross-sleeve covariance (and book series) requires the
streams to be **calendar-aligned**. HRP/inverse-variance here assume a synchronized
panel ``(T x K)``. The current per-sector champions are only approximately
contemporaneous, so the pipeline combines them as a best-effort diagnostic;
date-indexed sleeves (P5) make the combination exact. See ``OFFENSE_ROADMAP.md`` P4.
"""

import numpy as np

from new_pipeline.portfolio.covariance import clean_covariance
from new_pipeline.portfolio.hrp import hrp_weights, inverse_variance_weights


def portfolio_weights(returns_matrix, method="hrp", cov_method="rmt", min_obs=20):
    """Allocation weights across the K columns (sleeves) of ``returns_matrix`` (T x K).

    ``method``: ``"hrp"`` | ``"inverse_variance"`` | ``"equal"``; ``cov_method`` is
    passed to :func:`clean_covariance` (ignored by ``"equal"``).
    """
    matrix = np.asarray(returns_matrix, dtype=np.float64)
    if matrix.ndim != 2:
        matrix = matrix.reshape(-1, 1)
    k = matrix.shape[1]
    if k == 1:
        return np.ones(1)
    if method == "equal":
        return np.full(k, 1.0 / k)
    # Drop flat (zero-variance) sleeves — a dead return stream is not a strategy, and
    # HRP would otherwise route all weight to it as the "lowest-risk" asset.
    active = matrix.var(axis=0) > 0.0
    if active.sum() <= 1:
        weights = np.zeros(k)
        weights[np.argmax(active) if active.any() else 0] = 1.0
        return weights
    cov = clean_covariance(matrix[:, active], cov_method, min_obs)
    sub = inverse_variance_weights(cov) if method == "inverse_variance" else hrp_weights(cov)
    weights = np.zeros(k)
    weights[active] = sub
    return weights


def combine_returns(returns_matrix, method="hrp", cov_method="rmt", min_obs=20):
    """Allocate across sleeves and return ``(weights, book_returns)``.

    ``book_returns = returns_matrix @ weights`` — the combined per-period book series.
    """
    matrix = np.asarray(returns_matrix, dtype=np.float64)
    if matrix.ndim != 2:
        matrix = matrix.reshape(-1, 1)
    weights = portfolio_weights(matrix, method, cov_method, min_obs)
    return weights, matrix @ weights
