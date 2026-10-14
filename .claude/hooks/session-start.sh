#!/bin/bash
set -euo pipefail

# Quantum Avenger — SessionStart hook for Claude Code on the web.
# Installs the new_pipeline Python dependencies so `pytest` (and future
# linters) work out of the box in remote sessions. Synchronous by design:
# the session waits until dependencies are installed, avoiding races where
# tests are run before the environment is ready.

# Only run in the remote (web) environment; no-op for local sessions.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# Resolve the repo root: CLAUDE_PROJECT_DIR is set in web sessions; fall back
# to the script's location (.claude/hooks/ -> repo root) for manual runs.
PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$PROJECT_DIR"

# Install pipeline dependencies. Idempotent and cache-friendly: the container
# state is snapshotted after this hook, and pip reuses its wheel cache on reruns.
python3 -m pip install -r new_pipeline/requirements.txt

# Development tooling (ruff and friends) so linters work in the session.
if [ -f new_pipeline/requirements-dev.txt ]; then
  python3 -m pip install -r new_pipeline/requirements-dev.txt
fi

# Dashboard API layer (fastapi/uvicorn): the test suite imports fastapi
# directly (new_pipeline/tests/unit/test_api_*.py), so sessions need it for
# `pytest` to even collect.
if [ -f new_pipeline/requirements-api.txt ]; then
  python3 -m pip install -r new_pipeline/requirements-api.txt
fi

# React dashboard dependencies so `npm run build` (tsc + vite) works out of
# the box. npm reuses node_modules/ + its cache on container-snapshot reruns.
if [ -f frontend/package.json ] && command -v npm >/dev/null 2>&1; then
  (cd frontend && npm install --no-audit --no-fund)
fi

# Session environment.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  # Make the repo root importable so `import new_pipeline...` resolves the same
  # way `python -m pytest new_pipeline/tests` expects, regardless of cwd.
  echo "export PYTHONPATH=\"$PROJECT_DIR\"" >> "$CLAUDE_ENV_FILE"
  # CPU-only sandbox: disable Numba JIT so the @njit / @cuda.jit paths execute
  # in pure Python. Faster, deterministic, and it lets coverage trace those
  # bodies — the >=85% gate depends on it. Override per-command with
  # NUMBA_DISABLE_JIT=0 to exercise real JIT/CUDA compilation.
  echo "export NUMBA_DISABLE_JIT=\"1\"" >> "$CLAUDE_ENV_FILE"
fi
