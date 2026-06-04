"""Append-only trade log (Parquet) — the realized-fill record (Phase 6 contract).

Separate from the veto ledger (which records *decisions*): this captures order /
fill details and realized P&L for executed trades, and is the source of the
dashboard's performance KPIs. ``pnl`` is the per-trade fractional return.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

TRADE_LOG_SCHEMA = pa.schema(
    [
        ("timestamp", pa.timestamp("ns")),
        ("symbol", pa.string()),
        ("side", pa.string()),
        ("qty", pa.int32()),
        ("limit_price", pa.float64()),
        ("status", pa.string()),
        ("order_id", pa.string()),
        ("fill_price", pa.float64()),
        ("pnl", pa.float64()),
    ]
)


@dataclass
class TradeRecord:
    symbol: str
    side: str
    qty: int
    limit_price: float
    status: str
    order_id: str
    fill_price: float = 0.0
    pnl: float = 0.0
    timestamp: datetime | None = None


class TradeLog:
    def __init__(self, path):
        self._path = Path(path)

    def append(self, record: TradeRecord) -> None:
        moment = (record.timestamp or datetime.now(UTC)).replace(tzinfo=None)
        table = pa.table(
            {
                "timestamp": pa.array([moment], type=pa.timestamp("ns")),
                "symbol": [record.symbol],
                "side": [record.side],
                "qty": [int(record.qty)],
                "limit_price": [float(record.limit_price)],
                "status": [record.status],
                "order_id": [record.order_id],
                "fill_price": [float(record.fill_price)],
                "pnl": [float(record.pnl)],
            },
            schema=TRADE_LOG_SCHEMA,
        )
        if self._path.exists():
            table = pa.concat_tables([pq.read_table(self._path), table])
        self._path.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, self._path)

    def read(self) -> pa.Table:
        if not self._path.exists():
            return TRADE_LOG_SCHEMA.empty_table()
        return pq.read_table(self._path)

    def __len__(self) -> int:
        return self.read().num_rows
