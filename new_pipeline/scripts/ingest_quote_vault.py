"""Build the measured quote vault: NBBO half-spread + displayed depth.

One parquet per month under ``<vault_dir>/by_month/``, skip-if-exists resume,
mirroring the minute vault. Within a month we sample K short windows spread
across sessions AND across times of day, requesting quotes for symbols in
batches (the SIP quote endpoint takes a symbol list and auto-paginates), then
reduce to a per-symbol median half-spread and median touch notional.

Sampling rather than exhaustive capture is the deliberate trade: a full quote
history for 2,500 names over two years is billions of rows, while a 4x-biased
range estimator is what we are replacing. The approximation is disclosed in
intraday/quotes.py and recorded in every run manifest.

  python -m new_pipeline.scripts.ingest_quote_vault --start 2024-08 --end 2026-08
"""

from __future__ import annotations

import argparse
import os
import time
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import polars as pl

from new_pipeline.config import get_config
from new_pipeline.intraday.calendar import load_sessions
from new_pipeline.intraday.data import months_between
from new_pipeline.intraday.quotes import cell_file, summarize_quotes
from new_pipeline.intraday.universe import segment_symbols

# Minutes after the session open at which to sample: early, mid-morning,
# lunch, and the close-adjacent stretch, so a monthly median is not just a
# quiet-midday number.
SAMPLE_OFFSETS_MIN = (30, 120, 240, 355)
BATCH = 100


def _sample_windows(month_days: list[date], sessions: dict, k: int) -> list[datetime]:
    """K (session, time-of-day) sample points spread across the month."""
    if not month_days:
        return []
    picks = []
    step = max(len(month_days) // k, 1)
    for i in range(k):
        day = month_days[min(i * step, len(month_days) - 1)]
        offset = SAMPLE_OFFSETS_MIN[i % len(SAMPLE_OFFSETS_MIN)]
        start = sessions[day].open_utc + timedelta(minutes=offset)
        if start < sessions[day].close_utc:
            picks.append(start)
    return picks


def build_month(client, symbols: list[str], year: int, month: int,
                sessions: dict, window_s: int, k: int, sleep: float) -> pl.DataFrame:
    from alpaca.data.requests import StockQuotesRequest

    month_days = sorted(d for d in sessions if d.year == year and d.month == month)
    windows = _sample_windows(month_days, sessions, k)
    per_symbol: dict[str, list[dict]] = {}
    for start in windows:
        end = start + timedelta(seconds=window_s)
        for i in range(0, len(symbols), BATCH):
            batch = symbols[i:i + BATCH]
            try:
                data = client.get_stock_quotes(StockQuotesRequest(
                    symbol_or_symbols=batch, start=start, end=end, feed="sip")).data
            except Exception as exc:
                print(f"    window {start:%Y-%m-%d %H:%M} batch {i}: {exc}", flush=True)
                continue
            for symbol in batch:
                summary = summarize_quotes(data.get(symbol, []), symbol)
                if summary:
                    per_symbol.setdefault(symbol, []).append(summary)
            time.sleep(sleep)
    rows = []
    for symbol, samples in per_symbol.items():
        # Median ACROSS sample windows, so one wide moment cannot set the cell.
        halves = sorted(s["half_spread_bps"] for s in samples)
        touch = sorted(s["touch_notional"] for s in samples)
        rows.append({
            "symbol": symbol, "year": year, "month": month,
            "half_spread_bps": halves[len(halves) // 2],
            "touch_notional": touch[len(touch) // 2],
            "n_quotes": sum(s["n_quotes"] for s in samples),
        })
    return pl.DataFrame(rows) if rows else pl.DataFrame()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--start", required=True, help="YYYY-MM")
    parser.add_argument("--end", required=True, help="YYYY-MM")
    parser.add_argument("--vault-dir", default=None)
    parser.add_argument("--symbols", help="comma list override (smoke tests)")
    parser.add_argument("--windows", type=int, default=4, help="sample windows per month")
    parser.add_argument("--window-seconds", type=int, default=10)
    parser.add_argument("--sleep", type=float, default=0.15)
    args = parser.parse_args()

    cfg = get_config()
    api_key = os.environ.get("QA_ALPACA__API_KEY", "")
    secret = os.environ.get("QA_ALPACA__SECRET_KEY", "")
    if not api_key or not secret:
        raise SystemExit("QA_ALPACA__API_KEY / QA_ALPACA__SECRET_KEY required")

    from alpaca.data.historical import StockHistoricalDataClient
    client = StockHistoricalDataClient(api_key, secret)

    vault = Path(args.vault_dir or cfg.intraday.quote_vault_dir)
    symbols = args.symbols.split(",") if args.symbols else segment_symbols(cfg)
    sessions = load_sessions()
    sy, sm = map(int, args.start.split("-"))
    ey, em = map(int, args.end.split("-"))
    months = months_between(date(sy, sm, 1), date(ey, em, 1))
    print(f"quote vault: {len(symbols)} symbols, {len(months)} months -> {vault}")

    for idx, (year, month) in enumerate(months, 1):
        out = cell_file(vault, year, month)
        if out.exists():
            print(f"[{idx}/{len(months)}] {year}-{month:02d}: cached", flush=True)
            continue
        frame = build_month(client, symbols, year, month, sessions,
                            args.window_seconds, args.windows, args.sleep)
        out.parent.mkdir(parents=True, exist_ok=True)
        (frame if not frame.is_empty() else pl.DataFrame(schema={
            "symbol": pl.Utf8, "year": pl.Int64, "month": pl.Int64,
            "half_spread_bps": pl.Float64, "touch_notional": pl.Float64,
            "n_quotes": pl.Int64})).write_parquet(out)
        med = (round(float(frame["half_spread_bps"].median()), 2)
               if not frame.is_empty() else None)
        print(f"[{idx}/{len(months)}] {year}-{month:02d}: {frame.height} symbols, "
              f"median half-spread {med} bps", flush=True)
    print("done")


if __name__ == "__main__":
    main()


def _utc(*args) -> datetime:  # pragma: no cover - kept for interactive use
    return datetime(*args, tzinfo=UTC)
