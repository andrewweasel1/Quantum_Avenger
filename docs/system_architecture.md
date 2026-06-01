# Quantum Avenger: System Architecture & Orchestration

## 1. High-Level Topology
The Quantum Avenger is a local-first, hybrid fusion trading system designed to isolate deterministic quantitative mathematics from probabilistic Large Language Model (LLM) reasoning. 

- **Data Layer:** Asynchronous tick/news ingestion routed into out-of-core Parquet files.
- **Quant ML Engine:** Highly vectorized Polars/CuPy buffers executing structural math and Machine Learning algorithms (XGBoost).
- **LLM Reasoning Engine:** A local quantized model (Qwen 3 MoE) running via Ollama.
- **Bridging Protocol:** FastMCP (Model Context Protocol) exposing the Quant ML Engine's deterministic outputs as JSON-RPC tools to the LLM.
- **Orchestration:** LangGraph state machine acting as the Agentic RAG coordinator.

## 2. Dask & PyArrow Memory Management
To operate on consumer hardware without Out-of-Memory (OOM) failures, all massive financial datasets must be processed out-of-core.
- Utilize `psutil` to dynamically allocate Parquet block sizes (64MiB for 16GB RAM, up to 256MiB for 64GB+ workstations).
- ML models (XGBoost) must train using `ParquetDataIter` (a zero-copy PyArrow iterator) to stream data directly from NVMe to VRAM.

## 3. LangGraph & FastMCP Integration
The LLM is strictly prohibited from executing raw math. It must reason using an Agentic RAG loop managed by LangGraph.
- **The Grader Node:** LangGraph evaluates the LLM's query. If the LLM generates a hypothesis without sufficient mathematical backing, the Grader Node forces a retry or triggers a graceful fallback.
- **FastMCP Tools:** Python risk metric calculators (e.g., drawdown, volatility) are decorated with `@mcp.tool()`. The LLM queries these tools over `stdio` and receives immutable structured data.
- **LLM Throttling:** Asynchronous local LLM calls must be wrapped in `asyncio.Semaphore(20)` to prevent the local Ollama instance from crashing under parallelized tick loads.

## 4. Entity Anonymization & NLP Pipeline
To prevent the LLM from relying on dataset memorization (look-ahead bias):
- All ingested text (news, 10-Ks) is parsed via `spaCy` NER (`en_core_web_sm`).
- Tradable entities are masked (e.g., "NVIDIA" becomes "[COMPANY A]") before entering the LLM Verdict Engine.
- **Late Chunking:** Financial documents must be embedded as a full context block first, then split, ensuring pronoun references to masked entities remain intact.

## 5. Execution & The Shield Agent
LLM verdicts (`Supported`, `Weakly Supported`, `Rejected`) do not execute trades directly.
- **The Veto Gate:** Trades pass through a `Numba` JIT-compiled (`fastmath=True`), CPU-parallelized Risk Manager.
- If volatility stops (ATR multipliers) or hydrodynamic slippage limits are breached, the trade is deterministically blocked and logged to the "Veto Ledger".
