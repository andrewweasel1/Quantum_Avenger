# Quantum Avenger — Implementation Status & Remaining Work

> **Where the project is, and exactly what remains to fully realize it.** Companion to `ARCHITECTURE_ROADMAP.md` (current‑state architecture) and `quantitative_math.md` (the rigor reference). The `PHASE_*_SPECIFICATION.md` files are the original build specs — historical; this doc + the roadmap are the current source of truth.

**Snapshot.** ~115 modules under `new_pipeline/`; **333 tests** (330 pass / 3 skip on optional `torch`/`spaCy`/`alpaca` + 1 GPU); **~93 % branch coverage**; `ruff` clean; fully seeded/deterministic. The whole pipeline runs **offline with no network** (`python new_pipeline/main.py pipeline` / `trade`). What remains is **live integration, the agentic‑RAG depth, monitoring backends, and Phase‑7 hardening** — not core quant logic.

---

## Maturity matrix

Legend: **✅ Stable** · **◐ Offline‑complete, live deferred** · **○ Scaffolded / placeholder** · **✗ Not started**

| Subsystem | Status | Notes |
|---|---|---|
| Config / core (exceptions, logging, circuit breaker, seeding) | ✅ | Pydantic schema + env overlays; JSON logs + `trace_id`; deterministic seeding. |
| Data layer (vaults, ingestion, validation, news vault, sentiment builder) | ✅ | Out‑of‑core PyArrow; PIT news vault; causal sentiment feature builder. |
| Feature engine (`features/`) | ✅ | Polars engine, Shield + slippage, markov/regime fusion, **triple‑barrier labels**. CUDA kernels present; **CPU fallback is what runs in CI** (GPU box deferred). |
| Tournament (`tournament/`) | ✅ | **Span/ticker purged CPCV + φ paths**, **causal feature selection**, **uniqueness weighting**, XGBoost trainer, block‑wise simulator, per‑sector director. |
| Evaluation (`evaluation/`) | ✅ | DSR/N_eff/PSR/MinTRL, per‑regime DSR, **block‑bootstrap gauntlet**, PBO/CSCV, haircut, MinBTL, **path‑distribution DSR gate**, immutable registry. |
| Execution graph (`execution/orchestrator.py`, `mcp_tools.py`, ledgers) | ◐ | LangGraph Verdict→Grader→Risk‑Veto→Execute wired; deterministic MCP tools; veto/trade ledgers. Runs on fakes. |
| LLM client | ○ | **`FakeLLMClient` only — no live LLM is wired** (Ollama config exists, unused). |
| RAG (`execution/rag_engine.py`) | ○ | Late‑chunk + BM25 + a **hashing‑bag embedder placeholder**; **`retrieve()` is not called by the graph** and the evidence_for/against/missing loop is not built. |
| Anonymizer | ◐ | Offline **gazetteer** anonymizer complete (`entity_anonymizer.py`); live **spaCy** path (`anonymizer_spacy.py`) lazy‑imported + mock‑tested. |
| Adapters — market/broker/news/sentiment | ◐ | Fakes + `StaticUniverse`/`StaticNews` fully wired; **Alpaca**, **GDELT**, **EDGAR**, **FinBERT**, **spaCy** lazy‑imported, coverage‑omitted, mock‑tested — **not yet exercised against the real services**. |
| Monitoring / dashboard (`monitoring/`) | ◐ | Streamlit multipage renders from fixture parquet; KPI cards; telemetry text formatter. **Metrics collector / health are minimal; alert delivery (email/Slack/webhook) is stubbed; no live streaming.** |
| Models registry (`models/`) | ◐ | Minimal; the durable promotion registry lives in `evaluation/promotion.py`. |
| Hardening (`hardening/`) | ✗ | Only a chaos/load test exists; Docker/K8s/Terraform/CI/observability/secrets not started. |

---

## Remaining work to reach the wholly‑realized system

### 1. Live LLM wiring — ○ → ◐  (Phase 5 cutover)
- **Task:** implement an `OllamaLLMClient(LLMClient)` (verdict/grader) behind the existing `adapters/base.py::LLMClient` ABC; select it in `adapters/factory.py` when `fusion.ollama_endpoint` is configured (today the factory always returns `FakeLLMClient`).
- **Reuse:** `FusionConfig.{ollama_endpoint, llm_model_name, verdict_model, semaphore_limit}`; the `asyncio.Semaphore` throttle pattern in `execution/async_sentiment.py`.
- **Acceptance:** an offline contract test with a mocked HTTP endpoint; the LangGraph verdict path runs end‑to‑end against a local Ollama on an allowlisted host; MCP still forbids the LLM doing math (G1).

### 2. Agentic RAG — ○ → ✅  (Phase 5 depth)
- **Task:** (a) replace the hashing‑bag embedder in `execution/rag_engine.py` with a real sentence‑transformer embedder behind a pluggable `embed` interface (FAISS + the existing BM25 for hybrid retrieval); (b) wire `rag_engine.retrieve()` into `execution/orchestrator.py` as a retrieval node, and have the verdict/grader evaluate **evidence_for / evidence_against / missing_evidence** (the roadmap's agentic loop).
- **Acceptance:** deterministic offline test with a fixture corpus (retrieval recall on a known query); orchestrator graph test showing the evidence fields populated and a grader retry on insufficient evidence.

### 3. Live data / broker / news validation — ◐ → ✅  (Phase 5/7 cutover)
- **Task:** exercise the already‑written live adapters against real services on an allowlisted host — `market_alpaca.py`, `broker_alpaca.py`, `news_alpaca.py` (paper account via `QA_ALPACA__*`), `news_gdelt.py` (keyless egress), `news_edgar.py` (`news.edgar_identity` + `edgartools`), `sentiment_finbert.py` + `anonymizer_spacy.py` (model downloads). Drivers exist: `scripts/live_smoke.py`, `scripts/ingest_training_data.py --news --news-vault`.
- **Acceptance:** a paper smoke run (account snapshot → tiny order → positions); a real PIT news vault materialized and read back identically; fusion run with non‑zero `sentiment_score`.

### 4. Monitoring / ops backends — ◐ → ✅  (Phase 6 completion)
- **Task:** a real `MetricsCollector` (time‑series/rolling windows) + non‑trivial health checks; wire `monitoring/telemetry.py` to a Prometheus exporter; implement alert‑delivery backends (email / Slack / webhook) behind `monitoring/dashboard/notifications.py`; optional live streaming for the dashboard.
- **Acceptance:** `/metrics` serves real counters; an alert fires and is delivered on a threshold breach in a test harness; dashboard pages render live KPIs.

### 5. Phase‑7 production hardening — ✗ → ✅
- **Task:** Dockerfiles (app / dashboard / MCP), K8s manifests + node selectors (GPU for trainer/feature, CPU for dashboard/MCP), Terraform, a CI pipeline enforcing **ruff + golden tests + ≥85 % coverage**, Prometheus/Grafana, secrets via a manager, chaos/recovery playbooks; a **nightly GPU↔CPU reconciliation** job asserting kernel parity.
- **Acceptance:** images build; CI green with the coverage gate; `@pytest.mark.gpu` parity passes on a GPU runner; secrets never in the repo.

### 6. GPU execution path — ◐ → ✅
- **Task:** validate the `@cuda.jit` kernels in `features/gpu_kernels.py` and the XGBoost `device='cuda'` / `ExtMemQuantileDMatrix` path on a real GPU box; keep the CPU fallback as the CI default.
- **Acceptance:** GPU≈CPU within tolerance on the golden vectors (skip‑if‑no‑CUDA); end‑to‑end run on GPU.

### 7. Deferred quantitative‑rigor refinements (research)
- **Cross‑sectional leakage:** the per‑sector matrix pools tickers, so same‑date / different‑ticker correlation is not addressed by time‑ordered CPCV — add a cross‑sectional purge or group‑by‑date scheme.
- **Options‑mode labels:** an options payoff label behind the same label interface as a future `RunMode` (the triple‑barrier interface already anticipates it).
- **Nonlinear causal screen:** a transfer‑entropy / causal‑discovery alternative to the linear Granger screen (the selector already keys off a `feature_selection_method` switch).
- **Meta‑labelling:** a secondary model sizing/filtering the triple‑barrier primary (the sequential bootstrap utility is already in place for bagged meta‑models).

---

## Definition of done (wholly‑realized system)

A networked deployment where: promoted champions trade a live **paper** Alpaca account through the LangGraph graph with a **live Ollama** verdict + **real RAG** evidence loop and a **spaCy/FinBERT** sentiment path; PIT news flows from GDELT/EDGAR into the sentiment vault; the dashboard renders **live** KPIs with **delivered** alerts; the whole thing is **containerized and CI‑gated** (ruff + golden + ≥85 % coverage) with Prometheus observability and nightly GPU↔CPU reconciliation — while every offline guarantee (determinism, the full leakage‑hygiene + multiple‑testing rigor stack, golden‑pinned formulas) still holds, because live clients only swap in behind the identical adapter interfaces.
