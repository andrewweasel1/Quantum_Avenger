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


def _build_universe(cfg) -> StaticUniverseProvider:
    """The membership fixture selected by ``data.universe_path`` (empty -> the
    packaged 41-name default; e.g. the S&P 500 snapshot at
    ``new_pipeline/data/universe/sp500.csv``)."""
    from pathlib import Path

    path = getattr(cfg.data, "universe_path", "")
    return StaticUniverseProvider(Path(path) if path else None)


def build_adapters(cfg) -> AdapterBundle:
    """Return the adapter bundle for ``cfg.system.run_mode``."""
    mode = (cfg.system.run_mode or "offline").lower()
    if mode in OFFLINE_MODES:
        universe = _build_universe(cfg)
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


def build_llm_client(cfg) -> LLMClient:
    """The live Ollama client when fusion is enabled and an endpoint is configured;
    the deterministic fake otherwise. Gated on ``fusion.enabled`` (not just the
    endpoint) because ``defaults.yaml`` ships a localhost endpoint — going live
    with the LLM is an explicit flip, mirroring the FinBERT/spaCy stack."""
    if cfg.fusion.enabled and cfg.fusion.ollama_endpoint:
        from new_pipeline.adapters.llm_ollama import OllamaLLMClient

        return OllamaLLMClient.from_config(cfg)
    return FakeLLMClient()


def _build_live_adapters(cfg) -> AdapterBundle:  # pragma: no cover - needs the live SDK + egress
    """Assemble the live Alpaca adapters (lazy SDK import keeps offline runs clean).

    The LLM is the Ollama client when ``fusion.enabled`` + ``ollama_endpoint``
    say so (see ``build_llm_client``), else the deterministic fake.
    """
    from new_pipeline.adapters.broker_alpaca import AlpacaBroker
    from new_pipeline.adapters.market_alpaca import AlpacaMarketDataSource
    from new_pipeline.adapters.news_alpaca import AlpacaNewsSource

    creds = (cfg.alpaca.api_key, cfg.alpaca.secret_key)
    universe = _build_universe(cfg)
    sentiment_engine, anonymizer = _build_fusion(cfg, universe)
    return AdapterBundle(
        market_data=AlpacaMarketDataSource(*creds, feed=cfg.alpaca.data_feed),
        news=AlpacaNewsSource(*creds),
        llm=build_llm_client(cfg),
        broker=AlpacaBroker(*creds, paper=cfg.alpaca.paper),
        universe=universe,
        sentiment_engine=sentiment_engine,
        anonymizer=anonymizer,
    )


def _build_fusion(cfg, universe):
    """The fusion sentiment engine + anonymizer; deterministic fakes when off.

    Backends: ``fusion.sentiment_backend`` selects FinBERT (neural; lazy
    torch/transformers import, needs HF egress) or VADER (lexicon; base dep,
    no downloads). The spaCy anonymizer degrades to the offline gazetteer
    ``EntityAnonymizer`` when spaCy or its model isn't available, so fusion
    never hard-fails on the NER dependency.
    """
    gazetteer_anonymizer = EntityAnonymizer(
        vocabulary=universe.symbols(), gazetteer=universe.aliases()
    )
    if not cfg.fusion.enabled:
        return FakeSentimentEngine(), gazetteer_anonymizer

    if cfg.fusion.sentiment_backend == "vader":
        from new_pipeline.adapters.sentiment_vader import VaderSentimentEngine

        engine = VaderSentimentEngine()
    else:  # pragma: no cover - heavy ML deps (torch/transformers)
        from new_pipeline.adapters.sentiment_finbert import FinBERTSentimentEngine

        engine = FinBERTSentimentEngine(model_name=cfg.fusion.sentiment_model)

    try:  # pragma: no cover - spaCy + model are fusion-host extras
        from new_pipeline.execution.anonymizer_spacy import SpacyNewsAnonymizer

        anonymizer = SpacyNewsAnonymizer(universe.aliases(), spacy_model=cfg.fusion.spacy_model)
    except Exception:
        anonymizer = gazetteer_anonymizer
    return engine, anonymizer


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
        if provider == "vault":
            # A pre-ingested Parquet news vault (scripts/ingest_news_vault.py):
            # zero network in the run itself — fetch once, reuse forever.
            from pathlib import Path

            from new_pipeline.adapters.news_static import VaultNewsSource

            sources.append(VaultNewsSource(Path(cfg.news.vault_dir) / "news_vault.parquet"))
        elif provider == "alpaca":
            # Authenticated Benzinga feed — not per-IP rate-limited like GDELT.
            from new_pipeline.adapters.news_alpaca import AlpacaNewsSource

            sources.append(AlpacaNewsSource(cfg.alpaca.api_key, cfg.alpaca.secret_key))
        elif provider == "gdelt":
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
