# Quantum Avenger — Phased Execution Roadmap (historical, annotated)

> **Historical design checklist, annotated with current status.** This thematic 6‑phase outline predates implementation. The current source of truth is **`ARCHITECTURE_ROADMAP.md`** (architecture), **`IMPLEMENTATION_STATUS.md`** (status + remaining work), and **`quantitative_math.md`** (rigor). Status legend: **✅ done** · **◐ offline‑done, live deferred** · **○ deferred**.

## Phase 1: Environment & Out‑of‑Core Architecture — ✅
- ✅ `psutil` memory scaling + dynamically sized PyArrow Parquet vaults.
- ✅ `ParquetDataIter` zero‑copy streaming. *(Dask is optional/`system.dask_enabled`; market data via the adapter seam, not raw yfinance/RSS.)*

## Phase 2: Vectorized Quant Engine & Numba Shields — ✅
- ✅ Polars feature engine (volatility regimes, returns, ATR, ADV, spread, Amihud, NCSKEW/DUVOL); CUDA kernels with CPU fallback (CI default).
- ✅ Numba `@njit` Shield Agent (5 veto gates + asymmetric sentiment‑vol gate) + hydrodynamic slippage.

## Phase 3: NLP Anonymization & Throttled LLM Inference — ◐
- ✅ Entity anonymization: offline **gazetteer** default + live **spaCy** path.
- ○ **Ollama LLM not yet wired** — the verdict path uses `FakeLLMClient` (see IMPLEMENTATION_STATUS §1).
- ✅ `asyncio.Semaphore` throttle pattern (`execution/async_sentiment.py`).

## Phase 4: Machine Learning & Asymmetric Loss — ✅
- ✅ **Causal feature analysis** realized as the default selector (Granger directional screen + purged‑CPCV MDA), replacing associational correlation.
- ✅ Custom asymmetric financial‑loss objective (5× FP penalty) + sample‑uniqueness weighting folded into grad/hess.

## Phase 5: FastMCP Tooling & LangGraph Orchestration — ◐
- ✅ Deterministic quant functions exposed as MCP tools; LangGraph Verdict→Grader→Risk‑Veto→Execute state machine.
- ○ The full **Agentic‑RAG evidence loop** (real embedder + evidence_for/against/missing) is the remaining depth (IMPLEMENTATION_STATUS §2).

## Phase 6: Tournament Evaluation & Live Deployment — ◐
- ✅ HMM regime evaluator; **DSR ≥ 0.95** promotion — now part of a far larger gate stack (PSR/MinTRL/N_eff, PBO/CSCV, haircut, MinBTL, per‑regime DSR, **path‑distribution DSR gate**, block‑bootstrap gauntlet).
- ✅ Dashboard + PyArrow‑cached veto ledger — now the **React + FastAPI** app (`frontend/` + `new_pipeline/api/`); the Streamlit UI was built, then replaced (its data layer survives under `monitoring/dashboard/`).
- ◐ Alpaca live execution: adapters written + mock‑tested; **live cutover deferred** (IMPLEMENTATION_STATUS §3).
