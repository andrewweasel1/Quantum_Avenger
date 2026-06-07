from .cscv import cscv_partition_indices, cscv_splits, n_cscv_splits
from .dsr import (
    compute_deflated_sharpe_ratio,
    expected_max_sharpe,
    interpret_dsr,
    min_track_record_length,
    probabilistic_sharpe_ratio,
)
from .haircut import (
    HaircutResult,
    haircut_sharpe_ratio,
    minimum_profit_hurdle,
    multiple_testing_adjust,
)
from .hmm_gauntlet import fit_regime_hmm, run_hmm_synthetic_gauntlet
from .minbtl import backtest_length_is_sufficient, min_backtest_length
from .pbo import CSCVResult, evaluate_cscv, probability_of_backtest_overfitting
from .promotion import PromotionDecision, PromotionRegistry, assess_promotion
from .tearsheet import summary_metrics, write_html_tearsheet

__all__ = [
    "CSCVResult",
    "HaircutResult",
    "PromotionDecision",
    "PromotionRegistry",
    "assess_promotion",
    "backtest_length_is_sufficient",
    "compute_deflated_sharpe_ratio",
    "cscv_partition_indices",
    "cscv_splits",
    "evaluate_cscv",
    "expected_max_sharpe",
    "fit_regime_hmm",
    "haircut_sharpe_ratio",
    "interpret_dsr",
    "min_backtest_length",
    "min_track_record_length",
    "minimum_profit_hurdle",
    "multiple_testing_adjust",
    "n_cscv_splits",
    "probabilistic_sharpe_ratio",
    "probability_of_backtest_overfitting",
    "run_hmm_synthetic_gauntlet",
    "summary_metrics",
    "write_html_tearsheet",
]
