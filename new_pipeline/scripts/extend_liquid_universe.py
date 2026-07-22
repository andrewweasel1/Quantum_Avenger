"""Extend the Liquid-1500 point-in-time fixture FORWARD with fresh months.

The committed fixture's rule intervals end at its build date, so live trading
after that date sees only the open-ended S&P rows (the 76-per-leg problem).
This tool recomputes membership with the SAME causal rule
(:mod:`build_liquid_universe`) on a RECENT census + bars window and merges the
new member-months into the fixture under strict semantics:

- no row with ``end_date`` before the extension floor is ever modified —
  backtests ending before the floor read a byte-identical membership history
  (asserted at runtime, not assumed);
- a new interval that begins exactly where a ticker's existing interval ends
  EXTENDS that row; anything else is appended as a fresh interval (re-entries
  are real);
- tickers with external PIT rows (the S&P history) are never given rule rows,
  mirroring the builder's merge policy;
- brand-new tickers get Mid/Small Cap Extended labels by median ADV rank in
  the recent window.

Survivorship note: the recent bars come from the Alpaca registry candidates —
fine for a FORWARD extension (live names are active by definition; the census
still gates actual trading presence), unusable for history (see the ingest
script's audit note).

    python -m new_pipeline.scripts.extend_liquid_universe \
        --bars <recent_vault>/bars.parquet --census <recent>/census_short_volume.csv
"""

import argparse
import csv
from datetime import date
from pathlib import Path

import polars as pl
from new_pipeline.scripts.build_liquid_universe import (
    EXTENDED_MID,
    EXTENDED_SMALL,
    apply_gap_guard,
    membership_intervals,
    monthly_membership,
)


def fixture_rule_floor(rows: list[dict]) -> date:
    """First month the fixture does NOT cover: max end_date over closed rows."""
    ends = [date.fromisoformat(r["end_date"]) for r in rows if r["end_date"]]
    if not ends:
        raise ValueError("fixture has no closed intervals; nothing to extend")
    return max(ends)


def merge_extend(rows: list[dict], new_intervals: dict, labels: dict,
                 floor: date) -> tuple[list[dict], dict]:
    """Merge rule intervals (all clamped to >= floor) into fixture rows.

    Returns (merged rows, stats). Pre-floor rows are never mutated; an
    interval starting at a ticker's existing end EXTENDS that row in place."""
    pit_tickers = {r["ticker"] for r in rows if r["end_date"] == ""}
    by_ticker: dict[str, list[dict]] = {}
    for row in rows:
        by_ticker.setdefault(row["ticker"], []).append(row)
    stats = {"extended": 0, "appended": 0, "skipped_pit": 0, "new_tickers": 0}
    for ticker, spans in sorted(new_intervals.items()):
        if ticker in pit_tickers:
            stats["skipped_pit"] += 1
            continue
        existing = by_ticker.get(ticker)
        if existing is None:
            stats["new_tickers"] += 1
        for start, end in spans:
            start = max(start, floor)  # never regenerate covered history
            if start >= end:
                continue
            tail = None
            if existing:
                closed = [r for r in existing if r["end_date"]]
                if closed:
                    tail = max(closed, key=lambda r: r["end_date"])
            if tail is not None and tail["end_date"] == start.isoformat():
                tail["end_date"] = end.isoformat()  # contiguous -> extend
                stats["extended"] += 1
            else:
                row = {
                    "ticker": ticker,
                    "gics_sector": (existing[0]["gics_sector"] if existing
                                    else labels.get(ticker, EXTENDED_SMALL)),
                    "start_date": start.isoformat(),
                    "end_date": end.isoformat(),
                }
                rows.append(row)
                by_ticker.setdefault(ticker, []).append(row)
                stats["appended"] += 1
    return rows, stats


def assert_history_unchanged(old_rows: list[dict], new_rows: list[dict],
                             floor: date) -> None:
    """Every membership fact strictly BEFORE the floor must be identical."""
    def facts(rows):
        out = set()
        for r in rows:
            start = date.fromisoformat(r["start_date"])
            end = r["end_date"] and min(date.fromisoformat(r["end_date"]), floor)
            end = end if r["end_date"] else floor
            if start < end:
                out.add((r["ticker"], start.isoformat(), end.isoformat(),
                         r["gics_sector"]))
        return out
    if facts(old_rows) != facts(new_rows):
        raise AssertionError("pre-floor membership history changed — refusing to write")


def main() -> None:  # pragma: no cover - I/O shell around tested helpers
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bars", required=True, help="recent-window bars.parquet")
    parser.add_argument("--census", required=True, help="recent-window census CSV")
    parser.add_argument("--fixture", default="new_pipeline/data/universe/liquid1500_pit.csv")
    parser.add_argument("--out", default=None, help="default: overwrite --fixture")
    parser.add_argument("--top-n", type=int, default=1500)
    parser.add_argument("--min-price", type=float, default=5.0)
    parser.add_argument("--mid-cutoff", type=int, default=1000)
    parser.add_argument("--exclusions",
                        default="new_pipeline/data/universe/liquid_exclusions.csv")
    args = parser.parse_args()

    old_rows = list(csv.DictReader(open(args.fixture, encoding="utf-8")))
    rows = [dict(r) for r in old_rows]
    floor = fixture_rule_floor(rows)
    print(f"extension floor (first uncovered month): {floor}")

    bars = pl.read_parquet(args.bars)
    census = pl.read_csv(args.census, schema_overrides={"short_volume": pl.Int64,
                                                       "total_volume": pl.Int64})
    census = census.with_columns(pl.col("date").str.to_date()).select("ticker", "date")
    if args.exclusions and Path(args.exclusions).exists():
        excluded = {r["ticker"] for r in csv.DictReader(open(args.exclusions))}
        bars = bars.filter(~pl.col("ticker").is_in(list(excluded)))
        census = census.filter(~pl.col("ticker").is_in(list(excluded)))
    members = monthly_membership(bars, census, top_n=args.top_n,
                                 min_price=args.min_price)
    intervals = apply_gap_guard(membership_intervals(members, floor=floor), bars)
    med = dict(members.group_by("ticker").agg(pl.col("adv_rank").median()).iter_rows())
    labels = {t: (EXTENDED_MID if r <= args.mid_cutoff else EXTENDED_SMALL)
              for t, r in med.items()}

    merged, stats = merge_extend(rows, intervals, labels, floor)
    assert_history_unchanged(old_rows, merged, floor)
    out = Path(args.out or args.fixture)
    with open(out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, ["ticker", "gics_sector", "start_date", "end_date"])
        writer.writeheader()
        writer.writerows(merged)
    # keep the alias file total: new tickers alias to themselves
    alias_path = out.with_name(out.stem + "_aliases.csv")
    alias_rows = list(csv.DictReader(open(alias_path, encoding="utf-8")))
    covered = {r["ticker"] for r in alias_rows}
    for ticker in sorted({r["ticker"] for r in merged} - covered):
        alias_rows.append({"ticker": ticker, "alias": ticker})
    with open(alias_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, ["ticker", "alias"])
        writer.writeheader()
        writer.writerows(alias_rows)
    print(f"{out}: {len(merged)} rows ({stats})")


if __name__ == "__main__":  # pragma: no cover
    main()
