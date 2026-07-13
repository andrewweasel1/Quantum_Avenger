import pytest
from new_pipeline.adapters.factory import AdapterBundle, build_adapters
from new_pipeline.adapters.fakes import FakeBroker, FakeLLMClient, FakeMarketDataSource
from new_pipeline.config import get_config


def _cfg_with_mode(mode):
    cfg = get_config().model_copy(deep=True)
    cfg.system.run_mode = mode
    return cfg


def test_offline_mode_returns_fakes():
    bundle = build_adapters(_cfg_with_mode("backtest"))
    assert isinstance(bundle, AdapterBundle)
    assert isinstance(bundle.market_data, FakeMarketDataSource)
    assert isinstance(bundle.llm, FakeLLMClient)
    assert isinstance(bundle.broker, FakeBroker)


def test_live_mode_requires_credentials():
    cfg = _cfg_with_mode("live")  # default config has empty Alpaca keys
    with pytest.raises(ValueError, match="QA_ALPACA"):
        build_adapters(cfg)


def test_live_mode_builds_alpaca_adapters():
    pytest.importorskip("alpaca")  # live SDK; skipped in the offline CI image
    from new_pipeline.adapters.broker_alpaca import AlpacaBroker
    from new_pipeline.adapters.market_alpaca import AlpacaMarketDataSource
    from new_pipeline.adapters.news_alpaca import AlpacaNewsSource

    cfg = _cfg_with_mode("paper")
    cfg.alpaca.api_key = "dummy_key"
    cfg.alpaca.secret_key = "dummy_secret"
    bundle = build_adapters(cfg)

    assert isinstance(bundle.market_data, AlpacaMarketDataSource)
    assert isinstance(bundle.news, AlpacaNewsSource)
    assert isinstance(bundle.broker, AlpacaBroker)
    assert isinstance(bundle.llm, FakeLLMClient)  # LLM stays fake until Ollama is configured


def test_unknown_mode_raises():
    with pytest.raises(ValueError, match="unknown run_mode"):
        build_adapters(_cfg_with_mode("banana"))


def test_build_llm_client_selects_ollama_when_fusion_live(monkeypatch):
    from new_pipeline.adapters.factory import build_llm_client
    from new_pipeline.adapters.llm_ollama import OllamaLLMClient
    from new_pipeline.config import reload_config

    monkeypatch.setenv("QA_FUSION__ENABLED", "true")
    cfg = reload_config()
    assert isinstance(build_llm_client(cfg), OllamaLLMClient)

    cfg.fusion.enabled = False  # explicit flip back -> deterministic fake
    assert isinstance(build_llm_client(cfg), FakeLLMClient)

    cfg.fusion.enabled = True
    cfg.fusion.ollama_endpoint = ""  # enabled but no endpoint -> fake
    assert isinstance(build_llm_client(cfg), FakeLLMClient)


def test_pipeline_resolves_live_market_data_from_run_mode(monkeypatch, tmp_path):
    """run_offline_pipeline pulls the live-mode market source when fusion is off."""
    from new_pipeline.adapters import FakeMarketDataSource
    from new_pipeline.config import reload_config

    captured = {}

    def fake_build_adapters(cfg):
        captured["called"] = True
        bundle = build_adapters(_cfg_with_mode("offline"))  # a real offline bundle
        return bundle

    monkeypatch.setenv("QA_SYSTEM__RUN_MODE", "paper")
    monkeypatch.setenv("QA_ALPACA__API_KEY", "k")
    monkeypatch.setenv("QA_ALPACA__SECRET_KEY", "s")
    reload_config()
    import new_pipeline.adapters.factory as factory_module

    monkeypatch.setattr(factory_module, "build_adapters", fake_build_adapters)

    from new_pipeline.tournament.pipeline import run_offline_pipeline

    # Intercept before any heavy work: the frame builder gets the resolved source.
    def spy_frame(symbols, sectors, start, end, source, cfg, **kwargs):
        captured["source"] = source
        raise RuntimeError("stop after source resolution")

    monkeypatch.setattr("new_pipeline.tournament.pipeline.build_training_frame", spy_frame)
    try:
        run_offline_pipeline(tmp_path)
    except RuntimeError:
        pass
    assert captured.get("called"), "live run_mode should build the adapter bundle"
    assert isinstance(captured["source"], FakeMarketDataSource)  # from the injected bundle
