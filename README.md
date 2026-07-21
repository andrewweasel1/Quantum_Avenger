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
EDGAR vault ──┤   features/factors/events        └─ Universe L/S book (16-20
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

## Deploying to a live system (with GPU)

Container topology lives in `new_pipeline/hardening/`:

```bash
# CPU stack: API+dashboard, app, MCP, Prometheus
docker compose -f new_pipeline/hardening/docker/docker-compose.yml up -d --build

# GPU trainer image (host needs the NVIDIA container toolkit):
docker build -f new_pipeline/hardening/docker/Dockerfile.gpu -t quantum-avenger-gpu .
docker run --gpus all \
  -e QA_TOURNAMENT__DEVICE=cuda -e QA_GPU__CUDA_ENABLED=true \
  -e QA_ALPACA__API_KEY -e QA_ALPACA__SECRET_KEY \
  quantum-avenger-gpu pipeline
```

XGBoost picks up the GPU via `tournament.device=cuda`; CPU/GPU kernel parity
is asserted by the GPU-marked tests (`.github/workflows/nightly-gpu.yml`).

Kubernetes: apply `new_pipeline/hardening/k8s/` (`deployment.yaml`,
`api.yaml`, `configmap.yaml`, `hpa.yaml`, `networkpolicy.yaml`; put the
Alpaca pair in `secrets.yaml` via your secret manager — the committed file is
a template). The dashboard/API serves on the `api` service; runs execute as
isolated subprocesses inside the api pod, so size its requests accordingly.

## Live paper testing the champion

Deployment is a **human decision layered on top of the honest registry** —
gate rows are never rewritten; manual promotions append explicitly-marked
`MANUAL OVERRIDE` rows to the production registry.

```bash
# 1) promote the book + all 13 sector scorers out of a finished run
python -m new_pipeline.scripts.promote_candidates \
    --run-dir <runs>/<run_id>/output --key "Universe Long Short" --all-sectors
# (same thing over HTTP: POST /api/runs/{run_id}/promote
#  {"keys": ["Universe Long Short"], "all_sectors": true})

# 2) dry-run the daily book rebalance (prints the orders, submits nothing)
python -m new_pipeline.scripts.paper_trade_book

# 3) arm it for real, daily ~30 min before the close (cron/systemd timer)
python -m new_pipeline.scripts.paper_trade_book --execute
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
