# Quantum Avenger — Production Hardening (Phase 7)

Operational artifacts for building, shipping, observing, and recovering the system.

## Layout
- `docker/` — `Dockerfile.{api,app,mcp}` + `docker-compose.yml` (api + app +
  mcp + Prometheus). `Dockerfile.api` is the dashboard: a Node stage builds the
  React SPA, then uvicorn serves `/api` + the SPA on one origin (non-root,
  healthchecked, `QA_API_HOST=0.0.0.0`). `Dockerfile.gpu` is a CUDA trainer
  template (needs a GPU host).
- `k8s/` — `api.yaml` (dashboard Deployment + ClusterIP Service, auth forced
  on, probes on `/api/health`), `deployment.yaml` (app / mcp),
  `configmap.yaml`, `secrets.yaml` (placeholder template incl. `QA_API_TOKEN`),
  `hpa.yaml`, `networkpolicy.yaml`.
- `observability/` — `prometheus.yml` (scrapes `api:8000/metrics`) +
  `alert_rules.yml` + `grafana_dashboard.json`, all referencing metrics the
  code actually emits.
- `terraform/` — an explicit provider-agnostic skeleton (no cloud resources).
- `docs/` — deployment, recovery, and security guides.
- `chaos/` — `load_test.py` perf smoke (Shield + t+1 simulator throughput).

CI lives at `.github/workflows/ci.yml`: ruff + the offline test suite with a **≥85% coverage gate** (`NUMBA_DISABLE_JIT=1` so the `@njit` kernels are traced).

## Quickstart (from the repo root)
```
make install      # runtime + dev deps
make lint test    # ruff + tests
make coverage     # tests + the >=85% gate
make docker       # build all three images
make compose-up   # run the stack locally
```

## Metrics
The api serves `/metrics` (Prometheus text exposition): process counters
incremented by the orchestrator / runner / API plus KPI gauges computed from
the ledgers at scrape time and the weakest champion's `dsr_value`. When API
auth is enabled, give the scraper the bearer token (`authorization` block in
`prometheus.yml`).

## Scope notes
CI builds all three CPU images on every PR and smoke-tests the api container
(health + SPA). The api image's runtime layout, entrypoint, healthcheck
command, 0.0.0.0 binding, and run-subprocess spawn path are validated by a
staged-layout simulation; the app container still defaults to the `health`
command (point it at `pipeline`/`trade` per deployment), Terraform remains a
skeleton, and the MCP image runs the offline tool-inventory entrypoint until
the live FastMCP cutover. GPU: `Dockerfile.gpu` + the manual
`nightly-gpu.yml` parity workflow need a self-hosted CUDA runner.
