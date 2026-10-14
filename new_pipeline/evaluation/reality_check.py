"""Data-snooping reality checks across many strategies (offense roadmap P4, §J).

White's Reality Check (2000) and Hansen's SPA (2005): when the *best* of K searched
strategies looks profitable, is that genuine or just the luckiest draw from the
search? Both bootstrap the strategies' joint performance — a **shared** stationary
block bootstrap over the common time index (so cross-strategy dependence is kept) —
to produce a multiple-testing-aware p-value for "the best strategy beats the
benchmark". This complements PBO/DSR (which guard a single chosen champion) with a
guard over the *whole trial set* the grid search examined.

Reuses ``hmm_gauntlet.stationary_bootstrap_indices``. See ``docs/quantitative_math.md``
Part II §J.
"""

import numpy as np

from new_pipeline.core.seeding import active_seed
from new_pipeline.evaluation.hmm_gauntlet import stationary_bootstrap_indices


def _as_matrix(strategy_returns) -> np.ndarray:
    matrix = np.asarray(strategy_returns, dtype=np.float64)
    return matrix.reshape(-1, 1) if matrix.ndim == 1 else matrix


def whites_reality_check(
    strategy_returns, n_bootstrap=500, avg_block=10, benchmark=0.0, seed=None
) -> float:
    """White's Reality Check p-value for H0: the best strategy does *not* beat the
    benchmark. ``strategy_returns`` is ``(T, K)`` (a column per strategy). A small
    p-value ⇒ the best strategy's edge survives the multiplicity of the K searched.
    """
    returns = _as_matrix(strategy_returns)
    t = returns.shape[0]
    if t < 2 or returns.shape[1] < 1:
        return 1.0
    mean = returns.mean(axis=0)
    v = np.sqrt(t) * float((mean - benchmark).max())
    rng = np.random.default_rng(active_seed() if seed is None else seed)
    exceed = 0
    for _ in range(n_bootstrap):
        idx = stationary_bootstrap_indices(t, t, avg_block, rng)
        v_star = np.sqrt(t) * float((returns[idx].mean(axis=0) - mean).max())  # benchmark cancels
        if v_star >= v:
            exceed += 1
    return (exceed + 1) / (n_bootstrap + 1)  # +1 smoothing: never report exactly 0


def hansens_spa(
    strategy_returns, n_bootstrap=500, avg_block=10, benchmark=0.0, seed=None
) -> float:
    """Hansen's SPA *consistent* p-value for H0: no strategy beats the benchmark.

    Studentizes each strategy's average performance and recenters the bootstrap so
    that strategies which are significantly poor (very negative t-stat) are dropped
    from the null — sharper than White's RC, which a single bad strategy can dilute.
    Variance uses the i.i.d. plug-in std; the stationary bootstrap carries the
    dependence in the resampled distribution.
    """
    returns = _as_matrix(strategy_returns)
    t, k = returns.shape
    if t < 3 or k < 1:
        return 1.0
    d = returns - benchmark
    mean = d.mean(axis=0)
    std = d.std(axis=0, ddof=1)
    safe_std = np.where(std > 0.0, std, np.inf)  # zero-variance strategy -> excluded
    z = np.sqrt(t) * mean / safe_std
    t_spa = max(float(z.max()), 0.0)
    # consistent recentering: keep mean_k unless its t-stat is significantly negative.
    keep = z >= -np.sqrt(2.0 * np.log(np.log(t)))
    recenter = np.where(keep, mean, 0.0)
    rng = np.random.default_rng(active_seed() if seed is None else seed)
    exceed = 0
    for _ in range(n_bootstrap):
        idx = stationary_bootstrap_indices(t, t, avg_block, rng)
        z_star = np.sqrt(t) * (d[idx].mean(axis=0) - recenter) / safe_std
        if max(float(z_star.max()), 0.0) >= t_spa:
            exceed += 1
    return (exceed + 1) / (n_bootstrap + 1)
