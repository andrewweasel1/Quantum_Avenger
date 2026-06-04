"""Deflated Sharpe Ratio (Bailey & López de Prado).

Adjusts an observed Sharpe for (a) the number of trials explored, (b) sample
length, and (c) non-normal returns (skewness + kurtosis). The result is a
probability in [0, 1]; the promotion gate fires at >= 0.95.

Note: the deflation term uses *non-excess* kurtosis (normal = 3), correcting a
sign/units slip in the legacy reference implementation.
"""

import math

import numpy as np
from scipy import stats

EULER_MASCHERONI = 0.5772156649


def expected_max_sharpe(var_trials: float, n_trials: int) -> float:
    """E[max SR] under the null of zero true skill across ``n_trials``."""
    if n_trials < 2 or var_trials <= 0.0:
        return 0.0
    sigma = math.sqrt(var_trials)
    z_high = stats.norm.ppf(1.0 - 1.0 / n_trials)
    z_low = stats.norm.ppf(1.0 - 1.0 / (n_trials * math.e))
    return sigma * ((1.0 - EULER_MASCHERONI) * z_high + EULER_MASCHERONI * z_low)


def compute_deflated_sharpe_ratio(returns, trial_sharpes) -> float:
    """Probability the strategy's true Sharpe beats the null. Returns 0..1."""
    series = np.asarray(returns, dtype=np.float64)
    if series.size < 3:
        return 0.0
    std = series.std(ddof=1)
    if std <= 0.0:
        return 0.0
    sharpe = series.mean() / std
    skew = float(stats.skew(series))
    kurtosis = float(stats.kurtosis(series, fisher=False))  # non-excess (normal = 3)
    trials = np.asarray(trial_sharpes, dtype=np.float64)
    var_trials = float(np.var(trials, ddof=1)) if trials.size > 1 else 0.0
    sr0 = expected_max_sharpe(var_trials, trials.size)
    denominator = math.sqrt(
        max(1e-12, 1.0 - skew * sharpe + (kurtosis - 1.0) / 4.0 * sharpe**2)
    )
    statistic = (sharpe - sr0) * math.sqrt(series.size - 1) / denominator
    return float(stats.norm.cdf(statistic))


def interpret_dsr(dsr: float, threshold: float = 0.95) -> str:
    if dsr < 0.5:
        return "overfit"
    if dsr < threshold:
        return "insignificant"
    return "promote"
