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
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

from new_pipeline.adapters.base import Bar, MarketDataSource, MinuteBar


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


class AlpacaIntradayDataSource:
    """Minute-bar history for the intraday stack. SIP feed is the working
    default: minute coverage on IEX is a small fraction of tape volume, which
    poisons every volume-conditioned decision (participation caps, RVOL).
    Multi-symbol batched requests; the SDK auto-paginates at 10k bars/page.
    Bar timestamps are the bar OPEN time, tz-aware UTC, passed through
    unmodified — session semantics belong to the exchange calendar."""

    BATCH_SIZE = 100  # symbols per request; keeps URLs sane, pagination does the rest

    def __init__(self, api_key, secret_key, feed="sip", adjustment="all",
                 minutes: int = 1, client=None):
        self._client = client or StockHistoricalDataClient(api_key, secret_key)
        self._feed = DataFeed(feed)
        self._adjustment = Adjustment(adjustment)
        self._timeframe = TimeFrame(minutes, TimeFrameUnit.Minute)

    def history_minutes(self, symbols: list[str], start: datetime,
                        end: datetime) -> dict[str, list[MinuteBar]]:
        out: dict[str, list[MinuteBar]] = {}
        for i in range(0, len(symbols), self.BATCH_SIZE):
            batch = symbols[i:i + self.BATCH_SIZE]
            request = StockBarsRequest(
                symbol_or_symbols=batch,
                timeframe=self._timeframe,
                start=start,
                end=end,
                feed=self._feed,
                adjustment=self._adjustment,
            )
            barset = self._client.get_stock_bars(request)
            data = barset.data if hasattr(barset, "data") else barset
            for symbol in batch:
                out[symbol] = [
                    MinuteBar(
                        ts=bar.timestamp,
                        open=float(bar.open),
                        high=float(bar.high),
                        low=float(bar.low),
                        close=float(bar.close),
                        volume=int(bar.volume),
                        vwap=float(bar.vwap) if bar.vwap is not None else float(bar.close),
                    )
                    for bar in data.get(symbol, [])
                ]
        return out
