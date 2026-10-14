#!/usr/bin/env bash
# Checkpointed minute-vault ingest: one month at a time, each completed month
# tarred into data/minute_archives/ and committed+pushed — the git branch is
# the only reclaim-proof store in the research environment, so progress is
# monotonic across container reclaims. Idempotent: archived months restore
# into the scratchpad vault instead of refetching; a killed in-flight month
# resumes at file level on the next invocation.
#
# Usage: SC=<scratchpad dir> bash new_pipeline/scripts/minute_ingest_checkpointed.sh
set -euo pipefail
SC="${SC:?set SC to the scratchpad dir}"
REPO="$(pwd)"
VAULT="$SC/minute_vault/by_symbol_month"
ARCH="data/minute_archives"
mkdir -p "$VAULT" "$REPO/$ARCH"

MONTHS=$(python3 - <<'PY'
from datetime import date
from new_pipeline.intraday.data import months_between
print(" ".join(f"{y:04d}{m:02d}" for y, m in months_between(date(2024, 8, 1), date(2026, 8, 1))))
PY
)

for YM in $MONTHS; do
  TARBALL="$REPO/$ARCH/minute_$YM.tar"
  if [ -f "$TARBALL" ]; then
    if ! ls "$VAULT"/*_"$YM".parquet >/dev/null 2>&1; then
      tar -xf "$TARBALL" -C "$SC"
    fi
    echo "[$YM] archived (restored to vault)"
    continue
  fi
  Y=${YM:0:4}; M=${YM:4:2}
  QA_DATA__UNIVERSE_PATH=new_pipeline/data/universe/liquid1500_pit.csv \
    python -m new_pipeline.scripts.ingest_minute_vault \
    --start "$Y-$M" --end "$Y-$M" --sleep 0.25 --vault-dir "$SC/minute_vault"
  (cd "$SC" && tar -cf "$TARBALL" minute_vault/by_symbol_month/*_"$YM".parquet)
  BYTES=$(stat -c %s "$TARBALL")
  if [ "$BYTES" -gt 99000000 ]; then
    echo "[$YM] archive ${BYTES}B exceeds the 99MB push limit — split needed" >&2
    exit 3
  fi
  git add "$ARCH/minute_$YM.tar"
  git commit -q -m "Minute vault checkpoint $YM ($((BYTES / 1000000))MB)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01JCz1zKeRPyutPbqiAMDFQ6"
  git push -q -u origin claude/zen-davinci-sH7mS
  echo "[$YM] ingested + committed ($((BYTES / 1000000))MB)"
done
echo "ALL MONTHS CHECKPOINTED"
