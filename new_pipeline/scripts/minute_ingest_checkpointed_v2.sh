#!/usr/bin/env bash
# Checkpointed minute-vault ingest, v2: months whose tar would exceed the
# 99MB push ceiling are split into _a/_b halves by sorted symbol range —
# recent months carry more listed names and denser tape than the 70MB early
# months. Restore accepts any minute_${YM}*.tar so split and whole archives
# rehydrate identically. Otherwise identical to v1 (one month at a time,
# commit+push per completed month; the branch is the only reclaim-proof
# store; idempotent at file level).
#
# Usage: SC=<scratchpad dir> bash new_pipeline/scripts/minute_ingest_checkpointed_v2.sh
#   Backfill a different span:  SC=... START_YM=2021-09 END_YM=2024-07 bash ...
set -euo pipefail
SC="${SC:?set SC to the scratchpad dir}"
START_YM="${START_YM:-2024-08}"
END_YM="${END_YM:-2026-08}"
REPO="$(pwd)"
VAULT="$SC/minute_vault/by_symbol_month"
ARCH="data/minute_archives"
mkdir -p "$VAULT" "$REPO/$ARCH"

MONTHS=$(START_YM="$START_YM" END_YM="$END_YM" python3 - <<'PY'
import os
from datetime import date
from new_pipeline.intraday.data import months_between
sy, sm = map(int, os.environ["START_YM"].split("-"))
ey, em = map(int, os.environ["END_YM"].split("-"))
print(" ".join(f"{y:04d}{m:02d}"
                for y, m in months_between(date(sy, sm, 1), date(ey, em, 1))))
PY
)

commit_tar() {
  local tarball="$1" label="$2"
  local bytes
  bytes=$(stat -c %s "$tarball")
  git add "$tarball"
  git commit -q -m "Minute vault checkpoint $label ($((bytes / 1000000))MB)

Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01JCz1zKeRPyutPbqiAMDFQ6"
  git push -q -u origin claude/zen-davinci-sH7mS
}

for YM in $MONTHS; do
  if ls "$REPO/$ARCH"/minute_"$YM"*.tar >/dev/null 2>&1; then
    if ! ls "$VAULT"/*_"$YM".parquet >/dev/null 2>&1; then
      for t in "$REPO/$ARCH"/minute_"$YM"*.tar; do tar -xf "$t" -C "$SC"; done
    fi
    echo "[$YM] archived (restored to vault)"
    continue
  fi
  Y=${YM:0:4}; M=${YM:4:2}
  QA_DATA__UNIVERSE_PATH=new_pipeline/data/universe/liquid1500_pit.csv \
    python -m new_pipeline.scripts.ingest_minute_vault \
    --start "$Y-$M" --end "$Y-$M" --sleep 0.25 --vault-dir "$SC/minute_vault"
  TOTAL=$(cd "$SC" && du -cb minute_vault/by_symbol_month/*_"$YM".parquet | tail -1 | cut -f1)
  if [ "$TOTAL" -gt 95000000 ]; then
    mapfile -t FILES < <(cd "$SC" && ls minute_vault/by_symbol_month/*_"$YM".parquet | sort)
    HALF=$(( ${#FILES[@]} / 2 ))
    (cd "$SC" && printf '%s\n' "${FILES[@]:0:$HALF}" \
      | tar -cf "$REPO/$ARCH/minute_${YM}_a.tar" -T -)
    (cd "$SC" && printf '%s\n' "${FILES[@]:$HALF}" \
      | tar -cf "$REPO/$ARCH/minute_${YM}_b.tar" -T -)
    commit_tar "$REPO/$ARCH/minute_${YM}_a.tar" "${YM}a"
    commit_tar "$REPO/$ARCH/minute_${YM}_b.tar" "${YM}b"
    echo "[$YM] ingested + committed (split a/b, $((TOTAL / 1000000))MB total)"
  else
    (cd "$SC" && tar -cf "$REPO/$ARCH/minute_$YM.tar" minute_vault/by_symbol_month/*_"$YM".parquet)
    commit_tar "$REPO/$ARCH/minute_$YM.tar" "$YM"
    echo "[$YM] ingested + committed ($((TOTAL / 1000000))MB)"
  fi
done
echo "ALL MONTHS CHECKPOINTED"
