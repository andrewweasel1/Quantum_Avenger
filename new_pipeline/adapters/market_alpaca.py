"""Live Alpaca market-data adapter (``MarketDataSource``).

Wraps alpaca-py's ``StockHistoricalDataClient`` behind the project's ABC, mapping
Alpaca daily bars to the internal :class:`Bar`. Built only for a live
``run_mode`` (offline runs use the deterministic fake), so this module — and the
``alpaca`` import — is loaded lazily by the adapter factory. Requires egress to
``data.alpaca.markets`` at call time; the free IEX feed is the default.
"""

from datetime import date, datetime, time

from alpaca.data.enums import Adjustment, DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from new_pipeline.adapters.base import Bar, MarketDataSource


class AlpacaMarketDataSource(MarketDataSource):
    def __init__(self, api_key, secret_key, feed="iex", adjustment="all", client=None):
        self._client = client or StockHistoricalDataClient(api_key, secret_key)
        self._feed = DataFeed(feed)
        self._adjustment = Adjustment(adjustment)

    def history(self, symbol: str, start: date, end: date) -> list[Bar]:
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=datetime.combine(start, time.min),
            end=datetime.combine(end, time.max),
            feed=self._feed,
            adjustment=self._adjustment,
        )
        barset = self._client.get_stock_bars(request)
        bars = barset.data.get(symbol, []) if hasattr(barset, "data") else list(barset[symbol])
        return [
            Bar(
                day=bar.timestamp.date(),
                open=float(bar.open),
                high=float(bar.high),
                low=float(bar.low),
                close=float(bar.close),
                volume=int(bar.volume),
            )
            for bar in bars
        ]
