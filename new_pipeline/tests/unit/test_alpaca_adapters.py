from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

pytest.importorskip("alpaca")  # live SDK; skipped in the offline CI image

from new_pipeline.adapters.broker_alpaca import AlpacaBroker  # noqa: E402
from new_pipeline.adapters.market_alpaca import AlpacaMarketDataSource  # noqa: E402
from new_pipeline.adapters.news_alpaca import AlpacaNewsSource  # noqa: E402


def _bar(ts, close):
    return SimpleNamespace(
        timestamp=ts, open=close - 1, high=close + 1, low=close - 2, close=close, volume=1000
    )


def test_market_history_maps_bars_and_builds_request():
    client = MagicMock()
    client.get_stock_bars.return_value = SimpleNamespace(
        data={"AAPL": [_bar(datetime(2024, 1, 2, 9, 30), 100.0),
                       _bar(datetime(2024, 1, 3, 9, 30), 101.0)]}
    )
    source = AlpacaMarketDataSource("k", "s", client=client)
    bars = source.history("AAPL", date(2024, 1, 1), date(2024, 1, 31))

    assert [b.day for b in bars] == [date(2024, 1, 2), date(2024, 1, 3)]
    assert bars[0].close == 100.0 and bars[1].volume == 1000
    assert client.get_stock_bars.call_args.args[0].symbol_or_symbols == "AAPL"


def test_news_headlines_maps_articles():
    client = MagicMock()
    client.get_news.return_value = SimpleNamespace(
        data={"news": [SimpleNamespace(created_at=datetime(2024, 1, 2), headline="AAPL rallies")]}
    )
    source = AlpacaNewsSource("k", "s", client=client)
    items = source.headlines("AAPL", date(2024, 1, 2))

    assert items[0].headline == "AAPL rallies" and items[0].symbol == "AAPL"


def test_broker_market_order_and_positions():
    from alpaca.trading.requests import MarketOrderRequest

    client = MagicMock()
    client.submit_order.return_value = SimpleNamespace(
        status=SimpleNamespace(value="accepted"), id="abc-1", symbol="AAPL",
        qty="3", side=SimpleNamespace(value="buy"), limit_price=None, filled_avg_price=None,
    )
    client.get_all_positions.return_value = [
        SimpleNamespace(symbol="AAPL", qty="3", side=SimpleNamespace(value="long")),
        # real API contract (verified live 2026-07-22): qty is SIGNED for shorts
        SimpleNamespace(symbol="TSLA", qty="-2", side=SimpleNamespace(value="short")),
    ]
    broker = AlpacaBroker("k", "s", client=client)
    receipt = broker.submit_order({"symbol": "AAPL", "qty": 3, "side": "buy", "tif": "day"})

    assert receipt["order_id"] == "abc-1" and receipt["status"] == "accepted"
    assert receipt["qty"] == 3.0 and receipt["filled_avg_price"] == 0.0
    assert isinstance(client.submit_order.call_args.kwargs["order_data"], MarketOrderRequest)
    assert broker.get_positions() == {"AAPL": 3.0, "TSLA": -2.0}
    # fractional quantities survive to the API (int()-flooring made every
    # sub-share rebalance trim a qty-0 reject); whole floats submit as ints.
    broker.submit_order({"symbol": "AAPL", "qty": 0.494, "side": "sell", "tif": "day"})
    assert client.submit_order.call_args.kwargs["order_data"].qty == 0.494
    broker.submit_order({"symbol": "AAPL", "qty": 3.0, "side": "buy", "tif": "day"})
    assert client.submit_order.call_args.kwargs["order_data"].qty == 3


def test_broker_limit_order():
    from alpaca.trading.requests import LimitOrderRequest

    client = MagicMock()
    client.submit_order.return_value = SimpleNamespace(
        status="accepted", id="abc-2", symbol="AAPL", qty="1",
        side="buy", limit_price="101.5", filled_avg_price="101.5",
    )
    broker = AlpacaBroker("k", "s", client=client)
    receipt = broker.submit_order({"symbol": "AAPL", "qty": 1, "side": "buy", "limit_price": 101.5})

    request = client.submit_order.call_args.kwargs["order_data"]
    assert isinstance(request, LimitOrderRequest) and float(request.limit_price) == 101.5
    assert receipt["limit_price"] == 101.5 and receipt["filled_avg_price"] == 101.5


def test_broker_account_snapshot():
    client = MagicMock()
    client.get_account.return_value = SimpleNamespace(
        status="ACTIVE", cash="100000", equity="100500", buying_power="200000"
    )
    broker = AlpacaBroker("k", "s", client=client)
    assert broker.account() == {
        "status": "ACTIVE", "cash": 100000.0, "equity": 100500.0, "buying_power": 200000.0,
    }
