"""Subprocess entrypoint for one backtest run: ``python -m new_pipeline.api.run_job <run_dir>``.

Reads ``<run_dir>/spec.json`` (params + config overrides), installs the overridden
config as this process's singleton, runs ``run_offline_pipeline`` into ``<run_dir>/output``,
and records progress in ``<run_dir>/status.json``. Running in its own process isolates a
crash/cancel from the API server and lets runs go in parallel.
"""

import json
import sys
import traceback
from datetime import UTC, date
from pathlib import Path


def _now() -> str:
    # Date.now()/new Date() are unavailable in some sandboxes; datetime.now is fine here.
    from datetime import datetime

    return datetime.now(UTC).isoformat()


def _write_status(run_dir: Path, **fields) -> None:
    path = run_dir / "status.json"
    current = json.loads(path.read_text()) if path.exists() else {}
    current.update(fields)
    path.write_text(json.dumps(current, indent=2))


def main(run_dir: str) -> None:
    run_dir = Path(run_dir)
    spec = json.loads((run_dir / "spec.json").read_text())
    _write_status(run_dir, status="running", started_at=_now())
    try:
        from new_pipeline.api.overrides import build_overridden_config, install_config
        from new_pipeline.core.seeding import seed_everything
        from new_pipeline.tournament.pipeline import run_offline_pipeline

        install_config(build_overridden_config(spec.get("overrides")))
        seed_everything(int(spec.get("seed", 0)))

        params = spec.get("params") or {}
        output = run_dir / "output"
        output.mkdir(exist_ok=True)
        print(f"[run] starting backtest into {output}", flush=True)
        summary = run_offline_pipeline(
            output,
            start=date.fromisoformat(params.get("start", "2021-01-01")),
            end=date.fromisoformat(params.get("end", "2022-12-31")),
            max_symbols=params.get("max_symbols"),
        )
        (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str))
        promotions = summary.get("promotions") or {}
        _write_status(
            run_dir, status="done", finished_at=_now(),
            n_sectors=len(summary.get("sectors") or []),
            n_promoted=sum(1 for v in promotions.values() if v),
        )
        print("[run] done", flush=True)
    except Exception as exc:  # surface a clean error to the API
        _write_status(
            run_dir, status="failed", finished_at=_now(),
            error=f"{type(exc).__name__}: {exc}", traceback=traceback.format_exc(),
        )
        print(f"[run] FAILED: {exc}", flush=True)
        raise


if __name__ == "__main__":
    main(sys.argv[1])
