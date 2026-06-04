"""Append-only decision ledger (Parquet).

Every orchestrator outcome — executed or vetoed — is appended with the
nine-column schema the Phase 6 dashboard reads. ``veto_gate`` is "none" for
executed trades, otherwise the gate that rejected the trade
("grader" | "shield" | "execution").
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

LEDGER_SCHEMA = pa.schema(
    [
        ("timestamp", pa.timestamp("ns")),
        ("symbol", pa.string()),
        ("signal", pa.string()),
        ("entry_price", pa.float64()),
        ("veto_reason", pa.string()),
        ("veto_gate", pa.string()),
        ("dsr", pa.float64()),
        ("position_size", pa.int32()),
        ("execution_id", pa.string()),
    ]
)


@dataclass
class VetoRecord:
    symbol: str
    signal: str
    entry_price: float
    veto_reason: str
    veto_gate: str
    dsr: float
    position_size: int
    execution_id: str
    timestamp: datetime | None = None


class VetoLedger:
    def __init__(self, path):
        self._path = Path(path)

    def append(self, record: VetoRecord) -> None:
        moment = record.timestamp or datetime.now(UTC)
        table = pa.table(
            {
                "timestamp": pa.array([moment.replace(tzinfo=None)], type=pa.timestamp("ns")),
                "symbol": [record.symbol],
                "signal": [record.signal],
                "entry_price": [float(record.entry_price)],
                "veto_reason": [record.veto_reason],
                "veto_gate": [record.veto_gate],
                "dsr": [float(record.dsr)],
                "position_size": [int(record.position_size)],
                "execution_id": [record.execution_id],
            },
            schema=LEDGER_SCHEMA,
        )
        if self._path.exists():
            table = pa.concat_tables([pq.read_table(self._path), table])
        self._path.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, self._path)

    def read(self) -> pa.Table:
        if not self._path.exists():
            return LEDGER_SCHEMA.empty_table()
        return pq.read_table(self._path)

    def __len__(self) -> int:
        return self.read().num_rows
