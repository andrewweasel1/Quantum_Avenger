"""FINRA Reg SHO daily short-sale volume -> per-(ticker, date) records (pure helpers).

FINRA publishes one consolidated file per trading day at
``cdn.finra.org/equity/regsho/daily/CNMSshvol<YYYYMMDD>.txt`` — a pipe-delimited
table ``Date|Symbol|ShortVolume|ShortExemptVolume|TotalVolume|Market``. The
short-volume RATIO (ShortVolume / TotalVolume) is the signal input: an
unusually high fraction of a name's tape printing as short-marked is a fast,
forward-looking pressure gauge orthogonal to the price path.

This module holds the pure parse/URL logic shared by the resumable vault ingest
(``scripts/ingest_short_volume_vault``) and any live source; every network call
is injected so the whole path is unit-testable offline. The CDN keeps a rolling
~8-year window, so files before it (and market holidays) return 403/404 — the
caller treats a missing day as "no data" (neutral-filled downstream), never a
crash.
"""

import logging
from datetime import date, timedelta

_logger = logging.getLogger(__name__)

DAILY_URL = "https://cdn.finra.org/equity/regsho/daily/CNMSshvol{yyyymmdd}.txt"
_HEADER = "Date|Symbol|ShortVolume"  # first token of the real header row
RECORD_COLUMNS = ("date", "ticker", "short_volume", "total_volume")


def daily_url(day: date) -> str:
    return DAILY_URL.format(yyyymmdd=day.strftime("%Y%m%d"))


def parse_daily_file(text: str, universe: set[str] | None = None) -> list[dict]:
    """One CNMSshvol file -> ``{date, ticker, short_volume, total_volume}`` rows.

    Filters to ``universe`` when given (keeps the vault to the traded names),
    skips the header, malformed rows, and zero-total-volume rows (a ratio needs
    a positive denominator). ``date`` is ISO ``YYYY-MM-DD``.
    """
    records = []
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(_HEADER):
            continue
        parts = line.split("|")
        if len(parts) < 5:
            continue
        raw_date, symbol, short_v, total_v = parts[0], parts[1], parts[2], parts[4]
        # FINRA switched the daily files to FRACTIONAL volumes in 2026-02
        # (e.g. "669512.327688"); a strict isdigit() gate silently dropped
        # ~92% of rows as "malformed" and gutted the census. Accept any
        # non-negative decimal; trailer/summary lines still fail the parse.
        if not (raw_date.isdigit() and len(raw_date) == 8):
            continue  # trailer / summary lines
        try:
            short_f, total_f = float(short_v), float(total_v)
        except ValueError:
            continue
        if short_f < 0 or total_f < 0:
            continue
        ticker = symbol.strip().upper().replace("-", ".")  # match universe fixtures (BRK.B)
        if universe is not None and ticker not in universe:
            continue
        total = int(round(total_f))
        if total <= 0:
            continue
        records.append({
            "date": f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}",
            "ticker": ticker,
            "short_volume": int(round(short_f)),
            "total_volume": total,
        })
    return records


def trading_days(start: date, end: date) -> list[date]:
    """Weekday calendar in ``[start, end]`` (holidays simply 403 on fetch and are
    skipped; a full exchange calendar is unnecessary for a best-effort vault)."""
    days, day = [], start
    while day <= end:
        if day.weekday() < 5:
            days.append(day)
        day += timedelta(days=1)
    return days
