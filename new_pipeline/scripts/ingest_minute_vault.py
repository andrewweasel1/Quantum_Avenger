"""Resumable minute-bar vault ingest for the intraday stack.

Mirrors the short-volume/news vault pattern: one parquet per (symbol, month)
under ``<vault_dir>/by_symbol_month/``, skip-if-exists resume, so container
reclaims and rate limits only ever cost a re-run, never lost work. Fetches are
BATCHED across symbols per month (one multi-symbol request per ~100 names;
the SDK auto-paginates), which is an order of magnitude fewer requests than
per-symbol loops at Liquid-scale.

Empty months (symbol not yet listed / delisted) write an empty-schema parquet
marker so resume never refetches them.

Also owns the session-calendar fixture refresh (``--refresh-calendar``): the
exchange calendar (early closes included) is the authority every flat-by-close
decision keys off.

Usage:
  python -m new_pipeline.scripts.ingest_minute_vault \
      --start 2024-08 --end 2026-08 [--vault-dir ...] [--symbols AAPL,MSFT]
  python -m new_pipeline.scripts.ingest_minute_vault --refresh-calendar
"""

from __future__ import annotations

import argparse
import os
import time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import polars as pl
from new_pipeline.config import get_config
from new_pipeline.intraday.calendar import DEFAULT_FIXTURE, fetch_calendar, write_fixture
from new_pipeline.intraday.data import months_between, vault_file

_EMPTY_SCHEMA = {
    "ts": pl.Datetime("us", "UTC"), "open": pl.Float64, "high": pl.Float64,
    "low": pl.Float64, "close": pl.Float64, "volume": pl.Int64, "vwap": pl.Float64,
}


def _month_bounds(year: int, month: int) -> tuple[datetime, datetime]:
    start = datetime(year, month, 1, tzinfo=UTC)
    end = (datetime(year + 1, 1, 1, tzinfo=UTC) if month == 12
           else datetime(year, month + 1, 1, tzinfo=UTC))
    return start, end - timedelta(microseconds=1)


def _write_symbol_month(vault_dir: Path, symbol: str, year: int, month: int,
                        bars) -> None:
    out = vault_file(vault_dir, symbol, year, month)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not bars:
        pl.DataFrame(schema=_EMPTY_SCHEMA).write_parquet(out)
        return
    pl.DataFrame({
        "ts": [b.ts for b in bars],
        "open": [b.open for b in bars],
        "high": [b.high for b in bars],
        "low": [b.low for b in bars],
        "close": [b.close for b in bars],
        "volume": [b.volume for b in bars],
        "vwap": [b.vwap for b in bars],
    }).with_columns(pl.col("ts").dt.convert_time_zone("UTC")).write_parquet(out)


def _segment_symbols(cfg) -> list[str]:
    from new_pipeline.adapters import StaticUniverseProvider

    path = Path(cfg.data.universe_path) if cfg.data.universe_path else None
    universe = StaticUniverseProvider(path)
    segments = set(cfg.intraday.universe_segments)
    return sorted(t for t, sector in universe.sectors().items() if sector in segments)


def ingest(source, symbols: list[str], start: date, end: date, vault_dir: Path,
           sleep: float, batch: int = 100) -> dict:
    tally = {"fetched": 0, "cached": 0, "empty": 0}
    months = months_between(start, end)
    for i, (year, month) in enumerate(months):
        missing = [s for s in symbols if not vault_file(vault_dir, s, year, month).exists()]
        tally["cached"] += len(symbols) - len(missing)
        for j in range(0, len(missing), batch):
            chunk = missing[j:j + batch]
            m_start, m_end = _month_bounds(year, month)
            by_symbol = source.history_minutes(chunk, m_start, m_end)
            for symbol in chunk:
                bars = by_symbol.get(symbol, [])
                _write_symbol_month(vault_dir, symbol, year, month, bars)
                tally["fetched" if bars else "empty"] += 1
            time.sleep(sleep)
        print(f"[{i + 1}/{len(months)}] {year}-{month:02d}: {tally}", flush=True)
    return tally


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--start", help="YYYY-MM first month (default: history_months back)")
    parser.add_argument("--end", help="YYYY-MM last month (default: current month)")
    parser.add_argument("--vault-dir", default=None)
    parser.add_argument("--symbols", help="comma list override (smokes); default: segment universe")
    parser.add_argument("--sleep", type=float, default=0.3, help="pause between batched requests")
    parser.add_argument("--bar-minutes", type=int, default=None)
    parser.add_argument("--refresh-calendar", action="store_true",
                        help="fetch the exchange calendar fixture (2016..2027) and exit")
    args = parser.parse_args()

    cfg = get_config()
    api_key = os.environ.get("QA_ALPACA__API_KEY", "")
    secret = os.environ.get("QA_ALPACA__SECRET_KEY", "")
    if not api_key or not secret:
        raise SystemExit("QA_ALPACA__API_KEY / QA_ALPACA__SECRET_KEY required")

    if args.refresh_calendar:
        sessions = fetch_calendar(api_key, secret, date(2016, 1, 1), date(2027, 12, 31))
        n = write_fixture(sessions)
        print(f"calendar fixture: {n} sessions -> {DEFAULT_FIXTURE}")
        return

    from new_pipeline.adapters.market_alpaca import AlpacaIntradayDataSource

    vault_dir = Path(args.vault_dir or cfg.intraday.vault_dir)
    today = date.today()
    if args.end:
        end_y, end_m = map(int, args.end.split("-"))
    else:
        end_y, end_m = today.year, today.month
    if args.start:
        start_y, start_m = map(int, args.start.split("-"))
    else:
        back = cfg.intraday.history_months - 1
        start_y, start_m = end_y - (back // 12), end_m - (back % 12)
        if start_m < 1:
            start_y, start_m = start_y - 1, start_m + 12

    symbols = (args.symbols.split(",") if args.symbols else _segment_symbols(cfg))
    source = AlpacaIntradayDataSource(
        api_key, secret, feed=cfg.alpaca.data_feed,
        minutes=args.bar_minutes or cfg.intraday.bar_minutes)
    print(f"minute vault: {len(symbols)} symbols, "
          f"{start_y}-{start_m:02d}..{end_y}-{end_m:02d} -> {vault_dir}")
    tally = ingest(source, symbols, date(start_y, start_m, 1), date(end_y, end_m, 1),
                   vault_dir, sleep=args.sleep)
    print("done:", tally)


if __name__ == "__main__":
    main()
