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

# Make the repo root importable so `import new_pipeline...` resolves the same
# way `python -m pytest new_pipeline/tests` expects, regardless of cwd.
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo "export PYTHONPATH=\"$PROJECT_DIR\"" >> "$CLAUDE_ENV_FILE"
fi
