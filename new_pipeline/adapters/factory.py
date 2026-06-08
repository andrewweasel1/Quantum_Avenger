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
        raise NotImplementedError(
            f"run_mode={mode!r} needs the live adapters (adapters/llm_ollama.py, "
            "adapters/market_alpaca.py, adapters/broker_alpaca.py), which are not "
            "wired yet. Implement them behind the existing ABCs and extend "
            "build_adapters(); the trade loop itself does not change."
        )
    raise ValueError(f"unknown run_mode: {mode!r}")
