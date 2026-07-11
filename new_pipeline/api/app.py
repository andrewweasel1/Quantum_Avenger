"""FastAPI application for the decoupled React dashboard.

``create_app()`` wires the config / runs / monitor routers, enables CORS for the Vite
dev server, holds one shared ``RunManager`` on ``app.state`` (so live process handles
survive across requests), and — when a built front-end exists at ``frontend/dist`` —
serves it as a single-page app. The Python ML engine is never imported here; runs go
out to isolated ``run_job`` subprocesses.

Dev:  ``uvicorn new_pipeline.api.app:app --reload``  (React dev server proxies to it)
Prod: ``python -m new_pipeline.api.app``             (serves the built SPA + API)
"""

import os
from pathlib import Path

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from new_pipeline.api.auth import require_auth
from new_pipeline.api.jobs import RunManager
from new_pipeline.api.json_response import SafeJSONResponse
from new_pipeline.api.routers import config, monitor, runs

_DEFAULT_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
_STATIC_DIR = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def _cors_origins() -> list[str]:
    raw = os.environ.get("QA_API_CORS_ORIGINS")
    return [o.strip() for o in raw.split(",") if o.strip()] if raw else _DEFAULT_ORIGINS


def create_app(runs_dir: str | Path | None = None) -> FastAPI:
    app = FastAPI(
        title="Quantum Avenger API",
        version="0.1.0",
        default_response_class=SafeJSONResponse,  # coerce inf/NaN floats -> null
    )
    app.state.run_manager = RunManager(runs_dir)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=_cors_origins(),
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Data/control routers sit behind the (config-gated) bearer-token check; the
    # health probe and the SPA's static assets stay open for load balancers/browsers.
    protected = [Depends(require_auth)]
    app.include_router(config.router, dependencies=protected)
    app.include_router(runs.router, dependencies=protected)
    app.include_router(monitor.router, dependencies=protected)

    @app.get("/api/health", tags=["health"])
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/metrics", tags=["health"], dependencies=protected)
    def metrics():
        # Prometheus text exposition: process counters + ledger KPI gauges.
        # When auth is enabled, configure the scraper with the bearer token.
        from starlette.responses import PlainTextResponse

        from new_pipeline.monitoring.telemetry import TelemetryExporter, runtime_metrics

        body = TelemetryExporter().export(runtime_metrics())
        return PlainTextResponse(body, media_type="text/plain; version=0.0.4")

    if _STATIC_DIR.exists():  # pragma: no cover - only when the React app is built
        from fastapi.staticfiles import StaticFiles

        app.mount("/", StaticFiles(directory=str(_STATIC_DIR), html=True), name="spa")

    return app


app = create_app()


def main() -> None:  # pragma: no cover - server entrypoint
    import uvicorn

    uvicorn.run(
        app,
        host=os.environ.get("QA_API_HOST", "127.0.0.1"),
        port=int(os.environ.get("QA_API_PORT", "8000")),
    )


if __name__ == "__main__":  # pragma: no cover
    main()
