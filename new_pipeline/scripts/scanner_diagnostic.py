"""Scanner signal diagnostic: which candidate signals rank ORB trade outcomes?

Read-only. Rebuilds the session-daily aggregates + the causal signal menu over
a window, joins them to a committed trade ledger, and reports each signal's
per-session cross-sectional IC against realized per-trade GROSS basis points
(gross, not net: the question is which names carry edge before cost, since
cost is a separate, largely mechanical function of liquidity).

This spends NO trials — it is evidence for choosing which pre-registered
scanner variants to price in an official run, and it is disclosed as a look.

  python -m new_pipeline.scripts.scanner_diagnostic
      --ledger models/prod/evidence/orb_v1/intraday_orb_ledger.parquet
      --start 2024-09-01 --end 2026-07-31 [--combo 'k5|or_mid|none']
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, date, datetime
from pathlib import Path

import polars as pl
from new_pipeline.config import get_config
from new_pipeline.intraday.calendar import load_sessions
from new_pipeline.intraday.data import (
    filter_to_sessions,
    load_minutes,
    months_between,
    session_daily,
)
from new_pipeline.intraday.scanner import SIGNALS, apply_floors, build_signal_frame, signal_ic
from new_pipeline.intraday.universe import segment_symbols


def build_dailies(cfg, start: date, end: date) -> pl.DataFrame:
    sessions = load_sessions()
    symbols = segment_symbols(cfg)
    vault = Path(cfg.intraday.vault_dir)
    months = months_between(start, end)
    warm = ((months[0][0] - 1, 12) if months[0][1] == 1
            else (months[0][0], months[0][1] - 1))
    frames = []
    for year, month in [warm, *months]:
        w_start = datetime(year, month, 1, tzinfo=UTC)
        w_end = (datetime(year + 1, 1, 1, tzinfo=UTC) if month == 12
                 else datetime(year, month + 1, 1, tzinfo=UTC))
        chunk = filter_to_sessions(load_minutes(vault, symbols, w_start, w_end), sessions)
        if not chunk.is_empty():
            frames.append(session_daily(chunk))
    if not frames:
        raise SystemExit("no minute data — rehydrate the vault first")
    return pl.concat(frames).sort(["ticker", "date"])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--combo", default=None, help="restrict to one combo_key")
    parser.add_argument("--out", default=None, help="write the report JSON here")
    args = parser.parse_args()
    cfg = get_config()

    daily = build_dailies(cfg, date.fromisoformat(args.start), date.fromisoformat(args.end))
    signals = apply_floors(build_signal_frame(daily), cfg.intraday.min_adv_dollars,
                           cfg.intraday.min_price)
    print(f"dailies {daily.height} rows | signals {signals.height} rows "
          f"| eligible {int(signals['eligible'].sum())}")

    ledger = pl.read_parquet(args.ledger)
    if args.combo:
        ledger = ledger.filter(pl.col("combo_key") == args.combo)
    ledger = ledger.with_columns(
        (pl.col("shares") * pl.col("entry_px")).alias("_notional")
    ).with_columns(
        (pl.col("gross_pnl") / pl.col("_notional") * 1e4).alias("gross_bps"),
        (pl.col("net_pnl") / pl.col("_notional") * 1e4).alias("net_bps"),
        (pl.col("cost_dollars") / pl.col("_notional") * 1e4).alias("cost_bps"),
    )
    print(f"ledger {ledger.height} trades over {ledger['day'].n_unique()} sessions")

    report = {}
    for outcome in ("gross_bps", "cost_bps"):
        ic = signal_ic(ledger, signals, outcome=outcome)
        report[outcome] = ic
        print(f"\n=== per-session cross-sectional IC vs {outcome} ===")
        print(f"{'signal':16s} {'mean_IC':>9s} {'t':>7s} {'hit':>6s} {'sessions':>9s}")
        for name, stats in ic.items():
            print(f"{name:16s} {stats['mean_ic']:+9.4f} {stats['ic_t_stat']:+7.2f} "
                  f"{stats['hit_rate']:6.3f} {stats['n_sessions']:9d}")

    # Quintile view for the strongest gross-edge signals: does the top bucket
    # actually make money before cost, and what does it cost to trade?
    joined = ledger.join(signals, left_on=["day", "ticker"], right_on=["date", "ticker"],
                         how="inner")
    top = list(report["gross_bps"])[:4]
    print("\n=== quintile tables (1 = lowest signal value) ===")
    buckets = {}
    for signal in top:
        sub = joined.drop_nulls([signal])
        q = sub.with_columns(
            ((pl.col(signal).rank("ordinal") / pl.len() * 5).ceil()).alias("q"))
        table = (q.group_by("q").agg(
            pl.len().alias("n"),
            pl.col("gross_bps").mean().round(1).alias("gross_bps"),
            pl.col("cost_bps").mean().round(1).alias("cost_bps"),
            pl.col("net_bps").mean().round(1).alias("net_bps"))
            .sort("q"))
        buckets[signal] = table.to_dicts()
        print(f"\n-- {signal} (high {'good' if SIGNALS[signal] else 'bad'})")
        print(table)
    report["quintiles"] = buckets

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, indent=1, default=str))
        print(f"\nreport -> {args.out}")


if __name__ == "__main__":
    main()
