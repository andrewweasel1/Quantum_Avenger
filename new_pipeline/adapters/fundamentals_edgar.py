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

    def _default_fetch(self, symbol, start, end):  # pragma: no cover - egress + XBRL parse
        """Derive per-share book value, EPS, and ROE from EDGAR XBRL facts
        (StockholdersEquity / CommonSharesOutstanding, EarningsPerShareBasic,
        NetIncomeLoss). Validated on an allowlisted host with a real SEC identity."""
        import edgar

        edgar.set_identity(self._identity or "research research@example.com")
        company = edgar.Company(symbol)
        records = []
        for filing in company.get_filings(form=["10-K", "10-Q"]).filter(date=f"{start}:{end}"):
            facts = filing.obj().financials
            equity = float(facts.balance_sheet.loc["StockholdersEquity"].iloc[0])
            shares = float(facts.balance_sheet.loc["CommonSharesOutstanding"].iloc[0])
            eps = float(facts.income_statement.loc["EarningsPerShareBasic"].iloc[0])
            net_income = float(facts.income_statement.loc["NetIncomeLoss"].iloc[0])
            records.append(
                {
                    "as_of": filing.filing_date,
                    "book_value_per_share": equity / shares if shares else 0.0,
                    "earnings_per_share": eps,
                    "return_on_equity": net_income / equity if equity else 0.0,
                }
            )
        return records
