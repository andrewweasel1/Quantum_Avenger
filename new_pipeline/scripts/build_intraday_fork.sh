#!/usr/bin/env bash
# Produce the stripped source tree for the intraday fork.
#
# Reads ONLY from git (tracked files at HEAD) and writes ONLY into <dest>.
# It never modifies this repository, so it is safe to re-run.
#
# What it does, in order:
#   1. exports the tracked tree at HEAD into <dest>
#   2. lifts the intraday evidence out of models/prod/evidence -> <dest>/evidence
#   3. deletes the daily-book code, fixtures and artifacts (see EXCLUDE below)
#   4. keeps tournament/{simulator,regime_state}.py — the gauntlet imports
#      sharpe_ratio from them, and the gauntlet must not be edited
#   5. prunes tests that import now-absent modules
#   6. reports any remaining dangling new_pipeline imports
#
# Step 6 is a REPORT, not a guarantee: resolving the residue is the fork's
# first task. Nothing here is hidden behind a passing exit code.
#
# Usage: bash new_pipeline/scripts/build_intraday_fork.sh /path/to/fork
set -euo pipefail

DEST="${1:?usage: build_intraday_fork.sh <dest-dir>}"
SRC="$(git rev-parse --show-toplevel)"
cd "$SRC"

if [ -e "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null)" ]; then
  echo "refusing to write into a non-empty directory: $DEST" >&2
  exit 1
fi
mkdir -p "$DEST"

echo "==> exporting tracked tree at $(git rev-parse --short HEAD) -> $DEST"
if [ "${SKIP_DATA:-0}" = "1" ]; then
  # Structural dry run: everything but the 4.2GB vault archives, so the
  # import/prune checks below can be iterated in seconds. The real fork
  # export must run WITHOUT this.
  echo "    SKIP_DATA=1 — omitting data/minute_archives (structural check only)"
  git archive HEAD | tar -x -C "$DEST" --exclude='data/minute_archives/*'
else
  git archive HEAD | tar -x -C "$DEST"
fi

echo "==> lifting intraday evidence to evidence/"
mkdir -p "$DEST/evidence"
for run in orb_v1 orb_v2 meanrev_v1 meanrev_v2 meanrev_v3 meanrev_v4 \
           meanrev_v5 meanrev_v6 meanrev_v7; do
  if [ -d "$DEST/models/prod/evidence/$run" ]; then
    mv "$DEST/models/prod/evidence/$run" "$DEST/evidence/$run"
  fi
done
cp "$DEST/docs/fork/INTRADAY_HANDOVER.md" "$DEST/evidence/README.md" 2>/dev/null || true

# The daily long/short book: its live ledger, its champions, its construction
# code, its dashboard, and the PIT fixture whose monthly end-exclusive
# intervals exist only to serve daily rebalancing.
EXCLUDE=(
  models                                       # ledger, registry, boosters, daily evidence
  frontend                                     # 151MB daily-book dashboard
  reference_code                               # legacy pre-migration source
  new_pipeline/portfolio
  new_pipeline/api
  new_pipeline/hardening
  new_pipeline/analysis
  new_pipeline/scripts/paper_trade_book.py     # the live daily executor
  new_pipeline/main.py                         # daily entrypoint
  new_pipeline/execution/runner.py             # daily live orchestration
  new_pipeline/execution/orchestrator.py
  new_pipeline/data/training_db.py
  new_pipeline/scripts/check_health.py
  new_pipeline/scripts/ingest_training_data.py
  new_pipeline/scripts/promote_candidates.py
  new_pipeline/scripts/extend_liquid_universe.py
  new_pipeline/data/universe/liquid1500_pit.csv
  new_pipeline/config/champion_run_body.json
)
echo "==> dropping daily-book paths"
for p in "${EXCLUDE[@]}"; do
  if [ -e "$DEST/$p" ]; then
    printf '    - %s\n' "$p"
    rm -rf "$DEST/$p"
  fi
done

# tournament/: drop all of it EXCEPT the two modules evaluation/ imports.
echo "==> pruning tournament/ to the gauntlet's dependencies"
if [ -d "$DEST/new_pipeline/tournament" ]; then
  find "$DEST/new_pipeline/tournament" -type f ! -name '__init__.py' \
    ! -name 'simulator.py' ! -name 'regime_state.py' -delete
  find "$DEST/new_pipeline/tournament" -type d -empty -delete 2>/dev/null || true
  cat > "$DEST/new_pipeline/tournament/__init__.py" <<'INIT'
"""Pruned to the two modules new_pipeline.evaluation imports.

The daily long/short tournament does not travel to the intraday fork, but the
gauntlet imports ``sharpe_ratio`` from ``.simulator`` (and features/ imports
``causal_percentiles`` from ``.regime_state``). Carrying these two files is
deliberate: relocating the function would mean editing new_pipeline/evaluation,
which travels unmodified.

Deliberately empty — both are imported as submodules, so no re-export is
needed, and the original __init__ re-exported modules that are now absent.
"""
INIT
  echo "    kept: $(cd "$DEST/new_pipeline/tournament" && ls | tr '\n' ' ')"
fi

echo "==> pruning tests that import dropped modules, then checking imports"
python3 -I - "$DEST" <<'PY'
import ast, pathlib, sys, collections

dest = pathlib.Path(sys.argv[1])

def resolve(mod: str):
    rel = mod.replace(".", "/")
    for cand in (dest / (rel + ".py"), dest / rel / "__init__.py"):
        if cand.exists():
            return cand
    return None

def pkg_of(path):
    """Dotted package containing `path` (its __init__ counts as its own pkg)."""
    rel = path.relative_to(dest).with_suffix("")
    parts = list(rel.parts)
    if parts[-1] == "__init__":
        parts.pop()
    return parts[:-1] if path.name != "__init__.py" else parts


def pkg_imports(path):
    """Absolute AND relative new_pipeline imports. Relative ones matter: a
    pruned package's __init__ re-exporting `.deleted_mod` is invisible to an
    absolute-only scan, and that is exactly how it breaks at import time."""
    try:
        tree = ast.parse(path.read_text())
    except Exception:
        return set()
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.ImportFrom):
            if n.level:
                base = pkg_of(path)
                up = n.level - 1
                base = base[:len(base) - up] if up else base
                target = ".".join(base + ([n.module] if n.module else []))
                if target.startswith("new_pipeline"):
                    out.add(target)
                    out.update(f"{target}.{a.name}" for a in n.names
                               if resolve(f"{target}.{a.name}") is not None
                               or (dest / target.replace(".", "/") / f"{a.name}.py").exists())
            elif n.module and n.module.startswith("new_pipeline"):
                out.add(n.module)
        elif isinstance(n, ast.Import):
            out.update(a.name for a in n.names if a.name.startswith("new_pipeline"))
    return out

tests = sorted((dest / "new_pipeline" / "tests").rglob("test_*.py"))
dropped = []
for t in tests:
    missing = {m for m in pkg_imports(t) if resolve(m) is None}
    if missing:
        t.unlink()
        dropped.append((t.relative_to(dest), sorted(missing)[:2]))
print(f"    pruned {len(dropped)} of {len(tests)} test files")
for rel, miss in dropped[:8]:
    print(f"      - {rel}  (needs {', '.join(miss)})")
if len(dropped) > 8:
    print(f"      … and {len(dropped) - 8} more")

dangling = collections.defaultdict(set)
for py in sorted((dest / "new_pipeline").rglob("*.py")):
    for m in pkg_imports(py):
        if resolve(m) is None:
            dangling[m].add(str(py.relative_to(dest)))
if dangling:
    print(f"\n    DANGLING IMPORTS — {len(dangling)} module(s) referenced but absent:")
    for m, users in sorted(dangling.items()):
        shown = sorted(users)[:3]
        more = f" (+{len(users) - 3})" if len(users) > 3 else ""
        print(f"      {m}")
        for u in shown:
            print(f"          <- {u}{more if u == shown[-1] else ''}")
    print("\n    ^ resolve these before the first run. Do NOT fix one by editing")
    print("      new_pipeline/evaluation/ — the gauntlet travels unmodified.")
else:
    print("\n    no dangling new_pipeline imports")
PY

echo
echo "==> result"
du -sh "$DEST" 2>/dev/null | sed 's/^/    total  /'
for d in data/minute_archives data/quote_vault new_pipeline/intraday \
         new_pipeline/evaluation evidence; do
  [ -e "$DEST/$d" ] && printf '    %-26s %s\n' "$d" "$(du -sh "$DEST/$d" | cut -f1)"
done
echo
echo "Next, in the fork:"
echo "  1. read docs/fork/INTRADAY_HANDOVER.md before designing anything"
echo "  2. write a fork-specific claude.md (the inherited one encodes the"
echo "     daily book's rules, including a DSR > 0.95 threshold)"
echo "  3. set QA_ALPACA_INTRADAY__* ONLY — the daily book's keys must be absent"
echo "  4. resolve any dangling imports listed above"
