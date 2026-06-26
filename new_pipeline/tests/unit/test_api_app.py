"""HTTP surface of the dashboard API via TestClient (no real pipeline subprocess)."""

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from new_pipeline.api.app import create_app
from new_pipeline.config import reload_config
from new_pipeline.execution.trade_log import TradeLog, TradeRecord
from new_pipeline.execution.veto_ledger import VetoLedger, VetoRecord


class _FakePopen:
    """Fake ``run_job`` child: writes a couple of log lines + a terminal status."""

    def __init__(self, args, stdout=None, stderr=None, **kwargs):
        run_dir = Path(args[-1])
        if stdout is not None:
            stdout.write("[run] line one\n[run] line two\n")
            stdout.flush()
        path = run_dir / "status.json"
        state = json.loads(path.read_text()) if path.exists() else {}
        state.update({"status": "done", "n_sectors": 0})
        path.write_text(json.dumps(state))
        self.returncode = 0

    def poll(self):
        return 0

    def wait(self, timeout=None):
        return 0

    def terminate(self):  # pragma: no cover - finished fake is never terminated
        pass


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "new_pipeline.api.jobs.subprocess.Popen", lambda *a, **k: _FakePopen(*a, **k)
    )
    return TestClient(create_app(runs_dir=tmp_path / "runs"))


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_config_schema_and_current(client):
    schema = client.get("/api/config/schema")
    assert schema.status_code == 200
    assert schema.json()["groups"]

    current = client.get("/api/config")
    assert current.status_code == 200
    assert "tournament" in current.json()


def test_run_lifecycle_create_poll_results_logs_cancel(client):
    created = client.post("/api/runs", json={
        "params": {"start": "2021-01-01", "end": "2021-06-30", "max_symbols": 2},
        "overrides": {"tournament": {"num_boost_round": 10}},
    })
    assert created.status_code == 200
    run_id = created.json()["run_id"]

    assert client.get(f"/api/runs/{run_id}").json()["status"] == "done"
    assert any(r["run_id"] == run_id for r in client.get("/api/runs").json())

    results = client.get(f"/api/runs/{run_id}/results")
    assert results.status_code == 200
    assert results.json()["run_id"] == run_id  # parsed (empty) artifacts

    logs = client.get(f"/api/runs/{run_id}/logs").json()
    assert "line one" in logs["log"]

    cancelled = client.delete(f"/api/runs/{run_id}")
    assert cancelled.json() == {"run_id": run_id, "cancelled": False}  # already finished


def test_log_stream_emits_lines_then_terminal_status(client):
    run_id = client.post("/api/runs", json={"params": {"max_symbols": 1}}).json()["run_id"]
    with client.stream("GET", f"/api/runs/{run_id}/logs/stream") as response:
        assert response.status_code == 200
        body = "".join(response.iter_text())
    assert "data: [run] line one" in body
    assert "event: status" in body
    assert "data: done" in body


def test_unknown_run_endpoints_404(client):
    assert client.get("/api/runs/nope").status_code == 404
    assert client.get("/api/runs/nope/results").status_code == 404
    assert client.get("/api/runs/nope/logs").status_code == 404
    assert client.get("/api/runs/nope/logs/stream").status_code == 404
    assert client.delete("/api/runs/nope").status_code == 404


def test_bad_override_returns_422(client):
    response = client.post("/api/runs", json={
        "overrides": {"tournament": {"num_boost_round": "not-an-int"}},
    })
    assert response.status_code == 422


def test_monitor_endpoints_empty_are_graceful(client):
    assert client.get("/api/monitor/kpis").json()["total_decisions"] == 0
    assert client.get("/api/monitor/vetoes").json()["total"] == 0
    assert client.get("/api/monitor/performance").json()["equity_curve"] == []
    assert client.get("/api/monitor/risk").json()["gross_exposure"] == 0.0
    assert client.get("/api/monitor/registry").json() == {
        "active_champions": {}, "promotions": []
    }
    assert client.get("/api/monitor/alerts").json() == []
    assert client.get("/api/monitor/trades").json() == []


def test_monitor_endpoints_with_seeded_ledgers(tmp_path, monkeypatch):
    veto_path = tmp_path / "veto.parquet"
    trade_path = tmp_path / "trades.parquet"
    veto = VetoLedger(veto_path)
    veto.append(VetoRecord("AAPL", "BUY", 100.0, "executed", "none", 0.96, 10, "o1"))
    veto.append(VetoRecord("MSFT", "BUY", 100.0, "risk veto", "shield", 0.96, 0, ""))
    veto.append(VetoRecord("NVDA", "BUY", 100.0, "grader", "grader", 0.96, 0, ""))
    trades = TradeLog(trade_path)
    for pnl, oid in [(0.10, "a"), (-0.30, "b"), (0.08, "c")]:  # -30% drawdown -> alert
        trades.append(TradeRecord("AAPL", "buy", 10, 100.0, "filled", oid, pnl=pnl))

    monkeypatch.setenv("QA_DASHBOARD__VETO_LEDGER_PATH", str(veto_path))
    monkeypatch.setenv("QA_DASHBOARD__TRADE_LOG_PATH", str(trade_path))
    reload_config()
    client = TestClient(create_app(runs_dir=tmp_path / "runs"))

    kpis = client.get("/api/monitor/kpis").json()
    assert kpis["total_decisions"] == 3
    assert kpis["vetoed"] == 2

    assert len(client.get("/api/monitor/trades").json()) == 3
    assert client.get("/api/monitor/performance").json()["total_pnl"] == pytest.approx(-0.12)
    assert client.get("/api/monitor/vetoes").json()["by_gate"] == {"shield": 1, "grader": 1}

    alerts = client.get("/api/monitor/alerts").json()
    assert any(a["severity"] == "critical" for a in alerts)  # drawdown breach fired


def test_json_safe_coerces_non_finite_floats():
    from new_pipeline.api.json_response import json_safe

    cleaned = json_safe(
        {"a": float("inf"), "b": float("-inf"), "c": float("nan"), "d": 1.5,
         "nested": [float("inf"), {"e": float("nan")}], "s": "ok", "i": 3}
    )
    assert cleaned == {"a": None, "b": None, "c": None, "d": 1.5,
                       "nested": [None, {"e": None}], "s": "ok", "i": 3}


def test_results_with_infinite_metric_serialises_to_null(client, tmp_path):
    # A real run can record haircut_sharpe == inf; Starlette's default JSONResponse
    # would 500 on that. SafeJSONResponse must turn it into null and return 200.
    run_dir = tmp_path / "runs" / "infrun"
    (run_dir / "output").mkdir(parents=True)
    (run_dir / "status.json").write_text(json.dumps({"run_id": "infrun", "status": "done"}))
    (run_dir / "spec.json").write_text(json.dumps({"run_id": "infrun", "params": {}}))
    (run_dir / "output" / "promotion_registry.json").write_text(
        json.dumps({"promotions": [{"sector": "Tech", "haircut_sharpe": float("inf"),
                                    "dsr": float("nan"), "pbo": 0.0}],
                    "active_champions": {}})
    )
    response = client.get("/api/runs/infrun/results")
    assert response.status_code == 200
    promo = response.json()["promotions"][0]
    assert promo["haircut_sharpe"] is None
    assert promo["dsr"] is None
    assert promo["pbo"] == 0.0
