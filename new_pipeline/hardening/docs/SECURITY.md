# Security Guide

## Secrets
- Alpaca / Ollama credentials are injected only as `QA_`-prefixed env vars
  (`config/production.py`), sourced from a Kubernetes `Secret` / secrets manager.
- Never committed: no keys in the repo, configmaps, or images. Dev/test use the
  deterministic fakes, so no real credentials are needed offline.

## Dashboard API auth
- The FastAPI control plane (launch/cancel backtests, read config, monitor
  ledgers) ships with config-gated bearer-token auth: set
  `dashboard.auth_enabled: true` (or `QA_DASHBOARD__AUTH_ENABLED=true`) and
  provide `QA_API_TOKEN` in the environment. Comparison is constant-time and
  the gate **fails closed** — enabled with no token configured rejects all
  requests. `/api/health` and static assets stay open for probes/browsers.
- The server binds `127.0.0.1` by default (`QA_API_HOST`); never expose it
  beyond localhost without enabling auth.

## Containers
- All images run as a non-root user (uid 10001).
- Minimal `python:3.11-slim` base; `.dockerignore` excludes tests, docs, and
  caches from the build context.

## Determinism & isolation
- The LLM performs **no math** — every quantity flows through the deterministic
  MCP tools / Shield Agent (G1), bounding the blast radius of model misbehavior.
- `reference_code/` is read-only (enforced by a project `Edit`/`Write` deny rule).

## Supply chain
- Pin and scan dependencies (Dependabot / `pip-audit`) in CI.
- Coverage + lint gates block merges; the offline test suite needs no network.

## Audit
- The append-only veto ledger and trade log are the immutable record of every
  decision (executed or vetoed) with its gate and reason.
