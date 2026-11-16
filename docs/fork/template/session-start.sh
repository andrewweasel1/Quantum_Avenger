#!/bin/bash
set -euo pipefail

# Quantum Intraday — SessionStart hook for Claude Code on the web.
# Installs the Python dependencies so `pytest` and the linters work as soon as
# a session opens. Synchronous by design: the session waits, so nothing runs
# before the environment is ready.

# Only run in the remote (web) environment; no-op for local sessions.
if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

PROJECT_DIR="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
cd "$PROJECT_DIR"

python3 -m pip install -r new_pipeline/requirements.txt
python3 -m pip install -r new_pipeline/requirements-dev.txt
# This base image can ship a system Pillow built for a different Python, and
# pip treats it as satisfying matplotlib's requirement. Importing matplotlib
# then dies on PIL._imaging — and pytest 9 FAILS rather than skips an
# importorskip on that kind of ImportError (seen 2026-11-16). Install a real
# wheel ahead of the system package.
python3 -m pip install --ignore-installed pillow
# The Alpaca SDK is a core dependency of this project (market data and paper
# trading), not the optional live extra it was in the parent repository. It is
# installed here AND in CI so the two environments cannot drift apart: a suite
# that passes only because this container happens to have a package is the
# failure this guards against.
python3 -m pip install "alpaca-py>=0.33"

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  # Make the repo root importable so `import new_pipeline...` resolves the
  # same way `python -m pytest new_pipeline/tests` expects, regardless of cwd.
  echo "export PYTHONPATH=\"$PROJECT_DIR\"" >> "$CLAUDE_ENV_FILE"
  # CPU-only sandbox: disable Numba JIT so the @njit paths run in pure Python.
  # Deterministic, and it lets coverage trace those bodies.
  echo "export NUMBA_DISABLE_JIT=\"1\"" >> "$CLAUDE_ENV_FILE"
  # The intraday stack reads its symbol base from the Liquid fixture. The
  # framework default is a packaged 41-name fixture with none of the
  # extended-cap segments, so without this every run resolves zero symbols
  # (intraday.universe.assert_symbols refuses and names this variable).
  echo "export QA_DATA__UNIVERSE_PATH=\"new_pipeline/data/universe/liquid1500_pit.csv\"" >> "$CLAUDE_ENV_FILE"
fi
