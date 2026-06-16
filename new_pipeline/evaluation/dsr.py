"""Deflated & Probabilistic Sharpe Ratio (Bailey & López de Prado).

The Probabilistic Sharpe Ratio (PSR) is the probability the true Sharpe exceeds
a benchmark, adjusting for sample length and non-normal returns (skew + excess
kurtosis). The Deflated Sharpe Ratio (DSR) is PSR with the benchmark set to the
*expected maximum* Sharpe under ``n_trials`` skill-less strategies — i.e. it also
corrects for selection bias / multiple testing.

Note: the deflation term uses *non-excess* kurtosis (normal = 3).
"""

import math
from dataclasses import dataclass

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


@dataclass(frozen=True)
class DSRResult:
    """Rich Deflated-Sharpe report. ``dsr`` matches
    :func:`compute_deflated_sharpe_ratio` when ``trial_sharpes`` is supplied and
    ``n_trials == len(trial_sharpes)``; the rest are diagnostics. ``sr_annual`` is
    for human reporting only and never enters the test.
    """

    dsr: float                  # P(true SR > expected-max under the null), in [0, 1]
    psr_vs_zero: float          # PSR against benchmark 0
    sr_period: float            # native-frequency Sharpe used in the test
    sr_annual: float            # annualized Sharpe -- REPORTING ONLY
    sr0_period: float           # expected max SR under the null (deflation benchmark)
    n_obs: int
    n_trials: float             # may be fractional (effective number of trials)
    skew: float
    kurtosis: float             # non-excess (normal = 3)
    var_trial_sr: float
    used_fallback_variance: bool


def effective_number_of_trials(returns_matrix) -> float:
    """Effective trial count ``N_eff = N / (1 + (N-1)*r_bar)`` from the mean
    pairwise correlation ``r_bar`` of the trial OOS return streams (one trial per
    ROW). Grid-searched configs are correlated, so the raw trial count
    over-deflates the DSR; ``N_eff`` corrects it. ``r_bar`` is clamped to >= 0.
    """
    matrix = np.asarray(returns_matrix, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[0] < 2:
        return float(matrix.shape[0]) if matrix.ndim == 2 and matrix.shape[0] else 1.0
    n = matrix.shape[0]
    corr = np.corrcoef(matrix)
    off_diagonal = corr[~np.eye(n, dtype=bool)]
    off_diagonal = off_diagonal[np.isfinite(off_diagonal)]
    if off_diagonal.size == 0:
        return float(n)
    r_bar = float(np.clip(off_diagonal.mean(), 0.0, 1.0))
    return n / (1.0 + (n - 1) * r_bar)


def deflated_sharpe_report(
    returns,
    n_trials,
    trial_sharpes=None,
    periods_per_year: int = 252,
    min_obs: int = 30,
) -> DSRResult:
    """Full DSR report. ``n_trials`` is the (possibly effective) trial count that
    drives deflation; ``trial_sharpes`` (strongly preferred) supplies the
    cross-trial variance. Without trial Sharpes, falls back to the Lo (2002)
    asymptotic variance of a single Sharpe estimate. Samples shorter than
    ``min_obs`` return a 0.0 DSR rather than a misleading number.
    """
    series = np.asarray(returns, dtype=np.float64)
    series = series[~np.isnan(series)]
    n_obs = series.size
    sd = series.std(ddof=1) if n_obs > 1 else 0.0
    n_trials_f = float(max(n_trials, 1))

    if n_obs < max(min_obs, 3) or sd <= 0.0:
        return DSRResult(0.0, 0.0, 0.0, 0.0, 0.0, n_obs, n_trials_f, 0.0, 3.0, 0.0, True)

    sharpe, skew, kurtosis = _moments(series)
    sr_annual = sharpe * math.sqrt(periods_per_year)

    trials = None if trial_sharpes is None else np.asarray(trial_sharpes, dtype=np.float64)
    if trials is not None and trials.size > 1:
        var_trial = float(np.var(trials, ddof=1))
        used_fallback = False
    else:
        # Lo (2002): asymptotic variance of one Sharpe estimate under the null.
        var_trial = _deflation_term(sharpe, skew, kurtosis) / (n_obs - 1)
        used_fallback = True

    sr0 = expected_max_sharpe(var_trial, int(round(n_trials_f)))
    dsr = _psr_statistic(sharpe, skew, kurtosis, n_obs, sr0)
    psr0 = _psr_statistic(sharpe, skew, kurtosis, n_obs, 0.0)

    return DSRResult(
        dsr=dsr,
        psr_vs_zero=psr0,
        sr_period=sharpe,
        sr_annual=sr_annual,
        sr0_period=sr0,
        n_obs=n_obs,
        n_trials=n_trials_f,
        skew=skew,
        kurtosis=kurtosis,
        var_trial_sr=var_trial,
        used_fallback_variance=used_fallback,
    )
