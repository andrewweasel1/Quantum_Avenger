"""Live point-in-time fundamentals from SEC EDGAR (lazy ``edgartools``).

The per-symbol financial-facts fetch is injectable so the record→snapshot mapping
is unit-testable with no egress; the default lazily imports ``edgartools`` and is
validated on an allowlisted host (egress + a licensed SEC identity), like the other
live adapters. Coverage-omitted.
"""

from datetime import date

from new_pipeline.adapters.base import FundamentalSnapshot, FundamentalsSource


class EdgarFundamentalsSource(FundamentalsSource):
    """Maps EDGAR financial facts to :class:`FundamentalSnapshot` records.

    ``fetch(symbol, start, end) -> list[dict]`` (each with ``as_of``,
    ``book_value_per_share``, ``earnings_per_share``, ``return_on_equity``) is
    injectable; the default derives them from the company's XBRL filings.
    """

    def __init__(self, identity: str = "", fetch=None) -> None:
        self._identity = identity
        self._fetch = fetch

    def history(self, symbol: str, start: date, end: date) -> list[FundamentalSnapshot]:
        fetch = self._fetch or self._default_fetch
        snapshots = []
        for record in fetch(symbol, start, end):
            as_of = record["as_of"]
            as_of = as_of if isinstance(as_of, date) else date.fromisoformat(str(as_of))
            if as_of > end:
                continue
            snapshots.append(
                FundamentalSnapshot(
                    as_of=as_of,
                    book_value_per_share=float(record["book_value_per_share"]),
                    earnings_per_share=float(record["earnings_per_share"]),
                    return_on_equity=float(record["return_on_equity"]),
                )
            )
        return sorted(snapshots, key=lambda snap: snap.as_of)

    def _default_fetch(self, symbol, start, end):  # pragma: no cover - egress
        """One companyfacts GET per company via the shared mapping helpers
        (``data/edgar_companyfacts``): CIK-resolved, tag-fallback-robust, PIT
        ``as_of`` = filed date. Replaces the per-filing edgartools walk that
        broke on variant XBRL tags and delisted tickers."""
        from new_pipeline.data.edgar_companyfacts import fetch_company_records

        return fetch_company_records(
            symbol, start, end, identity=self._identity or "research research@example.com"
        )
