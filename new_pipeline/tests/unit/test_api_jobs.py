"""RunManager subprocess bookkeeping (create / status / list / cancel) on disk.

The actual ``run_job`` subprocess is faked here so the manager's state machine is
tested fast and deterministically; the real spawn is covered by the integration test.
"""

import json
from pathlib import Path

from new_pipeline.api.jobs import RunManager


class _FakePopen:
    """Stand-in for the ``run_job`` child: writes a terminal status + a log line."""

    def __init__(self, args, stdout=None, stderr=None, status="done", poll_value=0, **kwargs):
        self._run_dir = Path(args[-1])
        self.returncode = poll_value
        self._poll_value = poll_value
        self.terminated = False
        if stdout is not None:
            stdout.write("[run] fake start\n[run] fake done\n")
            stdout.flush()
        if status is not None:
            path = self._run_dir / "status.json"
            state = json.loads(path.read_text()) if path.exists() else {}
            state.update({"status": status})
            path.write_text(json.dumps(state))

    def poll(self):
        return self._poll_value

    def wait(self, timeout=None):
        return self._poll_value

    def terminate(self):
        self.terminated = True


def _patch_popen(monkeypatch, **fake_kwargs):
    monkeypatch.setattr(
        "new_pipeline.api.jobs.subprocess.Popen",
        lambda *a, **k: _FakePopen(*a, **{**k, **fake_kwargs}),
    )


def test_create_writes_spec_and_status_and_spawns(tmp_path, monkeypatch):
    _patch_popen(monkeypatch)
    manager = RunManager(tmp_path)
    run_id = manager.create({"max_symbols": 2}, {"tournament": {"num_boost_round": 10}}, seed=7)

    spec = json.loads((manager.run_dir(run_id) / "spec.json").read_text())
    assert spec["params"]["max_symbols"] == 2
    assert spec["overrides"]["tournament"]["num_boost_round"] == 10
    assert spec["seed"] == 7
    assert manager.status(run_id)["status"] == "done"  # the fake wrote a terminal status
    assert (manager.run_dir(run_id) / "run.log").read_text().startswith("[run] fake start")


def test_status_of_unknown_run_is_none(tmp_path):
    assert RunManager(tmp_path).status("does-not-exist") is None


def test_list_runs_sorted_newest_first(tmp_path, monkeypatch):
    _patch_popen(monkeypatch)
    manager = RunManager(tmp_path)
    first = manager.create({"max_symbols": 1}, {}, 0)
    second = manager.create({"max_symbols": 2}, {}, 0)
    # Force a deterministic created_at ordering (same-second spawns otherwise tie).
    for run_id, stamp in ((first, "2021-01-01T00:00:00"), (second, "2021-06-01T00:00:00")):
        spec_path = manager.run_dir(run_id) / "spec.json"
        spec = json.loads(spec_path.read_text())
        spec["created_at"] = stamp
        spec_path.write_text(json.dumps(spec))

    listed = manager.list_runs()
    assert [r["run_id"] for r in listed] == [second, first]
    assert listed[0]["params"]["max_symbols"] == 2


def test_status_reconciles_a_dead_process(tmp_path, monkeypatch):
    # Child exits non-zero without writing a terminal status -> reconcile to failed.
    _patch_popen(monkeypatch, status=None, poll_value=1)
    manager = RunManager(tmp_path)
    run_id = manager.create({}, {}, 0)
    (manager.run_dir(run_id) / "status.json").write_text(
        json.dumps({"run_id": run_id, "status": "running"})
    )
    state = manager.status(run_id)
    assert state["status"] == "failed"
    assert "exited with code 1" in state["error"]


def test_cancel_terminates_a_live_run(tmp_path, monkeypatch):
    _patch_popen(monkeypatch, status="running", poll_value=None)
    manager = RunManager(tmp_path)
    run_id = manager.create({}, {}, 0)
    assert manager.cancel(run_id) is True
    assert manager.status(run_id)["status"] == "cancelled"
    assert manager._procs[run_id].terminated is True


def test_cancel_of_finished_run_is_noop(tmp_path, monkeypatch):
    _patch_popen(monkeypatch)  # poll_value=0 -> already finished
    manager = RunManager(tmp_path)
    run_id = manager.create({}, {}, 0)
    assert manager.cancel(run_id) is False


def test_runs_dir_defaults_to_module_constant(tmp_path, monkeypatch):
    monkeypatch.setattr("new_pipeline.api.jobs.DEFAULT_RUNS_DIR", tmp_path / "default")
    manager = RunManager()  # no explicit dir -> falls back to the module default
    assert manager.runs_dir == tmp_path / "default"
    assert manager.runs_dir.exists()
