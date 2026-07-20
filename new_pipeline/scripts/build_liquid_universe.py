"""Build the Liquid-1500 point-in-time universe fixture from causal data.

Membership is GENERATED from a rule, never sourced from an index list:
at each month-end, the top ``--top-n`` symbols by trailing 63-trading-day
dollar ADV, with last close > ``--min-price``, among symbols the FINRA Reg SHO
census shows actually traded that month (the census enumerates EVERY traded
symbol daily from 2018-08 — survivorship-free, delisted names included).
Members hold for the following calendar month; contiguous months merge into
membership intervals (end-exclusive), clamped to the census floor.

The emitted fixture is the UNION of the externally-sourced S&P 500 PIT
intervals (unchanged — keeps 2016+ backtests identical pre-expansion, real
GICS sectors) and the rule intervals. Rule-only names carry synthetic buckets:
``Mid Cap Extended`` (median overall ADV rank <= mid cutoff) else ``Small Cap
Extended`` — GICS is unavailable outside the S&P history, and the tournament
just needs stable grouping labels.

Recycling guard: within a rule interval, a bar gap > ``--max-gap`` trading
days truncates the interval at the gap (reused symbols like CA restart as a
fresh interval only if re-qualified).

    python -m new_pipeline.scripts.build_liquid_universe \
        --bars <vault>/bars.parquet --census <census>/census_short_volume.csv \
        --out new_pipeline/data/universe/liquid1500_pit.csv
"""

import argparse
import csv
from datetime import date
from pathlib import Path

import polars as pl

CENSUS_FLOOR = date(2018, 9, 1)  # first full month after the CDN's 2018-08 start
EXTENDED_MID = "Mid Cap Extended"
EXTENDED_SMALL = "Small Cap Extended"


def monthly_membership(
    bars: pl.DataFrame, census: pl.DataFrame, top_n: int = 1500,
    min_price: float = 5.0, adv_window: int = 63, min_obs: int = 40,
    min_census_days: int = 10,
) -> pl.DataFrame:
    """(month, ticker, adv_rank) member rows: rule evaluated at each month-end.

    ``bars``: ticker/date/close/volume daily rows. ``census``: ticker/date rows
    proving the symbol traded that day (any volume). Membership applies to the
    month FOLLOWING the evaluation month (strictly causal)."""
    dollar = bars.sort(["ticker", "date"]).with_columns(
        (pl.col("close") * pl.col("volume")).alias("_dv")
    ).with_columns(
        pl.col("_dv").rolling_mean(window_size=adv_window, min_samples=min_obs)
        .over("ticker").alias("adv"),
        pl.col("date").dt.truncate("1mo").alias("month"),
    )
    month_end = (
        dollar.group_by("ticker", "month")
        .agg(pl.col("date").max().alias("_last"))
        .join(dollar, left_on=["ticker", "_last"], right_on=["ticker", "date"])
        .select("ticker", "month", "adv", pl.col("close").alias("px"))
    )
    presence = (
        census.with_columns(pl.col("date").dt.truncate("1mo").alias("month"))
        .group_by("ticker", "month").agg(pl.len().alias("_days"))
        .filter(pl.col("_days") >= min_census_days)
        .select("ticker", "month")
    )
    eligible = (
        month_end.join(presence, on=["ticker", "month"], how="inner")
        .filter((pl.col("px") > min_price) & pl.col("adv").is_not_null())
    )
    ranked = eligible.with_columns(
        pl.col("adv").rank(method="ordinal", descending=True).over("month").alias("adv_rank")
    ).filter(pl.col("adv_rank") <= top_n)
    # membership month = evaluation month + 1 (causal)
    return ranked.with_columns(
        pl.col("month").dt.offset_by("1mo").alias("member_month")
    ).select("ticker", "member_month", "adv_rank")


def membership_intervals(members: pl.DataFrame, floor: date = CENSUS_FLOOR):
    """Contiguous member-months -> [start, end) intervals per ticker."""
    rows = members.filter(pl.col("member_month") >= floor).sort(["ticker", "member_month"])
    intervals: dict[str, list[tuple[date, date]]] = {}
    for ticker, group in rows.group_by("ticker", maintain_order=True):
        months = group["member_month"].to_list()
        start = prev = months[0]
        for m in months[1:]:
            expected = date(prev.year + (prev.month == 12), prev.month % 12 + 1, 1)
            if m != expected:
                intervals.setdefault(ticker[0], []).append((start, expected))
                start = m
            prev = m
        end = date(prev.year + (prev.month == 12), prev.month % 12 + 1, 1)
        intervals.setdefault(ticker[0], []).append((start, end))
    return intervals


def apply_gap_guard(intervals, bars: pl.DataFrame, max_gap: int = 30):
    """Truncate an interval at a >max_gap-trading-day bar gap (symbol recycling
    / data hole guard): membership must be backed by continuous bar coverage."""
    trimmed = {}
    by_ticker = {t[0] if isinstance(t, tuple) else t: g["date"].sort().to_list()
                 for t, g in bars.select("ticker", "date").group_by("ticker")}
    for ticker, spans in intervals.items():
        days = by_ticker.get(ticker, [])
        out = []
        for start, end in spans:
            inside = [d for d in days if start <= d < end]
            if len(inside) < 2:
                continue
            cut = end
            for a, b in zip(inside, inside[1:], strict=False):
                if (b - a).days > max_gap * 1.6:  # ~calendar equivalent of trading days
                    cut = a
                    break
            if cut > start:
                out.append((start, min(cut, end)))
        if out:
            trimmed[ticker] = out
    return trimmed


def assign_buckets(members: pl.DataFrame, pit_sectors: dict[str, str],
                   mid_cutoff: int = 1000) -> dict[str, str]:
    """ticker -> sector label: real GICS for S&P-history names, else Mid/Small
    Extended by the ticker's MEDIAN overall ADV rank across its member months."""
    med = dict(members.group_by("ticker").agg(
        pl.col("adv_rank").median().alias("m"))
        .iter_rows())
    labels = {}
    for ticker, rank in med.items():
        if ticker in pit_sectors:
            labels[ticker] = pit_sectors[ticker]
        else:
            labels[ticker] = EXTENDED_MID if rank <= mid_cutoff else EXTENDED_SMALL
    return labels


def merge_with_pit(rule_intervals, labels, pit_rows: list[dict]) -> list[dict]:
    """Fixture rows: S&P PIT rows unchanged + rule intervals for rule-only
    tickers (a ticker with PIT rows keeps ONLY those — the S&P history remains
    the externally-audited source of truth for those names)."""
    pit_tickers = {r["ticker"] for r in pit_rows}
    rows = list(pit_rows)
    for ticker, spans in sorted(rule_intervals.items()):
        if ticker in pit_tickers:
            continue
        for start, end in spans:
            rows.append({
                "ticker": ticker, "gics_sector": labels[ticker],
                "start_date": start.isoformat(), "end_date": end.isoformat(),
            })
    return rows


def main() -> None:  # pragma: no cover - I/O orchestration around tested helpers
    parser = argparse.ArgumentParser(description="Build the Liquid-1500 PIT fixture")
    parser.add_argument("--bars", required=True)
    parser.add_argument("--census", required=True)
    parser.add_argument("--pit", default="new_pipeline/data/universe/sp500_pit.csv")
    parser.add_argument("--out", default="new_pipeline/data/universe/liquid1500_pit.csv")
    parser.add_argument("--top-n", type=int, default=1500)
    parser.add_argument("--min-price", type=float, default=5.0)
    args = parser.parse_args()

    bars = pl.read_parquet(args.bars)
    census = pl.read_csv(args.census, schema_overrides={"short_volume": pl.Int64,
                                                        "total_volume": pl.Int64})
    census = census.with_columns(pl.col("date").str.to_date()).select("ticker", "date")
    members = monthly_membership(bars, census, top_n=args.top_n, min_price=args.min_price)
    intervals = apply_gap_guard(membership_intervals(members), bars)

    pit_rows = list(csv.DictReader(open(args.pit, encoding="utf-8")))
    pit_sectors = {r["ticker"]: r["gics_sector"] for r in pit_rows}
    labels = assign_buckets(members, pit_sectors)
    rows = merge_with_pit(intervals, labels, pit_rows)

    out = Path(args.out)
    with open(out, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, ["ticker", "gics_sector", "start_date", "end_date"])
        writer.writeheader()
        writer.writerows(rows)
    # aliases: PIT aliases carried over; extended names alias to their own ticker.
    pit_alias = Path(args.pit).with_name(Path(args.pit).stem + "_aliases.csv")
    alias_rows = list(csv.DictReader(open(pit_alias, encoding="utf-8")))
    covered = {r["ticker"] for r in alias_rows}
    for ticker in sorted({r["ticker"] for r in rows} - covered):
        alias_rows.append({"ticker": ticker, "alias": ticker})
    with open(out.with_name(out.stem + "_aliases.csv"), "w", encoding="utf-8",
              newline="") as handle:
        writer = csv.DictWriter(handle, ["ticker", "alias"])
        writer.writeheader()
        writer.writerows(alias_rows)

    tickers = {r["ticker"] for r in rows}
    ext = {t for t in tickers if labels.get(t, "").endswith("Extended")}
    print(f"{out}: {len(rows)} interval rows, {len(tickers)} tickers "
          f"({len(ext)} extended: "
          f"{sum(1 for t in ext if labels[t] == EXTENDED_MID)} mid / "
          f"{sum(1 for t in ext if labels[t] == EXTENDED_SMALL)} small)")


if __name__ == "__main__":  # pragma: no cover
    main()
