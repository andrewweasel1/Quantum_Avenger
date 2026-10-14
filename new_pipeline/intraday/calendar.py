"""US equity session calendar: the single authority for open/close times.

Flat-by-close is only honest if "close" is the EXCHANGE's close — half days
(day after Thanksgiving, Christmas Eve, July 3rd) end at 13:00 ET, and a
16:00 assumption would fabricate three hours of fills a few times a year.
The fixture is fetched once from Alpaca's ``/calendar`` endpoint (which
carries early closes) and committed; loaders are pure and offline.

Fixture schema (``new_pipeline/data/calendar/us_equity_sessions.csv``):
``date,open_utc,close_utc`` — ISO-8601 UTC instants, one row per session.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

_ET = ZoneInfo("America/New_York")
DEFAULT_FIXTURE = (Path(__file__).resolve().parents[1]
                   / "data" / "calendar" / "us_equity_sessions.csv")
# A regular session is 6.5h; anything shorter is an early close.
_FULL_SESSION = timedelta(hours=6, minutes=30)


@dataclass(frozen=True)
class Session:
    day: date
    open_utc: datetime
    close_utc: datetime

    @property
    def is_early_close(self) -> bool:
        return (self.close_utc - self.open_utc) < _FULL_SESSION


def load_sessions(path: Path | None = None) -> dict[date, Session]:
    """{session date: Session} from the committed fixture. Raises if missing —
    a silent empty calendar would make every backtest silently zero-session."""
    path = path or DEFAULT_FIXTURE
    if not path.exists():
        raise FileNotFoundError(
            f"session calendar fixture missing: {path} — run "
            "scripts/ingest_minute_vault.py --refresh-calendar first"
        )
    sessions: dict[date, Session] = {}
    with path.open() as fh:
        for row in csv.DictReader(fh):
            day = date.fromisoformat(row["date"])
            sessions[day] = Session(
                day=day,
                open_utc=datetime.fromisoformat(row["open_utc"]),
                close_utc=datetime.fromisoformat(row["close_utc"]),
            )
    return sessions


def trading_days(start: date, end: date, sessions: dict[date, Session]) -> list[date]:
    return sorted(d for d in sessions if start <= d <= end)


def fetch_calendar(api_key: str, secret_key: str, start: date, end: date) -> list[Session]:
    """Pull the exchange calendar from Alpaca and normalize to UTC instants.

    Alpaca's ``Calendar`` model carries naive ET wall-clock open/close times;
    the ET->UTC conversion happens exactly here so everything downstream is
    tz-unambiguous."""
    from alpaca.trading.client import TradingClient
    from alpaca.trading.requests import GetCalendarRequest

    client = TradingClient(api_key, secret_key, paper=True)
    rows = client.get_calendar(GetCalendarRequest(start=start, end=end))
    sessions = []
    for row in rows:
        open_et = datetime.combine(row.date, row.open.time(), tzinfo=_ET)
        close_et = datetime.combine(row.date, row.close.time(), tzinfo=_ET)
        sessions.append(Session(
            day=row.date,
            open_utc=open_et.astimezone(UTC),
            close_utc=close_et.astimezone(UTC),
        ))
    return sessions


def write_fixture(sessions: list[Session], path: Path | None = None) -> int:
    path = path or DEFAULT_FIXTURE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(["date", "open_utc", "close_utc"])
        for s in sorted(sessions, key=lambda s: s.day):
            writer.writerow([s.day.isoformat(), s.open_utc.isoformat(), s.close_utc.isoformat()])
    return len(sessions)
