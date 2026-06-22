"""Causal feature selection — Granger directional screen + purged-CPCV MDA.

Two stages replace the purely associational clustered-permutation selector:

* **Stage A (causal screen):** a hand-rolled Granger F-test of each feature
  ``x_j -> fwd_ret`` controlling for the target's own lags, Benjamini-Yekutieli
  FDR-corrected across features. This keeps only features that *lead* the forward
  return, killing spurious contemporaneous correlations and pure-autocorrelation
  artifacts. ``fwd_ret`` over ``horizon`` bars is serially overlapping, so the
  F-test is deflated to an effective sample size ``n_eff = rows / horizon``
  (deterministic, conservative; reduces to the standard test at ``horizon=1``).
* **Stage B (robust redundancy):** Ward-cluster the survivors (reusing
  :func:`feature_selection.cluster_features`) and keep, per cluster, the feature
  with the highest mean-decrease-accuracy averaged across the *purged* CPCV folds
  — replacing today's single-split, un-purged permutation importance.

Granger gives direction/causality (but is linear-in-mean and silent on
redundancy); purged-CPCV MDA gives robust, nonlinear, model-faithful,
leakage-purged importance (but is associational). The hybrid upgrades both. Pure
numpy/scipy + the existing BHY adjuster; deterministic and offline.
"""

import numpy as np
from scipy import stats

from new_pipeline.evaluation.haircut import multiple_testing_adjust


def _ols_rss(design: np.ndarray, response: np.ndarray) -> tuple[float, int]:
    """Residual sum of squares + design rank from a least-squares fit."""
    coef, _residuals, rank, _sv = np.linalg.lstsq(design, response, rcond=None)
    resid = response - design @ coef
    return float(resid @ resid), int(rank)


def granger_pvalue(feature, target, lags: int = 3, horizon: int = 1) -> float:
    """F-test p-value that ``feature`` Granger-causes ``target``.

    Restricted model regresses ``target[t]`` on a constant + its own ``lags``;
    the unrestricted model adds the feature's ``lags``. Returns ``1.0`` (no
    causal contribution) for too-few samples or rank-deficient/degenerate designs
    rather than raising.
    """
    x = np.nan_to_num(np.asarray(feature, dtype=np.float64), nan=0.0)
    y = np.nan_to_num(np.asarray(target, dtype=np.float64), nan=0.0)
    n = y.size
    lag = int(lags)
    horizon = max(int(horizon), 1)
    if lag < 1 or x.size != n or n <= 2 * lag + 2:
        return 1.0

    rows = n - lag
    response = y[lag:]

    def _lagmat(series: np.ndarray) -> np.ndarray:  # column j = series[t-1-j]
        return np.column_stack([series[lag - 1 - j : n - 1 - j] for j in range(lag)])

    const = np.ones((rows, 1))
    target_lags = _lagmat(y)
    design_r = np.hstack([const, target_lags])
    design_u = np.hstack([const, target_lags, _lagmat(x)])

    rss_r, _ = _ols_rss(design_r, response)
    rss_u, rank_u = _ols_rss(design_u, response)
    if rank_u < design_u.shape[1] or rss_u <= 1e-12 or rss_r <= rss_u:
        return 1.0

    df1 = float(lag)
    df2 = rows / horizon - (2 * lag + 1)  # overlap-deflated effective denominator df
    if df2 < 1.0:
        return 1.0
    f_stat = ((rss_r - rss_u) / df1) / (rss_u / df2)
    return float(stats.f.sf(f_stat, df1, df2))


def granger_screen(
    feature_matrix,
    feature_names: list[str],
    target,
    lags: int = 3,
    horizon: int = 1,
    alpha: float = 0.10,
    mt_method: str = "bhy",
) -> tuple[list[str], dict[str, float]]:
    """Return (survivors, {name: BHY-adjusted p-value}) for the Granger screen.

    Features whose adjusted p-value is below ``alpha`` survive; the adjuster is
    the shared :func:`evaluation.haircut.multiple_testing_adjust` (BHY controls
    the FDR under arbitrary dependence between feature tests).
    """
    matrix = np.asarray(feature_matrix, dtype=np.float64)
    names = list(feature_names)
    pvalues = np.array(
        [granger_pvalue(matrix[:, j], target, lags, horizon) for j in range(matrix.shape[1])]
    )
    adjusted = multiple_testing_adjust(pvalues, method=mt_method)
    adjusted_map = {name: float(adjusted[j]) for j, name in enumerate(names)}
    survivors = [name for j, name in enumerate(names) if adjusted[j] < alpha]
    return survivors, adjusted_map
