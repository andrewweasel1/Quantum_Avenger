#!/usr/bin/env bash
# Produce the source tree for the intraday fork.
#
# Reads ONLY from git (tracked files at HEAD) and writes ONLY into <dest>.
# It never modifies this repository, so it is safe to re-run. Because it
# exports HEAD, uncommitted edits — including to the templates it installs —
# do not travel: commit first.
#
# What it does, in order:
#   1. exports the tracked tree at HEAD into <dest>
#   2. lifts the intraday evidence out of models/prod/evidence -> <dest>/evidence
#   3. deletes the daily-book code, fixtures, docs and artifacts (EXCLUDE below)
#   4. prunes tournament/ to the two modules the gauntlet imports plus the
#      generic validation primitives (CPCV, causal screen, weights, trainer)
#   5. installs the fork's own project files from docs/fork/template/
#   6. prunes tests that import now-absent modules; reports dangling imports
#   7. pins the gauntlet: code by SHA-256, thresholds by value
#
# It does NOT rewrite retained code or config. An earlier draft pointed the
# config default at the Liquid fixture; the framework's own suite objected
# (test_universe_path_config_selects_fixture pins the packaged 41-name
# default), and it was right — the fork's session hook exports
# QA_DATA__UNIVERSE_PATH instead, and intraday.universe.assert_symbols names
# that variable if a run ever resolves zero symbols without it.
#
# WHAT A PASSING RUN DOES AND DOES NOT PROVE. Steps 6-7 and the unit suite run
# on fakes. The first version of this script passed all of them (437 tests)
# while shipping a tree that resolved ZERO symbols, because it excluded the
# universe fixture the intraday stack reads and no fake could notice. A green
# suite is necessary, not sufficient: run the real pipeline in the tree (the
# smoke command in docs/fork/KICKOFF.md) before trusting it.
#
# Usage: bash new_pipeline/scripts/build_intraday_fork.sh /path/to/fork
#        SKIP_DATA=1 ...   structural dry run without the 4.2GB vault archives
set -euo pipefail

DEST="${1:?usage: build_intraday_fork.sh <dest-dir>}"
SRC="$(git rev-parse --show-toplevel)"
cd "$SRC"
TPL="docs/fork/template"

# A fresh clone of the (empty) target repository holds only .git; anything
# else means the destination is not ours to write into.
if [ -e "$DEST" ] && [ -n "$(ls -A "$DEST" 2>/dev/null | grep -vx '.git' || true)" ]; then
  echo "refusing to write into a non-empty directory: $DEST" >&2
  exit 1
fi
mkdir -p "$DEST"
DEST="$(cd "$DEST" && pwd)"

echo "==> exporting tracked tree at $(git rev-parse --short HEAD) -> $DEST"
if [ "${SKIP_DATA:-0}" = "1" ]; then
  # Structural dry run: everything but the vault archives, so the checks
  # below can be iterated in seconds. The real export must run WITHOUT this.
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

# The daily long/short book — its live ledger, champions, construction code,
# dashboard and roadmap — plus project files the fork replaces with its own.
#
# NOT here, deliberately: new_pipeline/data/universe/liquid1500_pit.csv. The
# intraday stack reads it (intraday.universe.segment_symbols) as its static
# symbol base; without it every run resolves zero symbols.
EXCLUDE=(
  models                                       # ledger, registry, boosters, daily evidence
  frontend                                     # 151MB daily-book dashboard
  reference_code                               # legacy pre-migration source
  codebase_bundle.md                           # 22k-line snapshot of the OLD codebase
  pack_repo.py
  mcp.json                                     # points at ./Quantum_Avenger paths
  .dockerignore
  .github/workflows/nightly-gpu.yml
  docs/ARCHITECTURE_ROADMAP.md                 # the daily system's roadmap and specs
  docs/FULL_SYSTEM_INTEGRATION_GUIDE.md
  docs/IMPLEMENTATION_STATUS.md
  docs/OFFENSE_ROADMAP.md
  docs/ROADMAP_2026.md
  docs/execution_roadmap.md
  docs/system_architecture.md
  docs/PHASE_1_SPECIFICATION.md
  docs/PHASE_2_SPECIFICATION.md
  docs/PHASE_3_SPECIFICATION.md
  docs/PHASE_4_SPECIFICATION.md
  docs/PHASE_5_SPECIFICATION.md
  docs/PHASE_6_SPECIFICATION.md
  docs/PHASE_7_SPECIFICATION.md
  new_pipeline/docs/API_REFERENCE.md
  new_pipeline/docs/ARCHITECTURE.md
  new_pipeline/portfolio
  new_pipeline/api
  new_pipeline/hardening
  new_pipeline/analysis
  new_pipeline/main.py                         # daily entrypoint
  new_pipeline/execution/runner.py             # daily live orchestration
  new_pipeline/execution/orchestrator.py
  new_pipeline/data/training_db.py
  new_pipeline/scripts/paper_trade_book.py     # the live daily executor
  new_pipeline/scripts/promote_candidates.py
  new_pipeline/scripts/check_health.py
  new_pipeline/scripts/ingest_training_data.py
  new_pipeline/scripts/rebuild_universe_forward.sh   # verifies via paper_trade_book
  new_pipeline/scripts/build_intraday_fork.sh        # this script
  new_pipeline/scripts/publish_intraday_fork.sh      # and its publisher
  new_pipeline/config/champion_run_body.json
  new_pipeline/config/CHAMPION.md
  new_pipeline/requirements-api.txt            # nothing outside api/ imports fastapi
)
echo "==> dropping daily-book paths"
for p in "${EXCLUDE[@]}"; do
  if [ -e "$DEST/$p" ]; then
    printf '    - %s\n' "$p"
    # :? aborts rather than expanding toward / if either is ever empty.
    rm -rf "${DEST:?}/${p:?}"
  fi
done

# tournament/: the daily long/short construction and its orchestration go;
# the generic validation primitives stay. Two are there because the gauntlet
# imports them (simulator.sharpe_ratio, regime_state.causal_percentiles) and
# the gauntlet must not be edited. The rest are what the plan of record's
# Phase 3 names — purged CPCV, the causal Granger screen, uniqueness weights,
# the XGBoost trainer and its asymmetric objective — none of which is specific
# to a daily horizon. With cpcv, objectives and simulator all present the
# package's own __init__ works unmodified, so nothing here is rewritten.
KEEP_TOURNAMENT=(
  __init__.py simulator.py regime_state.py
  cpcv.py causal_selection.py feature_selection.py ols.py
  sample_weights.py trainer.py objectives.py data_iterator.py
)
echo "==> pruning tournament/ to the gauntlet's dependencies + generic primitives"
if [ -d "$DEST/new_pipeline/tournament" ]; then
  for f in "$DEST"/new_pipeline/tournament/*; do
    name="$(basename "$f")"
    keep=0
    for k in "${KEEP_TOURNAMENT[@]}"; do [ "$name" = "$k" ] && keep=1; done
    if [ "$keep" = 0 ]; then
      rm -rf "${DEST:?}/new_pipeline/tournament/${name:?}"
    fi
  done
  for k in "${KEEP_TOURNAMENT[@]}"; do
    [ -e "$DEST/new_pipeline/tournament/$k" ] || { echo "expected tournament/$k is missing" >&2; exit 1; }
  done
  echo "    kept: $(cd "$DEST/new_pipeline/tournament" && ls | tr '\n' ' ')"
fi

echo "==> installing the fork's own project files"
[ -d "$DEST/$TPL" ] || { echo "templates missing at HEAD ($TPL) — commit them first" >&2; exit 1; }
install -m 644 "$DEST/$TPL/claude.md"      "$DEST/claude.md"
install -m 644 "$DEST/$TPL/README.md"      "$DEST/README.md"
install -m 644 "$DEST/$TPL/Makefile"       "$DEST/Makefile"
install -m 644 "$DEST/$TPL/ci.yml"         "$DEST/.github/workflows/ci.yml"
install -m 755 "$DEST/$TPL/session-start.sh" "$DEST/.claude/hooks/session-start.sh"
install -m 644 "$DEST/$TPL/settings.json"  "$DEST/.claude/settings.json"
install -m 644 "$DEST/$TPL/KICKOFF.md"     "$DEST/docs/fork/KICKOFF.md"
install -m 644 "$DEST/$TPL/test_gauntlet_fence.py" \
               "$DEST/new_pipeline/tests/unit/test_gauntlet_fence.py"
rm -rf "${DEST:?}/${TPL:?}"
cp "$DEST/docs/fork/INTRADAY_HANDOVER.md" "$DEST/evidence/README.md"

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
for rel, miss in dropped[:6]:
    print(f"      - {rel}  (needs {', '.join(miss)})")
if len(dropped) > 6:
    print(f"      … and {len(dropped) - 6} more")

dangling = collections.defaultdict(set)
for py in sorted((dest / "new_pipeline").rglob("*.py")):
    for m in pkg_imports(py):
        if resolve(m) is None:
            dangling[m].add(str(py.relative_to(dest)))
if dangling:
    print(f"\n    DANGLING IMPORTS — {len(dangling)} module(s) referenced but absent:")
    for m, users in sorted(dangling.items()):
        print(f"      {m}  <- {', '.join(sorted(users)[:3])}")
    print("\n    ^ resolve these before the first run. Do NOT fix one by editing")
    print("      new_pipeline/evaluation/ — the gauntlet travels unmodified.")
    sys.exit(1)
print("    no dangling new_pipeline imports")
PY

echo "==> pinning the gauntlet (code by hash, thresholds by value)"
(
  cd "$DEST"
  {
    echo "# SHA-256 of the promotion gauntlet at fork time. Checked by"
    echo "# new_pipeline/tests/unit/test_gauntlet_fence.py. Regenerate ONLY with"
    echo "# the owner's sign-off: see docs/fork/MANIFEST.md, \"Changing the gauntlet\"."
    sha256sum new_pipeline/evaluation/*.py \
              new_pipeline/tournament/simulator.py \
              new_pipeline/tournament/regime_state.py
  } > docs/fork/GAUNTLET.sha256
  env -i PATH="$PATH" PYTHONPATH="$DEST" python3 -c \
    "import json; from new_pipeline.config import get_config; print(json.dumps(get_config().evaluation.model_dump(), indent=1, sort_keys=True))" \
    > docs/fork/GAUNTLET_CONFIG.json
  echo "    $(grep -vc '^#' docs/fork/GAUNTLET.sha256) files pinned; $(python3 -c "import json;print(len(json.load(open('docs/fork/GAUNTLET_CONFIG.json'))))") thresholds pinned"
)

echo
echo "==> result"
du -sh "$DEST" 2>/dev/null | sed 's/^/    total  /'
for d in data/minute_archives data/quote_vault new_pipeline/intraday \
         new_pipeline/evaluation evidence; do
  [ -e "$DEST/$d" ] && printf '    %-26s %s\n' "$d" "$(du -sh "$DEST/$d" | cut -f1)"
done
echo
echo "Next: run the suite AND the smoke command in docs/fork/KICKOFF.md inside"
echo "      $DEST — a green suite alone is not proof the tree works."
