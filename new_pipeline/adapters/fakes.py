"""Deterministic, offline implementations of the adapter interfaces.

Used by dev and the entire test suite so no phase needs a network or live
credentials (G4). Every output is a pure function of its inputs — same call,
same result — which keeps tests reproducible (G6).
"""

import math
from datetime import date, datetime, timedelta

from new_pipeline.adapters.base import (
    Bar,
    LLMClient,
    MarketDataSource,
    NewsItem,
    NewsSource,
    SentimentResult,
    Verdict,
)
from new_pipeline.execution.broker import BrokerAdapter

_STANCE_BY_LABEL = {"bullish": "BULLISH", "bearish": "BEARISH", "neutral": "NEUTRAL"}


def _stable_unit(text: str) -> float:
    """Map text to a deterministic value in [-1.0, 1.0]."""
    total = sum(ord(char) for char in text)
    return ((total % 2001) - 1000) / 1000.0


class FakeLLMClient(LLMClient):
    def sentiment(self, text: str) -> SentimentResult:
        score = _stable_unit(text)
        if score > 0.1:
            label = "bullish"
        elif score < -0.1:
            label = "bearish"
        else:
            label = "neutral"
        return SentimentResult(score=score, label=label)

    def verdict(self, prompt: str) -> Verdict:
        stance = _STANCE_BY_LABEL[self.sentiment(prompt).label]
        return Verdict(stance=stance, rationale="deterministic fake verdict")


class FakeMarketDataSource(MarketDataSource):
    """Synthetic but well-formed OHLCV: a smooth sinusoid + drift, fully
    deterministic in the symbol and date (no RNG)."""

    def __init__(self, base_price: float = 100.0) -> None:
        self._base_price = base_price

    def history(self, symbol: str, start: date, end: date) -> list[Bar]:
        if end < start:
            return []
        anchor = (sum(ord(char) for char in symbol) % 50) + self._base_price
        bars: list[Bar] = []
        day = start
        i = 0
        while day <= end:
            close = anchor + 5.0 * math.sin(i / 7.0) + 0.05 * i
            open_ = anchor + 5.0 * math.sin((i - 1) / 7.0) + 0.05 * (i - 1)
            high = max(open_, close) + 1.0
            low = min(open_, close) - 1.0
            bars.append(
                Bar(
                    day=day,
                    open=round(open_, 4),
                    high=round(high, 4),
                    low=round(low, 4),
                    close=round(close, 4),
                    volume=1_000_000 + (i % 13) * 10_000,
                )
            )
            day += timedelta(days=1)
            i += 1
        return bars


class FakeNewsSource(NewsSource):
    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        return [
            NewsItem(
                timestamp=datetime(on.year, on.month, on.day),
                symbol=symbol,
                headline=f"{symbol} steady as markets digest data on {on.isoformat()}.",
            )
        ]


class FakeBroker(BrokerAdapter):
    """In-memory broker: records orders and tracks net positions."""

    def __init__(self) -> None:
        self._orders: list[dict] = []
        self._positions: dict[str, float] = {}

    def submit_order(self, order: dict) -> dict:
        symbol = str(order.get("symbol", ""))
        qty = float(order.get("qty", 0.0))
        side = str(order.get("side", "buy")).lower()
        signed = qty if side == "buy" else -qty
        self._positions[symbol] = self._positions.get(symbol, 0.0) + signed
        receipt = {
            "status": "filled",
            "order_id": f"fake-{len(self._orders) + 1}",
            **order,
        }
        self._orders.append(receipt)
        return receipt

    def get_positions(self) -> dict[str, float]:
        return dict(self._positions)

    @property
    def orders(self) -> list[dict]:
        return list(self._orders)
