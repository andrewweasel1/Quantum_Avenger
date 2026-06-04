# Security Guide

## Secrets
- Alpaca / Ollama credentials are injected only as `QA_`-prefixed env vars
  (`config/production.py`), sourced from a Kubernetes `Secret` / secrets manager.
- Never committed: no keys in the repo, configmaps, or images. Dev/test use the
  deterministic fakes, so no real credentials are needed offline.

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
