"""Dashboard data layer: load the ledgers and compute KPIs (Phase 6).

Pure data + math (no Streamlit) so it is fully unit-testable offline. Reads the
append-only veto ledger (decision analytics) and trade log (performance), and
derives the KPI dict + equity curve the UI renders. ``pnl`` rows are treated as
per-trade fractional returns.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from new_pipeline.evaluation.tearsheet import summary_metrics


@dataclass
class VetoSummary:
    total: int
    executed: int
    vetoed: int
    veto_rate: float
    by_gate: dict[str, int]


@dataclass
class Performance:
    total_pnl: float
    sharpe: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    equity_curve: list[float]


class RealtimeDataManager:
    def __init__(self, veto_ledger_path, trade_log_path):
        self._veto_path = Path(veto_ledger_path)
        self._trade_path = Path(trade_log_path)

    def veto_summary(self) -> VetoSummary:
        if not self._veto_path.exists():
            return VetoSummary(0, 0, 0, 0.0, {})
        gates = pq.read_table(self._veto_path).column("veto_gate").to_pylist()
        total = len(gates)
        executed = sum(1 for gate in gates if gate == "none")
        vetoed = total - executed
        by_gate: dict[str, int] = {}
        for gate in gates:
            if gate != "none":
                by_gate[gate] = by_gate.get(gate, 0) + 1
        return VetoSummary(total, executed, vetoed, vetoed / total if total else 0.0, by_gate)

    def performance(self) -> Performance:
        empty = Performance(0.0, 0.0, 0.0, 0.0, 0.0, [])
        if not self._trade_path.exists():
            return empty
        pnl = np.asarray(
            pq.read_table(self._trade_path).column("pnl").to_pylist(), dtype=np.float64
        )
        if pnl.size == 0:
            return empty
        metrics = summary_metrics(pnl)
        return Performance(
            total_pnl=float(pnl.sum()),
            sharpe=metrics["sharpe"],
            max_drawdown=metrics["max_drawdown"],
            win_rate=metrics["win_rate"],
            profit_factor=metrics["profit_factor"],
            equity_curve=np.cumprod(1.0 + pnl).tolist(),
        )

    def kpis(self) -> dict:
        veto = self.veto_summary()
        perf = self.performance()
        return {
            "total_decisions": veto.total,
            "executed": veto.executed,
            "vetoed": veto.vetoed,
            "veto_rate": veto.veto_rate,
            "total_pnl": perf.total_pnl,
            "sharpe": perf.sharpe,
            "max_drawdown": perf.max_drawdown,
            "win_rate": perf.win_rate,
            "profit_factor": perf.profit_factor,
        }
