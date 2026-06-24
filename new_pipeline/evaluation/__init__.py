from .alpha_eval import (
    ICReport,
    alpha_eval_report,
    evaluate_signals,
    ic_decay,
    information_coefficient,
)
from .cscv import cscv_partition_indices, cscv_splits, n_cscv_splits
from .dsr import (
    DSRResult,
    compute_deflated_sharpe_ratio,
    deflated_sharpe_report,
    effective_number_of_trials,
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
from .reality_check import hansens_spa, whites_reality_check
from .regime_dsr import QuantitativeEvaluator, RegimeVerdict, ThinRegimePolicy
from .tearsheet import summary_metrics, write_html_tearsheet

__all__ = [
    "CSCVResult",
    "DSRResult",
    "HaircutResult",
    "ICReport",
    "PromotionDecision",
    "PromotionRegistry",
    "QuantitativeEvaluator",
    "RegimeVerdict",
    "ThinRegimePolicy",
    "alpha_eval_report",
    "assess_promotion",
    "evaluate_signals",
    "ic_decay",
    "information_coefficient",
    "backtest_length_is_sufficient",
    "compute_deflated_sharpe_ratio",
    "cscv_partition_indices",
    "cscv_splits",
    "deflated_sharpe_report",
    "effective_number_of_trials",
    "evaluate_cscv",
    "expected_max_sharpe",
    "fit_regime_hmm",
    "haircut_sharpe_ratio",
    "hansens_spa",
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
    "whites_reality_check",
    "write_html_tearsheet",
]
