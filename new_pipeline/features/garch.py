"""GARCH(1,1) conditional volatility (offense roadmap §D).

The range estimators in ``vol_estimators.py`` measure *realized* vol over a window;
GARCH models the *conditional* variance ``σ²ₜ = ω + α·ε²ₜ₋₁ + β·σ²ₜ₋₁``, capturing
volatility clustering and persistence. The parameters are fit once by Gaussian MLE on
an in-sample warmup window; the variance recursion then runs **causally forward** (each
``σ²ₜ`` uses only ``εₜ₋₁``, ``σ²ₜ₋₁``, and the past-fit parameters), so the feature is
leak-free over the post-warmup region (null during the warmup, like other rolling
features). A strict per-bar refit is a noted, far more expensive follow-up.

Self-contained (numpy + ``scipy.optimize``). See ``docs/quantitative_math.md`` Part II §D.
"""

import numpy as np
import polars as pl
from scipy.optimize import minimize

TRADING_DAYS = 252
GARCH_FEATURE_NAMES = ("garch_vol",)


def _conditional_variance(eps: np.ndarray, omega, alpha, beta) -> np.ndarray:
    sigma2 = np.empty(eps.size)
    sigma2[0] = eps.var() if eps.var() > 0.0 else 1e-6
    for t in range(1, eps.size):
        sigma2[t] = omega + alpha * eps[t - 1] ** 2 + beta * sigma2[t - 1]
    return np.maximum(sigma2, 1e-12)


def _neg_loglik(params, eps) -> float:
    omega, alpha, beta = params
    if omega <= 0.0 or alpha < 0.0 or beta < 0.0 or alpha + beta >= 1.0:
        return 1e10  # enforce positivity + covariance stationarity
    sigma2 = _conditional_variance(eps, omega, alpha, beta)
    return 0.5 * float(np.sum(np.log(sigma2) + eps**2 / sigma2))


def fit_garch(returns):
    """Fit GARCH(1,1) ``(ω, α, β)`` by Gaussian MLE; also returns the fitted mean ``μ``."""
    r = np.asarray(returns, dtype=np.float64)
    mu = float(r.mean())
    eps = r - mu
    var = float(eps.var()) if eps.var() > 0.0 else 1e-6
    result = minimize(
        _neg_loglik, x0=[0.1 * var, 0.1, 0.8], args=(eps,), method="Nelder-Mead",
        options={"xatol": 1e-10, "fatol": 1e-10, "maxiter": 2000},
    )
    omega, alpha, beta = result.x
    return float(omega), float(max(alpha, 0.0)), float(max(beta, 0.0)), mu


def garch_conditional_volatility(returns, fit_window=TRADING_DAYS, annualize=True) -> np.ndarray:
    """Causal GARCH(1,1) conditional volatility: fit on the first ``fit_window`` returns,
    then run the variance recursion forward. Null for ``t < fit_window`` (warmup)."""
    r = np.asarray(returns, dtype=np.float64)
    n = r.size
    out = np.full(n, np.nan)
    if n < fit_window + 2:
        return out
    omega, alpha, beta, mu = fit_garch(r[:fit_window])
    eps = r - mu
    scale = TRADING_DAYS if annualize else 1.0
    sigma2 = float(eps[:fit_window].var())
    for t in range(1, n):
        sigma2 = omega + alpha * eps[t - 1] ** 2 + beta * sigma2
        if t >= fit_window:
            out[t] = float(np.sqrt(max(sigma2, 0.0) * scale))
    return out


def add_garch(ticker_frame: pl.DataFrame, fit_window: int = TRADING_DAYS) -> pl.DataFrame:
    """Append ``garch_vol`` (annualized GARCH conditional vol) to one ticker's
    date-sorted frame, computed from its ``returns`` column."""
    returns = ticker_frame["returns"].fill_null(0.0).to_numpy()
    return ticker_frame.with_columns(
        pl.Series("garch_vol", garch_conditional_volatility(returns, fit_window))
    )
