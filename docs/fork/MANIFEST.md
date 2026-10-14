# Fork manifest: what travels to the intraday repository, and why

Produced and verified by `new_pipeline/scripts/build_intraday_fork.sh`, which
reads only from git and writes only into its destination — it never modifies
this repository, so it is safe to re-run.

```
bash new_pipeline/scripts/build_intraday_fork.sh /path/to/fork
SKIP_DATA=1 bash ... /path/to/fork    # structural dry run, ~30s instead of ~5.5min
```

**Verified on the stripped tree**: zero dangling `new_pipeline` imports,
**437 passed / 6 skipped**, 95 of 150 test files retained. The 55 pruned test
files are the ones importing dropped daily-book modules; the script lists them
by name and by what they needed.

---

## Travels

| Path | Size | Why |
|---|---|---|
| `data/minute_archives/` | 4.2 GB, 63 tars | Minute vault, 2021-09..2026-08. Months of ingest. **Data, not assumptions** — carries no horizon bias. Each tar is already under the 100 MB file ceiling. |
| `data/quote_vault/` | 1.9 MB, 60 cells | Measured NBBO half-spread + displayed depth, 94.4% name-day coverage. Replaces a floor that was ~6× too conservative. |
| `new_pipeline/evaluation/` | 72 KB | **The gauntlet. Travels UNMODIFIED.** See the fence below. |
| `new_pipeline/intraday/` | 108 KB | The intraday stack: vaults, scanner, simulate, evaluate, quotes, calendar. |
| `new_pipeline/features/` | 132 KB | `microstructure.corwin_schultz`, `slippage.hydrodynamic_slippage_bps` are on the intraday import path. |
| `new_pipeline/{config,core,adapters,execution}/` | — | Config tree, seeding, broker adapters, broker ABC. |
| `new_pipeline/monitoring/` | — | Self-contained generic ops (alerting/health/metrics/telemetry); imports only `config`. `tests/conftest.py` needs it. |
| `new_pipeline/tournament/{simulator,regime_state}.py` | 244 lines | **Only** these two. See "the fence has a cost" below. |
| `evidence/` | 24 MB | `orb_v1..v2`, `meanrev_v1..v7` — returns matrices, trade ledgers, candidate manifests, FINDINGS. Lifted out of `models/prod/evidence/` so no daily-book artifact travels. |
| `docs/fork/INTRADAY_HANDOVER.md` | — | The four dead ends with their numbers. Also copied to `evidence/README.md`. |

## Does NOT travel

| Path | Why not |
|---|---|
| `models/` | The **live daily book**: `book_state.json` (the account ledger), `promotion_registry.json` (daily champions), `manual/` (champion boosters), and the daily sector-run evidence. A fork holding a valid registry could trade the live account. |
| `new_pipeline/scripts/paper_trade_book.py` | The live daily executor. |
| `new_pipeline/tournament/` (rest) | Daily long/short construction: cpcv, director, johansen, meta_labeling, stat_arb, causal_selection, trainer, pipeline. |
| `new_pipeline/data/universe/liquid1500_pit.csv` | PIT universe — **monthly, end-exclusive** membership intervals, an object built for daily rebalancing. The intraday stack bypasses it via `segment_symbols`. |
| `new_pipeline/config/champion_run_body.json` | The frozen daily champion's feature/factor config. |
| `new_pipeline/{portfolio,api,analysis}/` | Daily portfolio construction, the run API, daily analysis. |
| `new_pipeline/main.py`, `execution/{runner,orchestrator}.py`, `data/training_db.py`, `scripts/{check_health,ingest_training_data,promote_candidates,extend_liquid_universe}.py` | Daily orchestration and its entrypoints. Dropping these is what removes the last dangling imports. |
| `frontend/` | 151 MB daily-book dashboard. |
| `reference_code/` | Legacy pre-migration source. |

## The fence: `new_pipeline/evaluation/` is not the fork's to edit

Every rejection verdict in `evidence/` was produced by this code. Soften a gate
and the rejections stop being comparable to anything, including each other.

The risk is specific, not ceremonial: a fresh session told to build a
profitable intraday model, holding an editable copy of its own judge and
carrying no memory of why each gate exists, has one very cheap path to
success. It would not look like cheating — it would look like reasonable
engineering by someone who did not know the history.

If a gate genuinely looks wrong, write down the argument and the
counter-evidence. Do not change the number.

### The fence has a cost, and it is paid deliberately

`new_pipeline/evaluation/hmm_gauntlet.py` and `tearsheet.py` import
`sharpe_ratio` from `new_pipeline.tournament.simulator`; `features/market_state.py`
imports `causal_percentiles` from `tournament.regime_state`. So the gauntlet is
**not fully self-contained** — an architectural wart inherited from the daily
stack.

The clean-looking fix would be to move `sharpe_ratio` into `evaluation/`. That
would mean editing the gauntlet, so instead the fork carries two files (244
lines) it otherwise has no use for. `sharpe_ratio(returns, periods=252)` takes
`periods` as a parameter, so it is horizon-agnostic despite the daily default.

The script rewrites `tournament/__init__.py`, which is *not* the gauntlet, to
stop re-exporting the deleted modules.

## Two things that make the fork safe on day one

1. **Its own `claude.md`.** The inherited one encodes daily-book rules,
   including a promotion threshold of DSR > 0.95 stated for the daily stack.
   The intraday gauntlet adds a family-wise per-regime bar (T^K: 0.9025 at
   K=2, 0.857375 at K=3).
2. **`QA_ALPACA_INTRADAY__*` keys only.** The daily book's keys must be
   **absent** from the fork's environment. The intraday runner already refuses
   keys identical to the daily book's, but absence makes touching that account
   structurally impossible rather than merely guarded.

## Mechanics, corrected

A GitHub-side fork costs nothing to create and uploads nothing — forks share
object storage server-side. But **GitHub will not fork a repository into the
account that already owns it**, so in practice this is a *new repository* plus
a one-time upload of the 63 vault tarballs: an hour of pushing, not a blocker.

This session's GitHub access is scoped to `quantum_avenger`, so the new
repository must be created and populated from the session that owns it.

## A caveat on the import check

The script's dangling-import report is a **report, not a guarantee**. It
resolves absolute and relative `new_pipeline` imports statically; it cannot see
`importlib` calls, string-built module names, or plugin registries. It also
earned that caveat the hard way — the first version scanned absolute imports
only and passed a tree whose `tournament/__init__.py` still re-exported five
deleted modules. The suite caught it; the checker now handles relative imports.

Run the suite in the fork before trusting the tree.
