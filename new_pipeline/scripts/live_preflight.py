"""Live-data preflight: verify external egress + credentials before a live run.

Checks, in order:

1. GDELT DOC 2.0 API egress (``api.gdeltproject.org``) — news sentiment source.
   GDELT rate-limits to one request per ~5s, so an HTTP 429 still proves egress
   and is reported as reachable.
2. SEC egress — ``www.sec.gov`` (EDGAR archives + financial-statement data
   sets, the fundamentals source) and ``data.sec.gov`` (XBRL frames API, an
   optional faster path; blocked egress there only degrades fundamentals to
   the data-set path).
3. Alpaca credentials — read-only ``GET /v2/account`` against the paper
   trading API plus a one-symbol daily-bars probe against the data API.
   Nothing is ordered or mutated.

Exit code 0 when every *required* check passes (GDELT, www.sec.gov, Alpaca);
1 otherwise. ``data.sec.gov`` is advisory and never fails the preflight.

  PYTHONPATH=. python -m new_pipeline.scripts.live_preflight
"""

import sys
from dataclasses import dataclass

import requests

from new_pipeline.adapters.fundamentals_sec import sec_user_agent
from new_pipeline.config import get_config

TIMEOUT = 20.0

GDELT_PROBE = (
    "https://api.gdeltproject.org/api/v2/doc/doc"
    "?query=%22stock%20market%22&mode=artlist&maxrecords=1&format=json"
)
SEC_WWW_PROBE = "https://www.sec.gov/files/company_tickers.json"
SEC_DATA_PROBE = (
    "https://data.sec.gov/api/xbrl/companyconcept/CIK0000320193/us-gaap/Assets.json"
)


@dataclass(frozen=True)
class CheckResult:
    name: str
    ok: bool
    required: bool
    detail: str


def _probe_url(name: str, url: str, required: bool, ok_statuses: frozenset[int]) -> CheckResult:
    try:
        response = requests.get(url, timeout=TIMEOUT, headers={"User-Agent": sec_user_agent()})
    except requests.RequestException as exc:
        return CheckResult(name, False, required, f"egress failed: {exc.__class__.__name__}: {exc}")
    if response.status_code in ok_statuses:
        note = " (429 = GDELT rate limiter; egress confirmed)" if response.status_code == 429 else ""
        return CheckResult(name, True, required, f"HTTP {response.status_code}{note}")
    return CheckResult(name, False, required, f"HTTP {response.status_code}")


def check_gdelt() -> CheckResult:
    return _probe_url("GDELT (api.gdeltproject.org)", GDELT_PROBE, True, frozenset({200, 429}))


def check_sec() -> list[CheckResult]:
    return [
        _probe_url("SEC EDGAR (www.sec.gov)", SEC_WWW_PROBE, True, frozenset({200})),
        _probe_url("SEC XBRL API (data.sec.gov, advisory)", SEC_DATA_PROBE, False, frozenset({200})),
    ]


def check_alpaca() -> list[CheckResult]:
    cfg = get_config()
    if not (cfg.alpaca.api_key and cfg.alpaca.secret_key):
        detail = "QA_ALPACA__API_KEY / QA_ALPACA__SECRET_KEY not set"
        return [CheckResult("Alpaca credentials", False, True, detail)]
    results: list[CheckResult] = []
    try:
        from new_pipeline.adapters.broker_alpaca import AlpacaBroker

        account = AlpacaBroker(cfg.alpaca.api_key, cfg.alpaca.secret_key, paper=True).account()
        results.append(
            CheckResult(
                "Alpaca trading API (paper)", True, True,
                f"account status={account.get('status')} equity={account.get('equity')}",
            )
        )
    except Exception as exc:  # noqa: BLE001 - report any SDK/auth failure as a check result
        results.append(
            CheckResult(
                "Alpaca trading API (paper)", False, True, f"{exc.__class__.__name__}: {exc}"
            )
        )
    try:
        from datetime import date, timedelta

        from new_pipeline.adapters.market_alpaca import AlpacaMarketDataSource

        source = AlpacaMarketDataSource(
            cfg.alpaca.api_key, cfg.alpaca.secret_key, feed=cfg.alpaca.data_feed
        )
        end = date.today() - timedelta(days=1)
        bars = source.history("AAPL", end - timedelta(days=10), end)
        results.append(
            CheckResult(
                "Alpaca market data API", True, True,
                f"AAPL daily bars over last 10d: {len(bars)}",
            )
        )
    except Exception as exc:  # noqa: BLE001
        results.append(
            CheckResult("Alpaca market data API", False, True, f"{exc.__class__.__name__}: {exc}")
        )
    return results


def run_preflight() -> list[CheckResult]:
    return [check_gdelt(), *check_sec(), *check_alpaca()]


def main() -> int:
    results = run_preflight()
    width = max(len(result.name) for result in results)
    hard_failures = 0
    for result in results:
        if result.ok:
            mark = "PASS"
        elif result.required:
            mark, hard_failures = "FAIL", hard_failures + 1
        else:
            mark = "WARN"
        print(f"[{mark}] {result.name:<{width}}  {result.detail}")
    if hard_failures:
        print(f"\npreflight FAILED: {hard_failures} required check(s) failed")
        return 1
    print("\npreflight OK: all required checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
