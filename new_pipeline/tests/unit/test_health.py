"""Real health probes: absent state is healthy, broken state degrades."""

from new_pipeline.config import reload_config
from new_pipeline.monitoring.health import HealthCheck


def _point_paths_at(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_DATA__RAW_VAULT_DIR", str(tmp_path / "raw"))
    monkeypatch.setenv("QA_DATA__PROCESSED_VAULT_DIR", str(tmp_path / "processed"))
    monkeypatch.setenv("QA_DASHBOARD__VETO_LEDGER_PATH", str(tmp_path / "veto.parquet"))
    monkeypatch.setenv("QA_DASHBOARD__TRADE_LOG_PATH", str(tmp_path / "trades.parquet"))
    monkeypatch.setenv("QA_EVALUATION__REGISTRY_PATH", str(tmp_path / "registry.json"))
    return reload_config()


def test_absent_state_is_healthy(tmp_path, monkeypatch):
    cfg = _point_paths_at(tmp_path, monkeypatch)
    report = HealthCheck().status(cfg)
    assert report["status"] == "healthy"
    assert report["checks"]["config"] == "ok"
    assert report["checks"]["veto_ledger"] == "absent"
    assert report["checks"]["promotion_registry"] == "absent"


def test_present_valid_state_is_ok(tmp_path, monkeypatch):
    cfg = _point_paths_at(tmp_path, monkeypatch)
    (tmp_path / "raw").mkdir()
    (tmp_path / "registry.json").write_text('{"promotions": [], "active_champions": {}}')
    from new_pipeline.execution.veto_ledger import VetoLedger, VetoRecord

    VetoLedger(tmp_path / "veto.parquet").append(
        VetoRecord("AAPL", "BUY", 100.0, "executed", "none", 0.9, 1, "x")
    )
    checks = HealthCheck().status(cfg)["checks"]
    assert checks["raw_vault_dir"] == "ok"
    assert checks["veto_ledger"] == "ok"
    assert checks["promotion_registry"] == "ok"


def test_corrupt_registry_degrades(tmp_path, monkeypatch):
    cfg = _point_paths_at(tmp_path, monkeypatch)
    (tmp_path / "registry.json").write_text("{not json")
    report = HealthCheck().status(cfg)
    assert report["status"] == "degraded"
    assert report["checks"]["promotion_registry"].startswith("error")


def test_registry_without_promotions_key_degrades(tmp_path, monkeypatch):
    cfg = _point_paths_at(tmp_path, monkeypatch)
    (tmp_path / "registry.json").write_text('{"wrong": true}')
    assert HealthCheck().status(cfg)["status"] == "degraded"


def test_corrupt_ledger_degrades(tmp_path, monkeypatch):
    cfg = _point_paths_at(tmp_path, monkeypatch)
    (tmp_path / "veto.parquet").write_text("this is not parquet")
    report = HealthCheck().status(cfg)
    assert report["status"] == "degraded"
    assert report["checks"]["veto_ledger"].startswith("error")


def test_default_config_path_loads():
    # No cfg argument: loads the real config singleton without raising.
    assert HealthCheck().status()["checks"]["config"] == "ok"
