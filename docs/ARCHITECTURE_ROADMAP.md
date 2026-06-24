# Quantum Avenger — Architecture & Current State

## Context

Quantum Avenger is a hybrid **LLM + ML quantitative trading system**: unstructured data (news/filings) flows through an LLM for sentiment/verdict, while structured market data runs through a rigorous, vectorized quant pipeline (technical + microstructure features, CPCV backtesting, an XGBoost alpha model, a hard‑coded risk "Shield Agent"), with promotion gated by statistical significance, a Streamlit dashboard, and live paper‑trading via Alpaca.

**Status (this document supersedes the original "plan only" framing).** Phases 1–6 are **implemented and offline‑operational** in `new_pipeline/` — the whole chain runs with no network, fully seeded and deterministic, behind adapter interfaces with deterministic fakes. The statistical‑evaluation and leakage‑hygiene layer has been hardened well past the original spec (triple‑barrier labels, span/ticker‑aware purged CPCV with combinatorial backtest paths, sample‑uniqueness weighting, causal feature selection, a path‑distribution Deflated‑Sharpe gate, a golden‑file harness). What remains is **live integration** (the Ollama LLM client, plus validating the Alpaca/GDELT/EDGAR/FinBERT/spaCy adapters on a networked host), the **agentic‑RAG evidence loop + a real embedder**, **monitoring/alert backends**, and **Phase 7 production hardening**.

- **Test posture:** ~115 modules under `new_pipeline/`; **333 tests** (330 pass, 3 skipped on optional `torch`/`spaCy`/`alpaca` + 1 GPU), **~93 % branch coverage**, `ruff` clean (E/F/I/W/B/UP), reproducible under a single seed.

**Document map (source of truth).** This file is the current‑state architecture. Its companions: **`quantitative_math.md`** — the math/rigor reference (labels, CPCV, weighting, causal selection, the DSR/PBO/haircut/MinBTL/per‑regime/path‑DSR stack); **`IMPLEMENTATION_STATUS.md`** — the maturity matrix + detailed remaining work + definition of done. `ROADMAP_2026.md` (module/API + diagrams) and `FULL_SYSTEM_INTEGRATION_GUIDE.md` (operational contracts) are supporting references; `PHASE_1..7_SPECIFICATION.md` are the original build specs (historical — each carries a current status banner).

**Two standing decisions (unchanged):**
- **Compute:** **target a CUDA GPU directly** as the production runtime (`@cuda.jit`, CuPy, XGBoost `device='cuda'`). CPU fallback is one branch away and is the default in this CPU‑only sandbox; GPU paths are written but exercised on a real GPU box / skipped in CI.
- **Integrations:** the dev/sandbox is **fully offline** — every external dependency (LLM, broker, market data/news, universe, sentiment, anonymizer) sits behind an **adapter interface + deterministic fake/fixture**, so the whole system is unit‑testable with no network. Live clients are wired in behind the identical interface.

---

## Guiding principles

| # | Principle | Implication | Realized in |
|---|-----------|-------------|-------------|
| G1 | Deterministic ↔ probabilistic isolation | LLM never does math. Quant calcs are deterministic tools; a Shield Agent + Grader can veto any LLM verdict. | `execution/mcp_tools.py`, `execution/grader.py`, `features/shields.py` |
| G2 | Vectorization first | Polars lazy‑frames + Numba/CUDA kernels; no `iterrows()`; batch `predict`. | `features/polars_engine.py`, `features/gpu_kernels.py` |
| G3 | GPU is the production target | `@cuda.jit` kernels, XGBoost `device='cuda'`/`hist`, `ExtMemQuantileDMatrix`; CPU fallback. | `features/gpu_kernels.py`, `tournament/trainer.py`, `tournament/data_iterator.py` |
| G4 | External = adapter + fake | LLM/broker/market/news/universe/sentiment are ABCs with offline fakes; every path testable with no network. | `adapters/`, `execution/broker.py` |
| G5 | Backtesting hygiene | Purge before feature compute; **CPCV span/ticker purge + embargo**; asymmetric loss; survivorship‑safe universe; t+1 simulation; **no in‑sample feature selection**; **non‑IID label weighting**. | `tournament/cpcv.py`, `tournament/sample_weights.py`, `tournament/simulator.py` |
| G6 | Reproducibility | One `core/seeding.py::seed_everything(seed)`; **golden‑file tests pin every quant formula**. | `core/seeding.py`, `tests/golden/` |

**Central invariant (realized).** The Shield Agent `evaluate_risk_veto_gates(...)` is **one** Numba function in `features/shields.py`, imported by three call sites — the t+1 backtest simulator (`tournament/simulator.py`), the LangGraph Risk‑Veto node (`execution/orchestrator.py`), and the MCP risk tool (`execution/mcp_tools.py`). Never re‑implemented. The asymmetric `sentiment_volatility_gate` lives beside it.

---

## Current architecture by subsystem

Legend: **✅ complete & tested** · **◐ offline‑complete, live deferred** · **○ scaffolded / placeholder**.

| Package | Status | What's there | Key files |
|---|---|---|---|
| `config/` | ✅ | Pydantic schema + `defaults.yaml`, real `development`/`testing`/`production` overlays layered under `QA_`‑prefixed env overrides. | `schema.py`, `base.py`, `{development,testing,production}.py` |
| `core/` | ✅ | 20+‑leaf exception hierarchy; JSON logging + `trace_id`; CLOSED/OPEN/HALF_OPEN circuit breaker; `seed_everything`. | `exceptions.py`, `logging.py`, `circuit_breaker.py`, `seeding.py` |
| `adapters/` | ◐ | Deterministic fakes (market/broker/LLM/sentiment/news) + `StaticUniverse`/`StaticNews` fixtures fully wired offline; live **Alpaca** (market/broker/news), **GDELT**/**EDGAR** PIT news, **FinBERT** sentiment, **spaCy** anonymizer are lazy‑imported, coverage‑omitted, and unit‑tested via mock injection. **Ollama LLM is not yet wired — the verdict path always uses `FakeLLMClient`.** | `fakes.py`, `factory.py`, `market_alpaca.py`, `news_{gdelt,edgar,static,composite}.py`, `sentiment_finbert.py`, `universe_static.py` |
| `data/` | ✅ | Out‑of‑core PyArrow vaults, ingestion, schema validation, psutil row‑group sizing, PIT news vault, causal sentiment feature builder, training DB. | `ingestion.py`, `vaults.py`, `validation.py`, `news_vault.py`, `sentiment_feature_builder.py` |
| `features/` | ✅ | Polars engine (returns, Wilder ATR, ADV20, vol√252, regime flag, spread, Amihud, NCSKEW, DUVOL); CUDA kernels + CPU fallback; 5‑gate Shield + sentiment‑vol gate; hydrodynamic slippage; rolling‑HMM regime + sentiment fusion; **triple‑barrier labels + `fwd_ret` + `label_t1_offset`**; feature registry; pandas compiler oracle. | `polars_engine.py`, `gpu_kernels.py`, `shields.py`, `slippage.py`, `markov_regime.py`, `regime_fusion.py`, `labels.py` |
| `tournament/` | ✅ | Combinatorial **CPCV** (span + ticker purge, fractional embargo, backtest paths); zero‑copy `ParquetDataIter`; asymmetric objective (+ sample weights); XGBoost trainer (GPU/CPU, early stopping, `sample_weight`); grid search → per‑combo CPCV paths; t+1 + block‑wise simulator; per‑sector director (thread‑parallel); **causal feature selection**; **uniqueness sample weights**. | `cpcv.py`, `grid_search.py`, `director.py`, `trainer.py`, `objectives.py`, `simulator.py`, `causal_selection.py`, `sample_weights.py`, `feature_selection.py` |
| `evaluation/` | ✅ | Deflated/Probabilistic Sharpe + MinTRL + N_eff; per‑regime DSR; HMM synthetic gauntlet (stationary block bootstrap); PBO via CSCV; MinBTL; Harvey‑Liu haircut SR; multi‑gate promotion + immutable registry; tearsheet. | `dsr.py`, `regime_dsr.py`, `hmm_gauntlet.py`, `pbo.py`, `cscv.py`, `minbtl.py`, `haircut.py`, `promotion.py` |
| `execution/` | ◐ | LangGraph `StateGraph` Verdict→Grader→Risk‑Veto(Shield)→Execute/Fallback (≤3 retries); deterministic MCP tools; verdict/grader via `LLMClient`; broker seam (Fake ✅ / Alpaca stub); append‑only veto ledger + trade log; gazetteer anonymizer (offline) + spaCy (live). **RAG engine uses a hashing‑bag embedder placeholder and the agentic evidence_for/against/missing loop is not yet in the graph.** | `orchestrator.py`, `mcp_tools.py`, `verdict_engine.py`, `grader.py`, `runner.py`, `veto_ledger.py`, `rag_engine.py` |
| `monitoring/` | ◐ | Streamlit multipage dashboard (live monitor, veto analysis, trade log, model registry, risk, settings) rendering from veto‑ledger/trade‑log parquet; KPI cards; Prometheus‑text telemetry formatter. **Metrics collector / health check are minimal; alert delivery (email/Slack/webhook) is stubbed; no live streaming.** | `dashboard/`, `metrics.py`, `health.py`, `telemetry.py` |
| `models/` | ◐ | Minimal in‑memory registry + metadata dataclass; the **durable** promotion registry lives in `evaluation/promotion.py`. | `registry.py`, `metadata.py` |
| `hardening/` | ○ | Only a chaos/load test exists; Docker/K8s/Terraform/CI/observability/secrets are Phase‑7 TODO. | `chaos/load_test.py` |
| `scripts/` | ✅ | `main.py` CLI (`pipeline`/`trade`/`show-config`/`init-vaults`/`health`); MCP server; training‑data + news‑vault ingestion; live paper smoke. | `main.py`, `scripts/serve_mcp.py`, `scripts/ingest_training_data.py`, `scripts/live_smoke.py` |

---

## Quantitative rigor (the differentiator)

The leakage‑hygiene, labelling, and multiple‑testing stack — all offline, deterministic, and golden‑pinned:

- **Labels** — López de Prado **triple‑barrier**: ATR‑scaled profit‑take / stop (the stop mirrors the simulator's `atr_stop_multiplier`) + a vertical/time barrier; first‑touch outcome, conservative same‑bar ties → stop. Emits the binary `target_label`, the continuous `fwd_ret`, and `label_t1_offset` (the per‑sample event span). Friction label retained as the no‑OHLC fallback. (`features/labels.py`)
- **Cross‑validation** — combinatorial **purged CPCV**: purge by the *actual* label span `t1` (getTrainTimes), **ticker/block‑aware** so spans and t+1 never cross a ticker boundary in the concatenated per‑sector matrix; fractional embargo; reconstructs the φ = C(N−1,k−1) combinatorial **backtest paths**. (`tournament/cpcv.py`, `grid_search.py`)
- **Sample weighting** — overlapping triple‑barrier labels are non‑IID, so training is weighted by **average uniqueness** (concurrency⁻¹ over each span), folded into the asymmetric objective's grad/hess; sequential‑bootstrap utility provided. (`tournament/sample_weights.py`, `objectives.py`)
- **Feature selection** — **causal** by default: a Granger directional screen (feature → `fwd_ret`, controlling for the target's own lags, overlap‑deflated, BHY‑FDR) → Ward‑cluster survivors → keep the best **purged‑CPCV MDA** feature per cluster. Correlational clustered‑permutation retained as an option/fallback. (`tournament/causal_selection.py`)
- **Significance gates** — Deflated Sharpe (with **N_eff** effective‑trials correction), PSR/MinTRL, **DSR across the CPCV paths** (a path‑pass‑fraction gate), PBO via CSCV, Harvey‑Liu haircut SR, MinBTL, and a per‑regime DSR gate; the HMM synthetic gauntlet now resamples features with a **stationary block bootstrap** (preserves cross‑feature *and* temporal autocorrelation). (`evaluation/`)
- **Simulation** — t+1 entry with ATR stop and risk‑based sizing, run **block‑wise per group and per ticker** so no trade's exit borrows a non‑adjacent bar. (`tournament/simulator.py`)
- **Determinism + golden harness** — `tests/golden/` pins ATR/vol/Amihud/slippage, Kelly + the 5‑gate Shield, DSR/PSR/MinTRL/haircut, CPCV folds, Granger/MDA, uniqueness/sequential‑bootstrap, and the gauntlet output to fixed numbers.

---

## Inter‑phase data contracts

- **Raw vault:** `date(ts), open, high, low, close(f64), volume(i64), ticker(str)`.
- **Processed feature‑vault:** `date, ticker, open, high, low, close, volume, returns, atr, adv_20, volatility, regime(i8), spread_pct, roll_spread, amihud, ncskew, duvol, sentiment_score, [markov_prob_persist_0/1 when fusion enabled], target_label, fwd_ret, label_t1_offset`. `target_label` is the **triple‑barrier** label.
- **Candidate artifacts** (under `models.candidate_models_dir`): `{sector}_candidate.json` (booster) · `{sector}_candidate_features.json` `{features:[...], metadata:{sector,params}}` · `{sector}_returns_matrix.parquet` (per‑combo OOS) · `{sector}_paths.parquet` (champion CPCV paths).
- **Promotion registry** (immutable JSON): `{"promotions":[{sector, dsr, synthetic_sharpe, pbo, psr, haircut_sharpe, cpcv_path_pass_fraction, cpcv_path_dsr_median, promoted, reason, timestamp, model_path}], "active_champions":{sector:model_path}}`.
- **Veto ledger:** `timestamp(ns), symbol, signal, entry_price, veto_reason, veto_gate∈{grader,shield,execution}, dsr, position_size, execution_id`. **Trade log:** `timestamp, symbol, side, qty, limit_price, status, order_id, fill_price, pnl`. **KPI dict:** `{equity, pnl, sharpe, max_drawdown, win_rate, profit_factor}`.
- **MCP tool:** JSON‑RPC 2.0 / stdio; typed scalars in → structured dict out. **Shield (central):** `evaluate_risk_veto_gates(entry_price, atr, atr_multiplier, account_capital, max_risk_pct, current_qty, adv_20, volume_today, volatility) -> (approved: bool, position_size: float)`.

---

## Configuration

`config/schema.py` + `defaults.yaml`, overlaid by `{development,testing,production}.yaml` (selected via `QA_ENV`), then `QA_`‑prefixed env vars. Live groups: **Data, Feature, Model, Execution, Logging, Fusion, GPU, Tournament, Evaluation, MCP, RAG, News, Dashboard, System, Alpaca.** Rigor‑relevant knobs:

- `features`: `label_horizon`, `label_cost_bps`, `label_method` (`triple_barrier`|`friction`), `label_pt_mult`, `label_sl_mult`; `slippage_constant`, `regime_percentile`, `max_slippage_bps`, `crash_window`.
- `tournament`: `n_groups`, `test_groups`, `purge_days`, `embargo_days`, `embargo_pct`, `penalty_fp/fn`, `feature_selection_method` (`causal` default | `clustered_permutation`), `causal_alpha`, `causal_granger_lags`, `sample_weighting` (`uniqueness` default | `none`), `tree_method`, `device`, `max_workers`.
- `evaluation`: `dsr_promotion_threshold` (0.95), `use_effective_trials`, `psr_benchmark_sr`, `pbo_threshold`, `pbo_partitions`, `mt_method` (`bhy`), `enforce_minbtl`, `regime_gate_enabled`, `min_regime_obs`, `thin_regime_policy`, `cpcv_path_gate_enabled` (true), `cpcv_path_min_fraction`, `gauntlet_block_size`.

**Dependencies** are split so the SessionStart hook installs only CPU‑runnable wheels: `requirements.txt` (runtime), `requirements-gpu.txt` (cupy/numba‑CUDA/XGBoost‑GPU), `requirements-fusion.txt` (torch/transformers/spaCy), `requirements-live.txt` (alpaca‑py/edgartools), `requirements-dev.txt`. Live/heavy modules are `coverage`‑omitted and `pytest.importorskip`‑gated.

---

## Remaining goals

1. **Live integrations.** Wire a real **Ollama** client behind `LLMClient` (verdict/grader currently always use the fake); validate the Alpaca market/broker/news, GDELT/EDGAR, FinBERT, and spaCy adapters on an allowlisted networked host (`scripts/live_smoke.py`, `scripts/ingest_training_data.py`).
2. **Agentic RAG.** Replace the hashing‑bag embedder with a real neural embedder + FAISS/BM25, and wire the **evidence_for / evidence_against / missing_evidence** retrieval loop into the orchestrator (today it is verdict → grader only; `rag_engine.retrieve()` is unused by the graph).
3. **Monitoring / ops.** Real `MetricsCollector` + health checks, telemetry → Prometheus, alert‑delivery backends (email/Slack/webhook), optional live streaming for the dashboard.
4. **Phase 7 hardening.** Docker (app/dashboard/mcp), K8s, Terraform; CI enforcing the **≥85 % coverage gate** + golden tests; GPU node images + nightly GPU↔CPU reconciliation; secrets via a manager; chaos/recovery playbooks.
5. **Deferred rigor refinements.** Cross‑sectional (same‑date, different‑ticker) leakage in pooled per‑sector CPCV; options‑mode payoff labels behind the same label interface; a nonlinear / causal‑discovery feature screen beyond linear Granger (e.g. transfer entropy); meta‑labelling on top of the triple‑barrier primary.

---

## Resolved decisions *(defaults the build runs with — overridable)*

1. **DSR threshold:** gate stays **DSR ≥ 0.95** (Bailey/López de Prado 95 % confidence); config‑driven (`evaluation.dsr_promotion_threshold`); a stricter `0.99` tier can gate live‑capital allocation later.
2. **Pandas compiler:** kept as a CPU reference oracle; the Polars engine is the default and is golden‑tested against it.
3. **Universe/sectors:** `adapters/universe_static.py` reads a checked‑in point‑in‑time membership fixture (`data/universe/membership.csv`) + aliases (`aliases.csv`) — offline & survivorship‑safe; a licensed PIT dataset drops into the same interface.
4. **`target_label` — UPDATED:** the friction‑aware label has been **superseded by the López de Prado triple‑barrier label** (ATR profit‑take/stop matching the execution stop + vertical barrier), which also emits `fwd_ret` and the `label_t1_offset` event span that CPCV purges on. Friction‑aware horizon‑return is retained as the no‑OHLC fallback. Options‑mode payoff stays deferred behind the label interface.
5. **XGBoost API:** XGBoost ≥ 2.0, `tree_method='hist'` + `device='cuda'` (CPU fallback `device='cpu'`).
6. **Live secrets:** `QA_`‑prefixed env vars via `config/production.py`; in Phase 7 sourced from K8s/secret‑manager mounts; dev/test use fakes regardless.
7. **CI:** ≥85 % coverage gate, CPU‑only runners with `@pytest.mark.gpu` skipped; GPU↔CPU reconciliation nightly/manual on a GPU box.

**New decisions taken since the original plan:**
8. **Causal feature selection is the default selector** (`feature_selection_method='causal'`); the correlational clustered‑permutation selector remains available and is the automatic fallback when a CPCV split is infeasible.
9. **Uniqueness sample‑weighting is on by default** (`sample_weighting='uniqueness'`); it degrades to unit weights for non‑overlapping labels, so weightless callers are unchanged.
10. **The CPCV path‑distribution DSR gate is on by default** (`cpcv_path_gate_enabled=true`): a candidate must clear the DSR threshold across a configurable fraction of its reconstructed backtest paths, not just the averaged path.
11. **CPCV purge is span‑ and ticker‑aware** (by `t1`, capped at ticker runs); the HMM gauntlet uses a **stationary block bootstrap** for feature resampling.

---

## Risks & mitigations

| Risk | Mitigation |
|------|-----------|
| GPU‑only paths untestable in CI | CPU fallback per kernel; `@pytest.mark.gpu` skip‑if‑no‑CUDA; CUDA deps out of the SessionStart hook |
| LLM/broker nondeterminism | adapters + deterministic fakes; `trace_id` replay; MCP forbids LLM math |
| Overfitting / false discovery | DSR + N_eff deflation, PBO/CSCV, haircut SR, MinBTL, per‑regime DSR, **path‑distribution DSR gate**, HMM gauntlet, immutable registry |
| Look‑ahead / leakage (legacy bug class) | purge‑before‑compute; **CPCV span + ticker purge + embargo w/ self‑validation**; **non‑IID uniqueness weighting**; block‑wise t+1 simulation; no in‑sample selection; survivorship‑safe universe; **golden‑pinned formulas** |
| Heavy‑dep/weight downloads fail offline | split runtime/gpu/fusion/live/dev reqs; lazy imports; coverage‑omit + importorskip; pre‑bake weights in Phase‑7 images |
| Shield re‑impl drift (3 call sites) | single `features/shields.py`; shared golden decision‑table test |
| Live integrations still stubbed | identical adapter interface; mock‑injected unit tests for each live adapter; live smoke script gated to an allowlisted host |

---

## Verification

- **Offline end‑to‑end (works today, no network):** `python new_pipeline/main.py pipeline` runs fixtures → features + triple‑barrier labels → per‑sector causal selection + CPCV grid search (uniqueness‑weighted) → DSR/PBO/haircut/per‑regime/path‑DSR promotion; `python new_pipeline/main.py trade` drives promoted champions through the LangGraph graph (FakeLLM/FakeBroker) → veto‑ledger/trade‑log parquet → dashboard renders.
- **Test suite:** `python -m pytest new_pipeline/tests` (333 tests; 3 skipped on optional deps); `ruff check new_pipeline`; `NUMBA_DISABLE_JIT=1 python -m pytest new_pipeline/tests --cov=new_pipeline --cov-fail-under=85`. `tests/golden/` pins every quant formula; live/heavy adapters are mock‑injection tested and coverage‑omitted.
- **Live cutover (later):** install `requirements-live.txt` / `requirements-fusion.txt` on a networked host, set `run_mode`/`fusion.enabled` + `QA_ALPACA__*` / `news.edgar_identity`, swap the fakes for the live adapters behind the identical interfaces, and validate with `scripts/live_smoke.py`.
