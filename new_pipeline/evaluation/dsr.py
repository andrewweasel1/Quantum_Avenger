"""Deflated & Probabilistic Sharpe Ratio (Bailey & López de Prado).

The Probabilistic Sharpe Ratio (PSR) is the probability the true Sharpe exceeds
a benchmark, adjusting for sample length and non-normal returns (skew + excess
kurtosis). The Deflated Sharpe Ratio (DSR) is PSR with the benchmark set to the
*expected maximum* Sharpe under ``n_trials`` skill-less strategies — i.e. it also
corrects for selection bias / multiple testing.

Note: the deflation term uses *non-excess* kurtosis (normal = 3).
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


def _moments(series: np.ndarray):
    sharpe = series.mean() / series.std(ddof=1)
    skew = float(stats.skew(series))
    kurtosis = float(stats.kurtosis(series, fisher=False))  # non-excess (normal = 3)
    return sharpe, skew, kurtosis


def _deflation_term(sharpe: float, skew: float, kurtosis: float) -> float:
    """1 - γ₃·SR + (γ₄-1)/4·SR² — the variance factor of the SR estimator."""
    return 1.0 - skew * sharpe + (kurtosis - 1.0) / 4.0 * sharpe**2


def _psr_statistic(sharpe, skew, kurtosis, n_obs, benchmark_sr) -> float:
    denominator = math.sqrt(max(1e-12, _deflation_term(sharpe, skew, kurtosis)))
    return float(stats.norm.cdf((sharpe - benchmark_sr) * math.sqrt(n_obs - 1) / denominator))


def probabilistic_sharpe_ratio(returns, benchmark_sr: float = 0.0) -> float:
    """Probability the true (per-observation) Sharpe exceeds ``benchmark_sr``."""
    series = np.asarray(returns, dtype=np.float64)
    if series.size < 3 or series.std(ddof=1) <= 0.0:
        return 0.0
    return _psr_statistic(*_moments(series), series.size, benchmark_sr)


def min_track_record_length(returns, benchmark_sr: float = 0.0, prob: float = 0.95) -> float:
    """Minimum observations for PSR(benchmark_sr) to reach ``prob`` confidence."""
    series = np.asarray(returns, dtype=np.float64)
    if series.size < 3 or series.std(ddof=1) <= 0.0:
        return float("inf")
    sharpe, skew, kurtosis = _moments(series)
    if sharpe <= benchmark_sr:
        return float("inf")
    z = stats.norm.ppf(prob)
    return 1.0 + _deflation_term(sharpe, skew, kurtosis) * (z / (sharpe - benchmark_sr)) ** 2


def compute_deflated_sharpe_ratio(returns, trial_sharpes) -> float:
    """Probability the strategy's true Sharpe beats the expected max under the
    null of ``len(trial_sharpes)`` skill-less trials. Returns 0..1."""
    series = np.asarray(returns, dtype=np.float64)
    if series.size < 3 or series.std(ddof=1) <= 0.0:
        return 0.0
    trials = np.asarray(trial_sharpes, dtype=np.float64)
    var_trials = float(np.var(trials, ddof=1)) if trials.size > 1 else 0.0
    sr0 = expected_max_sharpe(var_trials, trials.size)
    return _psr_statistic(*_moments(series), series.size, sr0)


def interpret_dsr(dsr: float, threshold: float = 0.95) -> str:
    if dsr < 0.5:
        return "overfit"
    if dsr < threshold:
        return "insignificant"
    return "promote"
