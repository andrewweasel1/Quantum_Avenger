"""Composition root: assemble the external adapters for a run (principle G4).

``build_adapters`` is the single place that decides whether the engine talks to
deterministic fakes or live SDKs, keyed off ``system.run_mode``. Today only the
offline modes are wired; the live modes raise a clear error pointing at the
adapters that still need implementing. The runner and orchestrator depend on the
returned bundle, never on a concrete client — so going live is a config flip
plus three adapter implementations, no change to the trade loop.
"""

from dataclasses import dataclass, field

from new_pipeline.adapters.base import (
    LLMClient,
    MarketDataSource,
    NewsSource,
    SentimentEngine,
    UniverseProvider,
)
from new_pipeline.adapters.fakes import (
    FakeBroker,
    FakeFundamentalsSource,
    FakeLLMClient,
    FakeMarketDataSource,
    FakeNewsSource,
    FakeSentimentEngine,
)
from new_pipeline.adapters.universe_static import StaticUniverseProvider
from new_pipeline.execution.broker import BrokerAdapter
from new_pipeline.execution.entity_anonymizer import Anonymizer, EntityAnonymizer

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
    sentiment_engine: SentimentEngine = field(default_factory=FakeSentimentEngine)
    anonymizer: Anonymizer = field(default_factory=EntityAnonymizer)


def build_adapters(cfg) -> AdapterBundle:
    """Return the adapter bundle for ``cfg.system.run_mode``."""
    mode = (cfg.system.run_mode or "offline").lower()
    if mode in OFFLINE_MODES:
        universe = StaticUniverseProvider()
        return AdapterBundle(
            market_data=FakeMarketDataSource(),
            news=FakeNewsSource(),
            llm=FakeLLMClient(),
            broker=FakeBroker(),
            universe=universe,
            sentiment_engine=FakeSentimentEngine(),
            anonymizer=EntityAnonymizer(
                vocabulary=universe.symbols(), gazetteer=universe.aliases()
            ),
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
    universe = StaticUniverseProvider()
    sentiment_engine, anonymizer = _build_fusion(cfg, universe)
    return AdapterBundle(
        market_data=AlpacaMarketDataSource(*creds, feed=cfg.alpaca.data_feed),
        news=AlpacaNewsSource(*creds),
        llm=FakeLLMClient(),
        broker=AlpacaBroker(*creds, paper=cfg.alpaca.paper),
        universe=universe,
        sentiment_engine=sentiment_engine,
        anonymizer=anonymizer,
    )


def _build_fusion(cfg, universe):  # pragma: no cover - heavy ML deps (torch/transformers/spaCy)
    """FinBERT + spaCy when fusion is enabled; deterministic fakes otherwise.

    Lazy imports keep torch/transformers/spaCy out of the offline image; the
    gazetteer is built from the universe's ticker -> alias map.
    """
    if not cfg.fusion.enabled:
        return FakeSentimentEngine(), EntityAnonymizer(
            vocabulary=universe.symbols(), gazetteer=universe.aliases()
        )
    from new_pipeline.adapters.sentiment_finbert import FinBERTSentimentEngine
    from new_pipeline.execution.anonymizer_spacy import SpacyNewsAnonymizer

    return (
        FinBERTSentimentEngine(model_name=cfg.fusion.sentiment_model),
        SpacyNewsAnonymizer(universe.aliases(), spacy_model=cfg.fusion.spacy_model),
    )


def build_fundamentals_source(cfg, universe=None):
    """Point-in-time fundamentals for the value/quality factors: a deterministic fake
    (or a checked-in fixture when ``fundamentals.fixture_path`` is set) offline, the
    live EDGAR source otherwise."""
    mode = (cfg.system.run_mode or "offline").lower()
    if mode in OFFLINE_MODES:
        if cfg.fundamentals.fixture_path:
            from new_pipeline.adapters.fundamentals_static import StaticFundamentalsSource

            return StaticFundamentalsSource(cfg.fundamentals.fixture_path)
        return FakeFundamentalsSource()
    from new_pipeline.adapters.fundamentals_edgar import (  # pragma: no cover - egress
        EdgarFundamentalsSource,
    )

    return EdgarFundamentalsSource(identity=cfg.fundamentals.edgar_identity)  # pragma: no cover


def build_news_source(cfg, universe):
    """Point-in-time news source for the training/ingestion path: the deterministic
    fixture offline, a composite of the configured live providers otherwise. Kept
    separate from ``AdapterBundle.news`` (the runner's live trade-context feed)."""
    mode = (cfg.system.run_mode or "offline").lower()
    if mode in OFFLINE_MODES:
        from new_pipeline.adapters.news_static import StaticNewsSource

        return StaticNewsSource(cfg.news.fixture_path or None)
    return _build_live_news_source(cfg, universe)


def _build_live_news_source(cfg, universe):  # pragma: no cover - egress / live providers
    from new_pipeline.adapters.news_composite import CompositeNewsSource

    sources = []
    for provider in cfg.news.providers:
        if provider == "gdelt":
            from new_pipeline.adapters.news_gdelt import GdeltNewsSource

            sources.append(
                GdeltNewsSource(
                    universe.aliases(), endpoint=cfg.news.gdelt_endpoint, limit=cfg.news.limit
                )
            )
        elif provider == "edgar":
            from new_pipeline.adapters.news_edgar import EdgarFilingSource

            sources.append(
                EdgarFilingSource(
                    forms=cfg.news.edgar_forms,
                    identity=cfg.news.edgar_identity,
                    limit=cfg.news.limit,
                )
            )
    return CompositeNewsSource(sources)
