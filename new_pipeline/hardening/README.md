# Quantum Avenger — Production Hardening (Phase 7)

Operational artifacts for building, shipping, observing, and recovering the system.

## Layout
- `docker/` — `Dockerfile.{app,dashboard,mcp}` + `docker-compose.yml` (local prod-like stack).
- `k8s/` — `deployment.yaml` (app / dashboard / mcp), `service.yaml`, `configmap.yaml`.
- `observability/` — `prometheus.yml` scrape config + `alert_rules.yml`.
- `docs/` — deployment, recovery, and security guides.

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
`new_pipeline.monitoring.telemetry.render_prometheus` emits Prometheus text
exposition (gauges prefixed `quantum_avenger_`). Prometheus scrapes it and
`alert_rules.yml` fires on veto-rate, drawdown, DSR, and latency breaches.

## Scope notes
Dockerfiles, K8s manifests, and the Prometheus/alert configs are
deployment-ready templates; cloud-specific IaC (Terraform), ingress/HPA, and a
full chaos-test suite are the natural follow-ons (see `docs/DEPLOYMENT.md`).
The MCP image runs the offline tool-inventory entrypoint; the live FastMCP
stdio server is wired at the live cutover.
