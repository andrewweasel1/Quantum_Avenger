"""Covariance cleaning for portfolio construction (offense roadmap P4, §F/§H).

A sample covariance estimated from few observations is dominated by noise — its
small eigenvalues are unreliable and wreck any optimizer that inverts it. Two
standard cleaners:

* **RMT / Marchenko–Pastur denoising** (López de Prado): eigenvalues below the MP
  noise edge ``λ+ = (1 + √(N/T))²`` are replaced by their average (constant
  residual), keeping the signal eigenvalues — a dep-free, canonical denoiser.
* **Ledoit–Wolf shrinkage**: shrink the sample covariance toward a structured
  target; delegated to the battle-tested ``sklearn`` implementation (lazy import).

See ``docs/quantitative_math.md`` Part II §F/§H.
"""

import numpy as np


def cov_to_corr(cov):
    """Covariance -> (correlation, std-devs), with numerical clipping to [-1, 1]."""
    std = np.sqrt(np.diag(cov))
    safe = np.where(std > 0.0, std, 1.0)
    corr = cov / np.outer(safe, safe)
    return np.clip(corr, -1.0, 1.0), std


def corr_to_cov(corr, std):
    """Correlation + std-devs -> covariance."""
    return corr * np.outer(std, std)


def marchenko_pastur_max_eigenvalue(n_vars, n_obs) -> float:
    """Upper edge of the Marchenko–Pastur noise band for a correlation matrix
    (unit variance): ``λ+ = (1 + √(N/T))²``."""
    return float((1.0 + np.sqrt(n_vars / n_obs)) ** 2)


def denoise_covariance(cov, n_obs):
    """RMT constant-residual denoising: average the sub-MP-edge (noise) eigenvalues.

    Needs ``n_obs > n_vars`` for a meaningful edge; otherwise the input is returned
    unchanged. The top factor is always kept even if no eigenvalue clears the edge.
    """
    cov = np.asarray(cov, dtype=np.float64)
    n = cov.shape[0]
    if n < 2 or n_obs <= n:
        return cov
    corr, std = cov_to_corr(cov)
    eigvals, eigvecs = np.linalg.eigh(corr)
    order = np.argsort(eigvals)[::-1]  # descending: signal first
    eigvals, eigvecs = eigvals[order], eigvecs[:, order]
    lambda_max = marchenko_pastur_max_eigenvalue(n, n_obs)
    n_factors = max(int(np.sum(eigvals > lambda_max)), 1)
    if n_factors < n:
        eigvals = eigvals.copy()
        eigvals[n_factors:] = eigvals[n_factors:].mean()
    denoised_corr = eigvecs @ np.diag(eigvals) @ eigvecs.T
    scale = np.sqrt(np.diag(denoised_corr))  # rescale to a unit diagonal
    denoised_corr = denoised_corr / np.outer(scale, scale)
    return corr_to_cov(denoised_corr, std)


def ledoit_wolf_covariance(returns):
    """Ledoit–Wolf shrunk covariance of ``returns`` (T x N), via scikit-learn."""
    try:
        from sklearn.covariance import ledoit_wolf
    except ImportError as exc:  # pragma: no cover - sklearn ships with hmmlearn
        raise ImportError("Ledoit-Wolf shrinkage requires scikit-learn") from exc
    cov, _ = ledoit_wolf(np.asarray(returns, dtype=np.float64))
    return cov


def clean_covariance(returns, method="rmt", min_obs=20):
    """Sample covariance of ``returns`` (T x N), optionally cleaned.

    ``method``: ``"rmt"`` (Marchenko–Pastur denoise, when T > N), ``"ledoit_wolf"``
    (shrinkage), or ``"sample"`` (raw). Falls back to the raw sample covariance when
    there are too few observations to denoise.
    """
    matrix = np.asarray(returns, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[1] < 2:
        return np.atleast_2d(np.cov(matrix, rowvar=False))
    t, n = matrix.shape
    if method == "ledoit_wolf":
        return ledoit_wolf_covariance(matrix)
    cov = np.cov(matrix, rowvar=False)
    if method == "rmt" and t > n and t >= min_obs:
        return denoise_covariance(cov, t)
    return cov
