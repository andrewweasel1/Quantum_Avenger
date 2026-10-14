# Quantum Avenger: Integrated Development Roadmap 2026

> **Status banner (read first).** This roadmap predates much of the implementation; keep it for its **function‑interaction matrices, system‑topology diagrams, backtesting‑hygiene checklist, and risk‑veto tables**, which remain useful references. For definitive current state use the source‑of‑truth trio: **`ARCHITECTURE_ROADMAP.md`** (architecture), **`quantitative_math.md`** (rigor), **`IMPLEMENTATION_STATUS.md`** (status + remaining work). Notable items this body predates and that are **now implemented**: triple‑barrier labels; span/ticker‑aware purged CPCV with combinatorial backtest paths; **causal** (Granger + purged‑CPCV‑MDA) feature selection as default; sample‑uniqueness weighting; the full evaluation stack (DSR/N_eff/PSR/MinTRL, PBO/CSCV, haircut, MinBTL, per‑regime DSR, **path‑distribution DSR gate**); the stationary‑block‑bootstrap HMM gauntlet; the **React + FastAPI dashboard** (the Streamlit UI this body describes was built, then replaced — its data layer survives under `monitoring/dashboard/`); and the GDELT/EDGAR/static news adapters. Still deferred: live Ollama LLM (fake today), the real RAG embedder + agentic evidence loop, monitoring/alert backends, and the deploy half of Phase‑7 hardening (CI is live).

## Executive Summary

The Quantum Avenger is a **hybrid fusion trading system** that combines:
- **Deterministic Quantitative ML**: Vectorized Polars/CuPy engines, XGBoost models, and Numba JIT risk managers
- **Probabilistic LLM Reasoning**: Local quantized Ollama models (Qwen 3 MoE) for unstructured text analysis
- **Production-Grade Orchestration**: LangGraph state machines with FastMCP tooling bridging the quant and LLM layers

This roadmap outlines the evolution from reference implementation → modular production pipeline with clear separation of concerns, comprehensive error handling, and explicit function-level documentation.

---

## Part 1: High-Level System Architecture

### 1.1 System Topology Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         QUANTUM AVENGER FUSION SYSTEM                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 0: DATA INGESTION & MEMORY ORCHESTRATION                    │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌──────────────────────┐  ┌─────────────────────────────────────┐ │   │
│  │  │  yfinance Client     │  │  psutil Hardware Profiler           │ │   │
│  │  │  (OHLCV Feeds)       │  │  (Dynamic Parquet Block Sizing)     │ │   │
│  │  └──────────────────────┘  └─────────────────────────────────────┘ │   │
│  │           ↓                              ↓                           │   │
│  │  ┌──────────────────────────────────────────────────────────────┐   │   │
│  │  │  Out-of-Core Parquet Vault (PyArrow)                        │   │   │
│  │  │  - 64MB blocks (16GB RAM)  → 256MB blocks (64GB+ RAM)       │   │   │
│  │  │  - Zero-copy memory mapping via memory_map                 │   │   │
│  │  │  - Row group striping for Dask lazy evaluation             │   │   │
│  │  └──────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 1: FEATURE ENGINEERING (VECTORIZED)                         │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌────────────────────┐      ┌─────────────────────────────────┐  │   │
│  │  │  CPU-Bound         │      │  GPU-Accelerated (CUDA)         │  │   │
│  │  │  Polars Lazy       │      │  Numba JIT Kernels              │  │   │
│  │  │  Frames            │      │  - Spread calculations          │  │   │
│  │  │  - Rolling ATR     │      │  - Amihud illiquidity           │  │   │
│  │  │  - Log returns     │      │  - Non-cash skewness (NCSKEW)   │  │   │
│  │  │  - ADV₂₀           │      │  - Down/Up Volume Asymmetry     │  │   │
│  │  │  - Volatility      │      │                                 │  │   │
│  │  └────────────────────┘      └─────────────────────────────────┘  │   │
│  │           ↓                              ↓                         │   │
│  │  ┌────────────────────────────────────────────────────────────┐   │   │
│  │  │  spaCy NER + Entity Anonymization                         │   │   │
│  │  │  Replace [ticker] → [COMPANY A] to prevent LLM memorization│   │   │
│  │  │  Late Chunking: Preserve pronoun context across splits    │   │   │
│  │  └────────────────────────────────────────────────────────────┘   │   │
│  │           ↓                                                        │   │
│  │  ┌────────────────────────────────────────────────────────────┐   │   │
│  │  │  LLM Sentiment Fusion (Ollama + Asyncio)                 │   │   │
│  │  │  - asyncio.Semaphore(20) throttles concurrent requests  │   │   │
│  │  │  - nest_asyncio prevents event loop collisions          │   │   │
│  │  │  - Outputs: sentiment_score ∈ [-1, +1]                 │   │   │
│  │  └────────────────────────────────────────────────────────────┘   │   │
│  │           ↓                                                        │   │
│  │  ┌────────────────────────────────────────────────────────────┐   │   │
│  │  │  Processed Feature Vault (Parquet, PyArrow Backed)        │   │   │
│  │  │  [OHLCV] + [TECHNICAL] + [MICROSTRUCTURE] + [SENTIMENT]  │   │   │
│  │  └────────────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 2: TOURNAMENT BACKTESTING & MODEL SELECTION                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  Combinatorial Purged K-Fold Cross-Validation (CPCV)      │    │   │
│  │  │  - 6-group splits, 2-group holdout, temporal purge        │    │   │
│  │  │  - Embargo window prevents lookahead bias                 │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │           ↓                                                        │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  XGBoost Training (ParquetDataIter + ExtMemQuantileDMatrix) │   │   │
│  │  │  - Asymmetric Financial Loss: Penalty(FP) = 5× Penalty(FN)│   │   │
│  │  │  - CUDA-accelerated tree boosting                         │    │   │
│  │  │  - Adaptive VRAM caching (cache_host_ratio=0.75)          │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │           ↓                                                        │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  Returns Simulation & Risk Manager (Numba @njit)          │    │   │
│  │  │  - Simulates position sizing via ATR stops               │    │   │
│  │  │  - Calculates OOS returns per fold                       │    │   │
│  │  │  - Accumulates trials matrix for DSR computation         │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │           ↓                                                        │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  Candidate Model Registry (JSON)                          │    │   │
│  │  │  - Sector-specific XGBoost boosters                       │    │   │
│  │  │  - Feature manifold metadata                             │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 3: STATISTICAL EVALUATION & MODEL PROMOTION                 │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  Deflated Sharpe Ratio (DSR) Computation                  │    │   │
│  │  │  - Bailey & Lopez de Prado framework                      │    │   │
│  │  │  - Adjusts for skewness, kurtosis, multiple testing bias  │    │   │
│  │  │  - Promotion threshold: DSR > 0.95 (99.5th percentile)   │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │           ↓                                                        │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  Synthetic Generalization via Hidden Markov Model        │    │   │
│  │  │  - Fits 3-state HMM to extract volatility regimes         │    │   │
│  │  │  - Generates Monte Carlo synthetic returns               │    │   │
│  │  │  - Applies champion model to unobserved data             │    │   │
│  │  │  - Verifies Sharpe Ratio > 0 (true alpha, not luck)     │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │           ↓                                                        │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  HTML Tearsheet Generation (quantstats)                  │    │   │
│  │  │  - Performance metrics, drawdown analysis, Calmar ratio  │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │           ↓                                                        │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  Champion Model Registry (JSON)                          │    │   │
│  │  │  - Promoted models ready for live execution             │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                         │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  LAYER 4: LIVE EXECUTION & THE SHIELD AGENT                        │   │
│  ├─────────────────────────────────────────────────────────────────────┤   │
│  │  ┌─────────────────────────┐        ┌──────────────────────────┐   │   │
│  │  │  Live Market Data Feed  │        │  Champion Model Loader   │   │   │
│  │  │  (Alpaca WebSocket)     │        │  (from Registry)         │   │   │
│  │  └─────────────────────────┘        └──────────────────────────┘   │   │
│  │             ↓                              ↓                        │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  Live Feature Compilation                                │    │   │
│  │  │  - Ingest live tick data                                 │    │   │
│  │  │  - Update rolling windows (ATR, volatility, ADV)        │    │   │
│  │  │  - Anonymize ticker & fetch live sentiment              │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │             ↓                                                       │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  XGBoost Inference (Probability → Trading Signal)        │    │   │
│  │  │  P(profit) > confidence_threshold? → YES/NO              │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │             ↓                                                       │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  *** THE SHIELD AGENT *** (Numba JIT + fastmath=True)   │    │   │
│  │  │  ┌──────────────────────────────────────────────────────┐ │    │   │
│  │  │  │  Risk Veto Gates (microseconds latency)             │ │    │   │
│  │  │  │  1. Position Sizing: risk = (entry - stop) / entry  │ │    │   │
│  │  │  │     size = (capital × max_risk%) / risk_distance    │ │    │   │
│  │  │  │  2. Stop Loss Validation: stop = entry - (2× ATR)   │ │    │   │
│  │  │  │  3. Slippage Check: s = c·σ·√(Q/V) ≤ 50 bps limit   │ │    │   │
│  │  │  │  4. Liquidity Check: ADV₂₀ > order_size             │ │    │   │
│  │  │  │  5. Portfolio Check: avoid recursive over-allocation │ │    │   │
│  │  │  │                                                      │ │    │   │
│  │  │  │  If ANY gate FAILS → VETO trade, log to ledger      │ │    │   │
│  │  │  └──────────────────────────────────────────────────────┘ │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │             ↓                                                       │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  Approved Trade Execution via Alpaca API                 │    │   │
│  │  │  - Dynamic Limit Order: limit = close + (0.1 × ATR)     │    │   │
│  │  │  - TimeInForce: DAY (prevents overnight ghost fills)    │    │   │
│  │  │  - Fills logged to PyArrow Veto Ledger                 │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  │             ↓                                                       │   │
│  │  ┌────────────────────────────────────────────────────────────┐    │   │
│  │  │  Telemetry Dashboard (Streamlit + PyArrow Cache)        │    │   │
│  │  │  - Veto Ledger (reasons for rejection)                  │    │   │
│  │  │  - P&L curve, drawdown timeline                         │    │   │
│  │  │  - Model confidence distribution                        │    │   │
│  │  └────────────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow & State Transitions

```
                    ┌──────────────────────────────────────────────────┐
                    │  CLI ENTRY POINT (main.py)                       │
                    │  argparse: --refresh-raw, --fusion, --evaluate, --live │
                    └──────────────────┬───────────────────────────────┘
                                       │
                      ┌────────────────┴────────────────┐
                      │                                 │
                ┌─────▼──────┐              ┌──────────▼──────┐
                │  PHASE 1   │              │     PHASE 2     │
                │ Data Prep  │              │   Tournament    │
                │ & Training │              │  & Evaluation   │
                └─────┬──────┘              └────────┬────────┘
                      │                             │
         ┌────────────┴──────────────┐             │
         │                           │             │
    ┌────▼──────┐          ┌────────▼──────┐   ┌──▼──────────────┐
    │ data_     │          │ feature_      │   │ tournament.py   │
    │ingestion  │          │compiler.py    │   │                │
    │.py        │          │               │   │ • ParquetDataIter
    │           │          │ • Polars lazy │   │ • Asymmetric loss
    │ • yfinance│          │ • CUDA Numba  │   │ • CPCV splits
    │ • Reuters │          │ • spaCy NER   │   │ • XGBoost train
    │ • Entity  │          │ • Ollama LLM  │   │ • Risk simulator
    │   mask    │          │ • Async batch │   │                │
    └────┬──────┘          └────────┬──────┘   └──┬──────────────┘
         │                          │             │
    ┌────▼─────────────────────────▼─────┐       │
    │  RAW_VAULT (Parquet files by sector)│       │
    │  uncleaned OHLCV + news            │       │
    └────┬─────────────────────────────────┘       │
         │                                        │
    ┌────▼──────────────────────────────────────┐ │
    │  PROCESSED_VAULT (feature matrix)         │ │
    │  [close, high, low, volume, ...]          │ │
    │  [atr, adv20, sentiment, ncskew, ...]     │ │
    │  All ready for ML consumption             │ │
    └────┬────────────────────────────────────┬─┘ │
         │                                    │   │
    ┌────▼──────────────────────────────────┐│   │
    │ TOURNAMENT_RESULTS (per sector)       ││   │
    │ • returns_matrix_[sector].parquet     ││   │
    │ • benchmark_[sector].parquet          ││   │
    │ • candidate_[sector].json (model)     ││   │
    │ • candidate_[sector]_features.json    ││   │
    └────────────────────────────────────────┘   │
                                                 │
                                       ┌─────────▼─────────────┐
                                       │   evaluator.py        │
                                       │                       │
                                       │ • Deflated SR (DSR)   │
                                       │ • HMM synthetic synth  │
                                       │ • Promotion gates     │
                                       │ • HTML tearsheets     │
                                       └─────────┬─────────────┘
                                                 │
                    ┌────────────────────────────┴────────────────────┐
                    │                                                 │
         ┌──────────▼────────────┐                    ┌──────────────▼────────┐
         │  DSR >= 0.95          │                    │  DSR < 0.95 OR        │
         │  AND                  │                    │  Synthetic SR < 0     │
         │  Synthetic SR > 0     │                    │                       │
         │                       │                    │  → REJECTED           │
         │  → PROMOTED           │                    │    (Return to tuning) │
         └──────────┬────────────┘                    └───────────────────────┘
                    │
         ┌──────────▼────────────────────────┐
         │ PROD_MODELS_DIR                   │
         │ • [sector]_champion.json          │
         │ • [sector]_champion_features.json │
         └──────────┬────────────────────────┘
                    │
              ┌─────▼──────┐
              │  PHASE 3   │
              │ Live Trade │
              └─────┬──────┘
                    │
           ┌────────▼─────────────┐
           │   live_trader.py     │
           │                      │
           │ • Alpaca client init │
           │ • Sync portfolio     │
           │ • Load champion      │
           │ • Live feature build │
           │ • XGBoost inference  │
           │ • Shield Agent veto  │
           │ • Execute orders     │
           │ • Ledger logging     │
           └────────┬─────────────┘
                    │
         ┌──────────▼───────────────┐
         │  LIVE EXECUTION LEDGER   │
         │  (PyArrow + Parquet)     │
         │  • Orders executed/veto'd │
         │  • P&L per trade         │
         │ • Veto reasons logged     │
         └──────────┬───────────────┘
                    │
         ┌──────────▼──────────────┐
         │  dashboard.py           │
         │  (Streamlit + Plotly)   │
         │                         │
         │ Visualize telemetry     │
         │ • Equity curve          │
         │ • Drawdown timeline     │
         │ • Win rate              │
         │ • Veto breakdown        │
         └─────────────────────────┘
```

---

## Part 2: Core Module Breakdown & Integration Points

### 2.1 **Module: data_ingestion.py** 
**Responsibility**: Fetch survivorship-adjusted market data and ingest into out-of-core Parquet vault.

#### Functions:

| Function | Input | Output | Internal Flow | Integration Points |
|----------|-------|--------|---------------|--------------------|
| `get_survivorship_adjusted_universe()` | None | `Dict[ticker: str, sector: str]` | 1. Fetch S&P 500 constituents from Wikipedia<br>2. Parse HTML table<br>3. Build ticker-sector mapping | Consumed by `build_raw_vault()` |
| `raw_vault_is_populated()` | None | `bool` | 1. Check if `RAW_VAULT_DIR` exists<br>2. List subdirs (one per sector)<br>3. Return True if count > 0 | Used in orchestration to skip re-download |
| `reset_raw_vault()` | None | None | 1. Delete existing `RAW_VAULT_DIR`<br>2. Recreate empty dir | Cleanup before fresh run |
| `fetch_point_in_time_news(ticker, dates)` | `ticker: str`<br>`dates: pd.DatetimeIndex` | `pd.DataFrame` | 1. Stub implementation (synthetic news)<br>2. Return DataFrame indexed by date<br>**FUTURE**: Hook Reuters/Bloomberg RSS | Populated if `config.FUSION_ENABLED=True` |
| `ingest_raw_ticker(ticker, sector)` | `ticker: str`<br>`sector: str` | `bool` | 1. Download 1D OHLCV via yfinance<br>2. Validate min 252 bars (1 year)<br>3. Fetch news if fusion enabled<br>4. Convert to PyArrow backend<br>5. Save to `RAW_VAULT_DIR/sector={sector}/{ticker}.parquet` | Called in ThreadPoolExecutor loop from `build_raw_vault()` |
| `build_raw_vault(universe_map)` | `Dict[ticker, sector]` | None | 1. Reset vault<br>2. ThreadPoolExecutor loop over universe<br>3. Call `ingest_raw_ticker()` per thread<br>4. Log success count | Final output feeds `feature_compiler.py` |

**Memory Management**: 
- PyArrow backend ensures zero-copy semantics when passing data to Dask
- ThreadPoolExecutor = `os.cpu_count()` workers, prevents I/O bottleneck

**Error Handling**:
- Graceful exception logging per ticker (failed ingestion skipped)
- Minimum bar validation prevents training on incomplete timeseries

**Improvements for `/new_pipeline/`**:
- Add entity resolution (handle ticker changes, mergers)
- Implement circuit breaker for API rate limits
- Add retry logic with exponential backoff
- Log data quality metrics (null %, duplicates, outliers)

---

### 2.2 **Module: feature_compiler.py** 
**Responsibility**: Vectorized feature engineering + LLM sentiment fusion + GPU kernel execution.

#### Core Functions:

| Function | Input | Output | Internal Flow | Integration Points |
|----------|-------|--------|---------------|--------------------|
| `fetch_sentiment_async()` | `semaphore, session, headline, ticker` | `float` ∈ [-1, +1] | 1. Anonymize ticker (e.g., "NVDA" → "the company")<br>2. Build Ollama payload<br>3. POST to localhost:11434/api/generate<br>4. Parse JSON response for sentiment_score<br>5. Return 0.0 on timeout/error | Called in batch from `process_llm_batch_async()` |
| `process_llm_batch_async()` | `df: pd.DataFrame` | `list[float]` | 1. Create asyncio.Semaphore(20) to throttle<br>2. Create aiohttp.TCPConnector(limit=20)<br>3. Gather all fetch_sentiment_async() coroutines<br>4. Return list of sentiments in order | Called per Dask partition in `compute_partition_features()` |
| `compute_partition_features()` | `df: pd.DataFrame` (Dask partition) | `pd.DataFrame` | **Step 1: Base CPU Analytics**<br>1. Lower column names<br>2. Compute log returns<br>3. Compute ATR (14-period)<br>4. Compute ADV₂₀<br><br>**Step 2: NaN Purge**<br>5. Drop NaN rows<br><br>**Step 3: LLM Fusion**<br>6. If FUSION_ENABLED, batch async LLM calls<br>7. Insert sentiment_score column<br><br>**Step 4: VRAM Staging**<br>8. Convert all numeric cols to C-contiguous arrays<br>9. Push to GPU (cuda.to_device)<br><br>**Step 5: GPU Kernel Execution**<br>10. Configure thread blocks (256 threads/block)<br>11. Launch kernels for NCSKEW, DUVOL, AMIHUD<br>12. Copy results back to CPU<br>13. Append to DataFrame | Mapped across all Dask partitions via `.apply()` |
| `compile_features_from_raw()` | None | None | 1. Read RAW_VAULT_DIR as Dask DataFrame<br>2. Repartition optimally<br>3. Map `compute_partition_features()` across partitions<br>4. Persist to PROCESSED_VAULT_DIR | Called after `build_raw_vault()` in orchestration |

**GPU Kernels** (Numba @cuda.jit):
- `kernel_spreads()`: High-low spread normalization
- `kernel_amihud()`: |return| / (volume × price) illiquidity metric
- `kernel_ncskew()`: Negative Cash Skewness (third central moment)
- `kernel_duvol()`: Down/Up Volume asymmetry ratio

**Async LLM Integration**:
- `nest_asyncio.apply()` prevents event loop collision when running inside Dask worker
- Semaphore(20) prevents local Ollama from queue overflow
- Entity anonymization blocks ticker memorization by LLM

**Improvements for `/new_pipeline/`**:
- Add explicit error handling for CUDA OOM
- Fallback to CPU if VRAM unavailable
- Add progress bar for feature compilation
- Cache feature metadata (dtype, nulls %) for monitoring

---

### 2.3 **Module: tournament.py** 
**Responsibility**: Tournament backtesting with CPCV, asymmetric loss XGBoost training, and candidate model registration.

#### Core Classes/Functions:

| Entity | Input | Output | Internal Logic | Integration |
|--------|-------|--------|-----------------|-------------|
| **ParquetDataIter** (class) | `file_path: str`<br>`features: List[str]`<br>`target_col: str` | Inherits `xgb.DataIter` | **next()**: Read row groups from Parquet sequentially<br>- Maintains iterator state (`self.it`)<br>- Returns 1 (success) or 0 (end)<br>- Zero-copy via PyArrow table selection<br><br>**reset()**: Rewind iterator to start | Fed directly to `xgb.ExtMemQuantileDMatrix()` for out-of-core training |
| `simulate_risk_manager_njit()` | `signals`, `closes`, `lows`, `atrs`, `atr_multiplier`, `max_risk_pct` | `returns: np.ndarray` | **Per timestamp i**:<br>1. If signal==1:<br>   - entry = closes[i]<br>   - stop = entry - (atr_multiplier × atrs[i])<br>   - risk_distance = (entry - stop) / entry<br>   - size = (max_risk_pct / risk_distance), capped at 1.0<br>2. If stop hit at i+1: return -risk_distance × size<br>3. Else: return % change × size | Returns matrix fed to DSR computation in `evaluator.py` |
| `asymmetric_financial_loss()` | `preds: np.ndarray`<br>`dtrain: xgb.DMatrix` | `(grad, hess)` tuple | 1. Extract labels from DMatrix<br>2. Convert logit preds to probability<br>3. Compute base logloss grad/hess<br>4. **Asymmetric scaling**:<br>   - If label==0 (negative, FP): multiply grad/hess × 5.0<br>   - If label==1 (positive, FN): multiply grad/hess × 1.0<br>5. Return modified grad/hess | Passed as `obj=asymmetric_financial_loss` to `xgb.train()` |
| **ModularTournamentDirector** (class) | None (init) | None | **Constructor**:<br>- Load PROCESSED_VAULT_DIR as Dask DataFrame<br>- Subset by sector | |
| | | | **generate_cpcv_splits()**:<br>1. Split df.index into n_groups<br>2. Generate all C(n_groups, test_groups) combos<br>3. Per combo, designate test indices<br>4. Apply purge_gap & embargo_gap to train set<br>5. Yield (train_df, test_df) tuples | Prevents look-ahead via temporal gaps |
| | | | **tune_sector_grid()**:<br>1. Compute sector_df = subset by sector<br>2. Skip if len < 1000<br>3. Build param grid (max_depth=[1,2], lr=[0.01,0.05])<br>4. Per param combo:<br>   a. Per CPCV fold:<br>      - Write train_df to temp Parquet<br>      - Construct ParquetDataIter<br>      - Create ExtMemQuantileDMatrix<br>      - Train XGBoost with asymmetric_financial_loss<br>      - Predict on test set<br>      - Simulate risk manager → OOS returns<br>   b. Calculate trial Sharpe<br>5. Select best_params (max Sharpe)<br>6. Save candidate model + features JSON | Results feed `evaluator.py` for DSR evaluation |
| | | | **execute_gauntlet()**:<br>1. Iterate sectors<br>2. Call tune_sector_grid() per sector | Main entry point called in orchestration |

**CPCV Logic** (Critical for preventing look-ahead):
```
n_groups = 6
test_groups = 2

Example split:
Indices:  [0...n]
Groups:   [0|1|2|3|4|5]  
Test:     [0|1]  → hold out groups 0&1
Train:    [2|3|4|5]  but remove dates adjacent to test window ± purge_gap

Next split:
Test:     [0|2]
Train:    [1|3|4|5] minus temporal boundaries
...
```

**Adaptive VRAM Caching**:
- `cache_host_ratio=0.75` forces XGBoost to keep 75% of histogram cache in RAM
- Prevents CUDA OOM on mid-range GPUs (6GB-8GB)

**Improvements for `/new_pipeline/`**:
- Add parallel sector processing (Dask-based grid search)
- Implement early stopping callback
- Add feature importance tracking
- Log model metadata (training time, convergence)

---

### 2.4 **Module: evaluator.py** 
**Responsibility**: Deflated Sharpe Ratio (DSR) computation, synthetic HMM validation, and model promotion.

#### Core Functions:

| Function | Input | Output | Internal Logic | Integration |
|----------|-------|--------|-----------------|-------------|
| `compute_deflated_sharpe_ratio()` | `trial_matrix: pd.DataFrame`<br>`champion_returns: pd.Series` | `float` ∈ [0, 1] (DSR percentile) | **Step 1: Base Sharpe**<br>1. champ_sr = mean(champ_ret) / std(champ_ret)<br>2. Compute skew, kurtosis (excess)<br><br>**Step 2: Trials Variance**<br>3. Compute Sharpe per trial column<br>4. var_trials = var(all trial SRs)<br>5. N = num trials<br><br>**Step 3: Expected Max Sharpe Under Null**<br>6. euler_mascheroni = 0.5772156649<br>7. expected_max_sr = √var_trials × [scale factor]<br><br>**Step 4: Deflation**<br>8. T = len(champion_returns)<br>9. denom = √(1 - skew×SR + (kurtosis-1)/4 × SR²)<br>10. dsr_stat = (champ_sr - expected_max_sr) × √(T-1) / denom<br>11. Return P(Z ≤ dsr_stat) via norm.cdf() | Tests if champion Sharpe exceeds multiple testing benchmark |
| `run_hmm_synthetic_gauntlet()` | `sector_name: str`<br>`benchmark_returns: pd.Series` | `float` (Synthetic Sharpe) | **Step 1: HMM Regime Fitting**<br>1. Reshape benchmark_returns → column vector<br>2. Fit 3-state GaussianHMM<br>3. Extract parameters (means, covariances, transitions)<br><br>**Step 2: Monte Carlo Synthesis**<br>4. Generate synthetic_returns of same length<br>5. This sequence has NEVER been seen by the model<br><br>**Step 3: Feature Bootstrap**<br>6. Sample historical feature rows with replacement<br>7. Create synthetic_df matching synthetic_returns length<br>8. Destroy chronological look-ahead bias<br><br>**Step 4: Model Inference**<br>9. Load champion booster from JSON<br>10. Predict on synthetic_df → probabilities<br>11. signals = (probs > threshold).astype(int)<br><br>**Step 5: Sharpe Calculation**<br>12. strategy_returns = signals × synthetic_returns<br>13. Return mean / std | Confirms model generalizes to unobserved return distributions |
| `assess_sector()` | `sector_name: str` | None | **Step 1: Load Results**<br>1. Read returns_matrix_{sector}.parquet<br>2. Read benchmark_{sector}.parquet<br><br>**Step 2: DSR Computation**<br>3. Call compute_deflated_sharpe_ratio()<br><br>**Step 3: Synthetic Validation**<br>4. Call run_hmm_synthetic_gauntlet()<br><br>**Step 4: Promotion Decision**<br>5. If DSR ≥ 0.95 AND synthetic_sr > 0:<br>   - Rename candidate_*.json → champion_*.json<br>   - Generate HTML tearsheet<br>6. Else:<br>   - Log rejection<br>   - Delete candidate files (optional)<br><br>**Step 5: Cleanup**<br>7. Delete temporary returns_matrix/benchmark parquets | Single entry point for per-sector evaluation |
| `run_evaluation_gauntlet()` | None | None | 1. Loop all glob("returns_matrix_*.parquet")<br>2. Extract sector_name<br>3. Call assess_sector() | Main orchestration entry point |

**Deflated Sharpe Ratio Interpretation**:
- DSR < 0.5: Model significantly underperforms random (likely overfit)
- 0.5 ≤ DSR < 0.95: Statistically insignificant (high FDR)
- DSR ≥ 0.95: Genuine alpha signal (99.5th percentile)

**HMM Synthetic Validation**:
- Extracts market **regimes** (not future returns)
- Generates returns that match regime statistics but are temporally novel
- Tests model's **predictive power** not its memory

**Improvements for `/new_pipeline/`**:
- Add parallel sector evaluation
- Implement confidence intervals around DSR
- Add detailed tearsheet comparisons (champion vs benchmark)
- Track promotion history/audit trail

---

### 2.5 **Module: live_trader.py** 
**Responsibility**: Live market execution with LLM sentiment + Shield Agent risk veto.

#### Core Functions/Classes:

| Entity | Input | Output | Internal Logic | Integration |
|--------|-------|--------|-----------------|-------------|
| `fetch_live_sentiment()` | `ticker: str` | `float` ∈ [-1, +1] | 1. If not FUSION_ENABLED: return 0.0<br>2. Build synthetic headline<br>3. Anonymize ticker<br>4. POST to Ollama<br>5. Parse JSON sentiment_score<br>6. On timeout: return 0.0 with warning | Called per candidate trade in execution loop |
| `evaluate_risk_veto_gates()` | `entry_price`, `atr`, `atr_multiplier`, `account_capital`, `max_risk_pct` | `(approved: bool, position_size: float)` | **Risk Calculation**:<br>1. stop_loss = entry - (atr_multiplier × atr)<br>2. risk_per_share = entry - stop_loss<br><br>**Position Sizing**:<br>3. capital_at_risk = account_capital × max_risk_pct<br>4. position_size = capital_at_risk / risk_per_share<br>5. max_shares = account_capital / entry_price<br>6. size = min(size, max_shares)<br>7. size = floor(size) [prevent fractional share issues]<br><br>**Veto Logic**:<br>8. If risk_per_share ≤ 0: return (False, 0)<br>9. If size < 1: return (False, 0)<br>10. Else: return (True, size) | Gateway between ML signal and execution |
| **LiveTradingSandbox** (class) | `is_paper: bool` | Instance | **Constructor**:<br>- Initialize Alpaca TradingClient<br>- Log initialization | |
| | | | **sync_portfolio_state()**:<br>1. GET /positions from Alpaca<br>2. Build dict {ticker: qty}<br>3. Return dict | Prevents over-allocation bugs |
| | | | **load_champion_model()**:<br>1. Read sector_name_champion.json (XGBoost booster)<br>2. Read sector_name_champion_features.json (feature list)<br>3. Return (booster, features) tuple | Loaded once at startup |
| | | | **execute_live_cycle()**:<br>1. Sync portfolio state<br>2. Get account buying power<br><br>**Per row in current_data**:<br>3. Extract ticker<br>4. Create DMatrix from feature set<br>5. Get XGBoost probability<br><br>6. If prob > threshold:<br>   a. Call evaluate_risk_veto_gates()<br>   b. If approved:<br>      - Calculate delta_qty<br>      - If delta > 0:<br>        • limit_price = close + (0.1 × atr)<br>        • Build LimitOrderRequest<br>        • Submit to Alpaca<br>        • Log to ledger<br>   c. If veto'd:<br>      - Log rejection reason<br>      - Skip trade | Main execution loop, runs every tick |

**Key Safety Features**:
- **Position Sizing**: Capital × max_risk% / risk_distance (kelly-like)
- **Stop Validation**: Must be 2×ATR below entry (microstructure spread)
- **Fractional Floor**: Prevents Alpaca API rejections
- **Portfolio Sync**: Checks current state to avoid over-allocation
- **Limit Orders**: Uses local ATR volatility for price protection (no market slippage)

**Improvements for `/new_pipeline/`**:
- Add order fill monitoring (tracked vs actual)
- Implement stop-loss monitoring during hold
- Add profit-taking logic (scale out)
- Detailed P&L tracking per position
- Risk decay monitoring (open position P&L)

---

### 2.6 **Module: dashboard.py** 
**Responsibility**: Streamlit telemetry dashboard for live monitoring.

#### Dashboard Architecture (✅ implemented in `new_pipeline/monitoring/dashboard/`; alert delivery still stubbed):
- **KPI Cards**: Win rate, Sharpe, Max drawdown, DSR
- **Equity Curve**: Interactive Plotly chart
- **Veto Ledger**: Table of rejected trades with reasons
- **Trade Log**: Executed trades with entry/exit/P&L
- **Model Registry**: Currently active champions per sector

**Integration Points**:
- Read ledger from PyArrow-backed Parquet files
- Refresh on new trade events
- Filter by date range / sector / veto reason

**Improvements for `/new_pipeline/`**:
- Real-time updates via Streamlit session state
- Risk curve decomposition (by sector)
- Feature importance heatmap for current champion
- A/B testing dashboard (compare champion vs candidate models)

---

## Part 3: Integration Mind Map

### 3.1 Data Propagation Flow

```
┌─ USER CLI ────────────────────────────────────────────────┐
│ python main.py --refresh-raw --fusion --evaluate --live   │
└──────────────┬──────────────────────────────────────────────┘
               │
    ┌──────────▼──────────────┐
    │   ORCHESTRATOR (main.py)│
    │   • Dask initialization │
    │   • Logging setup       │
    │   • Argparse routing    │
    └──────────┬──────────────┘
               │
    ┌──────────▼──────────────────────────────────────────────────────┐
    │ --refresh-raw: PHASE 1 Data Ingestion                          │
    ├──────────────────────────────────────────────────────────────────┤
    │                                                                   │
    │  data_ingestion.get_survivorship_adjusted_universe()            │
    │  ↓ → Dict[ticker, sector]                                       │
    │  ↓                                                               │
    │  data_ingestion.build_raw_vault()                               │
    │  ├─ ThreadPoolExecutor loop                                     │
    │  ├─ per ticker: ingest_raw_ticker()                             │
    │  │   ├─ yfinance.download() → OHLCV                             │
    │  │   ├─ fetch_point_in_time_news() → news_df (if FUSION_ENABLED)│
    │  │   ├─ Convert PyArrow backend                                 │
    │  │   └─ Save to RAW_VAULT_DIR/{sector}/{ticker}.parquet         │
    │  └─ Log success count                                           │
    │  ↓ → RAW_VAULT populated                                        │
    │  ↓                                                               │
    │  feature_compiler.compile_features_from_raw()                   │
    │  ├─ Load RAW_VAULT as Dask DataFrame                            │
    │  ├─ Repartition & map compute_partition_features() across      │
    │  │   ├─ Base CPU analytics (returns, ATR, ADV)                  │
    │  │   ├─ Drop NaN rows                                           │
    │  │   ├─ If FUSION_ENABLED:                                      │
    │  │   │   ├─ process_llm_batch_async()                           │
    │  │   │   ├─ asyncio.Semaphore(20) throttles                     │
    │  │   │   └─ Assign sentiment_score column                       │
    │  │   ├─ VRAM staging (contiguous arrays)                        │
    │  │   ├─ CUDA kernel launches (NCSKEW, DUVOL, AMIHUD)           │
    │  │   └─ Copy results back to CPU                                │
    │  ├─ Persist to PROCESSED_VAULT_DIR (Parquet)                   │
    │  └─ → PROCESSED_VAULT ready                                     │
    │  ↓                                                               │
    │  tournament.ModularTournamentDirector().execute_gauntlet()      │
    │  ├─ Load PROCESSED_VAULT as Dask DataFrame                      │
    │  ├─ Per sector: tune_sector_grid()                              │
    │  │   ├─ Iterate CPCV splits                                     │
    │  │   │   ├─ For each (train_df, test_df) pair:                  │
    │  │   │   ├─ Train ParquetDataIter (zero-copy)                   │
    │  │   │   ├─ XGBoost train with asymmetric_financial_loss       │
    │  │   │   ├─ Predict on test → signals                           │
    │  │   │   ├─ simulate_risk_manager_njit() → OOS returns         │
    │  │   │   └─ Accumulate to returns_matrix                        │
    │  │   └─ Select best params (max trial Sharpe)                   │
    │  │   └─ Save candidate model: {sector}_candidate.json           │
    │  └─ → PROD_MODELS_DIR populated with candidates                 │
    │                                                                   │
    └──────────────────────────────────────────────────────────────────┘
               │
    ┌──────────▼──────────────────────────────────────────────────────┐
    │ --evaluate: PHASE 2 Statistical Evaluation                      │
    ├──────────────────────────────────────────────────────────────────┤
    │                                                                   │
    │  evaluator.QuantitativeEvaluator().run_evaluation_gauntlet()     │
    │  ├─ Per candidate model:                                         │
    │  │   ├─ assess_sector(sector_name)                              │
    │  │   │   ├─ Load returns_matrix_{sector}.parquet                │
    │  │   │   ├─ Load benchmark_{sector}.parquet                     │
    │  │   │   ├─ compute_deflated_sharpe_ratio()                     │
    │  │   │   │   └─ Adjusts for skew, kurtosis, # trials            │
    │  │   │   ├─ run_hmm_synthetic_gauntlet()                        │
    │  │   │   │   ├─ Fit HMM to benchmark returns                    │
    │  │   │   │   ├─ Generate synthetic returns (unobserved regime)  │
    │  │   │   │   ├─ Bootstrap features (destroy temporal order)    │
    │  │   │   │   └─ Infer on synthetic → calculate Sharpe           │
    │  │   │   ├─ Decision logic:                                      │
    │  │   │   │   ├─ If DSR >= 0.95 AND synthetic_SR > 0:           │
    │  │   │   │   │   └─ PROMOTE: rename candidate → champion       │
    │  │   │   │   │       └─ Generate HTML tearsheet                  │
    │  │   │   │   └─ Else: REJECT (log reason)                       │
    │  │   │   └─ Cleanup temporary files                             │
    │  │   └─ → Champion models in PROD_MODELS_DIR                    │
    │                                                                   │
    └──────────────────────────────────────────────────────────────────┘
               │
    ┌──────────▼──────────────────────────────────────────────────────┐
    │ --live: PHASE 3 Live Execution                                  │
    ├──────────────────────────────────────────────────────────────────┤
    │                                                                   │
    │  live_trader.LiveTradingSandbox(is_paper=True)                   │
    │  ├─ Initialize Alpaca TradingClient                              │
    │  ├─ Sync portfolio state (GET /positions)                        │
    │  ├─ Load champion models from PROD_MODELS_DIR                    │
    │  │   └─ Per sector: booster + features list                      │
    │  ├─ execute_live_cycle(current_data)                             │
    │  │   └─ Per tick in current_data:                                │
    │  │       ├─ Extract features                                     │
    │  │       ├─ XGBoost inference → probability                      │
    │  │       ├─ If prob > threshold:                                 │
    │  │       │   ├─ evaluate_risk_veto_gates()                       │
    │  │       │   │   ├─ Position sizing (kelly-like)                 │
    │  │       │   │   ├─ Stop loss validation (2× ATR)                │
    │  │       │   │   └─ Return (approved: bool, size: float)        │
    │  │       │   ├─ If approved:                                     │
    │  │       │   │   ├─ Calculate delta from current inventory       │
    │  │       │   │   ├─ Build LimitOrderRequest                      │
    │  │       │   │   ├─ Submit to Alpaca API                         │
    │  │       │   │   └─ Log to PyArrow ledger                        │
    │  │       │   └─ If veto'd:                                       │
    │  │       │       └─ Log rejection reason to ledger                │
    │  │       └─ → Execution ledger updated                           │
    │                                                                   │
    │  dashboard.py (Streamlit)                                        │
    │  ├─ Read execution ledger (Parquet)                              │
    │  ├─ Display KPIs (win rate, Sharpe, Max DD)                      │
    │  ├─ Plot equity curve                                            │
    │  ├─ Table of veto reasons                                        │
    │  └─ → Real-time telemetry visible                                │
    │                                                                   │
    └──────────────────────────────────────────────────────────────────┘
```

---

## Part 4: Quantitative Rigor & Validation Checkpoints

### 4.1 Backtesting Hygiene Checklist

| Checkpoint | Reference Module | Implementation | Validation |
|------------|------------------|-----------------|------------|
| **No Look-Ahead Bias** | `tournament.py` | CPCV splits with temporal purge & embargo gaps | Verify: dates in train ≠ dates in test ± buffer |
| **Signal Shift t+1** | `tournament.py` `simulate_risk_manager_njit()` | Entry at closes[i], exit at closes[i+1] | Confirm: signals[i] applied to returns[i+1:] |
| **Dynamic Slippage** | `quantitative_math.md` | Implement in Shield Agent: s = c·σ·√(Q/V) | Monitor: slippage ≤ 50 bps limit enforced |
| **Asymmetric Loss** | `tournament.py` | Custom objective: Penalty(FP)=5×Penalty(FN) | Test: false positives penalized more heavily |
| **Out-of-Sample Validation** | `tournament.py` `evaluator.py` | Returns calculated only on test folds | Confirm: no train data in OOS metrics |
| **Synthetic Generalization** | `evaluator.py` | HMM regime synthesis + feature bootstrap | Verify: synthetic returns never seen before |
| **DSR ≥ 0.95 Gate** | `evaluator.py` | Strict threshold for model promotion | Audit: only champions with high DSR in production |
| **Confidence Interval** | `evaluator.py` | Compute DSR bounds (sklearn bootstrap if needed) | Log: uncertainty ranges in tearsheet |

### 4.2 Risk Management Veto Gates (Shield Agent)

| Gate | Formula | Threshold | Consequence |
|------|---------|-----------|-------------|
| **Stop Loss Validity** | stop = entry - (2×ATR) | stop > 0 | Reject if stop < 0 or entry invalid |
| **Position Sizing** | size = (capital × max_risk%) / (entry-stop) | max_risk% = 2% | Never exceed 2% per trade |
| **Account Equity** | position_qty = floor(capital / entry) | size ≤ account_qty | Reject if insufficient buying power |
| **Liquidity** | ADV₂₀ × price | ADV₂₀ > order_size | Never trade > 25% of daily volume |
| **Slippage Impact** | s = c·σ·√(Q/V) | s ≤ 50 bps | Reject if estimated slippage > 50 bps |
| **Volatility Anomaly** | σ > 80th percentile(σ history) | regime_flag = high_vol | Tighten stops or reduce size in spike |

---

## Part 5: Development Phases for `/new_pipeline/`

### Phase 1: Core Pipeline Infrastructure (Weeks 1-2)
**Deliverables:**
- [ ] Modular folder structure: `/new_pipeline/{data, features, models, execution, tests}`
- [ ] Configuration management (environment variables, YAML configs)
- [ ] Centralized logging & monitoring
- [ ] Unit tests for each module
- [ ] Error handling patterns & circuit breakers

**Reference Integration**: Study `/reference_code/data_ingestion.py` for API patterns, error handling

---

### Phase 2: Vectorized Feature Engine (Weeks 2-4)
**Deliverables:**
- [ ] Polars lazy-frame feature compilation (replace pandas)
- [ ] CUDA kernel improvements (faster NCSKEW, DUVOL)
- [ ] spaCy NER + Late Chunking implementation
- [ ] Async LLM throttling with better error recovery
- [ ] Feature caching & metadata tracking
- [ ] Performance benchmarks

**Reference Integration**: Study `/reference_code/feature_compiler.py` for async patterns, GPU kernels

---

### Phase 3: Tournament & Evaluation (Weeks 4-6)
**Deliverables:**
- [ ] Parallel sector grid search (Dask-based)
- [ ] DSR confidence intervals & detailed metrics
- [ ] HMM synthetic validation improvements
- [ ] Model registry with versioning
- [ ] Promotion audit trail (who/what/when)
- [ ] Rejection reason tracking

**Reference Integration**: Study `/reference_code/tournament.py` (CPCV, ParquetDataIter) and `/reference_code/evaluator.py` (DSR, HMM)

---

### Phase 4: Live Execution & Shield Agent (Weeks 6-8)
**Deliverables:**
- [ ] Refactored risk veto gates (more granular)
- [ ] Order fill tracking & monitoring
- [ ] Stop-loss enforcement during hold
- [ ] Profit-taking logic (scale out)
- [ ] Position reconciliation
- [ ] Detailed P&L per trade

**Reference Integration**: Study `/reference_code/live_trader.py` (Alpaca API patterns, risk gates)

---

### Phase 5: LangGraph Orchestration & FastMCP (Weeks 8-10)
**Deliverables:**
- [ ] FastMCP tool registration for all quant functions
- [ ] LangGraph state machine (Agentic RAG loop)
- [ ] Grader node for LLM verdict validation
- [ ] JSON-RPC bridging between LLM ↔ Quant engine
- [ ] Fallback logic if LLM unavailable
- [ ] End-to-end integration tests

**Reference Integration**: Architecture from `/docs/system_architecture.md` (LangGraph + FastMCP section)

---

### Phase 6: Dashboard & Monitoring (Weeks 10-12)
**Deliverables:**
- [ ] Streamlit dashboard with real-time updates
- [ ] Equity curve + drawdown visualization
- [ ] Veto ledger table with filtering
- [ ] Trade log with P&L decomposition
- [ ] Model registry dashboard
- [ ] Risk metrics heatmap by sector

**Reference Integration**: ✅ implemented — first as a Streamlit multipage app, since replaced by the **React + FastAPI dashboard** (`frontend/` + `new_pipeline/api/`); the pure data layer (`monitoring/dashboard/{realtime,views,alerts}.py`, reading the veto‑ledger / trade‑log Parquet) survives and serves the API's monitor routes, superseding the `/reference_code/dashboard.py` stub.

---

### Phase 7: Production Hardening & Testing (Weeks 12-16)
**Deliverables:**
- [ ] Stress tests (OOM simulation, rate limit handling)
- [ ] Integration tests (end-to-end data flow)
- [ ] Performance profiling (latency per component)
- [ ] Documentation (API reference, deployment guide)
- [ ] Version control & CI/CD pipeline
- [ ] Disaster recovery & rollback procedures

---

## Part 6: Function Interaction Matrix

```
                     ┌─────────────────────────────────────────────────────────────┐
                     │ FUNCTION INTERACTION DEPENDENCY GRAPH                      │
                     └─────────────────────────────────────────────────────────────┘

DATA LAYER
├─ get_survivorship_adjusted_universe()
│  └─> build_raw_vault() ─────────────────────────┐
│                                                  ▼
├─ ingest_raw_ticker() ──┐            compile_features_from_raw() ─────┐
│  └─ fetch_point_in_time_news()      └─ compute_partition_features()  │
│                                          ├─ process_llm_batch_async()  │
│                                          │  └─ fetch_sentiment_async()  │
│                                          ├─ CUDA kernels               │
│                                          │  ├─ kernel_spreads()        │
│                                          │  ├─ kernel_amihud()         │
│                                          │  └─ kernel_ncskew()         │
│                                          └─> PROCESSED_VAULT_DIR ──────────┐
│                                                                             ▼
TOURNAMENT LAYER
├─ ModularTournamentDirector.execute_gauntlet()
│  └─ tune_sector_grid() ──────┐
│     ├─ generate_cpcv_splits()│
│     ├─ ParquetDataIter()     │
│     ├─ asymmetric_financial_loss() ─┐
│     └─ simulate_risk_manager_njit() │
│        └─> returns_matrix ────────┤─────┐
│                                   │     ▼
EVALUATION LAYER                    │
├─ QuantitativeEvaluator.run_evaluation_gauntlet()
│  └─ assess_sector()  ◄─────────────┤
│     ├─ compute_deflated_sharpe_ratio()
│     └─ run_hmm_synthetic_gauntlet()
│        └─> PROD_MODELS_DIR (champions) ──────┐
│                                               ▼
EXECUTION LAYER
├─ LiveTradingSandbox.__init__()
│  └─ Alpaca TradingClient
│
├─ load_champion_model() ◄───────────────────────┘
│  └─> (booster, features)
│
├─ fetch_live_sentiment() ◄──┐
│  └─> sentiment_score        │ (if FUSION_ENABLED)
│                             │
├─ evaluate_risk_veto_gates()─┤
│  └─> (approved: bool, size: float)
│
└─ execute_live_cycle()
   ├─ load_champion_model()
   ├─ Per tick:
   │  ├─ XGBoost.predict() → probability
   │  ├─ If prob > threshold:
   │  │  ├─ evaluate_risk_veto_gates()
   │  │  └─ If approved: Alpaca API call
   │  └─ Log to execution ledger
   └─> PyArrow ledger

DASHBOARD LAYER
└─ Streamlit dashboard
   └─ Read execution ledger (PyArrow)
      └─> KPIs, charts, tables
```

---

## Part 7: Key Improvements & Enhancements

### Data Ingestion
- [ ] Add tick-level data support (minute bars for intraday)
- [ ] Implement survivorship bias adjustment (handle delisted stocks)
- [ ] Add corporate action handling (splits, dividends)
- [ ] Rate limit management & retry logic

### Feature Engineering
- [ ] Lazy evaluation of expensive features (compute on-demand)
- [ ] Feature versioning & schema tracking
- [ ] Null/anomaly detection & reporting
- [ ] Cross-asset correlation calculations

### Tournament
- [ ] Parallel sector processing (Dask scheduling)
- [ ] Walk-forward analysis (expanding windows)
- [ ] Feature importance tracking per fold
- [ ] Hyperparameter optimization (Bayesian or grid)

### Evaluation
- [ ] Monte Carlo permutation testing
- [ ] Bootstrap confidence intervals
- [ ] Regime-conditional Sharpe ratios
- [ ] Drawdown analysis (max DD, recovery time)

### Execution
- [ ] Order fill monitoring (tracked vs actual)
- [ ] Stop-loss enforcement with alerts
- [ ] Profit-taking logic (scale out rules)
- [ ] Portfolio-level risk limits (VaR, CVaR)

### Dashboard
- [ ] Real-time tick updates
- [ ] Live heatmap of model confidence by sector
- [ ] A/B testing dashboard (champion vs candidate)
- [ ] Forensic logs (audit trail for every decision)

---

## Summary: The Quantum Avenger Development Roadmap

The Quantum Avenger fuses **rigorous quantitative ML** with **probabilistic LLM reasoning** in a production-grade hybrid system. This roadmap provides:

1. **System Architecture**: Complete topology from data ingestion → live execution
2. **Module Breakdown**: Function-level documentation with integration points
3. **Mind Map**: Data flow and dependency graphs
4. **Validation Checkpoints**: Backtesting hygiene & risk veto gates
5. **Development Phases**: 7-phase implementation plan (16 weeks)
6. **Enhancement Roadmap**: Improvements in data, features, models, execution, monitoring

**Key Principles**:
- **Vectorized over loops** (Polars, CUDA, Numba)
- **Deterministic quant isolated from probabilistic LLM** (FastMCP bridge)
- **No look-ahead bias** (CPCV with temporal purge)
- **Asymmetric capital preservation** (5× penalty on false positives)
- **Deflated Sharpe rigor** (DSR > 0.95 promotion threshold)
- **Shield Agent veto** (Numba JIT microsecond risk gates)

The `/new_pipeline/` directory will implement this roadmap with enhanced modularity, comprehensive error handling, and explicit documentation of every integration point.

---

**Next Steps**: Begin Phase 1 implementation when ready, starting with modular structure & configuration management.
