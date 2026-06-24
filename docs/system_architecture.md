# Quantum Avenger — Architecture Primer

> **Primer only.** A one‑page orientation to the design. The authoritative current‑state architecture is **`ARCHITECTURE_ROADMAP.md`**; the math/rigor is in **`quantitative_math.md`**; remaining work is in **`IMPLEMENTATION_STATUS.md`**.

A local‑first, hybrid **LLM + ML** trading system whose organizing principle is **isolating deterministic quantitative math from probabilistic LLM reasoning** — the LLM never does math; it queries deterministic tools and is overruled by a hard‑coded risk gate.

## 1. Topology
- **Data layer:** market/news ingestion into out‑of‑core PyArrow Parquet vaults (`psutil`‑sized row groups); XGBoost streams via a zero‑copy `ParquetDataIter` (NVMe → VRAM).
- **Quant ML engine:** vectorized Polars/Numba(/CUDA) feature engine → triple‑barrier labels → span/ticker‑purged CPCV tournament → XGBoost alpha model.
- **Evaluation:** a deflated‑Sharpe / PBO / haircut / per‑regime / path‑distribution gate stack promotes only statistically significant champions.
- **LLM reasoning:** a verdict/grader pass behind an `LLMClient` adapter. *Today this is a deterministic `FakeLLMClient`; a live Ollama (Qwen) client is the planned cutover (see IMPLEMENTATION_STATUS §1).*
- **Bridge:** **FastMCP** exposes the deterministic quant functions as JSON‑RPC tools over stdio.
- **Orchestration:** a **LangGraph** state machine: Verdict → Grader → Risk‑Veto(Shield) → Execute/Fallback.

## 2. Out‑of‑core memory
All large datasets are processed out‑of‑core: `psutil`‑dynamic Parquet block sizes and a `ParquetDataIter` so training never materializes the whole vault. GPU is the production target (XGBoost `device='cuda'`, `@cuda.jit` kernels) with a CPU fallback that is the CI default.

## 3. LangGraph & FastMCP
The LLM is prohibited from executing raw math (principle G1). It reasons through tools: risk/feature/Sharpe/DSR calculators are deterministic MCP tools; a **Grader node** forces a retry or graceful fallback when a verdict lacks mathematical backing; local LLM calls are `asyncio.Semaphore`‑throttled. *The full Agentic‑RAG evidence loop (real embedder + evidence_for/against/missing) is the remaining depth — see IMPLEMENTATION_STATUS §2.*

## 4. Entity anonymization
News/filings are anonymized before the LLM so it can't memorize tickers (a look‑ahead risk). The **offline default is a deterministic gazetteer** anonymizer (`execution/entity_anonymizer.py`); a live **spaCy** NER path (`execution/anonymizer_spacy.py`) is lazy‑imported behind the fusion deps.

## 5. Execution & the Shield Agent (central invariant)
LLM verdicts never execute directly. Every trade passes the **Numba `@njit` Shield** — `features/shields.py::evaluate_risk_veto_gates`, **one** function imported by three call sites (the t+1 backtest simulator, the LangGraph Risk‑Veto node, the MCP risk tool), never re‑implemented. ATR‑stop and hydrodynamic‑slippage breaches deterministically block the trade and append to the immutable **veto ledger**.
