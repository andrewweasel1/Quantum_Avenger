"""Contract between the live adapters and the *installed* SDKs (no network).

The other adapter tests inject MagicMock clients, which proves our mapping logic
but would hide a renamed class or changed constructor in a new alpaca-py release.
These tests run only where the real SDKs are installed (a live host, or a dev
box after `pip install -r requirements-live.txt`) and construct real clients
with dummy credentials — alpaca-py doesn't dial out at construction time.
"""

import datetime

import pytest

alpaca = pytest.importorskip("alpaca")


def test_alpaca_clients_construct_and_expose_adapter_methods():
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.historical.news import NewsClient
    from alpaca.trading.client import TradingClient

    market = StockHistoricalDataClient("dummy-key", "dummy-secret")
    assert callable(market.get_stock_bars)

    trading = TradingClient("dummy-key", "dummy-secret", paper=True)
    for method in ("submit_order", "get_all_positions", "get_account"):
        assert callable(getattr(trading, method))

    news = NewsClient("dummy-key", "dummy-secret")
    assert callable(news.get_news)


def test_request_models_accept_the_adapter_kwargs():
    from alpaca.data.requests import NewsRequest, StockBarsRequest
    from alpaca.data.timeframe import TimeFrame
    from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest

    start, end = datetime.datetime(2024, 1, 2), datetime.datetime(2024, 1, 10)
    StockBarsRequest(symbol_or_symbols="AAPL", timeframe=TimeFrame.Day, start=start, end=end)
    NewsRequest(symbols="AAPL", start=start, end=end, limit=10)
    LimitOrderRequest(symbol="AAPL", qty=1, side="buy", time_in_force="day", limit_price=100.0)
    MarketOrderRequest(symbol="AAPL", qty=1, side="buy", time_in_force="day")


def test_edgartools_importable_when_installed():
    edgar = pytest.importorskip("edgar")
    assert hasattr(edgar, "Company") or hasattr(edgar, "set_identity")
