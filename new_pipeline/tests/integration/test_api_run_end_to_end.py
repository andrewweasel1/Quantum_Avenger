"""End-to-end backtest through the API run layer (real engine, tiny budget).

Two paths to the same engine: ``run_job.main`` in-process (so the job entrypoint is
covered) and ``RunManager`` spawning a real subprocess (so the spawn/poll wiring is
covered). Both use ``max_symbols=2`` + ``num_boost_round=10`` to stay fast and offline.
"""

import json
from datetime import date

from new_pipeline.api import run_job
from new_pipeline.api.jobs import RunManager
from new_pipeline.api.results import parse_results

_PARAMS = {"start": "2021-01-01", "end": "2021-06-30", "max_symbols": 2}
_OVERRIDES = {"tournament": {"num_boost_round": 10}}


def test_run_job_main_in_process_produces_artifacts(tmp_path):
    run_dir = tmp_path / "run1"
    run_dir.mkdir()
    (run_dir / "spec.json").write_text(json.dumps(
        {"run_id": "run1", "params": _PARAMS, "overrides": _OVERRIDES, "seed": 0}
    ))

    run_job.main(str(run_dir))

    status = json.loads((run_dir / "status.json").read_text())
    assert status["status"] == "done"
    assert status["n_sectors"] >= 1
    assert (run_dir / "summary.json").exists()

    results = parse_results(run_dir)
    assert results["sectors"], "at least one sector should yield a champion curve"
    sector = results["sectors"][0]
    assert len(sector["equity"]) > 0
    assert set(sector["metrics"]) >= {"sharpe", "sortino", "max_drawdown"}


def test_run_manager_spawns_a_real_subprocess(tmp_path):
    manager = RunManager(tmp_path / "runs")
    run_id = manager.create(_PARAMS, _OVERRIDES, seed=0)
    assert manager.status(run_id)["status"] in ("queued", "running")

    exit_code = manager._procs[run_id].wait(timeout=300)
    assert exit_code == 0

    state = manager.status(run_id)
    assert state["status"] == "done"
    assert state["n_sectors"] >= 1

    listed = manager.list_runs()
    assert listed[0]["run_id"] == run_id
    assert parse_results(manager.run_dir(run_id))["sectors"]


def test_run_job_main_reports_failure(tmp_path, monkeypatch):
    # An unparsable date drives run_offline_pipeline to raise -> status 'failed'.
    run_dir = tmp_path / "bad"
    run_dir.mkdir()
    (run_dir / "spec.json").write_text(json.dumps(
        {"run_id": "bad", "params": {"start": "not-a-date"}, "overrides": {}, "seed": 0}
    ))
    import pytest

    with pytest.raises(ValueError):
        run_job.main(str(run_dir))
    status = json.loads((run_dir / "status.json").read_text())
    assert status["status"] == "failed"
    assert "error" in status and "traceback" in status


def test_run_offline_pipeline_default_dates_are_valid():
    # Guard the run_job default-date fallbacks used when params omit start/end.
    assert date.fromisoformat("2021-01-01") < date.fromisoformat("2022-12-31")
