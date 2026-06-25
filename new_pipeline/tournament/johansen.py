"""Johansen multivariate cointegration (offense roadmap §C).

Engle-Granger (``stat_arb``) cointegrates a *pair*; Johansen finds cointegrating
relationships among an N-asset *basket* via the reduced-rank (VECM) eigenproblem.
The leading eigenvector is the most-cointegrating linear combination — the basket
weights that form the most stationary spread, optimal for N>2 where a single OLS
hedge ratio is not enough.

We use Johansen for the *vector* and confirm cointegration by testing the resulting
spread with the existing :func:`stat_arb.adf_tstat` — sidestepping the
deterministic-assumption-sensitive Johansen critical-value tables while reusing a
verified stationarity test. The trace statistic rides along as a diagnostic.

Self-contained (numpy ``lstsq`` + ``eig``); no statsmodels. See
``docs/quantitative_math.md`` Part II §C.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class JohansenResult:
    eigenvalues: np.ndarray  # descending (squared canonical correlations, in (0,1))
    eigenvectors: np.ndarray  # columns = cointegrating vectors, same order
    trace_statistic: float  # trace test for the null of no cointegration (r=0)


def johansen_test(prices, lags: int = 1) -> JohansenResult:
    """Reduced-rank VECM cointegration test on ``prices`` (T x N, a column per asset,
    unrestricted constant). Returns the eigenvalues, cointegrating vectors, and the
    r=0 trace statistic."""
    levels = np.asarray(prices, dtype=np.float64)
    t = levels.shape[0]
    diffs = np.diff(levels, axis=0)  # ΔY, (T-1) x N
    lagged_levels = levels[:-1]  # Y_{t-1}, (T-1) x N
    k = max(int(lags), 0)
    rows = (t - 1) - k
    response = diffs[k:]  # ΔY_t
    levels_lag = lagged_levels[k:]  # Y_{t-1}
    # Regressors: k lagged differences + a constant.
    regressors = [np.ones((rows, 1))]
    for i in range(1, k + 1):
        regressors.append(diffs[k - i : (t - 1) - i])
    design = np.hstack(regressors)

    def _residualize(target: np.ndarray) -> np.ndarray:
        coef, *_ = np.linalg.lstsq(design, target, rcond=None)
        return target - design @ coef

    r0 = _residualize(response)  # ΔY with short-run dynamics removed
    r1 = _residualize(levels_lag)  # Y_{t-1} with short-run dynamics removed
    s00 = r0.T @ r0 / rows
    s11 = r1.T @ r1 / rows
    s01 = r0.T @ r1 / rows
    # Eigenproblem inv(S11)·S10·inv(S00)·S01 -> squared canonical correlations + β.
    matrix = np.linalg.inv(s11) @ s01.T @ np.linalg.inv(s00) @ s01
    eigvals, eigvecs = np.linalg.eig(matrix)
    eigvals, eigvecs = np.real(eigvals), np.real(eigvecs)
    order = np.argsort(eigvals)[::-1]
    eigvals, eigvecs = eigvals[order], eigvecs[:, order]
    clipped = np.clip(eigvals, 1e-12, 1.0 - 1e-12)
    trace = float(-rows * np.sum(np.log(1.0 - clipped)))
    return JohansenResult(eigvals, eigvecs, trace)


def johansen_basket(prices, lags: int = 1) -> np.ndarray:
    """Leading cointegrating vector for ``prices``, normalized so its first weight is
    1 (the basket weights; ``spread = prices @ vector`` is the stationary combination)."""
    vector = johansen_test(prices, lags).eigenvectors[:, 0]
    return vector / vector[0] if vector[0] != 0.0 else vector
