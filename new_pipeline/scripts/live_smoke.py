"""Live Alpaca paper-trading smoke test.

Confirms connectivity + order submission end to end: prints the account, submits
a tiny order for one symbol, and prints the resulting positions. Requires
QA_ALPACA__API_KEY / QA_ALPACA__SECRET_KEY and egress to
paper-api.alpaca.markets. Paper only.

  QA_ALPACA__API_KEY=... QA_ALPACA__SECRET_KEY=... PYTHONPATH=. \
      python new_pipeline/scripts/live_smoke.py --symbol AAPL --qty 1
"""

import argparse
import json

from new_pipeline.config import get_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Alpaca paper-trading smoke test")
    parser.add_argument("--symbol", default="AAPL")
    parser.add_argument("--qty", type=int, default=1)
    parser.add_argument("--limit-price", type=float, default=None)
    args = parser.parse_args()

    cfg = get_config()
    if not (cfg.alpaca.api_key and cfg.alpaca.secret_key):
        raise SystemExit("Set QA_ALPACA__API_KEY and QA_ALPACA__SECRET_KEY first.")
    if not cfg.alpaca.paper:
        raise SystemExit("Refusing to run the smoke test against a live-money account.")

    from new_pipeline.adapters.broker_alpaca import AlpacaBroker

    broker = AlpacaBroker(cfg.alpaca.api_key, cfg.alpaca.secret_key, paper=True)
    print("account:", json.dumps(broker.account(), indent=2))
    print("positions before:", broker.get_positions())
    order = {"symbol": args.symbol, "qty": args.qty, "side": "buy", "tif": "day"}
    if args.limit_price is not None:
        order["limit_price"] = args.limit_price
    print("order receipt:", json.dumps(broker.submit_order(order), indent=2))
    print("positions after:", broker.get_positions())


if __name__ == "__main__":
    main()
