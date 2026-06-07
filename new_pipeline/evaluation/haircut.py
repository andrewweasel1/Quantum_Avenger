"""Haircut Sharpe Ratio & multiple-testing adjustment (Harvey & Liu).

Harvey & Liu (2015), "Backtesting" + "...and the Cross-Section of Expected
Returns". A Sharpe ratio that survived a search over ``n_trials`` candidates is
inflated by selection bias. We turn the reported Sharpe into a t-stat, convert
to a p-value, inflate that p-value for the multiplicity of trials (Bonferroni /
Holm / Benjamini-Hochberg-Yekutieli), then map the adjusted p-value back to a
"haircut" Sharpe — what is left once the multiple-testing discount is applied.
"""

import math
from dataclasses import dataclass

import numpy as np
from scipy import stats


def _harmonic(n: int) -> float:
    """c(N) = Σ_{i=1}^{N} 1/i — the BHY dependency-correction constant."""
    return float(np.sum(1.0 / np.arange(1, n + 1)))


def multiple_testing_adjust(p_values, method: str = "bhy") -> np.ndarray:
    """Adjusted p-values (original order) controlling for multiplicity.

    ``bonferroni`` / ``holm`` control the family-wise error rate; ``bhy``
    (Benjamini-Yekutieli) controls the FDR under arbitrary dependence.
    """
    p = np.asarray(p_values, dtype=np.float64)
    m = p.size
    if m == 0:
        return p
    method = method.lower()
    if method == "bonferroni":
        return np.minimum(p * m, 1.0)

    order = np.argsort(p)
    p_sorted = p[order]
    adj_sorted = np.empty(m)
    if method == "holm":  # step-down, enforce non-decreasing
        running = 0.0
        for k in range(m):  # rank k+1
            running = max(running, (m - k) * p_sorted[k])
            adj_sorted[k] = min(running, 1.0)
    elif method == "bhy":  # step-up with Σ1/i correction, non-decreasing from top
        c_m = _harmonic(m)
        running = 1.0
        for k in range(m - 1, -1, -1):  # rank k+1 from M down to 1
            running = min(running, c_m * m / (k + 1) * p_sorted[k])
            adj_sorted[k] = min(running, 1.0)
    else:
        raise ValueError(f"unknown method: {method!r}")

    adj = np.empty(m)
    adj[order] = adj_sorted
    return adj


def _single_test_pvalue_factor(n_trials: int, method: str) -> float:
    """Multiplier turning a single p-value into its rank-1 adjusted p-value."""
    method = method.lower()
    if method in ("bonferroni", "holm"):
        return float(n_trials)
    if method == "bhy":
        return n_trials * _harmonic(n_trials)
    raise ValueError(f"unknown method: {method!r}")


@dataclass
class HaircutResult:
    adjusted_sharpe: float
    haircut_fraction: float
    adjusted_pvalue: float
    observed_tstat: float
    adjusted_tstat: float


def haircut_sharpe_ratio(
    observed_sr: float,
    n_obs: int,
    n_trials: int,
    method: str = "bhy",
    periods_per_year: float = 252.0,
) -> HaircutResult:
    """Discount an annualized Sharpe for having been the best of ``n_trials``."""
    years = n_obs / periods_per_year
    if observed_sr <= 0.0 or years <= 0.0 or n_obs < 2:
        return HaircutResult(max(observed_sr, 0.0), 0.0, 1.0, 0.0, 0.0)

    t_stat = observed_sr * math.sqrt(years)
    p_single = 2.0 * (1.0 - stats.norm.cdf(t_stat))  # two-sided
    p_adj = min(p_single * _single_test_pvalue_factor(n_trials, method), 1.0)
    p_adj = min(max(p_adj, 1e-16), 1.0)
    t_adj = float(stats.norm.ppf(1.0 - p_adj / 2.0))

    ratio = max(t_adj / t_stat, 0.0)
    return HaircutResult(
        adjusted_sharpe=observed_sr * ratio,
        haircut_fraction=max(1.0 - ratio, 0.0),
        adjusted_pvalue=p_adj,
        observed_tstat=t_stat,
        adjusted_tstat=t_adj,
    )


def minimum_profit_hurdle(
    n_obs: int,
    n_trials: int,
    method: str = "bhy",
    significance: float = 0.05,
    periods_per_year: float = 252.0,
) -> float:
    """Minimum annualized Sharpe that stays significant after the adjustment."""
    years = n_obs / periods_per_year
    if years <= 0.0:
        return float("inf")
    p_single = significance / _single_test_pvalue_factor(n_trials, method)
    t_required = float(stats.norm.ppf(1.0 - p_single / 2.0))
    return t_required / math.sqrt(years)
