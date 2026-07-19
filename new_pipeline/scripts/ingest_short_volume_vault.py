"""Resumable FINRA Reg SHO daily short-volume vault ingest.

Fetches one consolidated short-volume file per trading day, filters to the
universe, and writes ``<vault_dir>/by_date/<YYYYMMDD>.csv`` the moment it
arrives (already-present days are skipped, so an interrupted run resumes for
free). Merges into ``<vault_dir>/<out>`` in the ``date,ticker,short_volume,
total_volume`` schema :func:`new_pipeline.data.short_volume.attach_short_volume`
consumes. The CDN keeps a rolling ~8-year window; older days (and holidays) 403
and are recorded as empty — the backtest neutral-fills those dates.

    python -m new_pipeline.scripts.ingest_short_volume_vault \
        --universe new_pipeline/data/universe/sp500_pit.csv \
        --start 2018-08-01 --end 2025-12-31 \
        --vault-dir ./data/short_volume
"""

import argparse
import csv
import time
import urllib.request
from datetime import date
from pathlib import Path

from new_pipeline.adapters.universe_static import StaticUniverseProvider
from new_pipeline.data.finra_short_volume import (
    RECORD_COLUMNS,
    daily_url,
    parse_daily_file,
    trading_days,
)

_UA = "Quantum Avenger Research (contact: research@example.com)"


def fetch_text(url: str) -> str | None:  # pragma: no cover - egress
    """GET a daily file; None on 403/404 (before the rolling window, or holiday)."""
    request = urllib.request.Request(url, headers={"User-Agent": _UA})
    try:
        with urllib.request.urlopen(request, timeout=60) as resp:
            return resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        if exc.code in (403, 404):
            return None
        raise


def write_day_csv(path: Path, records: list[dict]) -> None:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, RECORD_COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def merge_vault(by_date_dir: Path, out_path: Path) -> int:
    rows = []
    for part in sorted(by_date_dir.glob("*.csv")):
        with open(part, encoding="utf-8", newline="") as handle:
            rows.extend(csv.DictReader(handle))
    rows.sort(key=lambda r: (r["ticker"], r["date"]))
    with open(out_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, RECORD_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def main() -> None:  # pragma: no cover - egress orchestration around tested helpers
    parser = argparse.ArgumentParser(description="Resumable FINRA short-volume vault ingest")
    parser.add_argument("--universe", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--vault-dir", default="new_pipeline/data/short_volume")
    parser.add_argument("--out", default="sp500_short_volume.csv")
    parser.add_argument("--sleep", type=float, default=0.1)
    args = parser.parse_args()

    universe = set(StaticUniverseProvider(Path(args.universe)).sectors())
    start, end = date.fromisoformat(args.start), date.fromisoformat(args.end)
    vault = Path(args.vault_dir)
    by_date = vault / "by_date"
    by_date.mkdir(parents=True, exist_ok=True)

    days = trading_days(start, end)
    tally = {"days": 0, "cached": 0, "empty": 0, "rows": 0}
    for n, day in enumerate(days, 1):
        out = by_date / f"{day.strftime('%Y%m%d')}.csv"
        if out.exists():
            tally["cached"] += 1
            continue
        text = fetch_text(daily_url(day))
        time.sleep(args.sleep)
        records = parse_daily_file(text, universe) if text else []
        write_day_csv(out, records)
        tally["days"] += 1
        tally["rows"] += len(records)
        if not records:
            tally["empty"] += 1
        if n % 100 == 0:
            print(f"[{n}/{len(days)}] {tally}", flush=True)

    total = merge_vault(by_date, vault / args.out)
    covered = len({r for part in by_date.glob("*.csv")
                   for r in _tickers(part)})
    print(f"merged {total} rows -> {vault / args.out} ({covered} tickers)", flush=True)


def _tickers(part: Path) -> set[str]:  # pragma: no cover
    with open(part, encoding="utf-8", newline="") as handle:
        return {row["ticker"] for row in csv.DictReader(handle)}


if __name__ == "__main__":  # pragma: no cover
    main()
