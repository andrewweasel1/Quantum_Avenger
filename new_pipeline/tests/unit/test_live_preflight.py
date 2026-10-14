"""Preflight helpers (pure parts — the egress fetch is injected)."""

from new_pipeline.scripts.live_preflight import (
    HOSTS,
    account_snapshot,
    check_credentials,
    check_egress,
    check_sdks,
)


def test_check_sdks_reports_status():
    report = check_sdks()
    assert set(report) == {"alpaca-py", "edgartools"}
    assert all(v.startswith(("ok", "MISSING")) for v in report.values())


def test_check_credentials_reflects_env(monkeypatch):
    monkeypatch.delenv("QA_ALPACA__API_KEY", raising=False)
    monkeypatch.setenv("QA_ALPACA__SECRET_KEY", "s")
    report = check_credentials()
    assert report["QA_ALPACA__API_KEY"] == "NOT SET"
    assert report["QA_ALPACA__SECRET_KEY"] == "set"
    assert "news.edgar_identity" in report


def test_check_egress_classifies_with_injected_fetch():
    report = check_egress(fetch=lambda url: "reachable (HTTP 401)")
    assert set(report) == set(HOSTS)
    assert all(v == "reachable (HTTP 401)" for v in report.values())


def test_account_snapshot_skips_without_credentials(monkeypatch):
    monkeypatch.delenv("QA_ALPACA__API_KEY", raising=False)
    monkeypatch.delenv("QA_ALPACA__SECRET_KEY", raising=False)
    assert account_snapshot() == "skipped (no credentials)"
