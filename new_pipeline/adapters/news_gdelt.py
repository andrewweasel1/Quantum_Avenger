"""GDELT DOC 2.0 news adapters (``NewsSource`` + daily tone series).

Two things live here:

* :class:`GdeltNewsSource` — per-symbol headlines via ``mode=artlist``,
  implementing the project ``NewsSource`` ABC.
* :func:`fetch_tone_series` / :func:`sector_tone_frame` — daily average tone
  (GDELT's document-level sentiment, roughly [-10, +10]) via
  ``mode=timelinetone``. One request returns a full daily series, which is how
  the S&P 500 backtest gets a *sector-level* news-sentiment feature without
  issuing 500+ rate-limited calls.

GDELT enforces ~1 request per 5 seconds per client; :class:`GdeltClient`
serializes calls behind that interval and retries 429s with backoff. Requires
egress to ``api.gdeltproject.org`` (verified by ``scripts/live_preflight``).
"""

import logging
import time
from datetime import date, datetime, timedelta
from pathlib import Path

import polars as pl
import requests

from new_pipeline.adapters.base import NewsItem, NewsSource
from new_pipeline.core.exceptions import NewsSourceError

logger = logging.getLogger(__name__)

DOC_API_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
MIN_REQUEST_INTERVAL = 6.0  # GDELT asks for >= 5s between requests
MAX_RETRIES = 8  # shared/proxied egress IPs get throttled well beyond 5s
TIMEOUT = 30.0

# GICS sector -> GDELT full-text query for sector-level tone. Phrases keep the
# match precise; the market query is the fallback for symbols/sectors with no
# series of their own.
MARKET_TONE_QUERY = '"stock market"'
SECTOR_TONE_QUERIES: dict[str, str] = {
    "Information Technology": '"technology stocks" OR "tech stocks"',
    "Health Care": '"healthcare stocks" OR "pharmaceutical industry"',
    "Financials": '"bank stocks" OR "financial stocks"',
    "Consumer Discretionary": '"retail stocks" OR "consumer spending"',
    "Consumer Staples": '"consumer staples" OR "food industry"',
    "Communication Services": '"media stocks" OR "telecom industry"',
    "Industrials": '"industrial stocks" OR "manufacturing sector"',
    "Energy": '"oil prices" OR "energy stocks"',
    "Utilities": '"utility stocks" OR "electric utilities"',
    "Real Estate": '"real estate market" OR "REIT"',
    "Materials": '"commodity prices" OR "mining industry"',
}


class GdeltClient:
    """Throttled GDELT DOC API client (shared by headlines + tone series)."""

    def __init__(self, session: requests.Session | None = None) -> None:
        self._session = session or requests.Session()
        self._last_request = 0.0

    def query(self, params: dict) -> dict:
        for attempt in range(MAX_RETRIES):
            self._throttle()
            response = self._session.get(DOC_API_URL, params=params, timeout=TIMEOUT)
            self._last_request = time.monotonic()
            if response.status_code == 429:
                logger.warning("GDELT 429; backing off (attempt %d)", attempt + 1)
                time.sleep(MIN_REQUEST_INTERVAL * (attempt + 1))
                continue
            if response.status_code != 200:
                raise NewsSourceError(f"GDELT HTTP {response.status_code}: {response.text[:200]}")
            try:
                return response.json()
            except ValueError as exc:
                # GDELT returns plain-text rate-limit notices with HTTP 200.
                if "limit requests" in response.text.lower():
                    logger.warning("GDELT soft rate limit; backing off (attempt %d)", attempt + 1)
                    time.sleep(MIN_REQUEST_INTERVAL * (attempt + 1))
                    continue
                raise NewsSourceError(f"GDELT non-JSON response: {response.text[:200]}") from exc
        raise NewsSourceError(f"GDELT rate-limited after {MAX_RETRIES} attempts")

    def _throttle(self) -> None:
        wait = MIN_REQUEST_INTERVAL - (time.monotonic() - self._last_request)
        if wait > 0:
            time.sleep(wait)


def _fmt(moment: datetime) -> str:
    return moment.strftime("%Y%m%d%H%M%S")


class GdeltNewsSource(NewsSource):
    """``NewsSource`` over GDELT artlist — headlines mentioning the company."""

    def __init__(self, company_names: dict[str, str], limit: int = 10, client=None) -> None:
        self._names = company_names  # ticker -> company name for the query
        self._limit = limit
        self._client = client or GdeltClient()

    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        name = self._names.get(symbol, symbol)
        payload = self._client.query(
            {
                "query": f'"{name}" sourcelang:english',
                "mode": "artlist",
                "maxrecords": self._limit,
                "format": "json",
                "startdatetime": _fmt(datetime.combine(on, datetime.min.time())),
                "enddatetime": _fmt(datetime.combine(on, datetime.max.time())),
            }
        )
        items = []
        for article in payload.get("articles", []):
            seen = article.get("seendate", "")
            try:
                stamp = datetime.strptime(seen, "%Y%m%dT%H%M%SZ")
            except ValueError:
                stamp = datetime.combine(on, datetime.min.time())
            items.append(NewsItem(timestamp=stamp, symbol=symbol, headline=article.get("title", "")))
        return items


def fetch_tone_series(query: str, start: date, end: date, client=None) -> pl.DataFrame:
    """Daily average tone for ``query`` as a (date, tone) frame via timelinetone."""
    client = client or GdeltClient()
    payload = client.query(
        {
            # GDELT requires parentheses around OR'd terms when combined with
            # other operators (like sourcelang:).
            "query": f"({query}) sourcelang:english",
            "mode": "timelinetone",
            "format": "json",
            "startdatetime": _fmt(datetime.combine(start, datetime.min.time())),
            "enddatetime": _fmt(datetime.combine(end + timedelta(days=1), datetime.min.time())),
        }
    )
    rows: list[dict] = []
    for series in payload.get("timeline", []):
        for point in series.get("data", []):
            stamp = point.get("date", "")
            try:
                day = datetime.strptime(stamp, "%Y%m%dT%H%M%SZ").date()
            except ValueError:
                continue
            rows.append({"date": day, "tone": float(point.get("value", 0.0))})
    if not rows:
        return pl.DataFrame(schema={"date": pl.Date, "tone": pl.Float64})
    return (
        pl.DataFrame(rows)
        .group_by("date")
        .agg(pl.col("tone").mean())
        .sort("date")
    )


def _cached_tone_series(
    query: str, name: str, start: date, end: date, client, cache_dir: Path | None
) -> pl.DataFrame:
    """Per-query Parquet cache so an interrupted multi-sector fetch resumes."""
    if cache_dir is None:
        return fetch_tone_series(query, start, end, client)
    cache_dir.mkdir(parents=True, exist_ok=True)
    slug = name.lower().replace(" ", "_")
    path = cache_dir / f"tone_{slug}_{start:%Y%m%d}_{end:%Y%m%d}.parquet"
    if path.exists():
        return pl.read_parquet(path)
    series = fetch_tone_series(query, start, end, client)
    if not series.is_empty():
        series.write_parquet(path)
    return series


def sector_tone_frame(
    sectors: list[str], start: date, end: date, client=None, cache_dir: Path | None = None
) -> pl.DataFrame:
    """(date, gics_sector, sentiment_score) for every requested GICS sector.

    Tone is z-scored per sector over the fetched window so the feature is
    scale-free; sectors whose GDELT query fails fall back to the market-level
    series (and ultimately to 0.0 — neutral — matching the engine default).
    """
    client = client or GdeltClient()
    try:
        market = _cached_tone_series(MARKET_TONE_QUERY, "market", start, end, client, cache_dir)
    except NewsSourceError as exc:
        logger.warning("GDELT market tone failed: %s", exc)
        market = pl.DataFrame(schema={"date": pl.Date, "tone": pl.Float64})
    frames: list[pl.DataFrame] = []
    for sector in sectors:
        query = SECTOR_TONE_QUERIES.get(sector)
        series = pl.DataFrame(schema={"date": pl.Date, "tone": pl.Float64})
        if query is not None:
            try:
                series = _cached_tone_series(query, sector, start, end, client, cache_dir)
            except NewsSourceError as exc:
                logger.warning("GDELT tone failed for sector %s: %s", sector, exc)
        if series.is_empty():
            series = market
        if series.is_empty():
            continue
        mean, std = series["tone"].mean(), series["tone"].std()
        score = (
            (pl.col("tone") - mean) / std if std and std > 0 else pl.lit(0.0)
        )
        frames.append(
            series.with_columns(
                pl.lit(sector).alias("gics_sector"), score.alias("sentiment_score")
            ).select("date", "gics_sector", "sentiment_score")
        )
    if not frames:
        return pl.DataFrame(
            schema={"date": pl.Date, "gics_sector": pl.String, "sentiment_score": pl.Float64}
        )
    return pl.concat(frames)
