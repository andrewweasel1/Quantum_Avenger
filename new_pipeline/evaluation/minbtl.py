"""Minimum Backtest Length (MinBTL).

Bailey, Borwein, López de Prado & Zhu (2014), "Pseudo-Mathematics and Financial
Charlatanism", eq. for the minimum sample needed to keep a claimed Sharpe out of
the no-skill regime. Under ``n_trials`` independent skill-less strategies the
expected maximum (annualized) Sharpe over ``y`` years is

    E[max SR] ≈ (1/√y) · [(1-γ)·Z⁻¹(1-1/N) + γ·Z⁻¹(1-1/(N·e))]

(the bracket is exactly ``dsr.expected_max_sharpe`` with unit trial variance).
Setting that equal to the reported Sharpe and solving for ``y`` gives MinBTL: a
backtest shorter than this *expects* the reported Sharpe from luck alone.
"""

from new_pipeline.evaluation.dsr import expected_max_sharpe


def min_backtest_length(
    n_trials: int, target_sharpe: float, periods_per_year: float = 1.0
) -> float:
    """Minimum backtest length for ``target_sharpe`` to clear the no-skill bound.

    Returns years by default; pass ``periods_per_year`` (e.g. 252) to express the
    result in observations instead. ``target_sharpe`` is annualized.
    """
    if target_sharpe <= 0.0:
        return float("inf")
    if n_trials < 2:
        return 0.0
    bound = expected_max_sharpe(1.0, n_trials)  # E[max SR] at unit trial variance
    return (bound / target_sharpe) ** 2 * periods_per_year


def backtest_length_is_sufficient(
    n_obs: int, n_trials: int, target_sharpe: float, periods_per_year: float = 252.0
) -> bool:
    """True when ``n_obs`` observations clear the MinBTL for the trial count."""
    required = min_backtest_length(n_trials, target_sharpe, periods_per_year)
    return n_obs >= required
