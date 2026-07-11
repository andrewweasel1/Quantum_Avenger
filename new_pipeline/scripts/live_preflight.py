"""One-command diagnosis of live-data-plane readiness.

Run on the host that will do live ingest / paper trading:

    python -m new_pipeline.scripts.live_preflight

Reports, without placing any order or mutating anything:
  1. SDKs        — alpaca-py / edgartools importability (+ versions)
  2. Credentials — QA_ALPACA__API_KEY / QA_ALPACA__SECRET_KEY present;
                   news.edgar_identity configured
  3. Egress      — each live host reachable through this network's policy
                   (an HTTP status, even 401/403, means REACHABLE; a
                   connect/DNS failure means the policy blocks it)
  4. Account     — if creds + egress line up, a read-only Alpaca paper
                   account snapshot (the safe first half of live_smoke)

Exit code 0 when the Alpaca path is fully ready (SDK + creds + egress);
1 otherwise. GDELT/EDGAR readiness is informational — news/fundamentals
ingest degrades gracefully to the offline fixtures without them.
"""

import os
import sys
import urllib.error
import urllib.request

HOSTS = {
    "alpaca-paper": "https://paper-api.alpaca.markets/v2/account",
    "alpaca-data": "https://data.alpaca.markets/v2/stocks/AAPL/bars?timeframe=1Day&limit=1",
    "gdelt": "https://api.gdeltproject.org/api/v2/doc/doc?query=test&maxrecords=1&format=json",
    "sec-edgar": "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=AAPL&count=1",
}


def check_sdks() -> dict[str, str]:
    out = {}
    try:
        import alpaca

        out["alpaca-py"] = f"ok ({getattr(alpaca, '__version__', 'unknown')})"
    except ImportError:
        out["alpaca-py"] = "MISSING — pip install -r new_pipeline/requirements-live.txt"
    try:
        import edgar  # noqa: F401  (edgartools)

        out["edgartools"] = "ok"
    except ImportError:
        out["edgartools"] = "MISSING — pip install -r new_pipeline/requirements-live.txt"
    return out


def check_credentials() -> dict[str, str]:
    def present(name):
        return "set" if os.environ.get(name) else "NOT SET"

    creds = {
        "QA_ALPACA__API_KEY": present("QA_ALPACA__API_KEY"),
        "QA_ALPACA__SECRET_KEY": present("QA_ALPACA__SECRET_KEY"),
    }
    try:
        from new_pipeline.config import get_config

        identity = get_config().news.edgar_identity
        creds["news.edgar_identity"] = identity or "NOT SET (required for EDGAR)"
    except Exception as exc:
        creds["news.edgar_identity"] = f"config error: {exc}"
    return creds


def check_egress(fetch=None) -> dict[str, str]:
    def default_fetch(url):
        request = urllib.request.Request(url, headers={"User-Agent": "qa-preflight"})
        try:
            with urllib.request.urlopen(request, timeout=10) as response:
                return f"reachable (HTTP {response.status})"
        except urllib.error.HTTPError as exc:  # an HTTP status means we got through
            return f"reachable (HTTP {exc.code})"
        except Exception as exc:
            return f"BLOCKED ({type(exc).__name__})"

    fetch = fetch or default_fetch
    return {name: fetch(url) for name, url in HOSTS.items()}


def account_snapshot() -> str:
    key = os.environ.get("QA_ALPACA__API_KEY")
    secret = os.environ.get("QA_ALPACA__SECRET_KEY")
    if not (key and secret):
        return "skipped (no credentials)"
    try:
        from alpaca.trading.client import TradingClient

        account = TradingClient(key, secret, paper=True).get_account()
        return f"ok — status={account.status} equity={account.equity}"
    except Exception as exc:
        return f"FAILED ({type(exc).__name__}: {exc})"


def main() -> int:  # pragma: no cover - orchestration; helpers are unit-tested
    sections = {
        "SDKs": check_sdks(),
        "Credentials": check_credentials(),
        "Egress": check_egress(),
    }
    for title, rows in sections.items():
        print(f"\n== {title} ==")
        for name, value in rows.items():
            print(f"  {name:<24} {value}")
    print("\n== Alpaca account (read-only) ==")
    print(f"  {account_snapshot()}")

    ready = (
        sections["SDKs"]["alpaca-py"].startswith("ok")
        and sections["Credentials"]["QA_ALPACA__API_KEY"] == "set"
        and sections["Credentials"]["QA_ALPACA__SECRET_KEY"] == "set"
        and sections["Egress"]["alpaca-paper"].startswith("reachable")
    )
    print(f"\nAlpaca live path: {'READY' if ready else 'NOT READY'}")
    return 0 if ready else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
