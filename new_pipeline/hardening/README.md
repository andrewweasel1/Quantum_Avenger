# Quantum Avenger — Production Hardening (Phase 7)

Operational artifacts for building, shipping, observing, and recovering the system.

## Layout
- `docker/` — `Dockerfile.{app,mcp}` + `docker-compose.yml` (local prod-like stack).
  The web dashboard (React SPA + FastAPI, `/frontend` + `new_pipeline/api/`) is
  **not containerized yet** — its image, service, and ingress land with the
  deployment phase.
- `k8s/` — `deployment.yaml` (app / mcp), `configmap.yaml`, `secrets.yaml`
  (placeholder template), `hpa.yaml`, `networkpolicy.yaml`.
- `observability/` — `prometheus.yml` scrape config + `alert_rules.yml` +
  `grafana_dashboard.json`. NOTE: the referenced `quantum_avenger_*` metrics are
  not emitted yet — wiring `MetricsCollector` into the runner/API and exposing
  `/metrics` is the observability phase.
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
`new_pipeline.monitoring.telemetry.render_prometheus` renders Prometheus text
exposition (gauges prefixed `quantum_avenger_`), but **nothing populates or
serves it yet** — no production code increments `MetricsCollector` and no
process runs `metrics_endpoint.serve_metrics`. `alert_rules.yml` /
`grafana_dashboard.json` name the intended metrics; they go live when the
observability phase wires collection into the runner/orchestrator/API.

## Scope notes
Dockerfiles and K8s manifests are templates, not a validated deployment: the
app container runs the `health` stub (not a trading loop), Terraform is a
skeleton, and the dashboard (React + FastAPI) has no image yet. The MCP image
runs the offline tool-inventory entrypoint; the live FastMCP stdio server is
wired at the live cutover. See `docs/DEPLOYMENT.md` for the current manual
steps.
