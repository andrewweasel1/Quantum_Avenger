#!/usr/bin/env bash
# Extend the Liquid-1500 PIT fixture forward by one month, end to end.
#
# Run this when paper_trade_book refuses with "PIT universe has only N live
# names". Coverage is monthly by construction, so this is a monthly chore:
# the fixture covers month M only once month M-1 is complete (membership is
# strictly causal, member_month = evaluation_month + 1).
#
# TWO SHARP EDGES, both of which have cost real time:
#
# 1. A FRESH VAULT DIR EVERY RUN. The bars ingest resumes at CHUNK-FILE
#    level, not by date: re-running against a populated vault with a later
#    --end skips all 58 cached chunks and never fetches the new session. The
#    extension then no-ops for want of the very day you re-ran to get. The
#    date stamp below exists for exactly this reason — do not point this at a
#    previous run's directory to "save time".
#
# 2. THE LIVE MONTH NEEDS TWO SESSIONS. apply_gap_guard requires >=2 bar days
#    inside an interval, so on the 1st trading day of a month the extension
#    legitimately produces nothing (2026-11-02: 1500 intervals built, 0
#    survived). Wait for the 2nd session. Do NOT relax the guard — it is what
#    makes membership mean "backed by continuous bar coverage".
#
# Usage: bash new_pipeline/scripts/rebuild_universe_forward.sh [YYYY-MM-DD end]
set -euo pipefail

END="${1:-$(date -u +%F)}"
# ~6 months of bars: clears the rule's 63-day rolling ADV at min_obs 40 with
# room to spare. Census only needs the evaluation month at >=10 days.
BARS_START="$(date -u -d "$END -6 months" +%Y-%m-01)"
CENSUS_START="$(date -u -d "$END -3 months" +%Y-%m-01)"
SC="${SC:-/tmp/universe_rebuild}"
VAULT="$SC/rebuild_$(date -u +%Y%m%dT%H%M%S)"
FIXTURE="new_pipeline/data/universe/liquid1500_pit.csv"
mkdir -p "$VAULT"

echo "==> rebuild window: bars $BARS_START..$END | census $CENSUS_START..$END"
echo "    fresh vault: $VAULT"

echo "==> 1/4 census (survivorship-free enumeration; no --universe filter)"
python3 -m new_pipeline.scripts.ingest_short_volume_vault \
  --start "$CENSUS_START" --end "$END" \
  --vault-dir "$VAULT/short_volume" --out census_short_volume.csv

CENSUS="$VAULT/short_volume/census_short_volume.csv"

echo "==> 2/4 daily bars (candidates intersected with the census)"
python3 -m new_pipeline.scripts.ingest_liquid_universe_vault \
  --start "$BARS_START" --end "$END" \
  --vault-dir "$VAULT/liquid_vault" --census "$CENSUS"

echo "==> 3/4 extend the fixture in place"
cp "$FIXTURE" "$VAULT/fixture_before.csv"
python3 -m new_pipeline.scripts.extend_liquid_universe \
  --bars "$VAULT/liquid_vault/bars.parquet" --census "$CENSUS" \
  --fixture "$FIXTURE"

echo "==> 4/4 verify what the book's own guard will see"
python3 - "$FIXTURE" <<'PY'
import sys
from datetime import date
from new_pipeline.scripts.paper_trade_book import universe_health
h = universe_health(sys.argv[1], date.today())
print(f"    live={h['live']} open_ended={h['open_ended']} "
      f"collapsed={h['collapsed']} coverage_to={h['cliff']}")
if h["collapsed"]:
    raise SystemExit(
        "    STILL COLLAPSED — the book will refuse. If the extension reported "
        "a NO-OP for want of a 2nd session, re-run on the next trading day; "
        "otherwise read the members/intervals/guard counts it printed.")
print("    OK — paper_trade_book will run. Commit the fixture + its alias file.")
PY

echo
echo "Then:  git add $FIXTURE ${FIXTURE%.csv}_aliases.csv && git commit"
echo "Then:  python3 -m new_pipeline.scripts.paper_trade_book --execute   (detached, by 15:30 ET)"
