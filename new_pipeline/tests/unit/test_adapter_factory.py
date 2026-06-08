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


def test_live_mode_is_not_wired_yet():
    with pytest.raises(NotImplementedError, match="live adapters"):
        build_adapters(_cfg_with_mode("live"))


def test_unknown_mode_raises():
    with pytest.raises(ValueError, match="unknown run_mode"):
        build_adapters(_cfg_with_mode("banana"))
