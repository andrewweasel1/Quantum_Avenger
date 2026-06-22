"""Adapter interfaces for every external boundary (principle G4).

The pipeline never imports a live SDK directly; it depends on these ABCs and is
handed a concrete implementation — a deterministic fake in dev/tests, a live
client in production. This keeps all 7 phases unit-testable with no network.

``BrokerAdapter`` deliberately stays in :mod:`new_pipeline.execution.broker`
(its original home); the fakes/live brokers implement that interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, timedelta


@dataclass(frozen=True)
class SentimentResult:
    score: float  # normalized to [-1.0, 1.0]
    label: str  # "bullish" | "bearish" | "neutral"


@dataclass(frozen=True)
class SentimentScore:
    """Deterministic FinBERT-style score: a signed scalar + class probabilities.

    Distinct from ``SentimentResult`` (the generative ``LLMClient``'s coarse
    score/label) — this is the deterministic sensor's richer output that the HMM
    fusion and decay-weighting consume.
    """

    signed: float  # P(pos) - P(neg), in [-1, 1]
    confidence: float  # max class probability, in [0, 1]
    p_pos: float
    p_neg: float
    p_neutral: float


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


class SentimentEngine(ABC):
    """Deterministic sentiment sensor (e.g. FinBERT in eval mode). It produces a
    number, not a generative verdict (G1), so it lives apart from ``LLMClient``."""

    @abstractmethod
    def score_headlines(self, texts: list[str], batch_size: int = 64) -> list[SentimentScore]:
        raise NotImplementedError


class MarketDataSource(ABC):
    @abstractmethod
    def history(self, symbol: str, start: date, end: date) -> list[Bar]:
        raise NotImplementedError


class NewsSource(ABC):
    @abstractmethod
    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        raise NotImplementedError

    def fetch(
        self, symbol: str, start: date, end: date, as_of: datetime | None = None
    ) -> list[NewsItem]:
        """All news for ``symbol`` in ``[start, end]`` (inclusive), optionally
        truncated to items knowable by ``as_of`` (``timestamp <= as_of`` — a hard
        look-ahead cutoff complementing the sentiment builder's session mapping).

        Default loops ``headlines`` per calendar day; range-native providers
        (fixture, GDELT, EDGAR) override this with a single query.
        """
        items: list[NewsItem] = []
        day = start
        while day <= end:
            items.extend(self.headlines(symbol, day))
            day += timedelta(days=1)
        if as_of is not None:
            items = [item for item in items if item.timestamp <= as_of]
        return items


class UniverseProvider(ABC):
    """Point-in-time, survivorship-safe trading universe."""

    @abstractmethod
    def members(self, as_of: date | None = None) -> list[UniverseMember]:
        raise NotImplementedError

    def symbols(self, as_of: date | None = None) -> list[str]:
        return [member.ticker for member in self.members(as_of)]

    def sectors(self, as_of: date | None = None) -> dict[str, str]:
        return {member.ticker: member.gics_sector for member in self.members(as_of)}

    def aliases(self, as_of: date | None = None) -> dict[str, list[str]]:
        """Ticker -> [company name, alias, ...] for the anonymizer gazetteer.

        Default empty (no aliases known); concrete providers may override.
        """
        return {}
