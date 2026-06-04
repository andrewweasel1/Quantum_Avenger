from .dsr import compute_deflated_sharpe_ratio, expected_max_sharpe, interpret_dsr
from .hmm_gauntlet import fit_regime_hmm, run_hmm_synthetic_gauntlet
from .promotion import PromotionDecision, PromotionRegistry, assess_promotion
from .tearsheet import summary_metrics, write_html_tearsheet

__all__ = [
    "PromotionDecision",
    "PromotionRegistry",
    "assess_promotion",
    "compute_deflated_sharpe_ratio",
    "expected_max_sharpe",
    "fit_regime_hmm",
    "interpret_dsr",
    "run_hmm_synthetic_gauntlet",
    "summary_metrics",
    "write_html_tearsheet",
]
