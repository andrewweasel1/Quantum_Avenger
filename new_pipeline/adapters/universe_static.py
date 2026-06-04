"""Offline, survivorship-safe universe loaded from a point-in-time CSV fixture.

Implements :class:`UniverseProvider` over ``data/universe/membership.csv``
(`ticker, gics_sector, start_date, end_date`). A licensed real point-in-time
membership dataset can replace the fixture with no code change.
"""

import csv
from datetime import date
from pathlib import Path

from new_pipeline.adapters.base import UniverseMember, UniverseProvider
from new_pipeline.core.exceptions import UniverseError
from new_pipeline.core.paths import data_dir

DEFAULT_MEMBERSHIP_PATH = data_dir() / "universe" / "membership.csv"


def _parse_optional_date(value: str | None) -> date | None:
    if value is None:
        return None
    value = value.strip()
    return date.fromisoformat(value) if value else None


class StaticUniverseProvider(UniverseProvider):
    def __init__(self, membership_path: Path | None = None) -> None:
        self._path = membership_path or DEFAULT_MEMBERSHIP_PATH
        self._members = self._load()

    def _load(self) -> list[UniverseMember]:
        if not self._path.exists():
            raise UniverseError(f"Universe membership fixture not found: {self._path}")
        members: list[UniverseMember] = []
        with open(self._path, encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                members.append(
                    UniverseMember(
                        ticker=row["ticker"].strip(),
                        gics_sector=row["gics_sector"].strip(),
                        start_date=date.fromisoformat(row["start_date"].strip()),
                        end_date=_parse_optional_date(row.get("end_date")),
                    )
                )
        if not members:
            raise UniverseError(f"Universe membership fixture is empty: {self._path}")
        return members

    def members(self, as_of: date | None = None) -> list[UniverseMember]:
        if as_of is None:
            return list(self._members)
        return [member for member in self._members if member.active_on(as_of)]
