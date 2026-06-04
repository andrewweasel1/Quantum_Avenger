"""Adapter interfaces for every external boundary (principle G4).

The pipeline never imports a live SDK directly; it depends on these ABCs and is
handed a concrete implementation — a deterministic fake in dev/tests, a live
client in production. This keeps all 7 phases unit-testable with no network.

``BrokerAdapter`` deliberately stays in :mod:`new_pipeline.execution.broker`
(its original home); the fakes/live brokers implement that interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class SentimentResult:
    score: float  # normalized to [-1.0, 1.0]
    label: str  # "bullish" | "bearish" | "neutral"


@dataclass(frozen=True)
class Verdict:
    stance: str  # "BULLISH" | "BEARISH" | "NEUTRAL"
    rationale: str


@dataclass(frozen=True)
class NewsItem:
    timestamp: datetime
    symbol: str
    headline: str


@dataclass(frozen=True)
class Bar:
    day: date
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class UniverseMember:
    ticker: str
    gics_sector: str
    start_date: date
    end_date: date | None = None

    def active_on(self, as_of: date) -> bool:
        """True if the member is in the index on ``as_of`` (end is exclusive)."""
        return self.start_date <= as_of and (self.end_date is None or as_of < self.end_date)


class LLMClient(ABC):
    """Sentiment + verdict generation. The LLM never computes risk/quant
    numbers (G1) — those go through deterministic tools."""

    @abstractmethod
    def sentiment(self, text: str) -> SentimentResult:
        raise NotImplementedError

    @abstractmethod
    def verdict(self, prompt: str) -> Verdict:
        raise NotImplementedError


class MarketDataSource(ABC):
    @abstractmethod
    def history(self, symbol: str, start: date, end: date) -> list[Bar]:
        raise NotImplementedError


class NewsSource(ABC):
    @abstractmethod
    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        raise NotImplementedError


class UniverseProvider(ABC):
    """Point-in-time, survivorship-safe trading universe."""

    @abstractmethod
    def members(self, as_of: date | None = None) -> list[UniverseMember]:
        raise NotImplementedError

    def symbols(self, as_of: date | None = None) -> list[str]:
        return [member.ticker for member in self.members(as_of)]

    def sectors(self, as_of: date | None = None) -> dict[str, str]:
        return {member.ticker: member.gics_sector for member in self.members(as_of)}
