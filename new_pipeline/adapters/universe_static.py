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
DEFAULT_ALIASES_PATH = data_dir() / "universe" / "aliases.csv"


def _parse_optional_date(value: str | None) -> date | None:
    if value is None:
        return None
    value = value.strip()
    return date.fromisoformat(value) if value else None


class StaticUniverseProvider(UniverseProvider):
    def __init__(
        self, membership_path: Path | None = None, aliases_path: Path | None = None
    ) -> None:
        self._path = membership_path or DEFAULT_MEMBERSHIP_PATH
        self._members = self._load()
        self._aliases_path = aliases_path or self._default_aliases_path()
        self._aliases = self._load_aliases()

    def _default_aliases_path(self) -> Path:
        """Prefer a sibling ``<stem>_aliases.csv`` next to the membership file
        (so ``sp500.csv`` pairs with ``sp500_aliases.csv``); else the packaged
        default. Keeps a universe fixture + its gazetteer a matched drop-in."""
        sibling = self._path.with_name(f"{self._path.stem}_aliases.csv")
        return sibling if sibling.exists() else DEFAULT_ALIASES_PATH

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

    def _load_aliases(self) -> dict[str, list[str]]:
        """Optional ``ticker,alias`` fixture (multi-row). Missing file -> no
        gazetteer (the anonymizer still masks the symbol vocabulary)."""
        if not self._aliases_path.exists():
            return {}
        aliases: dict[str, list[str]] = {}
        with open(self._aliases_path, encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                ticker = row["ticker"].strip()
                alias = row["alias"].strip()
                if ticker and alias:
                    aliases.setdefault(ticker, []).append(alias)
        return aliases

    def aliases(self, as_of: date | None = None) -> dict[str, list[str]]:
        if as_of is None:
            return {ticker: list(names) for ticker, names in self._aliases.items()}
        active = {member.ticker for member in self.members(as_of)}
        return {t: list(n) for t, n in self._aliases.items() if t in active}
