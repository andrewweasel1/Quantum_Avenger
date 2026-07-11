"""Bearer-token gate on the dashboard API (config-gated, env-sourced secret)."""

import pytest
from fastapi.testclient import TestClient
from new_pipeline.api.app import create_app
from new_pipeline.config import reload_config


@pytest.fixture
def secured_client(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_DASHBOARD__AUTH_ENABLED", "true")
    monkeypatch.setenv("QA_API_TOKEN", "s3cret-token")
    reload_config()
    return TestClient(create_app(runs_dir=tmp_path / "runs"))


def test_auth_disabled_by_default_allows_everything(tmp_path):
    client = TestClient(create_app(runs_dir=tmp_path / "runs"))
    assert client.get("/api/config/schema").status_code == 200
    assert client.get("/api/runs").status_code == 200


def test_enabled_rejects_missing_and_wrong_tokens(secured_client):
    assert secured_client.get("/api/config/schema").status_code == 401
    assert secured_client.get("/api/runs").status_code == 401
    assert secured_client.get("/api/monitor/kpis").status_code == 401
    wrong = {"Authorization": "Bearer wrong-token"}
    assert secured_client.get("/api/config/schema", headers=wrong).status_code == 401
    malformed = {"Authorization": "s3cret-token"}  # missing the Bearer scheme
    assert secured_client.get("/api/config/schema", headers=malformed).status_code == 401


def test_enabled_accepts_the_configured_token(secured_client):
    good = {"Authorization": "Bearer s3cret-token"}
    assert secured_client.get("/api/config/schema", headers=good).status_code == 200
    assert secured_client.get("/api/runs", headers=good).status_code == 200
    assert secured_client.get("/api/monitor/kpis", headers=good).status_code == 200


def test_health_probe_stays_open(secured_client):
    assert secured_client.get("/api/health").status_code == 200


def test_enabled_without_token_env_fails_closed(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_DASHBOARD__AUTH_ENABLED", "true")
    monkeypatch.delenv("QA_API_TOKEN", raising=False)
    reload_config()
    client = TestClient(create_app(runs_dir=tmp_path / "runs"))
    # No configured secret means nothing can authenticate — never silently open.
    assert client.get("/api/config/schema").status_code == 401
    empty = {"Authorization": "Bearer "}
    assert client.get("/api/config/schema", headers=empty).status_code == 401
