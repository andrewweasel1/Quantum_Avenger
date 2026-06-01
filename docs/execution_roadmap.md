# Quantum Avenger: Phased Execution Roadmap

## Phase 1: Environment & Out-of-Core Architecture
- Initialize Dask distributed cluster and `psutil` memory scaling protocols.
- Build the data ingestion pipeline (via `yfinance` and RSS), saving structured outputs as dynamically sized PyArrow-backed Parquet files.
- Implement the `ParquetDataIter` for zero-copy machine learning data streaming.

## Phase 2: Vectorized Quant Engine & Numba Shields
- Write Polars/CuPy lazy-frames to compute dynamic rolling buffers (Volatility Regimes, Log-Price Trend Slopes).
- Build the `Numba` JIT-compiled Risk Manager (The Shield Agent) to execute microsecond veto gates evaluating position sizing and ATR stops.
- Calculate and integrate dynamic hydrodynamic slippage functions.

## Phase 3: NLP Anonymization & Throttled LLM Inference
- Construct the `spaCy` Entity Anonymization pipeline to strip tickers/names from all text.
- Configure local LLM inference via Ollama (`qwen3:30b-a3b` MoE or `qwen3:8b` depending on VRAM constraints).
- Implement `asyncio.Semaphore(20)` to throttle concurrent HTTP requests to the LLM during live tick loads.

## Phase 4: Machine Learning & Asymmetric Loss
- Train the structured data models (XGBoost) using Causal Factor Analysis to replace standard associational correlation.
- Implement a custom Asymmetric Financial Loss objective function within XGBoost to penalize false positives.

## Phase 5: FastMCP Tooling & LangGraph Orchestration
- Decorate the quantitative feature generation and risk evaluation functions with `@mcp.tool()`.
- Architect the LangGraph state machine, enforcing the Agentic RAG loop where the LLM evaluates `evidence_for`, `evidence_against`, and `missing_evidence`.

## Phase 6: Tournament Evaluation & Live Deployment
- Build the `QuantitativeEvaluator` using Hidden Markov Models (`hmmlearn`) for volatility regime switching.
- Enforce the Deflated Sharpe Ratio (DSR) logic: Models must pass a DSR > 0.95 minimum threshold to advance.
- Connect the validated pipeline to the Alpaca REST/WebSocket API for live execution.
- Map the telemetry outputs to a Streamlit dashboard featuring the PyArrow-cached Veto Ledger.
