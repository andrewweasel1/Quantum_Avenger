"""Resumable GDELT news-vault ingest for a universe.

Fetch is the expensive, rate-limited, interruptible part of a news-driven run —
so it is decoupled from the backtest and made restart-proof: each symbol's
headlines land in their own ``<vault_dir>/by_symbol/<TICKER>.parquet`` the
moment they arrive, already-present symbols are skipped on re-run, and a final
merge writes the single ``news_vault.parquet`` that ``VaultNewsSource`` (the
``news.providers: ["vault"]`` backend) replays with zero network.

    python -m new_pipeline.scripts.ingest_gdelt_vault \
        --start 2021-01-01 --end 2024-12-31 \
        --universe new_pipeline/data/universe/sp500.csv \
        --vault-dir ./data/raw/news --limit 250

Re-run after any interruption; it picks up where it left off.
"""

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

_COLUMNS = ["timestamp", "ticker", "headline"]


def ingest_symbol(source, symbol: str, start: date, end: date, out_dir: Path) -> str:
    """Fetch one symbol into its own parquet; 'cached' if already present."""
    out = out_dir / f"{symbol.replace('/', '_').replace('.', '_')}.parquet"
    if out.exists():
        return "cached"
    try:
        items = source.fetch(symbol, start, end)
    except Exception as exc:
        print(f"  {symbol}: SKIP ({type(exc).__name__}: {str(exc)[:80]})", flush=True)
        return "skipped"
    frame = pd.DataFrame(
        [{"timestamp": i.timestamp, "ticker": i.symbol, "headline": i.headline} for i in items],
        columns=_COLUMNS,
    )
    frame.to_parquet(out, index=False)
    print(f"  {symbol}: {len(frame)} headlines", flush=True)
    return "fetched"


def merge_vault(by_symbol_dir: Path, vault_path: Path) -> int:
    parts = sorted(by_symbol_dir.glob("*.parquet"))
    frames = [pd.read_parquet(p) for p in parts]
    merged = (
        pd.concat(frames, ignore_index=True)
        if frames
        else pd.DataFrame(columns=_COLUMNS)
    )
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(vault_path, index=False)
    return len(merged)


def main() -> None:
    parser = argparse.ArgumentParser(description="Resumable GDELT news-vault ingest")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--universe", default="")
    parser.add_argument("--vault-dir", default="./data/raw/news")
    parser.add_argument("--limit", type=int, default=250)
    parser.add_argument("--min-interval", type=float, default=5.0)
    args = parser.parse_args()

    from new_pipeline.adapters.news_gdelt import GdeltNewsSource
    from new_pipeline.adapters.universe_static import StaticUniverseProvider

    universe = StaticUniverseProvider(Path(args.universe) if args.universe else None)
    source = GdeltNewsSource(
        universe.aliases(),
        limit=args.limit,
        min_interval=args.min_interval,
        retry_attempts=2,  # in a resumable ingest a re-run is cheaper than long backoffs
        retry_backoff=45.0,
    )
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    vault_dir = Path(args.vault_dir)
    by_symbol = vault_dir / "by_symbol"
    by_symbol.mkdir(parents=True, exist_ok=True)

    symbols = sorted(universe.sectors())
    tallies = {"fetched": 0, "cached": 0, "skipped": 0}
    for n, symbol in enumerate(symbols, 1):
        outcome = ingest_symbol(source, symbol, start, end, by_symbol)
        tallies[outcome] += 1
        if n % 25 == 0:
            print(f"[{n}/{len(symbols)}] {tallies}", flush=True)

    total = merge_vault(by_symbol, vault_dir / "news_vault.parquet")
    print(f"DONE {tallies} -> news_vault.parquet with {total} headlines", flush=True)


if __name__ == "__main__":
    main()
