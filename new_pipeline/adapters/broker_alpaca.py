"""Live Alpaca broker adapter (``BrokerAdapter``).

Wraps alpaca-py's ``TradingClient`` (paper by default) behind the project's
broker ABC. ``submit_order`` builds a market or limit order from the same dict
the orchestrator hands the fake broker and maps the Alpaca ``Order`` back to the
receipt shape the orchestrator/trade-log expect. Loaded lazily for a live
``run_mode``; requires egress to ``paper-api.alpaca.markets``.
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest

from new_pipeline.execution.broker import BrokerAdapter

_SIDE = {"buy": OrderSide.BUY, "sell": OrderSide.SELL}
_TIF = {
    "day": TimeInForce.DAY,
    "gtc": TimeInForce.GTC,
    "ioc": TimeInForce.IOC,
    "fok": TimeInForce.FOK,
    "opg": TimeInForce.OPG,
    "cls": TimeInForce.CLS,
}


class AlpacaBroker(BrokerAdapter):
    def __init__(self, api_key, secret_key, paper: bool = True, client=None):
        self._client = client or TradingClient(api_key, secret_key, paper=paper)

    def submit_order(self, order: dict) -> dict:
        symbol = str(order["symbol"])
        # Fractional quantities must survive to the API: int()-flooring here
        # turned the book's sub-share rebalance trims into qty-0 rejects and
        # silently re-introduced the long-leg rounding tilt the sizing fix
        # was meant to kill. Whole counts stay int for exact API formatting.
        qty_raw = float(order.get("qty", 0))
        qty = int(qty_raw) if qty_raw.is_integer() else round(qty_raw, 3)
        side = _SIDE[str(order.get("side", "buy")).lower()]
        tif = _TIF.get(str(order.get("tif", "day")).lower(), TimeInForce.DAY)
        limit_price = order.get("limit_price")
        if limit_price is not None:
            request = LimitOrderRequest(
                symbol=symbol, qty=qty, side=side, time_in_force=tif,
                limit_price=round(float(limit_price), 2),
            )
        else:
            request = MarketOrderRequest(symbol=symbol, qty=qty, side=side, time_in_force=tif)

        placed = self._client.submit_order(order_data=request)
        return {
            "status": _value(placed.status),
            "order_id": str(placed.id),
            "symbol": placed.symbol,
            "qty": float(placed.qty) if placed.qty is not None else float(qty),
            "side": _value(placed.side),
            "limit_price": float(placed.limit_price) if placed.limit_price is not None else None,
            "filled_avg_price": float(placed.filled_avg_price) if placed.filled_avg_price else 0.0,
        }

    def get_positions(self) -> dict[str, float]:
        positions: dict[str, float] = {}
        for pos in self._client.get_all_positions():
            # Alpaca already signs qty (shorts are negative); negating again on
            # side=="short" double-negated and reported shorts as longs — which
            # would poison the next rebalance's order diff.
            positions[pos.symbol] = float(pos.qty)
        return positions

    def account(self) -> dict:
        """Account snapshot — confirms connectivity and that it's the paper account."""
        acct = self._client.get_account()
        return {
            "status": _value(acct.status),
            "cash": float(acct.cash),
            "equity": float(acct.equity),
            "buying_power": float(acct.buying_power),
        }


def _value(enum_or_str) -> str:
    """Unwrap an Alpaca enum (``.value``) or pass a plain string through."""
    return getattr(enum_or_str, "value", str(enum_or_str))
