#!/usr/bin/env bash
# Rehydrate the minute vault from the committed monthly archives.
#
# Pure extraction: no network, no keys, no commits. The checkpointed ingest can
# also restore, but it then goes on to INGEST and PUSH any month it does not
# find archived — the wrong tool when all you want is the data back after a
# container reclaim.
#
#   bash new_pipeline/scripts/restore_minute_vault.sh <dest> [START_YM] [END_YM]
#   e.g. ... /scratch/vault            # everything
#        ... /scratch/vault 202605 202607   # only those months (YYYYMM)
#
# Then point the stack at it:  export QA_INTRADAY__VAULT_DIR=<dest>/minute_vault
set -euo pipefail

DEST="${1:?usage: restore_minute_vault.sh <dest-dir> [START_YM] [END_YM]}"
START="${2:-000000}"
END="${3:-999999}"
ARCH="$(git rev-parse --show-toplevel)/data/minute_archives"

shopt -s nullglob
tars=("$ARCH"/minute_*.tar)
if [ "${#tars[@]}" -eq 0 ]; then
  echo "no archives under $ARCH" >&2
  exit 1
fi
mkdir -p "$DEST"
n=0
for t in "${tars[@]}"; do
  ym="$(basename "$t" | sed -E 's/^minute_([0-9]{6}).*/\1/')"
  # 10# forces base ten: a bare leading zero would be read as octal.
  if [ "$((10#$ym))" -ge "$((10#$START))" ] && [ "$((10#$ym))" -le "$((10#$END))" ]; then
    tar -xf "$t" -C "$DEST"
    n=$((n + 1))
  fi
done
files="$(find "$DEST/minute_vault/by_symbol_month" -name '*.parquet' 2>/dev/null | wc -l)"
echo "restored $n archive(s): $files symbol-month files under $DEST/minute_vault"
echo "next: export QA_INTRADAY__VAULT_DIR=$DEST/minute_vault"
