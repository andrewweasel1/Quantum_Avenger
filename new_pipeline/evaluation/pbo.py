"""Probability of Backtest Overfitting (PBO) via CSCV.

Bailey, Borwein, López de Prado & Zhu (2014). Over every CSCV in-sample /
out-of-sample split we pick the trial that looks best in-sample and ask where it
ranks out-of-sample. If skill is real the IS winner keeps winning OOS; if the
backtest is overfit the IS winner is no better than a coin flip OOS, so its OOS
rank lands below the median. PBO is the fraction of splits where the IS-best
configuration underperforms the OOS median (rank logit <= 0).

Pure NumPy over the ``(n_obs, n_trials)`` matrix the tournament already emits.
"""

from dataclasses import dataclass

import numpy as np

from new_pipeline.evaluation.cscv import cscv_splits


def _sharpe_per_trial(block: np.ndarray) -> np.ndarray:
    """Column-wise Sharpe of a ``(n_obs, n_trials)`` block (0 rf, unscaled).

    Ranking is invariant to the annualization factor, so we skip the √periods
    term that ``simulator.sharpe_ratio`` applies — only the cross-trial order
    matters here.
    """
    mean = block.mean(axis=0)
    std = block.std(axis=0, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(std > 0.0, mean / std, 0.0)


def _even_partitions(n_obs: int, n_partitions: int) -> int:
    """Largest usable even partition count <= request and <= n_obs (0 if none)."""
    usable = min(n_partitions, n_obs)
    if usable % 2 != 0:
        usable -= 1
    return usable if usable >= 2 else 0


@dataclass
class CSCVResult:
    pbo: float
    probability_of_loss: float
    performance_degradation: float
    n_splits: int


def evaluate_cscv(returns_matrix, n_partitions: int = 10, score_fn=None) -> CSCVResult:
    """Run CSCV over the matrix and return PBO + degradation diagnostics."""
    matrix = np.asarray(returns_matrix, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[1] < 2:
        return CSCVResult(0.0, 0.0, 0.0, 0)
    partitions = _even_partitions(matrix.shape[0], n_partitions)
    if partitions == 0:
        return CSCVResult(0.0, 0.0, 0.0, 0)

    score = score_fn or _sharpe_per_trial
    n_trials = matrix.shape[1]
    logits, is_best, oos_best = [], [], []
    for is_index, oos_index in cscv_splits(matrix.shape[0], partitions):
        is_perf = score(matrix[is_index])
        oos_perf = score(matrix[oos_index])
        best = int(np.argmax(is_perf))
        # Relative OOS rank of the IS-best trial in (0, 1); rank 1..N -> /(N+1).
        rank = float(np.sum(oos_perf <= oos_perf[best])) / (n_trials + 1)
        rank = min(max(rank, 1e-9), 1.0 - 1e-9)
        logits.append(np.log(rank / (1.0 - rank)))
        is_best.append(is_perf[best])
        oos_best.append(oos_perf[best])

    logits = np.asarray(logits)
    is_best = np.asarray(is_best)
    oos_best = np.asarray(oos_best)
    pbo = float(np.mean(logits <= 0.0))
    prob_loss = float(np.mean(oos_best < 0.0))
    degradation = _degradation_slope(is_best, oos_best)
    return CSCVResult(pbo, prob_loss, degradation, logits.size)


def _degradation_slope(is_best: np.ndarray, oos_best: np.ndarray) -> float:
    """Slope of OOS-on-IS performance for the selected trials (<0 = decay)."""
    if is_best.size < 2 or np.ptp(is_best) == 0.0:
        return 0.0
    return float(np.polyfit(is_best, oos_best, 1)[0])


def probability_of_backtest_overfitting(
    returns_matrix, n_partitions: int = 10, score_fn=None
) -> float:
    """PBO over a ``(n_obs, n_trials)`` matrix; each column is one trial's PnL."""
    return evaluate_cscv(returns_matrix, n_partitions, score_fn).pbo
