"""Run endpoints: launch a backtest as an isolated subprocess, poll it, read results.

A ``POST /api/runs`` validates the config overrides (fail-fast 422 on a bad knob),
then spawns one ``run_job`` subprocess via the shared ``RunManager``. Progress is
polled with ``GET /api/runs/{id}`` or streamed line-by-line over SSE; parsed artifacts
come from ``GET /api/runs/{id}/results`` once the run is ``done``.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, ValidationError
from starlette.responses import StreamingResponse

from new_pipeline.api.jobs import RunManager
from new_pipeline.api.overrides import build_overridden_config
from new_pipeline.api.results import parse_results

router = APIRouter(prefix="/api/runs", tags=["runs"])

_TERMINAL = {"done", "failed", "cancelled"}


def get_run_manager(request: Request) -> RunManager:
    """The per-app ``RunManager`` (holds live process handles for cancellation)."""
    return request.app.state.run_manager


class RunParams(BaseModel):
    start: str = "2021-01-01"
    end: str = "2022-12-31"
    max_symbols: int | None = None


class RunRequest(BaseModel):
    params: RunParams = RunParams()
    overrides: dict = {}
    seed: int = 0


@router.post("")
def create_run(req: RunRequest, manager: RunManager = Depends(get_run_manager)) -> dict:
    """Validate the overrides, then launch one isolated backtest subprocess."""
    try:
        build_overridden_config(req.overrides)  # fail fast on a bad knob value/type
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc
    run_id = manager.create(req.params.model_dump(), req.overrides, req.seed)
    return manager.status(run_id) or {"run_id": run_id, "status": "queued"}


class PromoteRequest(BaseModel):
    keys: list[str] | None = None
    all_sectors: bool = False
    registry: str = "./models/prod/promotion_registry.json"


@router.post("/{run_id}/promote")
def promote_run_candidates(
    run_id: str, req: PromoteRequest, manager: RunManager = Depends(get_run_manager)
) -> dict:
    """MANUAL promotion of a run's candidates into the paper-trading registry.

    The run's own registry (the honest gate record) is never modified; entries
    land in the target registry with an explicit MANUAL OVERRIDE reason. Pass
    keys=["Universe Long Short"] for the book, all_sectors=true for the 13
    sector champions."""
    from new_pipeline.scripts.promote_candidates import manual_promote

    output = manager.run_dir(run_id) / "output"
    if not (output / "promotion_registry.json").exists():
        raise HTTPException(status_code=404, detail=f"no completed run registry for {run_id}")
    try:
        entries = manual_promote(output, keys=req.keys, all_sectors=req.all_sectors,
                                 registry_path=req.registry)
    except (KeyError, ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"promoted": [e["sector"] for e in entries], "registry": req.registry}


@router.get("")
def list_runs(manager: RunManager = Depends(get_run_manager)) -> list[dict]:
    """All runs (newest first), each with its live status + request params."""
    return manager.list_runs()


@router.get("/{run_id}")
def get_run(run_id: str, manager: RunManager = Depends(get_run_manager)) -> dict:
    state = manager.status(run_id)
    if state is None:
        raise HTTPException(status_code=404, detail="run not found")
    return state


@router.get("/{run_id}/results")
def get_results(run_id: str, manager: RunManager = Depends(get_run_manager)) -> dict:
    """Parsed artifacts (per-sector equity/metrics/CPCV paths, promotions, portfolio).

    Returns whatever exists on disk — fields are empty until the run is ``done``.
    """
    if manager.status(run_id) is None:
        raise HTTPException(status_code=404, detail="run not found")
    return parse_results(manager.run_dir(run_id))


@router.get("/{run_id}/logs")
def get_logs(run_id: str, manager: RunManager = Depends(get_run_manager)) -> dict:
    """The full captured stdout/stderr of the run (one-shot, non-streaming)."""
    if manager.status(run_id) is None:
        raise HTTPException(status_code=404, detail="run not found")
    log_path = manager.run_dir(run_id) / "run.log"
    return {"run_id": run_id, "log": log_path.read_text() if log_path.exists() else ""}


@router.get("/{run_id}/logs/stream")
def stream_logs(run_id: str, manager: RunManager = Depends(get_run_manager)) -> StreamingResponse:
    """Live SSE tail of the run log; closes when the run reaches a terminal status."""
    if manager.status(run_id) is None:
        raise HTTPException(status_code=404, detail="run not found")
    log_path = manager.run_dir(run_id) / "run.log"

    async def event_stream():
        position = 0
        while True:
            if log_path.exists():
                text = log_path.read_text()
                if len(text) > position:
                    for line in text[position:].splitlines():
                        yield f"data: {line}\n\n"
                    position = len(text)
            state = manager.status(run_id) or {}
            if state.get("status") in _TERMINAL:
                yield f"event: status\ndata: {state.get('status')}\n\n"
                return
            await asyncio.sleep(0.5)  # pragma: no cover - only hit while a run is live

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.delete("/{run_id}")
def cancel_run(run_id: str, manager: RunManager = Depends(get_run_manager)) -> dict:
    """Terminate a running backtest; no-op if it already finished."""
    if manager.status(run_id) is None:
        raise HTTPException(status_code=404, detail="run not found")
    return {"run_id": run_id, "cancelled": manager.cancel(run_id)}
