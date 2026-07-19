"""SEC companyfacts -> point-in-time fundamental snapshots (pure helpers).

One ``/api/xbrl/companyfacts/CIK##########.json`` call returns every XBRL
concept a company ever filed — the robust, cheap alternative to per-filing
document parsing (739 tickers = 739 GETs instead of ~20k, and tag FALLBACKS
instead of KeyErrors on variant filers). This module holds the pure mapping
logic shared by the resumable vault ingest (``scripts/ingest_fundamentals_vault``)
and the live ``EdgarFundamentalsSource``; every network call is injectable so
the whole path is unit-testable offline.

Point-in-time discipline: ``as_of`` is the **filed** date (when the numbers
became public knowledge), never the fiscal period end. Flow concepts (net
income, EPS) are annualized by period length so quarterly and annual filers
are cross-sectionally comparable.
"""

import json
import logging
import re
import urllib.parse
import urllib.request
from datetime import date

_logger = logging.getLogger(__name__)

TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
SEARCH_URL = (
    "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany"
    "&company={query}&type=10-K&owner=include&count=10&output=atom"
)
COMPANYFACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"

_FORMS = {"10-K", "10-Q", "10-K/A", "10-Q/A"}

# Ordered fallbacks: many issuers file variant tags (consolidated-equity,
# diluted-only EPS, IFRS-style ProfitLoss); first present-and-usable tag wins.
# CORE concepts must all resolve for a snapshot to exist; EXTRA concepts are
# best-effort (missing -> the derived quality/growth ratio is null -> neutral-
# filled downstream), so adding them never shrinks coverage.
TAG_FALLBACKS = {
    "equity": [
        ("us-gaap", "StockholdersEquity", "USD"),
        ("us-gaap", "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
         "USD"),
    ],
    "shares": [
        ("us-gaap", "CommonStockSharesOutstanding", "shares"),
        ("dei", "EntityCommonStockSharesOutstanding", "shares"),
        ("us-gaap", "WeightedAverageNumberOfSharesOutstandingBasic", "shares"),
        ("us-gaap", "CommonStockSharesIssued", "shares"),
    ],
    "eps": [
        ("us-gaap", "EarningsPerShareBasic", "USD/shares"),
        ("us-gaap", "EarningsPerShareDiluted", "USD/shares"),
    ],
    "net_income": [
        ("us-gaap", "NetIncomeLoss", "USD"),
        ("us-gaap", "ProfitLoss", "USD"),
    ],
}
_CORE_CONCEPTS = ("equity", "shares", "eps", "net_income")

# Extra concepts for the quality/growth factor families (best-effort).
_EXTRA_TAGS = {
    "revenue": [
        ("us-gaap", "RevenueFromContractWithCustomerExcludingAssessedTax", "USD"),
        ("us-gaap", "Revenues", "USD"),
        ("us-gaap", "SalesRevenueNet", "USD"),
        ("us-gaap", "RevenueFromContractWithCustomerIncludingAssessedTax", "USD"),
    ],
    "assets": [
        ("us-gaap", "Assets", "USD"),
    ],
    "gross_profit": [
        ("us-gaap", "GrossProfit", "USD"),
    ],
    "operating_cash_flow": [
        ("us-gaap", "NetCashProvidedByUsedInOperatingActivities", "USD"),
        ("us-gaap",
         "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations", "USD"),
    ],
}
# period measures (flows) -> annualize by span; balances (equity, shares,
# assets) are point-in-time and taken as-is.
_FLOW_CONCEPTS = {"eps", "net_income", "revenue", "gross_profit", "operating_cash_flow"}


def _entries(facts: dict, taxonomy: str, tag: str, unit: str) -> list[dict]:
    return (facts.get("facts", {}).get(taxonomy, {}).get(tag, {}).get("units", {})
            .get(unit, []))


def _annualization(entry: dict) -> float | None:
    """365/period-days for flow entries; None when the span is unusable."""
    start_raw, end_raw = entry.get("start"), entry.get("end")
    if not start_raw or not end_raw:
        return None
    span = (date.fromisoformat(end_raw) - date.fromisoformat(start_raw)).days
    if span < 60 or span > 400:  # not a quarterly/annual period
        return None
    return 365.0 / span


_ALL_TAGS = {**TAG_FALLBACKS, **_EXTRA_TAGS}


def _per_accession(facts: dict, concept: str) -> dict[str, tuple[float, str]]:
    """{accession: (value, filed)} for a concept — first fallback tag that
    yields usable entries wins; within an accession the latest period end wins;
    flow concepts are annualized by their period length."""
    for taxonomy, tag, unit in _ALL_TAGS[concept]:
        best: dict[str, tuple[str, float, str]] = {}  # accn -> (end, value, filed)
        for entry in _entries(facts, taxonomy, tag, unit):
            if entry.get("form") not in _FORMS or entry.get("val") is None:
                continue
            value = float(entry["val"])
            if concept in _FLOW_CONCEPTS:
                factor = _annualization(entry)
                if factor is None:
                    continue
                value *= factor
            accn, end, filed = entry.get("accn"), entry.get("end", ""), entry.get("filed")
            if not accn or not filed:
                continue
            if accn not in best or end > best[accn][0]:
                best[accn] = (end, value, filed)
        if best:
            return {accn: (value, filed) for accn, (_end, value, filed) in best.items()}
    return {}


def _ratio(numerator, denominator):
    """Safe ratio: None when either input is missing or the denominator is 0."""
    if numerator is None or denominator in (None, 0.0):
        return None
    return numerator / denominator


def _yoy_growth(current, prior):
    """Year-over-year growth on a comparable-scale base (|prior|); None if either
    is missing or prior is ~0 (growth off a zero base is meaningless)."""
    if current is None or prior in (None, 0.0):
        return None
    return (current - prior) / abs(prior)


def snapshot_records(facts: dict, start: date, end: date) -> list[dict]:
    """Complete PIT snapshots from one companyfacts JSON, sorted by ``as_of``.

    A snapshot is emitted per accession where the four CORE concepts resolve
    (equity/shares/eps/net_income); ``as_of`` = the accession's filed date; one
    snapshot per as_of (latest accession wins). Quality ratios (roa,
    gross_margin, accruals, ocf_per_share) are best-effort — null when an EXTRA
    concept is missing for that accession (never dropping the snapshot).
    Year-over-year revenue/earnings growth is computed against the snapshot
    ~365 days prior within this issuer (null when no comparable prior exists).
    """
    per = {concept: _per_accession(facts, concept) for concept in _ALL_TAGS}
    core = [per[c] for c in _CORE_CONCEPTS]
    common = set.intersection(*(set(m) for m in core)) if all(core) else set()
    records = {}
    for accn in common:
        equity, filed = per["equity"][accn]
        shares, _ = per["shares"][accn]
        eps, _ = per["eps"][accn]
        net_income, _ = per["net_income"][accn]
        as_of = date.fromisoformat(filed)
        if as_of < start or as_of > end or equity == 0.0 or shares == 0.0:
            continue
        revenue = per["revenue"].get(accn, (None,))[0]
        assets = per["assets"].get(accn, (None,))[0]
        gross_profit = per["gross_profit"].get(accn, (None,))[0]
        ocf = per["operating_cash_flow"].get(accn, (None,))[0]
        accruals = None if (assets in (None, 0.0) or ocf is None) else (net_income - ocf) / assets
        records[as_of] = {
            "as_of": as_of.isoformat(),
            "book_value_per_share": equity / shares,
            "earnings_per_share": eps,
            "return_on_equity": net_income / equity,
            "return_on_assets": _ratio(net_income, assets),
            "gross_margin": _ratio(gross_profit, revenue),
            "accruals": accruals,
            "ocf_per_share": _ratio(ocf, shares),
            "_revenue": revenue,  # scratch: growth basis, dropped before return
        }
    ordered = [records[k] for k in sorted(records)]
    _attach_growth(ordered)
    return ordered


def _attach_growth(ordered: list[dict]) -> None:
    """In-place YoY revenue/earnings growth vs the snapshot ~365d earlier (a
    300-430d window tolerates quarterly cadence); drops the scratch revenue."""
    dates = [date.fromisoformat(r["as_of"]) for r in ordered]
    revenues = [r["_revenue"] for r in ordered]  # snapshot before mutating
    eps = [r["earnings_per_share"] for r in ordered]
    for i, rec in enumerate(ordered):
        prior = None
        for j in range(i - 1, -1, -1):
            gap = (dates[i] - dates[j]).days
            if 300 <= gap <= 430:
                prior = j
                break
            if gap > 430:
                break
        p = prior  # None when no comparable prior-year filing exists
        rec["revenue_growth"] = _yoy_growth(revenues[i], revenues[p]) if p is not None else None
        rec["earnings_growth"] = _yoy_growth(eps[i], eps[p]) if p is not None else None
        del rec["_revenue"]


def load_ticker_map(fetch_json) -> dict[str, int]:
    """SEC's current ticker->CIK map (class-share dots normalized to match the
    universe fixtures: BRK-B -> BRK.B)."""
    raw = fetch_json(TICKER_MAP_URL)
    return {
        str(row["ticker"]).upper().replace("-", "."): int(row["cik_str"])
        for row in raw.values()
    }


def resolve_cik(ticker: str, company_name: str, ticker_map: dict[str, int],
                fetch_text) -> int | None:
    """CIK for a (possibly departed) name: the current ticker map first, then
    EDGAR full-company search on the curated company name. None if unresolved
    (the caller neutral-fills; never a crash)."""
    cik = ticker_map.get(ticker.upper())
    if cik:
        return cik
    if not company_name:
        return None
    try:
        atom = fetch_text(SEARCH_URL.format(query=urllib.parse.quote(company_name)))
    except Exception as exc:
        _logger.warning("CIK search failed for %s (%s): %s", ticker, company_name, exc)
        return None
    match = re.search(r"CIK=(\d{10})", atom) or re.search(r"<CIK>(\d+)</CIK>", atom)
    return int(match.group(1)) if match else None


def http_fetcher(identity: str):  # pragma: no cover - egress plumbing
    """(fetch_json, fetch_text) pair with the SEC-required identity header."""

    def _get(url: str) -> bytes:
        request = urllib.request.Request(url, headers={"User-Agent": identity})
        with urllib.request.urlopen(request, timeout=60) as resp:
            return resp.read()

    return (lambda url: json.loads(_get(url))), (lambda url: _get(url).decode("utf-8", "replace"))


def fetch_company_records(symbol: str, start: date, end: date, identity: str,
                          company_name: str = "") -> list[dict]:  # pragma: no cover - egress
    """Live one-call path used by ``EdgarFundamentalsSource``: resolve, GET
    companyfacts, map to snapshot records."""
    fetch_json, fetch_text = http_fetcher(identity)
    cik = resolve_cik(symbol, company_name, load_ticker_map(fetch_json), fetch_text)
    if cik is None:
        _logger.warning("no CIK for %s; no fundamentals", symbol)
        return []
    return snapshot_records(fetch_json(COMPANYFACTS_URL.format(cik=cik)), start, end)
