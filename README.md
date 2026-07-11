# Quantum Avenger

A hybrid **LLM + ML quantitative trading system**. Structured market data runs
through a rigorous, vectorized quant pipeline — cross-sectional + microstructure
features, triple-barrier labels, span/ticker-purged combinatorial CPCV, an
XGBoost tournament with causal feature selection, and a deep multiple-testing
promotion gauntlet (Deflated Sharpe, PBO, haircut SR, path-distribution DSR,
reality check) — while unstructured news flows through an anonymize → sentiment
→ LLM verdict → grader → hard-coded risk "Shield" veto graph before any order
is placed. A **React + FastAPI dashboard** drives and monitors the engine.

Everything runs **offline by default** (deterministic fakes behind every
external seam, fully seeded), so the entire system is testable with no network
and no credentials.

## Quickstart

```bash
# Engine (Python 3.11)
make install                            # runtime + dev + api deps
python new_pipeline/main.py pipeline    # offline backtest -> promotion registry
python new_pipeline/main.py trade       # offline paper session on fakes

# Dashboard — API + built SPA on one origin
pip install -r new_pipeline/requirements-api.txt
python -m new_pipeline.api.app          # serves /api + frontend/dist at :8000

# Dashboard — frontend development (hot reload, proxies /api -> :8000)
cd frontend && npm install && npm run dev
```

Tests / lint (CI enforces all of these plus a frontend build and `pip-audit`):

```bash
ruff check new_pipeline
NUMBA_DISABLE_JIT=1 python -m pytest new_pipeline/tests --cov=new_pipeline --cov-fail-under=85
```

## Layout

| Path | What lives there |
|---|---|
| `new_pipeline/features/` | Polars feature engine, cross-sectional factors, extended families (frac-diff, range-vol, microstructure, GARCH), triple-barrier labels, the Shield risk gates |
| `new_pipeline/tournament/` | Purged CPCV, causal selection, XGBoost trainer, grid search, meta-labeling, stat-arb (Engle-Granger/Johansen/OU), per-sector director |
| `new_pipeline/evaluation/` | DSR/PSR/PBO/haircut/MinBTL/per-regime gates, IC/ICIR alpha eval, reality checks, the immutable promotion registry |
| `new_pipeline/portfolio/` | HRP/NCO/IC-weighted combination on RMT- or Ledoit-Wolf-denoised covariance |
| `new_pipeline/execution/` | LangGraph verdict→grader→Shield orchestrator, MCP tools, RAG engine, brokers, append-only ledgers |
| `new_pipeline/adapters/` | ABCs + deterministic fakes for every external service; lazy live impls (Alpaca, GDELT, EDGAR, FinBERT, spaCy) |
| `new_pipeline/api/` | FastAPI layer: config-schema introspection, subprocess-isolated runs, results parsing, monitor endpoints, bearer-token auth |
| `frontend/` | React + TypeScript + Tailwind/shadcn SPA: Overview, Analytics, Live Monitor, Engine Control |
| `new_pipeline/hardening/` | CI lives in `.github/workflows/`; Docker/K8s/observability templates |
| `docs/` | See the document map below |

## Documentation map

- **`docs/ARCHITECTURE_ROADMAP.md`** — current-state architecture (the source of truth).
- **`docs/IMPLEMENTATION_STATUS.md`** — maturity matrix + the phased remaining-work plan.
- **`docs/quantitative_math.md`** — every quant method with formulas, status tags, and file pointers.
- **`docs/OFFENSE_ROADMAP.md`** — how the signal-generation layers were sequenced.
- `docs/PHASE_1..7_SPECIFICATION.md`, `docs/ROADMAP_2026.md` — historical build specs.

## Security posture

Secrets are **env-only** (`QA_ALPACA__*`, `QA_API_TOKEN`, …) — never in config
files or the repo. The dashboard API ships with config-gated bearer-token auth
(`dashboard.auth_enabled` + `QA_API_TOKEN`, fail-closed). The LLM performs no
math: every quantity flows through deterministic tools and the Shield veto.
