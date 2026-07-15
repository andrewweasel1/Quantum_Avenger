"""Champion promotion gate + immutable registry.

A candidate is promoted only if it clears every gate: Deflated Sharpe >=
threshold, HMM synthetic Sharpe > minimum, and (when supplied) Probability of
Backtest Overfitting <= threshold. PSR and the haircut Sharpe ride along as
recorded diagnostics. The registry is an append-only JSON audit:
``{"promotions": [...], "active_champions": {sector: model_path}}``.
"""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from new_pipeline.core.exceptions import PromotionError


@dataclass
class PromotionDecision:
    sector: str
    dsr: float
    synthetic_sharpe: float
    promoted: bool
    reason: str
    pbo: float | None = None
    psr: float | None = None
    haircut_sharpe: float | None = None
    cpcv_path_pass_fraction: float | None = None
    cpcv_path_dsr_median: float | None = None
    reality_check_pvalue: float | None = None
    n_trades: int | None = None


def assess_promotion(
    sector,
    dsr,
    synthetic_sharpe,
    dsr_threshold=0.95,
    synthetic_min=0.0,
    pbo=None,
    pbo_threshold=0.5,
    psr=None,
    haircut_sharpe=None,
    minbtl_satisfied=None,
    path_pass_fraction=None,
    path_fraction_threshold=0.5,
    path_dsr_median=None,
    path_gate_enabled=False,
    reality_check_pvalue=None,  # recorded; gates only when reality_check_gate_enabled
    reality_check_gate_enabled=False,
    reality_check_threshold=0.05,
    n_trades=None,
) -> PromotionDecision:
    """Apply every promotion gate; the first failure names the rejection reason.

    ``n_trades`` (when supplied) is the count of realized OOS trades behind the
    champion's return series. Zero trades means the entry threshold never fired —
    every statistic downstream is 0.0 *by construction*, so the zero-trade gate is
    checked first: "low DSR" on an all-zero series would misread a dead strategy
    as a weak one.

    The CPCV path gate (when enabled and supplied) requires at least
    ``path_fraction_threshold`` of the reconstructed backtest paths to clear the
    Deflated-Sharpe threshold individually — robustness beyond the single mean
    path's DSR.
    """
    path_gate = (
        path_gate_enabled
        and path_pass_fraction is not None
        and path_pass_fraction < path_fraction_threshold
    )
    gates = {
        "zero trades (entry threshold never fired)": n_trades is not None and n_trades == 0,
        "low DSR": dsr < dsr_threshold,
        "failed synthetic gauntlet": synthetic_sharpe <= synthetic_min,
        "overfit (high PBO)": pbo is not None and pbo > pbo_threshold,
        "backtest shorter than MinBTL": minbtl_satisfied is False,
        "unstable across CPCV paths": path_gate,
        "data-snooped (reality check)": (
            reality_check_gate_enabled
            and reality_check_pvalue is not None
            and reality_check_pvalue > reality_check_threshold
        ),
    }
    failed = [reason for reason, tripped in gates.items() if tripped]
    promoted = not failed
    return PromotionDecision(
        sector,
        dsr,
        synthetic_sharpe,
        promoted,
        "true alpha" if promoted else failed[0],
        pbo=pbo,
        psr=psr,
        haircut_sharpe=haircut_sharpe,
        cpcv_path_pass_fraction=path_pass_fraction,
        cpcv_path_dsr_median=path_dsr_median,
        reality_check_pvalue=reality_check_pvalue,
        n_trades=n_trades,
    )


class PromotionRegistry:
    def __init__(self, path):
        self._path = Path(path)
        self._data = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            return json.loads(self._path.read_text(encoding="utf-8"))
        return {"promotions": [], "active_champions": {}}

    def record(self, decision: PromotionDecision, model_path: str | None = None) -> dict:
        if decision.promoted and model_path is None:
            raise PromotionError("a promoted decision requires a model_path")
        entry = {
            "sector": decision.sector,
            "dsr": decision.dsr,
            "synthetic_sharpe": decision.synthetic_sharpe,
            "pbo": decision.pbo,
            "psr": decision.psr,
            "haircut_sharpe": decision.haircut_sharpe,
            "cpcv_path_pass_fraction": decision.cpcv_path_pass_fraction,
            "cpcv_path_dsr_median": decision.cpcv_path_dsr_median,
            "reality_check_pvalue": decision.reality_check_pvalue,
            "n_trades": decision.n_trades,
            "promoted": decision.promoted,
            "reason": decision.reason,
            "timestamp": datetime.now(UTC).isoformat(),
            "model_path": model_path,
        }
        self._data["promotions"].append(entry)  # append-only audit trail
        if decision.promoted:
            self._data["active_champions"][decision.sector] = model_path
        self._save()
        return entry

    def is_champion(self, sector) -> bool:
        return sector in self._data["active_champions"]

    def active_champions(self) -> dict:
        return dict(self._data["active_champions"])

    @property
    def promotions(self) -> list:
        return list(self._data["promotions"])

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")
