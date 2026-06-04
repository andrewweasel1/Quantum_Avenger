"""Champion promotion gate + immutable registry.

A candidate is promoted only if its Deflated Sharpe >= threshold AND its HMM
synthetic Sharpe > minimum. The registry is an append-only JSON audit:
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


def assess_promotion(
    sector, dsr, synthetic_sharpe, dsr_threshold=0.95, synthetic_min=0.0
) -> PromotionDecision:
    if dsr >= dsr_threshold and synthetic_sharpe > synthetic_min:
        return PromotionDecision(sector, dsr, synthetic_sharpe, True, "true alpha")
    reason = "low DSR" if dsr < dsr_threshold else "failed synthetic gauntlet"
    return PromotionDecision(sector, dsr, synthetic_sharpe, False, reason)


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
