"""Resumable fundamentals-vault ingest from SEC companyfacts.

Mirrors ``ingest_news_vault``: the rate-limited, interruptible fetch is
decoupled from the backtest. Each ticker's snapshots land in
``<vault_dir>/by_ticker/<TICKER>.csv`` the moment they arrive, already-present
tickers are skipped on re-run, and a final merge writes the single snapshots
CSV in the exact ``StaticFundamentalsSource`` schema — replayed with zero
network via ``fundamentals.fixture_path`` (the factory is vault-first in ALL
run modes).

    python -m new_pipeline.scripts.ingest_fundamentals_vault \
        --universe new_pipeline/data/universe/sp500_pit.csv \
        --start 2016-01-01 --end 2025-01-01 \
        --identity "Name email@example.com"

Departed tickers resolve via EDGAR company-name search seeded from the
universe's alias gazetteer; a ``--cik-overrides`` CSV (ticker,cik) is the
manual backstop. Unresolved names are recorded empty (the factor layer
neutral-fills them) — coverage is printed per sector so degradation is
visible, never silent.
"""

import argparse
import csv
import os
import time
from collections import defaultdict
from datetime import date
from pathlib import Path

from new_pipeline.data.fundamentals import ALL_FUNDAMENTAL_COLUMNS

_COLUMNS = ["ticker", "as_of", *ALL_FUNDAMENTAL_COLUMNS]


def write_ticker_csv(path: Path, ticker: str, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, _COLUMNS)
        writer.writeheader()
        for rec in records:
            writer.writerow({"ticker": ticker, **{k: rec.get(k) for k in _COLUMNS[1:]}})


def merge_vault(by_ticker_dir: Path, out_path: Path) -> int:
    """Concatenate per-ticker CSVs into the StaticFundamentalsSource fixture,
    sorted by (ticker, as_of)."""
    rows: list[dict] = []
    for part in sorted(by_ticker_dir.glob("*.csv")):
        with open(part, encoding="utf-8", newline="") as handle:
            rows.extend(csv.DictReader(handle))
    rows.sort(key=lambda r: (r["ticker"], r["as_of"]))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, _COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def coverage_table(universe, covered: set[str]) -> list[tuple[str, int, int]]:
    """(sector, covered, total) rows for the printed coverage report."""
    per_sector: dict[str, list[str]] = defaultdict(list)
    for ticker, sector in universe.sectors().items():
        per_sector[sector].append(ticker)
    return sorted(
        (sector, sum(1 for t in tickers if t in covered), len(tickers))
        for sector, tickers in per_sector.items()
    )


def load_cik_overrides(path: str) -> dict[str, int]:
    if not path:
        return {}
    with open(path, encoding="utf-8", newline="") as handle:
        return {r["ticker"].strip().upper(): int(r["cik"]) for r in csv.DictReader(handle)}


def main() -> None:  # pragma: no cover - egress orchestration around tested helpers
    from new_pipeline.adapters.universe_static import StaticUniverseProvider
    from new_pipeline.data.edgar_companyfacts import (
        COMPANYFACTS_URL,
        http_fetcher,
        load_ticker_map,
        resolve_cik,
        snapshot_records,
    )

    parser = argparse.ArgumentParser(description="Resumable fundamentals-vault ingest")
    parser.add_argument("--universe", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--identity", default=os.environ.get("QA_FUNDAMENTALS__EDGAR_IDENTITY", ""))
    parser.add_argument("--vault-dir", default="new_pipeline/data/fundamentals")
    parser.add_argument("--out", default="sp500_snapshots.csv")
    parser.add_argument("--cik-overrides", default="")
    parser.add_argument("--sleep", type=float, default=0.15)  # SEC guidance ~10 req/s
    args = parser.parse_args()
    if not args.identity:
        raise SystemExit("--identity (or QA_FUNDAMENTALS__EDGAR_IDENTITY) is required by SEC")

    universe = StaticUniverseProvider(Path(args.universe))
    names = {t: (aliases[0] if aliases else "") for t, aliases in universe.aliases().items()}
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    vault = Path(args.vault_dir)
    by_ticker = vault / "by_ticker"
    by_ticker.mkdir(parents=True, exist_ok=True)

    fetch_json, fetch_text = http_fetcher(args.identity)
    ticker_map = load_ticker_map(fetch_json)
    overrides = load_cik_overrides(args.cik_overrides)

    tickers = sorted(universe.sectors())
    tallies = {"fetched": 0, "cached": 0, "unresolved": 0, "empty": 0}
    for n, ticker in enumerate(tickers, 1):
        out = by_ticker / f"{ticker.replace('/', '_').replace('.', '_')}.csv"
        if out.exists():
            tallies["cached"] += 1
            continue
        cik = overrides.get(ticker) or resolve_cik(
            ticker, names.get(ticker, ""), ticker_map, fetch_text
        )
        time.sleep(args.sleep)
        if cik is None:
            print(f"  {ticker}: UNRESOLVED (no CIK)", flush=True)
            write_ticker_csv(out, ticker, [])
            tallies["unresolved"] += 1
            continue
        try:
            facts = fetch_json(COMPANYFACTS_URL.format(cik=cik))
            records = snapshot_records(facts, start, end)
        except Exception as exc:
            print(f"  {ticker}: SKIP ({type(exc).__name__}: {str(exc)[:70]})", flush=True)
            write_ticker_csv(out, ticker, [])
            tallies["empty"] += 1
            continue
        write_ticker_csv(out, ticker, records)
        tallies["fetched" if records else "empty"] += 1
        if records:
            print(f"  {ticker}: {len(records)} snapshots", flush=True)
        if n % 50 == 0:
            print(f"[{n}/{len(tickers)}] {tallies}", flush=True)
        time.sleep(args.sleep)

    total = merge_vault(by_ticker, vault / args.out)
    covered = set()
    for part in by_ticker.glob("*.csv"):
        with open(part, encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                covered.add(row["ticker"])
                break
    print(f"DONE {tallies} -> {args.out} with {total} snapshots", flush=True)
    print("coverage by sector (covered/total):", flush=True)
    for sector, have, tot in coverage_table(universe, covered):
        print(f"  {sector:26s} {have:3d}/{tot}", flush=True)


if __name__ == "__main__":
    main()
