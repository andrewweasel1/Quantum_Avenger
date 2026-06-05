"""Dashboard data views for the model-registry and risk pages (Phase 6).

Pure data over the promotion registry (JSON) and the trade log (Parquet), so the
pages stay thin and the logic is unit-testable offline.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq


def model_registry_view(registry_path) -> dict:
    """Active champions + promotion history from the immutable registry JSON."""
    path = Path(registry_path)
    if not path.exists():
        return {"active_champions": {}, "promotions": []}
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class RiskView:
    gross_exposure: float
    position_count: int
    largest_position: float
    concentration: float  # largest position notional / gross exposure


def risk_view(trade_log_path) -> RiskView:
    """Net per-symbol notional exposure and concentration from the trade log."""
    path = Path(trade_log_path)
    if not path.exists():
        return RiskView(0.0, 0, 0.0, 0.0)
    table = pq.read_table(path)
    if table.num_rows == 0:
        return RiskView(0.0, 0, 0.0, 0.0)

    symbols = table.column("symbol").to_pylist()
    qty = np.asarray(table.column("qty").to_pylist(), dtype=np.float64)
    price = np.asarray(table.column("limit_price").to_pylist(), dtype=np.float64)
    sign = np.where(np.array(table.column("side").to_pylist()) == "buy", 1.0, -1.0)
    signed_notional = sign * qty * price

    exposure: dict[str, float] = {}
    for symbol, value in zip(symbols, signed_notional, strict=True):
        exposure[symbol] = exposure.get(symbol, 0.0) + float(value)

    notionals = np.array([abs(v) for v in exposure.values()])
    gross = float(notionals.sum())
    largest = float(notionals.max()) if notionals.size else 0.0
    open_positions = int((notionals > 0.0).sum())
    return RiskView(gross, open_positions, largest, largest / gross if gross > 0.0 else 0.0)
