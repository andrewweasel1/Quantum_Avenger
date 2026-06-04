# Quantum Avenger — Architecture & Execution Roadmap (7 Phases)

## Context

Quantum Avenger is a hybrid **LLM + ML quantitative trading system**: unstructured data (news/filings) flows through an LLM for sentiment/verdict, while structured market data is run through a rigorous, vectorized quant pipeline (technical + microstructure features, CPCV backtesting, an XGBoost alpha model, a hard‑coded risk "Shield Agent"), with promotion gated by statistical significance, a Streamlit dashboard, and finally live paper‑trading via Alpaca.

**Why this plan exists.** The work so far stood up the project tooling (ruff, a web SessionStart hook, a `reference_code/` read‑only guardrail) and Phase 1 is ~85% built in `new_pipeline/`. The `docs/` specs define a full **7‑phase / ~16‑week** build, and `reference_code/` is a working‑but‑flawed legacy prototype ("Quantum Sentinel V6") that encodes the intended algorithms *and* a catalog of bugs we must not reproduce. Before writing more code, we need one agreed **architecture + sequencing map** so each phase has clear deliverables, contracts, and acceptance criteria.

**Scope of this deliverable (confirmed with user):** a **plan only — no implementation yet**, covering all 7 phases.

**Two further decisions (confirmed):**
- **Compute:** design to **target a CUDA GPU directly** as the production runtime (`@cuda.jit`, CuPy, XGBoost `device='cuda'`). CPU fallback only where it's one branch away. (This container is CPU‑only, so GPU paths are written but exercised on a real GPU box / skipped in CI.)
- **Integrations:** the dev/sandbox is **fully offline** — every external dependency (LLM, broker, market data/news, universe) sits behind an **adapter interface + deterministic fake/fixture**, so all 7 phases are unit‑testable with no network. Live clients are wired in later behind the identical interface.

**Intended outcome:** an approved roadmap we execute phase‑by‑phase, starting with closing Phase 1 + standing up the offline‑adapter/seeding foundation.

---

## Guiding principles

| # | Principle | Implication |
|---|-----------|-------------|
| G1 | Deterministic ↔ probabilistic isolation | LLM never does math. All quant calcs exposed as **FastMCP** JSON‑RPC tools; a deterministic Shield Agent + Grader can veto any LLM verdict. |
| G2 | Vectorization first | Polars lazy‑frames + Numba/CUDA kernels; **no `iterrows()`**; batch `predict`, never per‑row (both legacy bugs). |
| G3 | GPU is the production target | Real `@cuda.jit` kernels, CuPy buffers, XGBoost `device='cuda'` + `ExtMemQuantileDMatrix(cache_host_ratio=0.75)`. |
| G4 | External = adapter + fake | LLM, broker, market‑data, news, universe are ABCs with offline fakes. Every phase testable with no network. |
| G5 | Backtesting hygiene | Purge **before** feature compute; CPCV purge+embargo; asymmetric loss; survivorship‑safe universe; t+1 simulation; **no in‑sample feature selection**. |
| G6 | Reproducibility | One `core/seeding.py::seed_everything(seed)`; golden‑file tests pin every quant formula to fixed numbers. |

**Central invariant:** the Shield Agent `evaluate_risk_veto_gates(...)` is **one** Numba function in `features/shields.py`, imported by three call sites — the P3 t+1 backtest sim, the P5 LangGraph Risk‑Veto node, and a P5 MCP tool. Never re‑implemented.

---

## Target module layout (`new_pipeline/`)

`[reuse]` exists & solid · `[extend]` exists, must grow · `[NEW]` to create.

```
config/      schema.py[extend] base.py[reuse] defaults.yaml[extend]
             development.py/testing.py/production.py[extend: today all 3 are stubs returning get_config()]
core/        exceptions.py[extend 5→20+] logging.py[extend: JSON + trace_id] constants.py[reuse] paths.py[reuse]
             circuit_breaker.py[NEW] seeding.py[NEW]
adapters/    [NEW package — the offline seam]
             base.py(LLMClient, MarketDataSource, NewsSource, UniverseProvider ABCs)  fakes.py(deterministic fakes)
             llm_ollama.py  market_alpaca.py  broker_alpaca.py  universe_static.py   [live, wired P5+]
data/        base.py/ingestion.py/vaults.py/validation.py[reuse]   schemas.py[NEW: pyarrow vault schemas]
features/    base.py/registry.py/compiler.py[reuse: compiler=CPU fallback oracle]
             polars_engine.py[NEW P2]  gpu_kernels.py[NEW P2]  shields.py[NEW P2]  slippage.py[NEW P2]
models/      metadata.py/registry.py[reuse: P4 adds durable promotion registry]
tournament/  [NEW P3] cpcv.py data_iterator.py objectives.py trainer.py grid_search.py simulator.py
evaluation/  [NEW P4] dsr.py hmm_gauntlet.py promotion.py tearsheet.py
execution/   broker.py/risk.py[reuse]  mcp_server.py entity_anonymizer.py rag_engine.py
             verdict_engine.py grader.py orchestrator.py veto_ledger.py   [NEW P5]
monitoring/  health.py/metrics.py/telemetry.py[reuse/extend]  dashboard/[NEW P6: app.py, pages/, realtime.py, alerts.py]
hardening/   [NEW P7] docker/ k8s/ terraform/ ci/ observability/ chaos/ recovery/
utils/       decorators.py/retry.py/serialization.py/time.py[reuse]
scripts/     check_health.py[FIX broken import]
tests/       conftest.py/fixtures/[extend]  unit/ integration/[extend]  golden/[NEW]
```

**Adapter placement:** new top‑level `adapters/` holds the LLM/market/news/universe ABCs + fakes. **Exception:** `BrokerAdapter` already lives at `execution/broker.py` — keep it there; `adapters/broker_alpaca.py` and `adapters/fakes.py::FakeBroker` implement it (avoid two broker abstractions).

---

## Per‑phase roadmap

### Phase 1 — Core infra gap‑closure *(~85% done; quick low‑risk win)*
- `core/logging.py`[extend]: JSON formatter + `trace_id` contextvar (today: plain `%(asctime)s…` per `defaults.yaml`).
- `core/circuit_breaker.py`[NEW]: CLOSED/OPEN/HALF_OPEN, pairs with `utils/retry.py` + `utils/decorators.py::@retry`.
- `core/exceptions.py`[extend]: 5 → 20+ (per‑phase leaves: `ShieldVetoError`, `TournamentError`, `EvaluationError`, `MCPToolError`, `BrokerError`, …).
- `config/{development,testing,production}.py`[extend]: replace stubs with real overlays — a `QA_ENV` selector layering `{env}.yaml` **beneath** the existing `QA_`‑prefixed env overrides in `config/base.py`.
- `scripts/check_health.py`[FIX]: `from monitoring.health` → `from new_pipeline.monitoring.health`.
- Stand up `adapters/base.py` + `adapters/fakes.py` + `core/seeding.py` now (bakes in G4 + G6 before any quant code).
- **Acceptance:** structured JSON logs carry `trace_id`; 3 real env overlays; breaker unit‑tested; health script runs; coverage gate ≥85%; all 11 existing tests still pass.

### Phase 2 — Vectorized quant engine + Shield Agent
- `features/polars_engine.py`: `compute_returns`, `compute_atr`(Wilder), `compute_adv`(20d), `compute_rolling_volatility`(√252), `tag_volatility_regimes`(80th‑pct → `regime∈{0,1}`), `compute_spreads`→`spread_pct`, `compute_amihud_illiquidity`→`amihud`.
- `features/gpu_kernels.py`: `@cuda.jit` spreads / Amihud / NCSKEW / DUVOL + CuPy host wrappers + CPU fallback (guarded by `features.gpu_enabled`, already in config).
- `features/shields.py`: `@njit(fastmath=True) evaluate_risk_veto_gates(entry_price, atr, atr_multiplier, account_capital, max_risk_pct, current_qty, adv_20, volume_today, volatility) -> (approved: bool, position_size: float)` — 5 gates: stop validity, Kelly sizing, liquidity ≤25% ADV, slippage ≤50 bps, portfolio reconciliation; plus `calculate_kelly_position_size`, `enforce_volatility_stop`.
- `features/slippage.py`: `S = c·σ·√(Q/V)` (c≈0.5), `adjust_slippage_by_regime` (2× in high‑vol).
- **Reuse:** register features in `features/registry.py::feature_registry`; `execution/risk.py::RiskManager.compute_position_size` is the **golden oracle** for gate‑2.
- **Offline:** pure functions; golden vectors for ATR/vol/Amihud/slippage; Shield decision table.
- **Acceptance:** features match golden; Shield <100 µs benchmark; GPU≈CPU within tol (skip‑if‑no‑CUDA); **purge NaNs before compute**.

### Phase 3 — Tournament backtesting
- `tournament/cpcv.py`: `CPCVSplitGenerator(n_groups=6, purge_days=5, embargo_days=5)` → C(6,2)=15 folds; self‑validates no train/test overlap.
- `tournament/data_iterator.py`: `ParquetDataIter(xgb.DataIter)` zero‑copy.
- `tournament/objectives.py`: `asymmetric_financial_loss(preds, dtrain, penalty_fp=5.0, penalty_fn=1.0)` → grad/hess ×5 where `label==0`.
- `tournament/trainer.py`: `ExtMemQuantileDMatrix(iter, cache_host_ratio=0.75)`, `device='cuda'`, `tree_method='hist'` (CPU fallback `device='cpu'`).
- `tournament/grid_search.py` + `tournament/simulator.py` (t+1 sim calls the **P2 Shield**).
- **Artifacts out** (under `models.candidate_models_dir`): `{sector}_candidate.json`, `{sector}_candidate_features.json`, `returns_matrix.parquet`.
- **Reuse:** `models/metadata.py::ModelMetadata`; `data/schemas.py`; `core/seeding.py`.
- **Acceptance:** 15 folds w/ verified gaps; custom objective trains; reproducible under seed; **no in‑sample feature selection**.

### Phase 4 — Statistical evaluation / promotion
- `evaluation/dsr.py`: `compute_deflated_sharpe_ratio`, `expected_max_sr(var_trials, n_trials)` (Euler–Mascheroni ≈0.5772156649), `interpret_dsr`; deflation via skew γ₃ + kurtosis γ₄.
- `evaluation/hmm_gauntlet.py`: 3‑state `GaussianHMM(covariance_type='full')` → synthetic returns → **correlation‑preserving** feature bootstrap → infer → synthetic Sharpe > 0.
- `evaluation/promotion.py`: gate = `DSR ≥ dsr_promotion_threshold AND synthetic_sr > 0`; `PromotionRegistry` immutable JSON (`{promotions:[], active_champions:{}}`) into `models.prod_models_dir`.
- `evaluation/tearsheet.py`: quantstats HTML (optional dep).
- **Acceptance:** DSR matches golden; gate deterministic; registry append‑only. **Flag:** resolve the 0.95‑vs‑"99.5th‑percentile" label (Resolved decision #1).

### Phase 5 — Live execution / orchestration *(offline‑testable end‑to‑end)*
- `execution/mcp_server.py`: `FastMCP` exposing **30+ deterministic tools** (risk/feature/market/position) wrapping P2–P4 functions; stdio transport.
- `execution/entity_anonymizer.py`: spaCy `en_core_web_sm` NER masking ("Apple"→"[COMPANY_A]") + deanonymize.
- `execution/rag_engine.py`: late chunking + sentence‑transformers + Faiss + BM25.
- `execution/verdict_engine.py` + `grader.py`: LLM verdict + grader **via `LLMClient` adapter**.
- `execution/orchestrator.py`: LangGraph `StateGraph` Verdict→Grader→Risk‑Veto(Shield)→Execute/Fallback, ≤3 retries.
- `execution/veto_ledger.py`: append‑only parquet (9‑col schema below).
- **Reuse:** `features/shields.py` IS the Risk‑Veto node; `execution/broker.py::BrokerAdapter` is the broker seam (live = `adapters/broker_alpaca.py`, DAY‑TIF limit orders).
- **Offline (linchpin):** `FakeLLMClient` scripted verdicts/grades, `FakeBroker` records orders in memory, fake market/news fixtures → whole graph unit‑tested with no network.
- **Acceptance:** deterministic verdict→approve/veto→ledger row; MCP tools callable over stdio; LLM does no math.

### Phase 6 — Dashboard / monitoring
- `monitoring/dashboard/`: Streamlit multipage (live monitor, veto analysis, trade log, model registry, risk, settings); `realtime.py::RealtimeDataManager` reads veto‑ledger + trade‑log parquet; KPI cards (equity, P&L, Sharpe, drawdown, win rate, profit factor); `alerts.py`.
- **Reuse:** P4 `PromotionRegistry` for the registry page; `monitoring/metrics.py::MetricsCollector`.
- **Offline:** develop against fixture parquet from the P5 fake flow; snapshot‑test KPIs vs golden.
- **Acceptance:** all 6 pages render from fixtures; KPIs match golden; alerts fire on threshold breach.

### Phase 7 — Production hardening
- `hardening/`: Docker (app/dashboard/mcp), K8s, Terraform, CI/CD (lint + ≥85% coverage + golden tests), Prometheus+Grafana, chaos/load tests, secrets, recovery playbooks.
- **Reuse:** `core/circuit_breaker.py` + `utils/retry.py` in recovery; wire `monitoring/telemetry.py` (stub) to Prometheus; SessionStart‑hook pattern informs CI install.
- **GPU:** GPU base image + node selectors for trainer/feature service; CPU image for dashboard/MCP.
- **Acceptance:** images build; CI green w/ coverage gate; chaos/recovery documented; secrets never in repo.

---

## Inter‑phase data contracts *(define in `data/schemas.py` + JSON shapes)*

- **Raw vault** (P1→P2): `date(ts), open, high, low, close(f64), volume(i64), ticker(str)` — matches `compiler.py::_validate_dataframe`.
- **Processed feature‑vault** (P2→P3): `date, ticker, open, high, low, close, volume, returns, atr, adv_20, volatility, regime(i8), spread_pct, amihud, ncskew, duvol, sentiment_score, target_label`.
- **Candidate artifacts** (P3→P4): `{sector}_candidate.json` (booster) · `{sector}_candidate_features.json` `{features:[...], metadata:{sector,params,created_at}}` · `returns_matrix.parquet`.
- **Promotion registry** (P4→P5/P6): immutable `{"promotions":[{sector,model_path,dsr,synthetic_sr,timestamp}], "active_champions":{sector:model_path}}`.
- **Veto ledger** (P5→P6): `timestamp(ns), symbol, signal, entry_price(f64), veto_reason, veto_gate∈{grader,shield,execution}, dsr(f64), position_size(i32), execution_id`.
- **Trade log** (P5→P6): `timestamp, symbol, side, qty, limit_price, status, order_id, fill_price, pnl`.
- **KPI dict** (P6): `{equity, pnl, sharpe, max_drawdown, win_rate, profit_factor}`.
- **MCP tool** (P5): JSON‑RPC 2.0 / stdio; typed scalars in → structured dict out (e.g. slippage → `{slippage_bps, slippage_usd, approval, reasoning}`).
- **Shield Agent (central):** `evaluate_risk_veto_gates(entry_price, atr, atr_multiplier, account_capital, max_risk_pct, current_qty, adv_20, volume_today, volatility) -> (approved: bool, position_size: float)`.

---

## Cross‑cutting

**Config additions** (`config/schema.py` + `defaults.yaml`; current nests: Data/Feature/Model/Execution/Logging/Fusion/System — verified):

| Phase | Add |
|------|-----|
| P1 | `GPUConfig{device, fallback_to_cpu}` (consolidate w/ existing `features.gpu_enabled`); `LoggingConfig += json_logs, trace_enabled` |
| P2 | `FeatureConfig += slippage_constant(0.5), regime_percentile(80), bps_scaler(10000), max_slippage_bps(50)`; `ExecutionConfig += max_adv_coverage(0.25)` |
| P3 | `TournamentConfig{n_groups:6, purge_days:5, embargo_days:5, penalty_fp:5.0, penalty_fn:1.0, cache_host_ratio:0.75, tree_method:'hist', device:'cuda', sectors:[...]}` |
| P4 | `EvaluationConfig{dsr_promotion_threshold:0.95, hmm_states:3, hmm_n_iter:1000, synthetic_sr_min:0.0, registry_path}` |
| P5 | `MCPConfig{transport:'stdio'}`, `RAGConfig{embedder, faiss_index_path, top_k, chunk_size}`, `ExecutionConfig += ledger_dir, max_retries:3, tif:'day'`, `FusionConfig += verdict_model` (already has ollama_endpoint, semaphore_limit:20) |
| P6 | `DashboardConfig{trade_log_path, veto_ledger_path, refresh_seconds, alert_thresholds}` |
| P7 | `SystemConfig += env, prometheus_port` |

**Dependency phasing.** Today installed: `pydantic, pytest, pyyaml, numpy, pandas`. The SessionStart hook installs `requirements.txt` synchronously every web session, so split: `requirements.txt` (runtime CPU‑installable), `requirements-gpu.txt` (cupy / numba‑CUDA / XGBoost‑GPU — **not** in the hook), `requirements-dev.txt`.

| Phase | New deps |
|------|----------|
| P2 | `polars, numba, pyarrow` (GPU: `cupy`, numba‑CUDA) |
| P3 | `xgboost, scipy` (CPU wheel installs offline; `device='cuda'` runtime‑only) |
| P4 | `hmmlearn`, `quantstats`(optional) |
| P5 | `fastmcp, langgraph, spacy(+en_core_web_sm), sentence-transformers, faiss-cpu, rank-bm25, jsonschema`; live‑only: `alpaca-py`, Ollama client |
| P6 | `streamlit` |
| opt | `dask` (`system.dask_enabled` exists), `pandas_ta` |

**Seeding:** `core/seeding.py::seed_everything(seed)` for `random/numpy/torch` (xgboost/hmmlearn take per‑call `random_state` seeded from the same value), called at every entrypoint + test.

**Testing:** offline unit tests via `adapters/fakes.py`; `tests/golden/` pins ATR, vol√252, Amihud, slippage, asymmetric grad/hess, DSR, Kelly; `@pytest.mark.gpu` skip‑if‑no‑CUDA (assert CPU≈GPU); property tests for Shield invariants (never negative size; veto ⇒ size 0); coverage gate **≥85%**.

---

## Sequencing & milestones

```
P1 ─► P2 ─► P3 ─► P4 ─► P5 ─► P6 ─► P7
       │            ▲      ▲
       └── Shield ──┴──────┘   (P5 reuses P2 Shield; P5 MCP wraps P2/P3/P4)
adapters/+seeding (built in P1) ─► consumed by P2,P3,P5,P6
```
- **Parallel once P1 lands:** `adapters/`, `seeding`, `data/schemas`, `tests/golden`; within P2 the engine / shields+slippage / GPU kernels are 3 independent streams; P6 builds on fixtures before P5 live wiring.
- **Hard serial:** P3 needs P2 vault+Shield; P4 needs P3 returns_matrix; P5 Risk‑Veto needs P2 Shield.
- **Milestones:** M1 P1+adapters/seeding · M2 P2 (golden‑tested) · M3 P3+P4 (candidate→DSR→promotion on fixtures) · M4 P5 (offline graph+MCP+ledger) · M5 P6+P7.

**Recommended first increment after approval:** **finish P1 + stand up `adapters/base.py`, `adapters/fakes.py`, `core/seeding.py` together** — closes the near‑done phase for a quick win and lays the offline+determinism foundation every later phase tests against. Concretely: fix `check_health.py`, add JSON/trace_id logging, replace the 3 config‑overlay stubs, add the circuit breaker, land adapters/fakes/seeding.

---

## Resolved decisions *(answered; defaults the build runs with — overridable)*

1. **DSR threshold (P4):** Gate stays **DSR ≥ 0.95** (95% confidence — canonical Bailey/López de Prado; DSR is itself a probability). The docs' "99.5th percentile" is a wording error → read as "95th percentile / 95% confidence". Config‑driven (`evaluation.dsr_promotion_threshold: 0.95`); a stricter `0.99` "high‑conviction" tier can gate live‑capital allocation later.
2. **Pandas compiler (P2):** **Keep** `features/compiler.py` as a CPU reference oracle behind `FeatureConfig.engine='polars'|'pandas'`; the Polars engine is the default and is golden‑tested against it.
3. **Universe/sectors (P3):** `adapters/universe_static.py` implements a `UniverseProvider` interface fed by a checked‑in **point‑in‑time membership fixture** at `data/universe/membership.csv` (`ticker, gics_sector, start_date, end_date`) + a synthetic‑but‑realistic default spanning the **11 GICS sectors** (= `TournamentConfig.sectors`) — offline & survivorship‑safe by construction. **The one spot needing real production data later:** a licensed PIT membership dataset drops into the same interface, no code change.
4. **`target_label` (P2/P3):** **Friction‑aware equities label** — `1` if the t+1 forward return over `label_horizon` beats round‑trip cost (slippage + fees), else `0`; horizon + cost model config‑driven. Matches the Alpaca equities target and the 5× asymmetric loss (FP = trade that loses after costs). Options‑mode payoff deferred behind the same label interface as a future `RunMode`.
5. **XGBoost API (P3):** Target **XGBoost ≥ 2.0** with `tree_method='hist'` + `device='cuda'` (CPU fallback `device='cpu'`); the spec's `gpu_hist` is the deprecated pre‑2.0 spelling.
6. **Live secrets (P5/P7):** `QA_`‑prefixed **env vars** consumed by `config/production.py` (reusing the override path in `config/base.py`); in P7 sourced from K8s/secret‑manager mounts. Never committed; dev/test use fakes regardless.
7. **CI (P7):** **≥85% coverage gate**, **CPU‑only runners** with `@pytest.mark.gpu` always skipped in CI; GPU↔CPU reconciliation runs nightly/manual on a GPU box.

---

## Risks & mitigations

| Risk | Mitigation |
|------|-----------|
| GPU‑only paths untestable in CI | CPU fallback per kernel; `@pytest.mark.gpu` skip‑if‑no‑CUDA; CUDA deps out of the SessionStart hook |
| LLM/broker nondeterminism | adapters + deterministic fakes; trace_id replay; MCP forbids LLM math |
| Overfitting / false discovery | DSR deflation + HMM gauntlet + **both** promotion gates + immutable registry |
| Look‑ahead / leakage (legacy bug class) | purge‑before‑compute; CPCV purge+embargo w/ self‑validation; no in‑sample selection; survivorship‑safe universe; correlation‑preserving bootstrap |
| Heavy‑dep/weight downloads fail offline | split runtime/gpu/dev reqs; pre‑bake model weights in P7 images; mark download tests offline‑skip |
| Shield re‑impl drift (3 call sites) | single `features/shields.py`; shared golden decision‑table test |
| Scope/timeline (7 phases) | phase gates w/ acceptance + ≥85% coverage; parallelize adapters/P2 streams/P6‑on‑fixtures; ship M1 fast |

---

## Verification

This is a **plan**, so "verification" = the acceptance gates each phase must pass, plus how we'll validate the first increment when we execute it.

- **Per‑phase gates** are listed under each phase above; every phase ends green only when its golden/offline tests pass and coverage ≥85% (e.g., P2 Shield <100 µs + GPU≈CPU; P3 CPCV no‑overlap + reproducible under seed; P4 DSR matches golden + deterministic gate; P5 deterministic fake verdict→veto→ledger; P6 pages render from fixtures).
- **Cross‑phase:** golden‑file tests (`tests/golden/`) pin quant formulas; `@pytest.mark.gpu` reconciles GPU vs CPU on a real GPU box; the Shield decision‑table test is shared across its 3 call sites.
- **First‑increment validation (M1):** `python -m pytest new_pipeline/tests` stays green (existing + new); `python new_pipeline/scripts/check_health.py` runs; a structured log line shows JSON + `trace_id`; `QA_ENV=testing` selects the testing overlay; circuit‑breaker + seeding + fakes have unit tests; ruff clean.
- **End‑to‑end (later):** an **offline** dry run — fixtures → P2 features → P3 candidate → P4 promotion → P5 LangGraph (FakeLLM/FakeBroker) → veto‑ledger/trade‑log parquet → P6 dashboard renders — all with no network, fully seeded/reproducible. Live wiring (Ollama/Alpaca/market data) swaps fakes for real adapters at the P5/P7 cutover.
