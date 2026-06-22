"""Live SEC EDGAR filings adapter (``NewsSource``) via ``edgartools``.

Long-form filings (8-K / 10-Q / 10-K) become :class:`NewsItem`s whose ``headline``
is a concise descriptor scored through ``SentimentEngine.score_headlines`` (FinBERT
truncates at 512 tokens; full-text ``score_document`` aggregation is a future
refinement). ``edgartools`` is imported lazily and the module is coverage-omitted;
an injected ``client`` lets the filing -> NewsItem mapping be tested without the
package or egress. SEC requires a "Name email" identity (``cfg.news.edgar_identity``).
"""

from __future__ import annotations

from datetime import date, datetime

from new_pipeline.adapters.base import NewsItem, NewsSource


def _as_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def _summary(filing) -> str:
    for attr in ("primary_doc_description", "summary", "form"):
        text = getattr(filing, attr, None)
        if text:
            return str(text)
    return "filing"


class EdgarFilingSource(NewsSource):
    def __init__(self, forms=None, identity: str = "", limit: int = 20, client=None):
        self._forms = list(forms) if forms else ["8-K", "10-Q", "10-K"]
        self._limit = limit
        if client is not None:
            self._client = client
        else:  # pragma: no cover - needs edgartools + egress
            import edgar

            if identity:
                edgar.set_identity(identity)
            self._client = edgar

    def fetch(self, symbol, start, end, as_of=None) -> list[NewsItem]:
        company = self._client.Company(symbol)
        items: list[NewsItem] = []
        for filing in company.get_filings(form=self._forms):
            filed = _as_date(getattr(filing, "filing_date", None))
            if filed is None or not (start <= filed <= end):
                continue
            timestamp = datetime(filed.year, filed.month, filed.day)
            if as_of is not None and timestamp > as_of:
                continue
            form = getattr(filing, "form", "filing")
            headline = f"{symbol} {form} {filed.isoformat()}: {_summary(filing)}"[:512]
            items.append(NewsItem(timestamp=timestamp, symbol=symbol, headline=headline))
            if len(items) >= self._limit:
                break
        return items

    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        return self.fetch(symbol, on, on)
