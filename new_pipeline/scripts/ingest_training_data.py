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
    parser.add_argument(
        "--news-vault",
        action="store_true",
        help="materialize a point-in-time news vault (Parquet) before enriching",
    )
    args = parser.parse_args()

    configure_logging()
    cfg = get_config()
    bundle = build_adapters(cfg)
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)

    news_source = sentiment_engine = anonymizer = None
    if args.news:
        from new_pipeline.adapters.factory import build_news_source

        news_source = build_news_source(cfg, bundle.universe)
        sentiment_engine, anonymizer = bundle.sentiment_engine, bundle.anonymizer
        if args.news_vault:
            from pathlib import Path

            from new_pipeline.adapters.news_static import VaultNewsSource
            from new_pipeline.data.news_vault import ingest_news_vault

            vault_path = Path(cfg.news.vault_dir) / f"news_{args.start}_{args.end}.parquet"
            ingest_news_vault(news_source, bundle.universe, start, end, vault_path)
            news_source = VaultNewsSource(vault_path)

    summary = build_training_database(
        args.out,
        bundle.market_data,
        bundle.universe,
        start=start,
        end=end,
        cfg=cfg,
        news_source=news_source,
        sentiment_engine=sentiment_engine,
        anonymizer=anonymizer,
    )
    summary["columns"] = len(summary["columns"])
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
