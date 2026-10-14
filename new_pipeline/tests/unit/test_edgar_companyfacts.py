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


def _facts_with_extras(rev=800.0, assets=5000.0, gp=500.0, ocf=90.0):
    """One filing plus the optional quality concepts (all in the same accession)."""
    facts = _facts()
    q = {"start": "2021-01-01", "end": "2021-03-31"}
    ug = facts["facts"]["us-gaap"]
    ug["RevenueFromContractWithCustomerExcludingAssessedTax"] = {
        "units": {"USD": [_entry(rev, "A1", "2021-05-01", q["end"], q["start"])]}}
    ug["Assets"] = {"units": {"USD": [_entry(assets, "A1", "2021-05-01", "2021-03-31")]}}
    ug["GrossProfit"] = {"units": {"USD": [_entry(gp, "A1", "2021-05-01", q["end"], q["start"])]}}
    ug["NetCashProvidedByUsedInOperatingActivities"] = {
        "units": {"USD": [_entry(ocf, "A1", "2021-05-01", q["end"], q["start"])]}}
    return facts


def test_snapshot_records_quality_ratios_when_extras_present():
    rec = snapshot_records(_facts_with_extras(), date(2021, 1, 1), date(2021, 12, 31))[0]
    f = 365.0 / 89.0  # flows annualized
    ni, ocf, assets = 100.0 * f, 90.0 * f, 5000.0
    assert abs(rec["return_on_assets"] - ni / assets) < 1e-9
    assert abs(rec["gross_margin"] - (500.0 * f) / (800.0 * f)) < 1e-9  # ratio: factor cancels
    assert abs(rec["accruals"] - (ni - ocf) / assets) < 1e-9
    assert abs(rec["ocf_per_share"] - ocf / 100.0) < 1e-9


def test_snapshot_records_extras_optional_null_when_missing():
    # No extra concepts -> the core snapshot still emits, quality ratios null.
    rec = snapshot_records(_facts(), date(2021, 1, 1), date(2021, 12, 31))[0]
    assert rec["book_value_per_share"] == 20.0  # core intact
    for col in ("return_on_assets", "gross_margin", "accruals", "ocf_per_share"):
        assert rec[col] is None
    assert rec["revenue_growth"] is None and rec["earnings_growth"] is None


def _annual_facts(accn, filed, p_start, p_end, end, rev, eps, equity=2000.0,
                  shares=100.0, ni=100.0):
    """One annual-ish filing; flows share the SAME period span across years so the
    annualization factor cancels in the YoY growth ratio (exact-value tests)."""
    ug = {}
    def flow(v):
        return _entry(v, accn, filed, p_end, p_start)
    ug["StockholdersEquity"] = {"units": {"USD": [_entry(equity, accn, filed, end)]}}
    ug["CommonStockSharesOutstanding"] = {"units": {"shares": [_entry(shares, accn, filed, end)]}}
    ug["EarningsPerShareBasic"] = {"units": {"USD/shares": [flow(eps)]}}
    ug["NetIncomeLoss"] = {"units": {"USD": [flow(ni)]}}
    ug["RevenueFromContractWithCustomerExcludingAssessedTax"] = {"units": {"USD": [flow(rev)]}}
    return ug


def _merge(*ugs):
    out: dict = {}
    for ug in ugs:
        for tag, payload in ug.items():
            if tag in out:
                for unit, rows in payload["units"].items():
                    out[tag]["units"].setdefault(unit, []).extend(rows)
            else:
                out[tag] = {"units": {u: list(r) for u, r in payload["units"].items()}}
    return {"facts": {"us-gaap": out}}


def test_snapshot_records_yoy_growth_across_filings():
    # Matched 305-day spans (Mar1->Dec31) so annualization cancels: rev 1000->1250
    # (+25%), eps 3.0->3.6 (+20%), filings ~365d apart.
    prior = _annual_facts("A1", "2021-03-01", "2020-03-01", "2020-12-31", "2020-12-31",
                          rev=1000.0, eps=3.0)
    current = _annual_facts("A2", "2022-03-01", "2021-03-01", "2021-12-31", "2021-12-31",
                            rev=1250.0, eps=3.6)
    recs = snapshot_records(_merge(prior, current), date(2020, 1, 1), date(2022, 12, 31))
    assert [r["as_of"] for r in recs] == ["2021-03-01", "2022-03-01"]
    assert abs(recs[-1]["revenue_growth"] - 0.25) < 1e-9
    assert abs(recs[-1]["earnings_growth"] - 0.20) < 1e-9
    assert recs[0]["revenue_growth"] is None  # first filing: no comparable prior


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
