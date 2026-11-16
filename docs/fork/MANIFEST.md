# Manifest: what is in this repository, and why

This repository was produced from the parent daily long/short project by
`new_pipeline/scripts/build_intraday_fork.sh`, which reads only from git and
writes only into its destination. Everything below describes the result.

## How it was verified

| check | result |
|---|---|
| dangling `new_pipeline` imports (absolute and relative) | none |
| `ruff check new_pipeline` | clean |
| test suite, in this repository's CI environment (Alpaca SDK installed, no `QA_*` variables) | **498 passed, 6 skipped** |
| coverage against the parent's unchanged 85% gate | **91.28%** |
| gauntlet fence, tamper-tested | catches an edited gate and a softened default |
| **real pipeline, scrubbed environment** | ran end to end — see below |

The last row is the one that matters, and it exists because the first version
of this fork did not have it. That version passed 437 unit tests and would not
have run: it excluded the universe fixture the intraday stack reads, so every
run resolved **zero symbols**, and its documentation told the reader not to
reach for the file that fixed it. The suite runs on fakes and could not see
either problem. A green suite is necessary, not sufficient.

The six skips are optional extras this project does not install —
sentence-transformers (2), torch, spaCy, a CUDA device, and edgartools. None
is an Alpaca test: the SDK is installed in sessions and in CI alike, so the
two environments cannot disagree about it.

### The smoke run (reproduce it — see `docs/fork/KICKOFF.md`)

One month of the inherited mean-reversion book, 2026-07-01..2026-07-31, with
no environment beyond `PYTHONPATH`, the universe path and the vault path:

```
intraday_orb: 2634 symbols, 22 sessions
dailies: 74009 rows, 1750 names
quote vault: 108765 cells, measured-spread coverage 51.1% of name-days
scanner[attention|tradable|dislocation|volatility|cheap_gap]: 22/22 sessions, top 50
simulated: 22 sessions x 160 trials (5 scanners x 32 constructions), 14602 trades
verdict: promoted=False reason='low DSR' dsr=0.0000 null_margin=0.571 pbo=0.179
```

This is a plumbing check on a REJECTED strategy over 22 sessions. Its verdict
means nothing; that it ran is the point. Two numbers in it look wrong and are
not — see "Known seams".

## Travels

| Path | Size | Why |
|---|---|---|
| `data/minute_archives/` | 4.2 GB, 63 tars | Minute vault, 2021-09..2026-08, Small/Mid Cap Extended segments. Data, not assumptions. Each tar is under the 100 MB file ceiling. |
| `data/quote_vault/` | 1.9 MB, 60 cells | Measured NBBO half-spread and touch depth by month. Replaced a floor that was ~6× too conservative. |
| `new_pipeline/evaluation/` | 72 KB | **The gauntlet. Unmodified and pinned.** |
| `new_pipeline/intraday/` | 112 KB | Vault loaders, cost model, simulator, scanner, evaluator. The cost model and simulator are sound infrastructure; `orb.py`, `meanrev.py` and the scanner variants are REJECTED strategies, kept so the evidence stays reproducible. |
| `new_pipeline/data/universe/liquid1500_pit.csv` (+ aliases, exclusions) | 285 KB | **Required.** The intraday stack's static symbol base — see "Known seams". |
| `new_pipeline/{config,core,adapters,execution,features,monitoring,data}/` | — | Config tree, seeding, broker and data adapters, features, generic ops. |
| `new_pipeline/tournament/` (10 modules) | ~950 lines | `simulator` and `regime_state` because the gauntlet imports them (see "The fence has a cost"); `cpcv`, `causal_selection`, `feature_selection`, `ols`, `sample_weights`, `trainer`, `objectives`, `data_iterator` because they are the generic validation primitives the plan's Phase 3 names. |
| `new_pipeline/scripts/` | — | Vault ingest and restore, quote vault, spread calibration, `signal_ic`, universe build/extend. |
| `evidence/` | 24 MB | `orb_v1..v2`, `meanrev_v1..v7`: returns matrices, trade ledgers, manifests, findings. |
| `docs/fork/`, `docs/intraday_learned_model_plan.md`, `docs/quantitative_math.md` | — | Handover, this manifest, the kickoff brief, the plan of record. |

## Does NOT travel

| Path | Why not |
|---|---|
| `models/` | The parent's **live paper book**: its account ledger, promotion registry and champion boosters. A fork holding a valid registry could trade that account. |
| `new_pipeline/scripts/paper_trade_book.py`, `promote_candidates.py` | The live daily executor and its promotion tool. |
| `new_pipeline/tournament/` (the rest) | The daily long/short book and its orchestration: `long_short`, `pipeline`, `director`, `grid_search`, `stat_arb`, `johansen`, `meta_labeling`, `accounting`. |
| `new_pipeline/{portfolio,api,analysis,hardening}/`, `main.py`, `execution/{runner,orchestrator}.py`, `data/training_db.py` | Daily portfolio construction, run API, deployment and orchestration. |
| `frontend/` | 151 MB dashboard for the daily book. |
| the parent's roadmap and phase specifications, `codebase_bundle.md` | They describe the daily system; this project starts from the handover instead. |
| `config/champion_run_body.json`, `config/CHAMPION.md` | The frozen daily champion's configuration. |
| the parent's `claude.md`, `README.md`, `Makefile`, CI workflow, session hook, `.claude/settings.json`, `mcp.json` | Replaced by this project's own. |
| the parent's Dependabot config | The owner chose on 2026-11-16 not to run automated dependency PRs here. Requirements are open `>=` ranges, so such PRs only raise floors that installs already exceed, and on a private repository each one spends CI minutes. Version bumps are deliberate changes. |

**What the plan's Phase 3 can and cannot reuse.** The primitives it names
travel with their tests: the purged CPCV splitter, the causal Granger screen
(BHY-adjusted), López de Prado uniqueness weights, and the XGBoost trainer
with the asymmetric false-positive objective. The daily orchestration that
wired them together does not, and should not be rebuilt in its image.

One thing is genuinely new work: `cpcv.py` splits a time-ordered index into
contiguous blocks by ROW POSITION and has no notion of a session. Split an
event panel that way and a block boundary lands mid-session, putting one
session's events on both sides of a train/test edge. Session-grouped folds —
split over the session index, then expand to event rows — must be built, with
the test the plan demands that no session appears in both train and test of
any fold. Its span-based purge and embargo are worth reusing in session time.

## The fence: `new_pipeline/evaluation/` is not this project's to edit

Every rejection verdict in `evidence/` was produced by this code under these
settings. Soften either and the rejections stop being comparable to anything.
The risk is specific: a session asked to find a profitable model, holding an
editable copy of its own judge and no memory of why each gate exists, has one
very cheap path to success. It would not look like cheating.

Three mechanical layers, because prose alone has not been enough here:

1. **Code pins.** `docs/fork/GAUNTLET.sha256` holds the SHA-256 of every
   `new_pipeline/evaluation/*.py` and of the two `tournament/` modules the
   gauntlet imports. `tests/unit/test_gauntlet_fence.py` fails on any change,
   and on any new unpinned module appearing in `evaluation/`.
2. **Threshold pins.** `docs/fork/GAUNTLET_CONFIG.json` holds the effective
   `evaluation` config. The same test re-reads it in a scrubbed subprocess and
   fails on drift.
3. **Edit denial.** `.claude/settings.json` denies the Edit and Write tools on
   `new_pipeline/evaluation/**` and on the code-pin file.

**What the fence cannot see:** a `QA_EVALUATION__*` variable set at run time
overrides a pinned default without touching the repository. So every run's
candidate manifest now records `evaluation_config` — the effective settings
that verdict was reached under. A softened run shows up in its own evidence.
Read that field when you read a verdict.

### Changing the gauntlet (owner sign-off only)

Sometimes a change is right. It is never incidental. With the owner's explicit
sign-off, make the change and regenerate both pins in the same commit:

```
{ sed -n '1,3p' docs/fork/GAUNTLET.sha256
  sha256sum new_pipeline/evaluation/*.py \
            new_pipeline/tournament/simulator.py \
            new_pipeline/tournament/regime_state.py; } > /tmp/pins && mv /tmp/pins docs/fork/GAUNTLET.sha256
env -i PATH="$PATH" PYTHONPATH="$PWD" python3 -c "import json; from new_pipeline.config import get_config; print(json.dumps(get_config().evaluation.model_dump(), indent=1, sort_keys=True))" > docs/fork/GAUNTLET_CONFIG.json
```

Decided so far: on 2026-11-16 the owner chose to leave White's Reality Check a
recorded diagnostic rather than a gate, keeping the judge config-identical to
the parent's.

### The fence has a cost, and it is paid deliberately

`evaluation/hmm_gauntlet.py` and `tearsheet.py` import `sharpe_ratio` from
`tournament.simulator`; `features/market_state.py` imports
`causal_percentiles` from `tournament.regime_state`. The gauntlet is not fully
self-contained. Relocating the function would mean editing the judge, so those
two files travel and are pinned alongside it. `sharpe_ratio(returns, periods=252)`
takes `periods` as a parameter, so it is horizon-agnostic despite the default.

## Environment and credentials

- **This project runs in its own cloud environment**, one that has never
  held another project's keys. Every script here reads the generic
  `QA_ALPACA__*` names, so if this project were opened in an environment
  holding a different account's keys under those names, it would use that
  account and nothing in code could tell.
- **One dedicated paper account**, as `QA_ALPACA__API_KEY` /
  `QA_ALPACA__SECRET_KEY`. Environment variables only; never in a file.
- The kickoff's first check is the account's open-position count: a new
  account holds none, the daily book's holds several hundred.
- Hosts: `paper-api.alpaca.markets`, `data.alpaca.markets`,
  `stream.data.alpaca.markets`, and `cdn.finra.org` for the census the
  universe extension uses.

## Known seams

Things that are true, slightly awkward, and cheaper to read here than to
rediscover.

- **The universe path is an environment variable.** The framework's default
  universe is a packaged 41-name fixture with none of the extended-cap
  segments. The session hook exports
  `QA_DATA__UNIVERSE_PATH=new_pipeline/data/universe/liquid1500_pit.csv`; if a
  run ever lacks it, `intraday.universe.assert_symbols` refuses and names it.
- **The static base is not point-in-time.** `segment_symbols` takes every
  ticker that ever carried a Small or Mid Cap Extended label (2,634 names) and
  ignores the fixture's monthly intervals. Per-session eligibility is causal;
  the base set is not.
- **`defaults.yaml` still lists five scanner variants.** `schema.py` documents
  the collapse to `attention` alone, but the YAML overrides it, so an
  un-configured run prices 160 trials across variants already rejected. Every
  official run since `meanrev_v5` set
  `QA_INTRADAY__SCANNER_VARIANTS='["attention"]'` by hand.
- **`measured_spread_coverage` counts the warm-up month.** Its denominator
  includes the month loaded for trailing statistics, which has no quote stats
  by construction. On the one-month smoke run it reads 51.1% while coverage
  inside the window is **98.0%**. On the 60-month run it read 94.4%, slightly
  understating the truth for the same reason.
- **`_intraday_keys` wants a second key pair.** `intraday_paper_session`
  requires `QA_ALPACA_INTRADAY__*` to be set and to DIFFER from the generic
  pair — a guard from the parent, where two books shared an environment. Here
  there is one account. Collapse it to the single pair when a promoted
  strategy first needs the paper session; never satisfy it with another
  account's keys.
- **The checkpointed ingest commits and pushes.**
  `minute_ingest_checkpointed_v2.sh` ingests any month it does not find
  archived, then commits and pushes it to the checked-out branch. To get data
  back after a container reclaim use `restore_minute_vault.sh`, which only
  extracts.
- **The ORB note says 78 trials; its matrices hold 72.** The programme total
  of 776 is 704 mean-reversion plus 72 opening-range, by the committed
  returns matrices.
- **CI uses a sparse checkout** that omits the 4.2 GB of vault archives; no
  test reads them. A full checkout cost about seven minutes per job in the
  parent.
