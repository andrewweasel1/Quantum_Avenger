"""EDGAR filings adapter (edgartools-bound, coverage-omitted). The filing ->
NewsItem mapping is validated with an injected client (no edgartools, no egress)."""

from datetime import date


class _Filing:
    def __init__(self, form, filing_date, summary):
        self.form = form
        self.filing_date = filing_date
        self.summary = summary


class _Company:
    def __init__(self, symbol):
        self.symbol = symbol

    def get_filings(self, form=None):
        return [
            _Filing("8-K", "2021-01-08", "Material definitive agreement"),
            _Filing("10-Q", "2020-12-31", "Prior-year filing out of range"),
        ]


class _Client:
    Company = _Company


def test_maps_filings_within_range():
    from new_pipeline.adapters.news_edgar import EdgarFilingSource

    src = EdgarFilingSource(forms=["8-K", "10-Q"], client=_Client())
    items = src.fetch("AAPL", date(2021, 1, 1), date(2021, 12, 31))
    assert len(items) == 1  # the 2020 filing is outside the window
    assert items[0].symbol == "AAPL"
    assert items[0].timestamp.date() == date(2021, 1, 8)
    assert "8-K" in items[0].headline and "Material definitive agreement" in items[0].headline
