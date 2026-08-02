# Quantum Avenger

A quantitative trading research system built around one idea: **a strategy is
only as real as the gauntlet it survives.** Every candidate — thirteen
per-sector XGBoost models and one universe-wide long/short book — is judged by
a multiple-testing-aware promotion gauntlet on honest, point-in-time data with
full costs. Nothing is promoted by a human picking a good-looking backtest.

## Current state (2026-07)

The frozen champion is the **Universe Long Short book** on the Liquid-1500
universe (`config/CHAMPION.md`, run `36a3e7abc9cb`): census-window net Sharpe
**1.02**, Sortino 1.66, max drawdown −7%, ~225 names per leg, breakeven cost
64bps vs 10 charged, borrow and slippage paid. Every full-sample gate is green
(DSR 0.998 at 16 deflated trials, PBO 0.27, CPCV path pass 1.00, Reality Check
p 0.006, permutation-null margin +2.0). The family-wise per-regime gate reads
calm-state DSR **0.857 vs the 0.857375 bar** — a statistical coin-edge; the
spec is frozen and re-run unchanged as forward data accrues. The registry
(`promotion_registry.json`) is the source of truth for what passed and why.

## How it works

```
FINRA census ─┐                                  ┌─ 13 sector models (CPCV grid)
Alpaca SIP ───┼─ point-in-time Liquid-1500 ──────┤
EDGAR vault ──┤   features/factors/events        └─ Universe L/S book (16-20+
GDELT vault ──┘                                      deflated trial columns)
                                                        │
              DSR·N_eff │ PBO │ PSR │ CPCV paths │ permutation null │
              White's RC │ family-wise per-regime HMM gate │ costs+borrow
                                                        │
                                        promotion_registry.json (append-only)
```

Key honesty machinery: survivorship-free universe generated from the FINRA
Reg SHO daily census (delisted names included); calendar-time accounting;
turnover-based hydrodynamic slippage plus stock-loan borrow; deflated Sharpe
with correlation-adjusted effective trial counts; a family-wise per-regime
bar (`T^K`) on exogenous HMM market states with a leak-free causal
cross-check; pre-registered variant factorials priced by the same deflation.

## Quickstart

```bash
pip install -r new_pipeline/requirements.txt
NUMBA_DISABLE_JIT=1 python -m pytest new_pipeline/tests   # ~700 tests
QA_API_RUNS_DIR=./runs python -m new_pipeline.api.app     # dashboard on :8000
```

Official runs POST the committed frozen body (set `news.vault_dir` to a local
GDELT vault first — see `config/CHAMPION.md`):

```bash
curl -X POST localhost:8000/api/runs -H 'Content-Type: application/json' \
     --data @new_pipeline/config/champion_run_body.json
```

Credentials live ONLY in environment variables — `QA_ALPACA__API_KEY` /
`QA_ALPACA__SECRET_KEY` (paper keys start with `PK`). Never commit keys.

## Deploying WITHOUT containers (bare metal / VM)

Everything is plain Python; Docker/K8s are optional packaging. A single box
(4+ cores, 16GB RAM, ~20GB disk for vaults/runs) runs the whole system:

```bash
git clone <repo> && cd Quantum_Avenger
python3.11 -m venv .venv && . .venv/bin/activate
pip install -r new_pipeline/requirements.txt

# secrets + service config in an env file OUTSIDE the repo, e.g. /etc/quantum-avenger.env:
#   QA_ALPACA__API_KEY=PK...          QA_ALPACA__SECRET_KEY=...
#   QA_API_RUNS_DIR=/var/lib/quantum-avenger/runs
#   QA_EXECUTION__LEDGER_DIR=/var/lib/quantum-avenger/ledger

set -a; . /etc/quantum-avenger.env; set +a
python -m new_pipeline.api.app          # API + dashboard on 127.0.0.1:8000
```

As systemd units (survives reboots; run daily jobs with timers):

```ini
# /etc/systemd/system/qa-api.service
[Service]
WorkingDirectory=/opt/Quantum_Avenger
EnvironmentFile=/etc/quantum-avenger.env
ExecStart=/opt/Quantum_Avenger/.venv/bin/python -m new_pipeline.api.app
Restart=on-failure

# /etc/systemd/system/qa-paper.service (+ a .timer for Mon-Fri 15:30 ET)
[Service]
Type=oneshot
WorkingDirectory=/opt/Quantum_Avenger
EnvironmentFile=/etc/quantum-avenger.env
ExecStart=/opt/Quantum_Avenger/.venv/bin/python -m new_pipeline.scripts.paper_trade_book --execute
```

Put the API behind any TLS reverse proxy (nginx/caddy) if exposed; it also
runs fine bound to localhost with SSH tunneling. GPU on bare metal: install
CUDA 12 + a GPU xgboost wheel and set `QA_TOURNAMENT__DEVICE=cuda`
`QA_GPU__CUDA_ENABLED=true` — no container required.

## Deploying with Docker / Kubernetes (optional)

```bash
docker compose -f new_pipeline/hardening/docker/docker-compose.yml up -d --build
docker build -f new_pipeline/hardening/docker/Dockerfile.gpu -t quantum-avenger-gpu .
docker run --gpus all -e QA_TOURNAMENT__DEVICE=cuda -e QA_GPU__CUDA_ENABLED=true \
  -e QA_ALPACA__API_KEY -e QA_ALPACA__SECRET_KEY quantum-avenger-gpu pipeline
```

Kubernetes manifests: `new_pipeline/hardening/k8s/` (`deployment.yaml`,
`api.yaml`, `configmap.yaml`, `hpa.yaml`, `networkpolicy.yaml`;
`secrets.yaml` is a template — fill via your secret manager).

## Configuration & flags

One config system everywhere: `new_pipeline/config/defaults.yaml` (documented
defaults = the frozen champion's book construction) validated by
`config/schema.py` (the exhaustive typed reference). Every key is overridable
two ways, deepest-wins:

1. **Environment**: `QA_<SECTION>__<KEY>` — e.g. `QA_LONG_SHORT__EVAL_START=2018-09-01`,
   `QA_TOURNAMENT__NUM_BOOST_ROUND=50`, `QA_FUSION__ENABLED=true`.
2. **Run body**: the `overrides` object POSTed to `/api/runs` (see
   `config/champion_run_body.json`) — this is how official runs pin their spec.

Load-bearing knobs by section (see `schema.py` for every field):

| Section | Knob | Meaning (champion value) |
|---|---|---|
| `data` | `universe_path` | PIT membership CSV (`liquid1500_pit.csv`) |
| `alpaca` | `data_feed` | `sip` (full history incl. delisted) |
| `features` | `label_horizon`, `factor_set`, `extended_features`, `event_features`, `factor_null_policy` | 21d triple-barrier; 4 price + 3 fundamental factors; 7 families; on; `neutral` |
| `fusion` | `enabled`, `sentiment_backend`, `markov_features` | on / `vader` / off |
| `fundamentals` | `fixture_path` | committed EDGAR vault (`liquid_snapshots.csv`) |
| `news` | `providers`, `vault_dir` | `["vault"]` + local GDELT vault |
| `tournament` | `num_boost_round`, `feature_selection_method`, `sample_weighting`, `enable_meta_labeling` | 100 / `causal` / `uniqueness` / off (tested: no effect) |
| `execution` | `backtest_slippage_enabled`, `account_capital`, `confidence_threshold` | on / notional for impact + paper sizing / 0.55 |
| `long_short` | `enabled`, `quantile`, `cost_bps`, `rebalance_days`, `score_smoothing_days`, `rebalance_band`, `vol_target_annual`, `eval_start`, `short_borrow_bps`, `causal_window_days` | the champion book: on/0.2/10/5/5/0.5/0.05/2018-09-01/50/252 |
| `long_short` (variant trials) | `calm_cost_variants`, `calm_rebalance_band`, `calm_rebalance_days`, `moe_variants`, `structure_variants` | factorial columns priced by deflation: on/1.5/10/off/off |
| `evaluation` | `dsr_promotion_threshold`, `regime_family_wise`, `cpcv_path_gate_enabled`, `pbo_threshold`, `reality_check_enabled` | THE GATES — 0.95 / on (bar `T^K`) / on (≥0.5) / 0.5 / observability. Do not soften. |
| `system` | `run_mode` | `backtest` (offline fakes) / `paper` / `live` — selects adapters |

Inspect the merged config any time: `python -m new_pipeline.main show-config`.

## Running the full stack and individual parts

Every stage runs independently; vault builders are resumable (re-run to
continue after an interruption).

```bash
# ---- full stack -------------------------------------------------------------
QA_API_RUNS_DIR=./runs python -m new_pipeline.api.app     # API + dashboard + run launcher
python -m new_pipeline.main pipeline                      # one offline pipeline run, no API
python -m new_pipeline.main health                        # adapter/config health check
python -m new_pipeline.main show-config | less            # effective config
python -m new_pipeline.scripts.serve_mcp                  # MCP server (agent tooling)

# ---- data ingest (independent, resumable) -----------------------------------
# survivorship-free traded-symbol census + short-flow (FINRA Reg SHO, 2018-08+)
python -m new_pipeline.scripts.ingest_short_volume_vault \
    --start 2018-08-01 --end 2025-12-31 --vault-dir ./vaults/census
# census-seeded daily bars for the Liquid-1500 build (Alpaca SIP, adjustment=all)
python -m new_pipeline.scripts.ingest_liquid_universe_vault \
    --start 2016-01-01 --end 2025-12-31 --vault-dir ./vaults/liquid
# generate the point-in-time Liquid-1500 membership fixture from those two
python -m new_pipeline.scripts.build_liquid_universe \
    --bars ./vaults/liquid/bars.parquet --census ./vaults/census/census_short_volume.csv \
    --out new_pipeline/data/universe/liquid1500_pit.csv
# EDGAR companyfacts fundamentals (PIT as_of=filing date; resolves delisted CIKs)
python -m new_pipeline.scripts.ingest_fundamentals_vault \
    --universe new_pipeline/data/universe/liquid1500_pit.csv \
    --start 2016-01-01 --end 2025-12-31 --identity "You <you@example.com>" \
    --vault-dir ./vaults/fundamentals --out new_pipeline/data/fundamentals/liquid_snapshots.csv
# GDELT news vault (feeds VADER sentiment + news-burst features)
python -m new_pipeline.scripts.ingest_news_vault \
    --source gdelt --universe new_pipeline/data/universe/sp500_pit.csv \
    --start 2016-01-01 --end 2025-12-31 --vault-dir ./vaults/news
# 30-minute intraday bars (research only; see the intraday memo)
python -m new_pipeline.scripts.ingest_intraday_vault \
    --universe new_pipeline/data/universe/sp500_pit.csv \
    --start 2024-01-01 --end 2025-12-31 --vault-dir ./vaults/intraday --workers 4
# S&P 500 PIT fixture (external membership history)
python -m new_pipeline.scripts.build_pit_universe --history-file <membership.csv>

# ---- backtests / gauntlet ---------------------------------------------------
curl -X POST localhost:8000/api/runs -H 'Content-Type: application/json' \
     --data @new_pipeline/config/champion_run_body.json      # official frozen run
# ad-hoc experiment: same body with ONE overrides field changed = one variable

# ---- promotion & paper trading ---------------------------------------------
python -m new_pipeline.scripts.promote_candidates --run-dir <runs>/<id>/output \
    --key "Universe Long Short" --all-sectors                # or POST /api/runs/{id}/promote
python -m new_pipeline.scripts.paper_trade_book              # dry-run (prints orders)
python -m new_pipeline.scripts.paper_trade_book --execute    # submit to paper account
python -m new_pipeline.main trade                            # sector-model trade-graph replay
python -m new_pipeline.scripts.live_preflight                # broker/data connectivity check
python -m new_pipeline.scripts.live_smoke --symbol AAPL --qty 1   # 1-share paper round-trip

# ---- tests ------------------------------------------------------------------
NUMBA_DISABLE_JIT=1 python -m pytest new_pipeline/tests --cov=new_pipeline
```

## Updating the frozen champion (when a better model appears)

The freeze exists so forward data is confirmatory, not curated. The protocol:

1. **A challenger earns it in-registry.** Run the candidate spec as a variant
   column inside the standing factorial (deflation prices the selection), or
   as its own one-variable run. It must beat the incumbent on the gates —
   ideally `promoted: true` outright; at minimum a strictly better verdict
   under identical windows and costs. A better-looking net Sharpe alone is
   not evidence (run-to-run bar refetches wobble column Sharpes ±0.02-0.1;
   the gate verdicts are the stable object).
2. **Re-freeze in one commit** touching three places so they can never drift:
   `config/champion_run_body.json` (the new spec), `config/CHAMPION.md`
   (run id, numbers, what changed and why), and the `long_short` block in
   `config/defaults.yaml`/`schema.py` if book-construction values moved.
3. **Restart the forward clock.** The new spec's forward test starts at its
   freeze date; prior forward evidence belongs to the old spec. Note the
   supersession in CHAMPION.md rather than deleting history.
4. **Re-deploy paper trading** against the new run's artifacts:
   `promote_candidates --run-dir <new_run>/output --key "Universe Long Short"
   --all-sectors`, then delete `models/prod/book_state.json` so band/vol
   state re-seeds cleanly on the next executor run.

Never edit the frozen body between runs "just to try something" — that is a
new experiment and belongs in an ad-hoc run body, not the champion file.

## Live paper testing the champion

Deployment is a **human decision layered on top of the honest registry** —
gate rows are never rewritten; manual promotions append explicitly-marked
`MANUAL OVERRIDE` rows to the production registry.

```bash
python -m new_pipeline.scripts.promote_candidates \
    --run-dir <runs>/<run_id>/output --key "Universe Long Short" --all-sectors
python -m new_pipeline.scripts.paper_trade_book              # dry-run first
python -m new_pipeline.scripts.paper_trade_book --execute    # daily, ~30 min before close
```

The executor scores every universe name with its sector's deployed booster
(the standard train/serve approximation of the backtest's out-of-sample
bagged scores), applies the frozen book mechanics (5d smoothing, sector
z-scores, global quantile cliff with exit-band hysteresis, rolling-252
calm-state policy, causal 5% vol target, 5-day rebalance grid; state carried
in `models/prod/book_state.json`), reconciles against live Alpaca paper
positions, and submits market-order diffs. It hard-refuses non-paper keys and
always constructs the broker with `paper=True`. Per-sector threshold models
can additionally be replayed through the trade-graph runner
(`new_pipeline/execution/runner.py`), which skips book-level champions.

## Intraday stack (small/mid-cap ORB v1)

A sibling product line under `new_pipeline/intraday/`: minutes-scale,
always flat by the EXCHANGE close (early closes honored via the committed
session calendar), long-only opening range breakout on a hybrid universe
(liquidity-filtered extended-cap base + a causal-at-open daily scanner).
It rides the same honest gauntlet on per-session returns — deflated DSR
with N_eff over the 12-combo trial family, CSCV PBO, the family-wise
per-regime HMM gate, and a TIMING null (same picks, random entry minutes,
identical range-derived exits and spread-dominated costs) in the standard
`synthetic_sharpe` slot. Promotion key: `"Intraday ORB"`.

```bash
# one-time: session calendar fixture (committed) + minute-bar vault (resumable)
python -m new_pipeline.scripts.ingest_minute_vault --refresh-calendar
python -m new_pipeline.scripts.ingest_minute_vault --start 2024-08 --end 2026-08

# official backtest through the gauntlet
python -m new_pipeline.intraday.run --start 2024-09-01 --end 2026-07-31

# paper session runner (bare-metal host only; dry-run default)
python -m new_pipeline.scripts.intraday_paper_session            # plan
python -m new_pipeline.scripts.intraday_paper_session --execute  # trade one session
```

The paper runner trades ONLY through dedicated keys
(`QA_ALPACA_INTRADAY__API_KEY/SECRET_KEY`, PK-prefixed) and refuses to run
if they are missing or identical to the daily book's keys — the two live
books never share an account, margin, or day-trade counts. It requires an
active `"Intraday ORB"` promotion in the registry, submits bracket orders
(server-side stop/target legs), and must live on a persistent host: a
reclaimable research container cannot hold a 6.5-hour session loop.

## Repository map

| Path | What lives there |
|---|---|
| `new_pipeline/tournament/` | CPCV grid, sector tournament, L/S book + variant factorials, gates wiring |
| `new_pipeline/evaluation/` | DSR/PBO/PSR/reality-check, family-wise per-regime gate, promotion registry |
| `new_pipeline/features/` | price/factor/event/short-flow feature families |
| `new_pipeline/data/` + `scripts/ingest_*` | PIT universes, EDGAR/GDELT/FINRA vault builders (resumable) |
| `new_pipeline/scripts/` | universe builder, ingests, `promote_candidates`, `paper_trade_book` |
| `new_pipeline/api/` + `app/` | FastAPI backend + React dashboard (runs, analytics, promotion gates) |
| `new_pipeline/hardening/` | Dockerfiles (incl. GPU), compose, K8s manifests, CI images |
| `new_pipeline/config/` | schema + defaults (champion values), `champion_run_body.json`, `CHAMPION.md` |
