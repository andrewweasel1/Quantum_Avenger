"""Resumable SIP daily-bar vault for Liquid-N universe candidates. [RESEARCH]

STATUS — KNOWN SURVIVORSHIP LIMITATION (2026-07 audit): Alpaca's asset registry
is NOT a complete delisting history. Verified against the S&P PIT fixture's
departed names: only 60% of known departures appear in the registry (40%
missing entirely — ATVI, AET, BRCM, CBS, ...; the "inactive" list is mostly
OTC). A backtest universe enumerated from this registry therefore MISSES ~40%
of delistings and carries material survivorship bias in any extension beyond
the externally-sourced S&P 500 PIT fixture. Usable honestly only for (a)
forward/live universes (no history needed) or (b) explicitly-caveated
time-limited extensions. Kept as the ingest half of that future work.

Enumerates US common-stock candidates from Alpaca's asset registry (active +
partial inactive), filters obvious non-common instruments (warrants/units/
rights/preferred/ETF-family names), then ingests split+dividend-adjusted
(``adjustment=all``) SIP daily bars per candidate in batched multi-symbol
requests. Bars land in ``<vault>/chunks/<i>.parquet`` per symbol-chunk
(already-present chunks are skipped: resumable) and merge into ``bars.parquet``.

    python -m new_pipeline.scripts.ingest_liquid_universe_vault \
        --start 2015-01-01 --end 2025-12-31 --vault-dir ./data/liquid_vault
"""

import argparse
import json
import os
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ASSETS_URL = "https://paper-api.alpaca.markets/v2/assets?status={status}&asset_class=us_equity"
BARS_URL = "https://data.alpaca.markets/v2/stocks/bars"
_EXCHANGES = {"NYSE", "NASDAQ", "ARCA", "AMEX", "BATS", "NYSEARCA", "NYSEMKT"}
# Name substrings that mark non-common-stock instruments. Kept conservative:
# REIT "Trust" names are legitimate holdings, so bare "TRUST" is NOT excluded —
# fund-family names and explicit instrument words are.
_EXCLUDE_NAME = re.compile(
    r"WARRANT|RIGHTS?\b|\bUNITS?\b|PREFERRED|\bPFD\b|DEPOSITARY|%|"
    r"\bETF\b|\bETN\b|ISHARES|SPDR|PROSHARES|DIREXION|VANECK|WISDOMTREE|"
    r"INDEX FUND|EXCHANGE.TRADED|CLOSED.END",
    re.IGNORECASE,
)
# Symbols with a suffix class-share dot are fine (BRK.A); 5+ letter symbols
# ending in W/R/U are overwhelmingly warrants/rights/units.
_EXCLUDE_SYMBOL = re.compile(r"^[A-Z]{4,}[WRU]$")


def filter_candidates(assets: list[dict]) -> list[str]:
    """Common-stock candidate symbols from the raw asset registry rows."""
    keep = []
    for asset in assets:
        symbol = (asset.get("symbol") or "").strip().upper()
        name = asset.get("name") or ""
        if not symbol or asset.get("class") not in (None, "us_equity"):
            continue
        if asset.get("exchange") not in _EXCHANGES:
            continue
        if _EXCLUDE_NAME.search(name) or _EXCLUDE_SYMBOL.match(symbol):
            continue
        keep.append(symbol)
    return sorted(set(keep))


def chunk(symbols: list[str], size: int) -> list[list[str]]:
    return [symbols[i:i + size] for i in range(0, len(symbols), size)]


def _headers() -> dict:  # pragma: no cover - env plumbing
    return {
        "APCA-API-KEY-ID": os.environ.get("QA_ALPACA__API_KEY", ""),
        "APCA-API-SECRET-KEY": os.environ.get("QA_ALPACA__SECRET_KEY", ""),
    }


def _get_json(url: str, retries: int = 5):  # pragma: no cover - egress
    for attempt in range(retries):
        request = urllib.request.Request(url, headers=_headers())
        try:
            with urllib.request.urlopen(request, timeout=90) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as exc:
            if exc.code == 429:  # rate limited: back off and retry
                time.sleep(10.0 * (attempt + 1))
                continue
            if exc.code in (403, 404, 422):
                return None
            if attempt == retries - 1:
                raise
            time.sleep(3.0 * (attempt + 1))
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt == retries - 1:
                return None
            time.sleep(3.0 * (attempt + 1))
    return None


def fetch_chunk_bars(symbols, start, end, sleep) -> list[dict]:  # pragma: no cover - egress
    """All daily bars for one symbol chunk (paginated multi-symbol request).

    A 400 (one unknown/mal-formed symbol poisons the whole multi-symbol
    request) bisects the batch recursively, so bad census symbols cost their
    own sub-request instead of the run."""
    rows, token = [], None
    base = (
        f"{BARS_URL}?symbols={','.join(urllib.parse.quote(s) for s in symbols)}"
        f"&timeframe=1Day&adjustment=all&feed=sip&limit=10000"
        f"&start={start}&end={end}"
    )
    while True:
        url = base + (f"&page_token={token}" if token else "")
        try:
            payload = _get_json(url)
        except urllib.error.HTTPError as exc:
            if exc.code == 400 and len(symbols) > 1:
                mid = len(symbols) // 2
                return (fetch_chunk_bars(symbols[:mid], start, end, sleep)
                        + fetch_chunk_bars(symbols[mid:], start, end, sleep))
            if exc.code == 400:
                return rows  # single bad symbol: skip it
            raise
        if payload is None:
            break
        for symbol, bars in (payload.get("bars") or {}).items():
            for bar in bars:
                rows.append({
                    "ticker": symbol, "date": bar["t"][:10], "open": bar["o"],
                    "high": bar["h"], "low": bar["l"], "close": bar["c"],
                    "volume": bar["v"],
                })
        token = payload.get("next_page_token")
        if not token:
            break
        time.sleep(sleep)
    return rows


def main() -> None:  # pragma: no cover - egress orchestration around tested helpers
    import polars as pl

    parser = argparse.ArgumentParser(description="Liquid-universe SIP bar vault ingest")
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--vault-dir", default="data/liquid_vault")
    parser.add_argument("--chunk-size", type=int, default=100)
    parser.add_argument("--sleep", type=float, default=0.35)  # ~170 req/min headroom
    args = parser.parse_args()

    vault = Path(args.vault_dir)
    chunks_dir = vault / "chunks"
    chunks_dir.mkdir(parents=True, exist_ok=True)

    candidates_path = vault / "candidates.json"
    if candidates_path.exists():
        symbols = json.loads(candidates_path.read_text())
    else:
        assets = []
        for status in ("active", "inactive"):
            payload = _get_json(ASSETS_URL.format(status=status))
            assets.extend(payload or [])
        symbols = filter_candidates(assets)
        candidates_path.write_text(json.dumps(symbols))
    print(f"candidates: {len(symbols)} symbols", flush=True)

    batches = chunk(symbols, args.chunk_size)
    tally = {"fetched": 0, "cached": 0, "rows": 0}
    for index, batch in enumerate(batches):
        out = chunks_dir / f"{index:05d}.parquet"
        if out.exists():
            tally["cached"] += 1
            continue
        rows = fetch_chunk_bars(batch, args.start, args.end, args.sleep)
        frame = pl.DataFrame(
            rows,
            schema={"ticker": pl.Utf8, "date": pl.Utf8, "open": pl.Float64,
                    "high": pl.Float64, "low": pl.Float64, "close": pl.Float64,
                    "volume": pl.Float64},
        )
        frame.write_parquet(out)
        tally["fetched"] += 1
        tally["rows"] += frame.height
        if (index + 1) % 10 == 0:
            print(f"[{index + 1}/{len(batches)}] {tally}", flush=True)
        time.sleep(args.sleep)

    merged = pl.concat([pl.read_parquet(p) for p in sorted(chunks_dir.glob("*.parquet"))])
    merged = merged.with_columns(pl.col("date").str.to_date()).sort(["ticker", "date"])
    merged.write_parquet(vault / "bars.parquet")
    print(f"merged {merged.height:,} bars, {merged['ticker'].n_unique():,} tickers "
          f"-> {vault / 'bars.parquet'}", flush=True)


if __name__ == "__main__":  # pragma: no cover
    main()
