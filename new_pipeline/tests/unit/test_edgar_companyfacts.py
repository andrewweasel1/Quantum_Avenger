"""companyfacts -> PIT snapshots: tag fallbacks, filed-date discipline, CIK resolution."""

from datetime import date

from new_pipeline.data.edgar_companyfacts import (
    load_ticker_map,
    resolve_cik,
    snapshot_records,
)


def _entry(val, accn, filed, end, start=None, form="10-Q"):
    row = {"val": val, "accn": accn, "filed": filed, "end": end, "form": form}
    if start:
        row["start"] = start
    return row


def _facts(equity_tag="StockholdersEquity", shares_tag="CommonStockSharesOutstanding",
           eps_tag="EarningsPerShareBasic", ni_tag="NetIncomeLoss"):
    """One quarterly filing (accn A1, filed 2021-05-01, period Q1-2021)."""
    q = {"start": "2021-01-01", "end": "2021-03-31"}
    return {
        "facts": {
            "us-gaap": {
                equity_tag: {"units": {"USD": [_entry(2000.0, "A1", "2021-05-01",
                                                      "2021-03-31")]}},
                shares_tag: {"units": {"shares": [_entry(100.0, "A1", "2021-05-01",
                                                         "2021-03-31")]}},
                eps_tag: {"units": {"USD/shares": [_entry(1.0, "A1", "2021-05-01",
                                                          q["end"], q["start"])]}},
                ni_tag: {"units": {"USD": [_entry(100.0, "A1", "2021-05-01",
                                                  q["end"], q["start"])]}},
            }
        }
    }


def test_snapshot_records_map_and_annualize():
    records = snapshot_records(_facts(), date(2021, 1, 1), date(2021, 12, 31))
    assert len(records) == 1
    rec = records[0]
    assert rec["as_of"] == "2021-05-01"  # the FILED date, not the period end
    assert rec["book_value_per_share"] == 2000.0 / 100.0
    # Q1 2021 spans 89 days -> flows annualized by 365/89.
    factor = 365.0 / 89.0
    assert abs(rec["earnings_per_share"] - 1.0 * factor) < 1e-9
    assert abs(rec["return_on_equity"] - (100.0 * factor) / 2000.0) < 1e-9


def test_tag_fallbacks_cover_variant_filers():
    facts = _facts(
        equity_tag="StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
        eps_tag="EarningsPerShareDiluted",
        ni_tag="ProfitLoss",
    )
    records = snapshot_records(facts, date(2021, 1, 1), date(2021, 12, 31))
    assert len(records) == 1  # variant tags resolve via the fallback lists


def test_incomplete_filing_yields_no_snapshot():
    facts = _facts()
    del facts["facts"]["us-gaap"]["NetIncomeLoss"]  # income concept missing entirely
    assert snapshot_records(facts, date(2021, 1, 1), date(2021, 12, 31)) == []


def test_filed_outside_window_is_dropped():
    assert snapshot_records(_facts(), date(2022, 1, 1), date(2022, 12, 31)) == []


def test_load_ticker_map_normalizes_class_shares():
    raw = {"0": {"cik_str": 1067983, "ticker": "BRK-B", "title": "BERKSHIRE"},
           "1": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}}
    mapping = load_ticker_map(lambda url: raw)
    assert mapping["BRK.B"] == 1067983
    assert mapping["AAPL"] == 320193


def test_resolve_cik_map_first_then_name_search():
    ticker_map = {"AAPL": 320193}
    assert resolve_cik("AAPL", "Apple", ticker_map, lambda url: "") == 320193
    atom = '<entry><link href="...CIK=0001418091&type=10-K"/></entry>'
    assert resolve_cik("TWTR", "Twitter", ticker_map, lambda url: atom) == 1418091
    assert resolve_cik("ZZZZ", "", ticker_map, lambda url: "") is None  # no name -> None
    assert resolve_cik("YYYY", "Nowhere Corp", ticker_map, lambda url: "no match") is None
