"""Composition root: assemble the external adapters for a run (principle G4).

``build_adapters`` is the single place that decides whether the engine talks to
deterministic fakes or live SDKs, keyed off ``system.run_mode``. Today only the
offline modes are wired; the live modes raise a clear error pointing at the
adapters that still need implementing. The runner and orchestrator depend on the
returned bundle, never on a concrete client — so going live is a config flip
plus three adapter implementations, no change to the trade loop.
"""

from dataclasses import dataclass

from new_pipeline.adapters.base import LLMClient, MarketDataSource, NewsSource, UniverseProvider
from new_pipeline.adapters.fakes import (
    FakeBroker,
    FakeLLMClient,
    FakeMarketDataSource,
    FakeNewsSource,
)
from new_pipeline.adapters.universe_static import StaticUniverseProvider
from new_pipeline.execution.broker import BrokerAdapter

# Offline, network-free modes that resolve to deterministic fakes.
OFFLINE_MODES = frozenset({"offline", "backtest", "replay", "sim", "development", "testing"})
# Modes that require the live SDK adapters (not yet implemented).
LIVE_MODES = frozenset({"live", "paper", "production"})


@dataclass(frozen=True)
class AdapterBundle:
    market_data: MarketDataSource
    news: NewsSource
    llm: LLMClient
    broker: BrokerAdapter
    universe: UniverseProvider


def build_adapters(cfg) -> AdapterBundle:
    """Return the adapter bundle for ``cfg.system.run_mode``."""
    mode = (cfg.system.run_mode or "offline").lower()
    if mode in OFFLINE_MODES:
        return AdapterBundle(
            market_data=FakeMarketDataSource(),
            news=FakeNewsSource(),
            llm=FakeLLMClient(),
            broker=FakeBroker(),
            universe=StaticUniverseProvider(),
        )
    if mode in LIVE_MODES:
        if not (cfg.alpaca.api_key and cfg.alpaca.secret_key):
            raise ValueError(
                f"run_mode={mode!r} requires QA_ALPACA__API_KEY and "
                "QA_ALPACA__SECRET_KEY (never commit them)."
            )
        return _build_live_adapters(cfg)
    raise ValueError(f"unknown run_mode: {mode!r}")


def _build_live_adapters(cfg) -> AdapterBundle:  # pragma: no cover - needs the live SDK + egress
    """Assemble the live Alpaca adapters (lazy SDK import keeps offline runs clean).

    The LLM stays the deterministic fake until an Ollama endpoint is configured —
    Alpaca covers market data, news, and order execution. Going fully live is a
    drop-in LLM client here, no change elsewhere.
    """
    from new_pipeline.adapters.broker_alpaca import AlpacaBroker
    from new_pipeline.adapters.market_alpaca import AlpacaMarketDataSource
    from new_pipeline.adapters.news_alpaca import AlpacaNewsSource

    creds = (cfg.alpaca.api_key, cfg.alpaca.secret_key)
    return AdapterBundle(
        market_data=AlpacaMarketDataSource(*creds, feed=cfg.alpaca.data_feed),
        news=AlpacaNewsSource(*creds),
        llm=FakeLLMClient(),
        broker=AlpacaBroker(*creds, paper=cfg.alpaca.paper),
        universe=StaticUniverseProvider(),
    )
