"""SEC EDGAR fundamentals adapter (Financial Statement Data Sets).

``data.sec.gov`` (the XBRL frames/companyfacts API) is often unreachable from
sandboxed runners, so this adapter uses the quarterly **Financial Statement
Data Sets** ZIPs served from ``www.sec.gov`` instead — one ~70 MB archive per
quarter containing every XBRL fact filed with the SEC:

    https://www.sec.gov/files/dera/data/financial-statement-data-sets/<yyyy>q<n>.zip

Per quarter we keep only 10-K/10-Q submissions for the requested CIKs and the
handful of us-gaap tags needed for three slow-moving fundamentals features:

* ``fund_rev_yoy``    — year-over-year revenue growth (same-filing comparative)
* ``fund_net_margin`` — net income / revenue
* ``fund_roe``        — net income / stockholders' equity

Every feature is stamped with the filing's ``filed`` date and merged into the
bar frame with a *backward* as-of join, so a bar only ever sees fundamentals
that were public on that day (no look-ahead, G5).

SEC requires a descriptive User-Agent with a contact address; override the
default with ``QA_SEC__USER_AGENT``. Filtered facts are cached per quarter as
Parquet so repeat backtests never re-download.
"""

import io
import logging
import os
import zipfile
from datetime import date
from pathlib import Path

import polars as pl
import requests

from new_pipeline.core.exceptions import AdapterError

logger = logging.getLogger(__name__)

DATASET_URL = "https://www.sec.gov/files/dera/data/financial-statement-data-sets/{quarter}.zip"
DEFAULT_USER_AGENT = "QuantumAvenger research (andrew.weasel.1@gmail.com)"
TIMEOUT = 120.0

REVENUE_TAGS = (
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "SalesRevenueNet",
)
NET_INCOME_TAGS = ("NetIncomeLoss",)
EQUITY_TAGS = (
    "StockholdersEquity",
    "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest",
)
ALL_TAGS = (*REVENUE_TAGS, *NET_INCOME_TAGS, *EQUITY_TAGS)
FEATURE_COLUMNS = ("fund_rev_yoy", "fund_net_margin", "fund_roe")
_RATIO_CLIP = 5.0  # tame data glitches (restatements, near-zero denominators)


def sec_user_agent() -> str:
    return os.environ.get("QA_SEC__USER_AGENT", DEFAULT_USER_AGENT)


def quarters_for_range(start: date, end: date) -> list[str]:
    """Data-set quarter names whose filings can land inside [start, end]."""
    quarters: list[str] = []
    year, quarter = start.year, (start.month - 1) // 3 + 1
    while (year, quarter) <= (end.year, (end.month - 1) // 3 + 1):
        quarters.append(f"{year}q{quarter}")
        quarter += 1
        if quarter == 5:
            year, quarter = year + 1, 1
    return quarters


class SecFundamentalsSource:
    """Point-in-time fundamentals features from EDGAR financial data sets."""

    def __init__(
        self,
        cache_dir: Path,
        ciks_by_ticker: dict[str, int],
        session: requests.Session | None = None,
    ) -> None:
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._ciks_by_ticker = dict(ciks_by_ticker)
        self._session = session or requests.Session()

    def features(self, start: date, end: date) -> pl.DataFrame:
        """(ticker, filed, fund_rev_yoy, fund_net_margin, fund_roe), one row per filing."""
        facts: list[pl.DataFrame] = []
        for quarter in quarters_for_range(start, end):
            try:
                facts.append(self._quarter_facts(quarter))
            except AdapterError as exc:
                logger.warning("skipping SEC data set %s: %s", quarter, exc)
        if not facts:
            return _empty_features()
        return build_fundamentals_features(pl.concat(facts), self._ciks_by_ticker)

    def _quarter_facts(self, quarter: str) -> pl.DataFrame:
        cache_path = self._cache_dir / f"{quarter}.parquet"
        if cache_path.exists():
            return pl.read_parquet(cache_path)
        zip_path = self._cache_dir / f"{quarter}.zip"  # pre-seeded archive, if any
        if zip_path.exists():
            payload = zip_path.read_bytes()
        else:
            url = DATASET_URL.format(quarter=quarter)
            logger.info("downloading SEC financial data set %s", quarter)
            try:
                response = self._session.get(
                    url, timeout=TIMEOUT, headers={"User-Agent": sec_user_agent()}
                )
            except requests.RequestException as exc:
                raise AdapterError(f"SEC data set download failed: {exc}") from exc
            if response.status_code != 200:
                raise AdapterError(f"SEC data set HTTP {response.status_code} for {url}")
            payload = response.content
        facts = _parse_dataset_zip(payload, set(self._ciks_by_ticker.values()))
        facts.write_parquet(cache_path)
        return facts


def _read_tsv(archive: zipfile.ZipFile, name: str, columns: list[str]) -> pl.DataFrame:
    with archive.open(name) as handle:
        return pl.read_csv(
            io.BytesIO(handle.read()),
            separator="\t",
            quote_char=None,
            columns=columns,
            infer_schema_length=0,  # everything as string; cast explicitly below
        )


def _parse_dataset_zip(payload: bytes, ciks: set[int]) -> pl.DataFrame:
    """Filter one quarter's sub.txt/num.txt down to our CIKs + tags."""
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        subs = _read_tsv(archive, "sub.txt", ["adsh", "cik", "form", "filed"])
        subs = (
            subs.with_columns(pl.col("cik").cast(pl.Int64), pl.col("filed").cast(pl.Int64))
            .filter(pl.col("form").is_in(["10-K", "10-Q"]) & pl.col("cik").is_in(list(ciks)))
        )
        nums = _read_tsv(
            archive, "num.txt",
            ["adsh", "tag", "ddate", "qtrs", "uom", "segments", "coreg", "value"],
        )
    # segments == '' keeps only consolidated totals (dimensional/segment facts
    # like per-product revenue or equity components would poison the ratios).
    nums = nums.filter(
        pl.col("adsh").is_in(subs["adsh"].implode())
        & pl.col("tag").is_in(list(ALL_TAGS))
        & (pl.col("uom") == "USD")
        & (pl.col("segments").is_null() | (pl.col("segments") == ""))
        & (pl.col("coreg").is_null() | (pl.col("coreg") == ""))
        & (pl.col("value") != "")
    ).with_columns(
        pl.col("ddate").cast(pl.Int64),
        pl.col("qtrs").cast(pl.Int64),
        pl.col("value").cast(pl.Float64, strict=False),
    )
    return (
        nums.drop("uom", "segments", "coreg")
        .drop_nulls("value")
        .unique(subset=["adsh", "tag", "ddate", "qtrs"], keep="first")
        .join(subs, on="adsh", how="inner")
        .select("cik", "adsh", "form", "filed", "tag", "ddate", "qtrs", "value")
    )


def _first_available(facts: pl.LazyFrame, tags: tuple[str, ...], alias: str) -> pl.LazyFrame:
    """Per (adsh, ddate, qtrs): the value of the first tag in ``tags`` that exists."""
    ranked = (
        facts.filter(pl.col("tag").is_in(list(tags)))
        .with_columns(
            pl.col("tag").replace_strict(
                {tag: rank for rank, tag in enumerate(tags)}, return_dtype=pl.Int64
            ).alias("_rank")
        )
        .sort("_rank")
        .group_by("adsh", "ddate", "qtrs", maintain_order=True)
        .agg(pl.col("value").first().alias(alias))
    )
    return ranked


def build_fundamentals_features(
    facts: pl.DataFrame, ciks_by_ticker: dict[str, int]
) -> pl.DataFrame:
    """Per-filing features from raw facts. Pure + deterministic (unit-testable).

    Flows (revenue, net income) use the filing's primary duration — quarterly
    (qtrs=1) for 10-Qs, annual (qtrs=4) for 10-Ks — at the latest ``ddate``;
    the year-ago comparative in the same filing supplies the YoY denominator.
    Equity is the latest instant (qtrs=0) value.
    """
    if facts.is_empty():
        return _empty_features()
    lazy = facts.lazy()
    primary_qtrs = pl.when(pl.col("form") == "10-K").then(4).otherwise(1)
    meta = lazy.select("adsh", "cik", "form", "filed").unique()

    revenue = _first_available(lazy, REVENUE_TAGS, "revenue")
    income = _first_available(lazy, NET_INCOME_TAGS, "net_income")
    equity = _first_available(lazy, EQUITY_TAGS, "equity")

    flows = meta.join(revenue, on="adsh").join(
        income, on=["adsh", "ddate", "qtrs"], how="left"
    )
    flows = flows.filter(pl.col("qtrs") == primary_qtrs)
    latest = flows.group_by("adsh").agg(pl.col("ddate").max().alias("_latest"))
    current = flows.join(latest, on="adsh").filter(pl.col("ddate") == pl.col("_latest"))
    year_ago = flows.join(latest, on="adsh").filter(
        pl.col("ddate") <= pl.col("_latest") - 9500  # ~1 year earlier in yyyymmdd space
    ).group_by("adsh").agg(pl.col("revenue").sort_by("ddate").last().alias("revenue_prior"))

    equity_latest = (
        equity.filter(pl.col("qtrs") == 0)
        .group_by("adsh")
        .agg(pl.col("equity").sort_by("ddate").last())
    )

    joined = (
        current.join(year_ago, on="adsh", how="left")
        .join(equity_latest, on="adsh", how="left")
        .with_columns(
            _safe_ratio(pl.col("revenue") - pl.col("revenue_prior"), pl.col("revenue_prior"))
            .alias("fund_rev_yoy"),
            _safe_ratio(pl.col("net_income"), pl.col("revenue")).alias("fund_net_margin"),
            _safe_ratio(pl.col("net_income"), pl.col("equity")).alias("fund_roe"),
        )
        .with_columns(
            pl.col("filed").cast(pl.String).str.to_date("%Y%m%d").alias("filed"),
        )
        .select("cik", "filed", *FEATURE_COLUMNS)
        .collect()
    )
    tickers = pl.DataFrame(
        {"ticker": list(ciks_by_ticker), "cik": [int(v) for v in ciks_by_ticker.values()]}
    )
    return (
        joined.join(tickers, on="cik", how="inner")
        .select("ticker", "filed", *FEATURE_COLUMNS)
        .sort("ticker", "filed")
    )


def _safe_ratio(numerator: pl.Expr, denominator: pl.Expr) -> pl.Expr:
    return (
        pl.when(denominator.abs() > 1e-9)
        .then((numerator / denominator).clip(-_RATIO_CLIP, _RATIO_CLIP))
        .otherwise(None)
    )


def _empty_features() -> pl.DataFrame:
    return pl.DataFrame(
        schema={
            "ticker": pl.String,
            "filed": pl.Date,
            **{column: pl.Float64 for column in FEATURE_COLUMNS},
        }
    )


def merge_fundamentals(bars: pl.DataFrame, features: pl.DataFrame) -> pl.DataFrame:
    """As-of join per ticker: each bar sees the latest filing on or before its date.

    Missing values stay neutral (0.0) so tickers without filings keep trading.
    """
    if features.is_empty():
        return bars.with_columns(
            *[pl.lit(0.0).alias(column) for column in FEATURE_COLUMNS]
        )
    merged = bars.sort("ticker", "date").join_asof(
        features.rename({"filed": "date"}).sort("ticker", "date"),
        on="date",
        by="ticker",
        strategy="backward",
    )
    return merged.with_columns(
        *[pl.col(column).fill_null(0.0) for column in FEATURE_COLUMNS]
    )
