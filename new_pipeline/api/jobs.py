"""Manage backtest runs as isolated subprocesses (one ``run_job`` process each).

Each run gets a directory under ``QA_API_RUNS_DIR`` (default ``./data/api_runs``)
holding ``spec.json`` (request), ``status.json`` (live state), ``run.log`` (stdout),
and an ``output/`` dir of artifacts. State lives on disk so it survives an API
restart; the in-memory handle map only tracks live processes for cancellation.
"""

import json
import os
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path

from new_pipeline.monitoring.metrics import get_metrics

DEFAULT_RUNS_DIR = Path(os.environ.get("QA_API_RUNS_DIR", "./data/api_runs"))


def _now() -> str:
    return datetime.now(UTC).isoformat()


class RunManager:
    def __init__(self, runs_dir: Path | str | None = None) -> None:
        self.runs_dir = Path(runs_dir) if runs_dir else DEFAULT_RUNS_DIR
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self._procs: dict[str, subprocess.Popen] = {}

    def run_dir(self, run_id: str) -> Path:
        return self.runs_dir / run_id

    def create(self, params: dict, overrides: dict | None, seed: int = 0) -> str:
        run_id = uuid.uuid4().hex[:12]
        run_dir = self.run_dir(run_id)
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / "spec.json").write_text(json.dumps(
            {"run_id": run_id, "params": params, "overrides": overrides or {},
             "seed": seed, "created_at": _now()}, indent=2))
        (run_dir / "status.json").write_text(json.dumps(
            {"run_id": run_id, "status": "queued"}, indent=2))
        log = open(run_dir / "run.log", "w")  # noqa: SIM115 - handed to the child
        try:
            self._procs[run_id] = subprocess.Popen(
                [sys.executable, "-m", "new_pipeline.api.run_job", str(run_dir)],
                stdout=log, stderr=subprocess.STDOUT,
            )
        finally:
            log.close()  # the child holds its own dup of the fd
        get_metrics().increment("api_runs_launched_total")
        return run_id

    def status(self, run_id: str) -> dict | None:
        path = self.run_dir(run_id) / "status.json"
        if not path.exists():
            return None
        state = json.loads(path.read_text())
        proc = self._procs.get(run_id)
        live = state.get("status") in ("queued", "running")
        if live and proc is not None and proc.poll() is not None:
            # the process exited without writing a terminal status -> it died.
            if proc.returncode not in (0, None):
                state["status"] = "failed"
                state.setdefault("error", f"process exited with code {proc.returncode}")
        return state

    def list_runs(self) -> list[dict]:
        runs = []
        for run_dir in self.runs_dir.iterdir():
            if not run_dir.is_dir():
                continue
            state = self.status(run_dir.name)
            if state is None:
                continue
            spec_path = run_dir / "spec.json"
            if spec_path.exists():
                spec = json.loads(spec_path.read_text())
                state["params"] = spec.get("params")
                state["created_at"] = spec.get("created_at")
            runs.append(state)
        runs.sort(key=lambda r: r.get("created_at") or "", reverse=True)
        return runs

    def cancel(self, run_id: str) -> bool:
        proc = self._procs.get(run_id)
        if proc is not None and proc.poll() is None:
            proc.terminate()
            path = self.run_dir(run_id) / "status.json"
            state = json.loads(path.read_text()) if path.exists() else {"run_id": run_id}
            state.update({"status": "cancelled", "finished_at": _now()})
            path.write_text(json.dumps(state, indent=2))
            return True
        return False
