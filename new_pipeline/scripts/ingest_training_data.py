"""Build a training database from Alpaca historical data (live) or fakes (offline).

  PYTHONPATH=. QA_SYSTEM__RUN_MODE=live QA_ALPACA__API_KEY=... QA_ALPACA__SECRET_KEY=... \
      python new_pipeline/scripts/ingest_training_data.py \
      --start 2023-06-01 --end 2023-12-31 --out data/processed/training.parquet --news

Live mode pulls real bars (+ optional news sentiment) from Alpaca and needs an
allowlisted host; any offline run_mode uses the deterministic fakes.
"""

import argparse
import json
from datetime import date

from new_pipeline.adapters.factory import build_adapters
from new_pipeline.config import get_config
from new_pipeline.core.logging import configure_logging
from new_pipeline.data.training_db import build_training_database


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Quantum Avenger training database")
    parser.add_argument("--start", default="2023-06-01")
    parser.add_argument("--end", default="2023-12-31")
    parser.add_argument("--out", default="data/processed/training.parquet")
    parser.add_argument("--news", action="store_true", help="enrich rows with news sentiment")
    args = parser.parse_args()

    configure_logging()
    cfg = get_config()
    bundle = build_adapters(cfg)
    summary = build_training_database(
        args.out,
        bundle.market_data,
        bundle.universe,
        start=date.fromisoformat(args.start),
        end=date.fromisoformat(args.end),
        cfg=cfg,
        news_source=bundle.news if args.news else None,
        llm=bundle.llm if args.news else None,
    )
    summary["columns"] = len(summary["columns"])
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
