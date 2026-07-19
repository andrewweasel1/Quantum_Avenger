"""Deterministic, offline implementations of the adapter interfaces.

Used by dev and the entire test suite so no phase needs a network or live
credentials (G4). Every output is a pure function of its inputs — same call,
same result — which keeps tests reproducible (G6).
"""

import math
from datetime import date, datetime, timedelta

from new_pipeline.adapters.base import (
    Bar,
    FundamentalSnapshot,
    FundamentalsSource,
    LLMClient,
    MarketDataSource,
    NewsItem,
    NewsSource,
    SentimentEngine,
    SentimentResult,
    SentimentScore,
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


class FakeSentimentEngine(SentimentEngine):
    """Deterministic sentiment sensor: a signed score in [-1, 1] (same hash as
    FakeLLMClient) plus a coherent 3-class distribution (signed = p_pos - p_neg,
    probabilities sum to 1)."""

    def score_headlines(self, texts, batch_size: int = 64) -> list[SentimentScore]:
        scores: list[SentimentScore] = []
        for text in texts:
            signed = _stable_unit(text)
            p_pos = max(signed, 0.0)
            p_neg = max(-signed, 0.0)
            p_neutral = 1.0 - abs(signed)
            scores.append(
                SentimentScore(
                    signed=signed,
                    confidence=max(p_pos, p_neg, p_neutral),
                    p_pos=p_pos,
                    p_neg=p_neg,
                    p_neutral=p_neutral,
                )
            )
        return scores


def _quarter_dates(start_year: int, end_year: int) -> list[date]:
    return [date(y, m, 1) for y in range(start_year, end_year + 1) for m in (1, 4, 7, 10)]


class FakeFundamentalsSource(FundamentalsSource):
    """Deterministic synthetic fundamentals: quarterly snapshots whose values are a
    pure function of the symbol and quarter (no RNG)."""

    def history(self, symbol: str, start: date, end: date) -> list[FundamentalSnapshot]:
        if end < start:
            return []
        seed = sum(ord(char) for char in symbol)
        bvps0 = 10.0 + (seed % 40)  # book value per share, 10..50
        eps0 = 1.0 + (seed % 8)  # earnings per share, 1..9
        roe0 = 0.05 + (seed % 25) / 100.0  # return on equity, 0.05..0.30
        roa0 = 0.02 + (seed % 15) / 100.0  # return on assets, 0.02..0.17
        gm0 = 0.20 + (seed % 50) / 100.0  # gross margin, 0.20..0.70
        acc0 = -0.05 + (seed % 10) / 100.0  # accruals, -0.05..0.05
        ocfps0 = eps0 * (1.1 + (seed % 5) / 10.0)  # ocf/share tracks eps
        snapshots: list[FundamentalSnapshot] = []
        for i, as_of in enumerate(_quarter_dates(start.year - 1, end.year)):
            if as_of > end:
                break
            snapshots.append(
                FundamentalSnapshot(
                    as_of=as_of,
                    book_value_per_share=round(bvps0 * (1.0 + 0.01 * i), 4),
                    earnings_per_share=round(eps0 * (1.0 + 0.005 * i), 4),
                    return_on_equity=round(roe0, 4),
                    return_on_assets=round(roa0, 4),
                    gross_margin=round(gm0, 4),
                    accruals=round(acc0, 4),
                    ocf_per_share=round(ocfps0 * (1.0 + 0.005 * i), 4),
                    # growth appears once a year of history exists (>= 4 quarters).
                    revenue_growth=round(0.02 + (seed % 12) / 100.0, 4) if i >= 4 else None,
                    earnings_growth=round(0.005 * 4, 4) if i >= 4 else None,
                )
            )
        return snapshots


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
