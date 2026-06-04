from datetime import date

from new_pipeline.adapters import (
    FakeBroker,
    FakeLLMClient,
    FakeMarketDataSource,
    FakeNewsSource,
)


def test_fake_llm_is_deterministic():
    llm = FakeLLMClient()
    first = llm.sentiment("Apple beats earnings")
    second = llm.sentiment("Apple beats earnings")
    assert first == second
    assert -1.0 <= first.score <= 1.0
    assert first.label in {"bullish", "bearish", "neutral"}


def test_fake_llm_verdict_stance():
    verdict = FakeLLMClient().verdict("some prompt")
    assert verdict.stance in {"BULLISH", "BEARISH", "NEUTRAL"}


def test_fake_market_data_well_formed_ohlc():
    bars = FakeMarketDataSource().history("AAPL", date(2024, 1, 1), date(2024, 1, 10))
    assert len(bars) == 10
    for bar in bars:
        assert bar.high >= max(bar.open, bar.close)
        assert bar.low <= min(bar.open, bar.close)
        assert bar.volume > 0


def test_fake_market_data_empty_for_reversed_range():
    bars = FakeMarketDataSource().history("AAPL", date(2024, 1, 10), date(2024, 1, 1))
    assert bars == []


def test_fake_news_returns_headline():
    items = FakeNewsSource().headlines("MSFT", date(2024, 6, 1))
    assert len(items) == 1
    assert "MSFT" in items[0].headline


def test_fake_broker_tracks_positions():
    broker = FakeBroker()
    receipt = broker.submit_order({"symbol": "AAPL", "qty": 10, "side": "buy"})
    assert receipt["status"] == "filled"
    broker.submit_order({"symbol": "AAPL", "qty": 4, "side": "sell"})
    assert broker.get_positions()["AAPL"] == 6.0
    assert len(broker.orders) == 2
