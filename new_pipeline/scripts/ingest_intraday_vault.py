"""Resumable SIP 30-minute-bar vault for the S&P 500 PIT universe.

Feeds the intraday feasibility study: SIP intraday history reaches back to
2016-01 and is served for DELISTED names too (verified: TWTR), so the vault
rides the same externally-sourced, survivorship-free PIT fixture as the daily
pipeline — no new universe risk. Bars are split+dividend-adjusted
(``adjustment=all``) and include extended-hours prints; regular-session
filtering happens at study time (timestamps are UTC).

Chunked multi-symbol requests land in ``<vault>/chunks/<i>.parquet`` (existing
chunks are skipped -> interrupted runs resume) and merge into ``bars30m.parquet``.

    python -m new_pipeline.scripts.ingest_intraday_vault \
        --universe new_pipeline/data/universe/sp500_pit.csv \
        --start 2016-01-01 --end 2025-12-31 --vault-dir ./data/intraday_vault
"""

import argparse
import csv
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BARS_URL = "https://data.alpaca.markets/v2/stocks/bars"


def universe_symbols(universe_path: Path) -> list[str]:
    with open(universe_path, encoding="utf-8", newline="") as handle:
        return sorted({row["ticker"].strip() for row in csv.DictReader(handle)})


def chunk(symbols: list[str], size: int) -> list[list[str]]:
    return [symbols[i:i + size] for i in range(0, len(symbols), size)]


def _headers() -> dict:  # pragma: no cover - env plumbing
    return {
        "APCA-API-KEY-ID": os.environ.get("QA_ALPACA__API_KEY", ""),
        "APCA-API-SECRET-KEY": os.environ.get("QA_ALPACA__SECRET_KEY", ""),
    }


def _get_json(url: str, retries: int = 5):  # pragma: no cover - egress
    for attempt in range(retries):
        request = urllib.request.Request(url, headers=_headers())
        try:
            with urllib.request.urlopen(request, timeout=120) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                time.sleep(10.0 * (attempt + 1))
                continue
            if exc.code in (403, 404, 422):
                return None
            if attempt == retries - 1:
                raise
            time.sleep(3.0 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == retries - 1:
                return None
            time.sleep(3.0 * (attempt + 1))
    return None


def fetch_chunk(symbols, start, end, sleep) -> list[dict]:  # pragma: no cover - egress
    rows, token = [], None
    base = (
        f"{BARS_URL}?symbols={','.join(urllib.parse.quote(s) for s in symbols)}"
        f"&timeframe=30Min&adjustment=all&feed=sip&limit=10000"
        f"&start={start}T00:00:00Z&end={end}T23:59:59Z"
    )
    while True:
        url = base + (f"&page_token={urllib.parse.quote(token)}" if token else "")
        payload = _get_json(url)
        if payload is None:
            break
        for symbol, bars in (payload.get("bars") or {}).items():
            for bar in bars:
                rows.append({
                    "ticker": symbol, "ts": bar["t"], "open": bar["o"], "high": bar["h"],
                    "low": bar["l"], "close": bar["c"], "volume": float(bar["v"]),
                })
        token = payload.get("next_page_token")
        if not token:
            break
        time.sleep(sleep)
    return rows


def main() -> None:  # pragma: no cover - egress orchestration around tested helpers
    from concurrent.futures import ThreadPoolExecutor, as_completed

    import polars as pl

    parser = argparse.ArgumentParser(description="SIP 30-min bar vault for the PIT universe")
    parser.add_argument("--universe", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--vault-dir", default="data/intraday_vault")
    parser.add_argument("--chunk-size", type=int, default=25)
    parser.add_argument("--sleep", type=float, default=0.35)
    # 3 concurrent chunk workers ~= 90-100 req/min, well under Alpaca's 200/min.
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()

    vault = Path(args.vault_dir)
    chunks_dir = vault / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)
    symbols = universe_symbols(Path(args.universe))
    print(f"universe: {len(symbols)} symbols", flush=True)

    batches = chunk(symbols, args.chunk_size)
    todo = [(i, b) for i, b in enumerate(batches)
            if not (chunks_dir / f"{i:05d}.parquet").exists()]
    print(f"chunks: {len(batches)} total, {len(batches) - len(todo)} cached, "
          f"{len(todo)} to fetch", flush=True)

    schema = {"ticker": pl.Utf8, "ts": pl.Utf8, "open": pl.Float64, "high": pl.Float64,
              "low": pl.Float64, "close": pl.Float64, "volume": pl.Float64}

    def work(item):
        index, batch = item
        rows = fetch_chunk(batch, args.start, args.end, args.sleep)
        pl.DataFrame(rows, schema=schema).write_parquet(chunks_dir / f"{index:05d}.parquet")
        return index, len(rows)

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = [pool.submit(work, item) for item in todo]
        for future in as_completed(futures):
            index, n_rows = future.result()
            done += 1
            print(f"[chunk {index:05d} done, {n_rows:,} rows] {done}/{len(todo)}", flush=True)

    merged = pl.concat([pl.read_parquet(p) for p in sorted(chunks_dir.glob("*.parquet"))])
    merged = merged.with_columns(
        pl.col("ts").str.to_datetime("%Y-%m-%dT%H:%M:%SZ", time_zone="UTC")
    ).sort(["ticker", "ts"])
    merged.write_parquet(vault / "bars30m.parquet")
    print(f"merged {merged.height:,} bars, {merged['ticker'].n_unique()} tickers "
          f"-> {vault / 'bars30m.parquet'}", flush=True)


if __name__ == "__main__":  # pragma: no cover
    main()
