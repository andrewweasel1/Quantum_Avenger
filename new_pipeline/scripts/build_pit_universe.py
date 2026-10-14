"""Build the point-in-time S&P 500 universe fixture from index-change history.

Source: the fja05680/sp500 dataset (github.com/fja05680/sp500) — reconstructed
S&P 500 membership since 1996, maintained from the original Clenow/Norgate list
plus tracked index changes. Intervals are swept from the DAILY components file
(one row per change date with the full ticker list): a ticker's membership
interval opens on the first row listing it and closes (end-exclusive) on the
first later row that drops it, re-entries opening new intervals (e.g. AAL).
The dataset's precomputed ``sp500_ticker_start_end.csv`` is NOT used — it goes
stale around symbol renames (it closes FB at the 2022 META rename with no
successor row), whereas sweeping the daily file after folding ``RENAMES``
yields the continuous interval under the surviving symbol. This script adds
the two things the dataset lacks — GICS sectors and Alpaca-fetchable symbols —
and emits:

    new_pipeline/data/universe/sp500_pit.csv          (ticker,gics_sector,start_date,end_date)
    new_pipeline/data/universe/sp500_pit_aliases.csv  (ticker,alias)

Sectors come from the current-constituent ``sp500.csv`` when the ticker is in
it, else from the committed curated map ``pit_sector_overrides.csv`` (departed
names, recent additions, and post-rename symbols; best-effort GICS with the
company name that seeds the news-gazetteer alias). An unmapped ticker is a hard
error so the map stays complete by construction.

Membership intervals are restricted to those intersecting 2015-01-01+ — this
fixture backs the 2018+ backtests (with factor warmup), and a bounded window
keeps the curated map tractable. Alpaca serves full bar history for delisted
tickers on the SIP feed (verified: TWTR, FRC, XLNX, CERN, ATVI), so departed
names are genuinely backtestable; renamed equities are folded onto the symbol
Alpaca serves today via ``RENAMES``.

    python -m new_pipeline.scripts.build_pit_universe          # fetch + build
    python -m new_pipeline.scripts.build_pit_universe --list-unmapped
"""

import argparse
import csv
import io
import sys
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

from new_pipeline.core.paths import data_dir

_BASE = "https://raw.githubusercontent.com/fja05680/sp500/master/"
HISTORY_FILE = "S&P 500 Historical Components & Changes (Updated).csv"

WINDOW_START = date(2015, 1, 1)

# Dataset symbol -> the symbol Alpaca serves TODAY (same equity renamed; the
# broker carries the unified history under the new name). Merger-created
# entities (e.g. UTX+RTN -> RTX, DISCA -> WBD) are NOT renames: the old lines
# stay as departures with their own bar history.
RENAMES = {
    "FB": "META", "ANTM": "ELV", "FISV": "FI", "WLTW": "WTW", "HRS": "LHX",
    "TMK": "GL", "JEC": "J", "CDAY": "DAY", "FLT": "CPAY", "PEAK": "DOC",
    "SYMC": "GEN", "NLOK": "GEN", "VIAC": "PARA", "LB": "BBWI", "KORS": "CPRI",
    "CTL": "LUMN", "CHK": "EXE", "BK": "BNY", "ABC": "COR", "BLL": "BALL",
    "BHGE": "BKR", "COG": "CTRA", "PKI": "RVTY", "RE": "EG", "HCP": "DOC",
}

# Second share classes of companies the fixture already carries one class for
# (the current-constituent file keeps one listing per company).
DROP = {"GOOG", "CMCSK", "DISCK", "UA"}


def normalize_ticker(raw: str) -> str:
    """Uppercase, class-share dash -> dot (BRK-B -> BRK.B), fold renames."""
    ticker = raw.strip().upper().replace("-", ".")
    return RENAMES.get(ticker, ticker)


def load_intervals(history_text: str) -> dict[str, list[tuple[date, date | None]]]:
    """Sweep the daily components file into per-ticker membership intervals.

    Each row is ``date, "T1,T2,..."`` on an index-change date. A ticker's
    interval opens on the first row listing it and closes END-EXCLUSIVE on the
    date of the first later row that drops it (matching ``active_on``'s
    ``as_of < end``); presence in the final row leaves it open-ended. Symbols
    are normalized (renames folded) BEFORE the sweep, so a mid-stream ticker
    change reads as continuous membership under the surviving symbol. Only
    intervals intersecting the window are kept."""
    rows = []
    for row in csv.DictReader(io.StringIO(history_text)):
        members = {normalize_ticker(t) for t in row["tickers"].split(",")} - DROP
        rows.append((date.fromisoformat(row["date"].strip()), members))
    rows.sort(key=lambda r: r[0])

    spans: dict[str, list[tuple[date, date | None]]] = {}
    open_since: dict[str, date] = {}
    for day, members in rows:
        for ticker in members - open_since.keys():
            open_since[ticker] = day
        for ticker in list(open_since.keys() - members):
            spans.setdefault(ticker, []).append((open_since.pop(ticker), day))
    for ticker, start in open_since.items():  # present in the final row
        spans.setdefault(ticker, []).append((start, None))

    kept = {
        ticker: [s for s in intervals if s[1] is None or s[1] >= WINDOW_START]
        for ticker, intervals in spans.items()
    }
    return {t: sorted(s) for t, s in kept.items() if s}


def load_sectors(snapshot_path: Path, overrides_path: Path):
    """(ticker -> sector, ticker -> company-name-alias) from the snapshot +
    curated overrides. Snapshot wins (it is the maintained GICS source)."""
    sectors: dict[str, str] = {}
    names: dict[str, str] = {}
    with open(overrides_path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            sectors[row["ticker"].strip()] = row["gics_sector"].strip()
            names[row["ticker"].strip()] = row["company_name"].strip()
    with open(snapshot_path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            sectors[row["ticker"].strip()] = row["gics_sector"].strip()
    return sectors, names


def build_rows(intervals, sectors) -> list[dict]:
    """One fixture row per membership interval; hard-error on unmapped tickers."""
    unmapped = sorted(t for t in intervals if t not in sectors)
    if unmapped:
        raise SystemExit(
            f"{len(unmapped)} tickers lack a GICS sector — add them to "
            f"pit_sector_overrides.csv: {' '.join(unmapped)}"
        )
    rows = []
    for ticker in sorted(intervals):
        for start, end in intervals[ticker]:
            rows.append({
                "ticker": ticker,
                "gics_sector": sectors[ticker],
                "start_date": start.isoformat(),
                "end_date": end.isoformat() if end else "",
            })
    return rows


def build_aliases(intervals, names, aliases_path: Path) -> list[dict]:
    """Gazetteer rows: copy the maintained aliases for tickers that have them,
    else the curated company name. Every fixture ticker must end up covered."""
    existing: dict[str, list[str]] = {}
    with open(aliases_path, encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            existing.setdefault(row["ticker"].strip(), []).append(row["alias"].strip())
    rows, uncovered = [], []
    for ticker in sorted(intervals):
        if ticker in existing:
            rows.extend({"ticker": ticker, "alias": a} for a in existing[ticker])
        elif ticker in names:
            rows.append({"ticker": ticker, "alias": names[ticker]})
        else:
            uncovered.append(ticker)
    if uncovered:
        raise SystemExit(f"tickers without any alias/company name: {' '.join(uncovered)}")
    return rows


def validate_fixture(intervals, history_text: str | None = None) -> None:
    """Hard sanity asserts on well-known index events + structural invariants."""
    tsla = intervals["TSLA"]
    assert tsla[-1][0] == date(2020, 12, 21), f"TSLA add date drifted: {tsla}"
    twtr_end = intervals["TWTR"][-1][1]
    assert twtr_end is not None and twtr_end.year == 2022, f"TWTR exit drifted: {twtr_end}"
    frc_end = intervals["FRC"][-1][1]
    assert frc_end is not None and frc_end.year == 2023, f"FRC exit drifted: {frc_end}"
    for ticker, spans in intervals.items():
        for (_s1, e1), (s2, _e2) in zip(spans, spans[1:], strict=False):
            assert e1 is not None and s2 > e1, f"{ticker} intervals overlap: {spans}"
        for start, end in spans:
            assert end is None or end > start, f"{ticker} empty interval"
    open_ended = {t for t, spans in intervals.items() if any(e is None for _s, e in spans)}
    assert 480 <= len(open_ended) <= 515, f"open-ended membership count: {len(open_ended)}"
    if history_text is not None:  # cross-check vs the dataset's latest daily row
        last = list(csv.reader(io.StringIO(history_text)))[-1]
        latest = {normalize_ticker(t) for t in last[1].split(",")} - DROP
        drift = latest.symmetric_difference(open_ended)
        assert len(drift) <= 15, f"open-ended set drifts from latest row by {sorted(drift)}"


def _download(name: str) -> str:  # pragma: no cover - egress
    with urllib.request.urlopen(_BASE + urllib.parse.quote(name), timeout=60) as resp:
        return resp.read().decode("utf-8")


def main() -> None:  # pragma: no cover - orchestration around tested helpers
    parser = argparse.ArgumentParser(description="Build the PIT S&P 500 fixture")
    parser.add_argument("--list-unmapped", action="store_true",
                        help="print tickers lacking a sector mapping and exit")
    parser.add_argument("--history-file", default="",
                        help="local copy of the historical-components CSV (skips download)")
    args = parser.parse_args()

    universe_dir = data_dir() / "universe"
    history = (Path(args.history_file).read_text(encoding="utf-8")
               if args.history_file else _download(HISTORY_FILE))
    intervals = load_intervals(history)
    sectors, names = load_sectors(
        universe_dir / "sp500.csv", universe_dir / "pit_sector_overrides.csv"
    )
    if args.list_unmapped:
        missing = sorted(t for t in intervals if t not in sectors)
        print("\n".join(missing) or "(all mapped)")
        sys.exit(0)

    validate_fixture(intervals, history)
    rows = build_rows(intervals, sectors)
    aliases = build_aliases(intervals, names, universe_dir / "sp500_aliases.csv")

    fixture = universe_dir / "sp500_pit.csv"
    with open(fixture, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, ["ticker", "gics_sector", "start_date", "end_date"])
        writer.writeheader()
        writer.writerows(rows)
    alias_path = universe_dir / "sp500_pit_aliases.csv"
    with open(alias_path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, ["ticker", "alias"])
        writer.writeheader()
        writer.writerows(aliases)
    tickers = {r["ticker"] for r in rows}
    print(f"{fixture}: {len(rows)} interval rows, {len(tickers)} tickers")
    print(f"{alias_path}: {len(aliases)} alias rows")


if __name__ == "__main__":
    main()
