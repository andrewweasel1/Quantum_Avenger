# Codebase Bundle: Quantum_Avenger

## Project Structure
```text
📁 ./
  📄 mcp.json
  📄 claude.md
  📄 pack_repo.py
  📁 reference_code/
    📄 tournament.py
    📄 main.py
    📄 live_trader.py
    📄 data_ingestion.py
    📄 requirements.txt
    📄 config.py
    📄 evaluator.py
    📄 dashboard.py
    📄 feature_compiler.py
  📁 new_pipeline/
    📄 main.py
    📄 requirements-dashboard.txt
    📄 requirements-gpu.txt
    📄 __init__.py
    📄 setup.py
    📄 requirements.txt
    📄 README.md
    📄 requirements-dev.txt
    📄 requirements-live.txt
    📄 pyproject.toml
    📁 features/
      📄 shields.py
      📄 slippage.py
      📄 polars_engine.py
      📄 gpu_kernels.py
      📄 __init__.py
      📄 compiler.py
      📄 registry.py
      📄 base.py
      📄 labels.py
    📁 tournament/
      📄 director.py
      📄 objectives.py
      📄 data_iterator.py
      📄 pipeline.py
      📄 __init__.py
      📄 simulator.py
      📄 feature_selection.py
      📄 cpcv.py
      📄 trainer.py
      📄 grid_search.py
    📁 adapters/
      📄 news_alpaca.py
      📄 factory.py
      📄 fakes.py
      📄 broker_alpaca.py
      📄 __init__.py
      📄 universe_static.py
      📄 base.py
      📄 market_alpaca.py
    📁 core/
      📄 circuit_breaker.py
      📄 seeding.py
      📄 paths.py
      📄 exceptions.py
      📄 __init__.py
      📄 logging.py
      📄 constants.py
    📁 execution/
      📄 mcp_tools.py
      📄 grader.py
      📄 runner.py
      📄 orchestrator.py
      📄 verdict_engine.py
      📄 async_sentiment.py
      📄 __init__.py
      📄 entity_anonymizer.py
      📄 rag_engine.py
      📄 risk.py
      📄 veto_ledger.py
      📄 broker.py
      📄 trade_log.py
    📁 evaluation/
      📄 haircut.py
      📄 minbtl.py
      📄 promotion.py
      📄 tearsheet.py
      📄 __init__.py
      📄 hmm_gauntlet.py
      📄 pbo.py
      📄 cscv.py
      📄 dsr.py
    📁 models/
      📄 metadata.py
      📄 __init__.py
      📄 registry.py
    📁 config/
      📄 defaults.yaml
      📄 schema.py
      📄 testing.yaml
      📄 __init__.py
      📄 development.py
      📄 base.py
      📄 production.yaml
      📄 testing.py
      📄 development.yaml
      📄 production.py
    📁 docs/
      📄 LOGGING_GUIDE.md
      📄 API_REFERENCE.md
      📄 ARCHITECTURE.md
      📄 ERROR_HANDLING.md
      📄 CONFIG_GUIDE.md
      📄 TESTING_GUIDE.md
    📁 data/
      📄 training_db.py
      📄 validation.py
      📄 __init__.py
      📄 ingestion.py
      📄 base.py
      📄 sizing.py
      📄 vaults.py
      📁 universe/
    📁 scripts/
      📄 check_health.py
      📄 serve_mcp.py
      📄 ingest_training_data.py
      📄 live_smoke.py
    📁 monitoring/
      📄 telemetry.py
      📄 metrics_endpoint.py
      📄 __init__.py
      📄 metrics.py
      📄 health.py
      📁 dashboard/
        📄 auth.py
        📄 alerts.py
        📄 __init__.py
        📄 views.py
        📄 app.py
        📄 notifications.py
        📄 realtime.py
        📁 pages/
          📄 06_settings.py
          📄 03_trade_log.py
          📄 02_veto_analysis.py
          📄 05_risk_dashboard.py
          📄 01_live_monitor.py
          📄 04_model_registry.py
    📁 utils/
      📄 time.py
      📄 retry.py
      📄 decorators.py
      📄 serialization.py
      📄 __init__.py
    📁 tests/
      📄 conftest.py
      📄 __init__.py
      📁 unit/
        📄 test_tournament_core.py
        📄 test_psr_mintrl.py
        📄 test_telemetry.py
        📄 test_adapters_fakes.py
        📄 test_dsr.py
        📄 test_feature_selection.py
        📄 test_trade_log.py
        📄 test_feature_registry.py
        📄 test_serve_mcp.py
        📄 test_evaluation.py
        📄 test_polars_engine.py
        📄 test_logging.py
        📄 test_dashboard_auth.py
        📄 test_haircut.py
        📄 test_verdict_grader.py
        📄 test_alerts.py
        📄 test_exceptions_hierarchy.py
        📄 test_veto_ledger.py
        📄 test_retry.py
        📄 test_data_ingestion.py
        📄 test_seeding.py
        📄 test_adapter_factory.py
        📄 test_gpu_rolling_dispatch.py
        📄 test_config.py
        📄 test_cscv_pbo.py
        📄 test_realtime.py
        📄 test_gpu_kernels.py
        📄 test_notifications.py
        📄 test_trainer.py
        📄 test_shields.py
        📄 test_ingestion_parallel.py
        📄 test_metrics_endpoint.py
        📄 test_crash_risk.py
        📄 test_orchestrator.py
        📄 test_logging_structured.py
        📄 test_minbtl.py
        📄 test_sizing.py
        📄 test_universe.py
        📄 test_circuit_breaker.py
        📄 test_entity_anonymizer.py
        📄 test_async_sentiment.py
        📄 test_mcp_tools.py
        📄 test_training_db.py
        📄 test_exceptions.py
        📄 test_feature_compiler.py
        📄 test_slippage.py
        📄 test_trainer_early_stopping.py
        📄 test_rag_engine.py
        📄 test_promotion.py
        📄 test_dashboard_views.py
        📄 test_alpaca_adapters.py
        📄 test_labels.py
        📄 test_config_overlays.py
        📄 test_backtest.py
        📄 test_cpcv.py
      📁 integration/
        📄 test_execution_flow.py
        📄 test_whole_engine.py
        📄 test_offline_pipeline.py
        📄 test_director_parallel.py
        📄 test_streaming_compile.py
        📄 __init__.py
        📄 test_director.py
        📄 test_tournament_flow.py
        📄 test_vault_flow.py
      📁 fixtures/
        📄 sample_data.py
        📄 __init__.py
        📄 config_fixtures.py
    📁 analysis/
      📄 __init__.py
      📄 backtest.py
    📁 hardening/
      📄 README.md
      📁 terraform/
      📁 observability/
        📄 grafana_dashboard.json
        📄 alert_rules.yml
        📄 prometheus.yml
      📁 docs/
        📄 RECOVERY.md
        📄 DEPLOYMENT.md
        📄 SECURITY.md
      📁 chaos/
        📄 scenarios.md
        📄 load_test.py
      📁 docker/
        📄 docker-compose.yml
      📁 k8s/
        📄 secrets.yaml
        📄 service.yaml
        📄 networkpolicy.yaml
        📄 deployment.yaml
        📄 ingress.yaml
        📄 configmap.yaml
        📄 hpa.yaml
  📁 .github/
    📁 workflows/
      📄 ci.yml
  📁 docs/
    📄 ARCHITECTURE_ROADMAP.md
    📄 PHASE_1_SPECIFICATION.md
    📄 FULL_SYSTEM_INTEGRATION_GUIDE.md
    📄 execution_roadmap.md
    📄 PHASE_5_SPECIFICATION.md
    📄 PHASE_2_SPECIFICATION.md
    📄 PHASE_7_SPECIFICATION.md
    📄 PHASE_6_SPECIFICATION.md
    📄 ROADMAP_2026.md
    📄 PHASE_4_SPECIFICATION.md
    📄 PHASE_3_SPECIFICATION.md
    📄 quantitative_math.md
    📄 system_architecture.md
  📁 data/
    📁 metadata/
      📄 feature_registry.yaml
  📁 .claude/
    📄 settings.json
    📁 hooks/
```

---

## File Contents

### File: `mcp.json`

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "./Quantum_Avenger"
      ]
    },
    "git": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-git",
        "--repository",
        "./Quantum_Avenger"
      ]
    }
  }
}
```

---

### File: `claude.md`

```markdown
# Quantum Avenger Architecture: Agentic Coding Ruleset & Persona

## Role & Persona
You are an elite Quantitative Analyst, an expert Python Programmer, and a pioneer AI Systems Architect specializing in "fused" hybrid trading systems. Your expertise bridges the gap between traditional mathematical finance, advanced machine learning (ML), and Large Language Models (LLMs) used for financial analysis and algorithmic trading.

## Objective
Your goal is to synthesize unstructured data (e.g., sentiment, NLP signals, SEC filings, knowledge graphs) with structured quantitative ML pipelines (e.g., time-series forecasting, factor models, risk management). You must design, code, backtest, and optimize production-grade hybrid financial systems.

## 1. Python Programming & Data Engineering Excellence
- **Standards:** Write production-grade, clean, PEP 8 compliant Python code with explicit type-hinting.
- **Vectorization over Loops:** NEVER use standard Python `for` loops for time-series analysis. Prioritize vectorized operations using `Polars` (lazy-frames), `NumPy`, or `CuPy` (CUDA-accelerated NumPy) to ensure maximum execution speed.
- **Out-of-Core Processing:** For massive financial datasets, utilize `Dask` orchestration and `PyArrow` zero-copy iterators for Parquet file handling. Dynamically allocate Parquet block sizes (64MiB - 256MiB) based on `psutil` physical RAM sensors to prevent Out-of-Memory (OOM) failures.
- **Modular Structure:** Enforce a strict pipeline topology: Data Ingestion -> Feature Engineering -> Modeling -> Orchestration -> Execution/Backtest.

## 2. Quantitative Rigor & ML Architecture
- **Backtesting Hygiene:** Explicitly account for liquidity constraints and avoid look-ahead bias by strictly shifting signals forward by $t+1$ before calculating returns. 
- **Slippage Modeling:** Discard fixed slippage assumptions. Implement dynamic hydrodynamic slippage modeling calculated as: $c \cdot \sigma \cdot \sqrt{Q/V}$ (where $Q$ is order size, $V$ is rolling volume, and $\sigma$ is volatility).
- **Asymmetric Financial Loss:** When training `XGBoost` or `LightGBM` models, implement custom asymmetric objective functions that penalize False Positives (direct capital loss) 5x more heavily than False Negatives (opportunity cost).
- **Evaluation Metrics:** Discard generic ML accuracy metrics. Evaluate all out-of-sample models using the **Deflated Sharpe Ratio (DSR)** via `scipy.stats`, adjusting for non-Normal returns (Skewness and Kurtosis) and controlling for the False Discovery Rate (FDR) across multiple backtest trials. The promotion threshold for live execution is a DSR > 0.95.
- **Regime Detection:** Utilize Hidden Markov Models (`hmmlearn`) to dynamically tag volatility regimes.

## 3. Hybrid Fused System Architecture (ML + LLM)
- **Deterministic vs. Probabilistic Isolation:** LLMs are strictly prohibited from calculating mathematical or risk metrics. All quantitative calculations must be written as deterministic Python functions and exposed to the LLM orchestrator via JSON-RPC using the **FastMCP** library.
- **Entity Anonymization:** To defeat LLM look-ahead bias and hallucination, unstructured text (news, 10-K filings) MUST pass through a `spaCy` NER pipeline to mask tradable entities (e.g., replacing "Apple" with "[COMPANY A]") before reaching the LLM Verdict Engine.
- **Advanced RAG:** Implement **Late Chunking** to preserve semantic context across chunk boundaries, and utilize **Agentic RAG** (via `LangGraph`) with self-correcting Grader nodes to ensure the LLM verifies alpha signals before committing to a verdict.

## 4. Execution Pipeline & The Shield Agent
- **Low-Latency Veto Gates:** Design the final execution risk manager (The "Shield Agent") using `Numba` JIT compilation (`fastmath=True`) and Intel TBB. This layer must calculate volatility stops (ATR multipliers) and dynamically reject LLM verdicts in microseconds if portfolio risk parameters are breached.
- **Live Routing:** Integrate validated execution logic with asynchronous REST/WebSocket wrappers for the Alpaca paper-trading API. 

## 5. Agentic Workflow Constraints (MCP Interaction)
- **Action Verification:** Before creating or modifying files using the `@mcp/server-filesystem` tool, always read the target directory structure to verify dependencies.
- **Mathematical Soundness:** Provide statistical justifications or mathematical formulas (e.g., cointegration, mean reversion) as comments when implementing quantitative methods.
- **Version Control:** After writing and successfully testing a local execution script (e.g., verifying no memory leaks exist), autonomously use the `@mcp/server-git` tool to commit the optimized code to the repository.

## Tone and Style
Direct, highly technical, analytical, and objective. Avoid generic financial disclaimers. Focus exclusively on actionable, vectorized code, crisp architectural logic, and mathematically sound explanations.

## 6. Legacy Codebase Reference & Migration Protocol
The existing source code is located exclusively in the `/reference_code/` directory. 
- **READ-ONLY CONSTRAINT:** You are strictly prohibited from modifying, deleting, or saving any files within the `/reference_code/` directory. Treat this directory as an immutable reference library.
- **TARGET DIRECTORY:** All new pipeline architecture, vectorized Python modules, and backtesting scripts must be authored and saved exclusively in the `/new_pipeline/` directory.

### Required Reading Protocol
Before beginning any implementation in `/new_pipeline/`, you MUST use your filesystem MCP tool to read the corresponding modules in `/reference_code/` to understand the previous logic. Specifically:
- Read `/reference_code/feature_compiler.py` before authoring new Polars/CuPy vectorized operations.
- Read `/reference_code/tournament.py` before implementing the Deflated Sharpe Ratio (DSR) or out-of-core PyArrow iterators.
- Read `/reference_code/live_trader.py` before building the Numba JIT risk veto gates.
- Read `/docs/PHASE_1_SPECIFICATION.md` through `/docs/PHASE_7_SPECIFICATION.md` and `/docs/FULL_SYSTEM_INTEGRATION_GUIDE.md` to align implementation with the project architecture and phase contracts.
- Use `/docs/ROADMAP_2026.md` as the top-level execution plan for roadmap sequencing and milestone delivery.

# Project Guidelines
You must read the following files in the `/docs/` directory to understand the project architecture and roadmap before executing commands:
- `/docs/system_architecture.md`
- `/docs/execution_roadmap.md`
- `/docs/quantitative_math.md`

```

---

### File: `pack_repo.py`

```py
import os
from pathlib import Path

# Configuration
OUTPUT_FILE = "codebase_bundle.md"
# Folders and files to completely ignore (add yours here)
IGNORE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "env", "build", "dist"}
IGNORE_FILES = {OUTPUT_FILE, ".DS_Store", "package-lock.json"}
# Supported text file extensions
SUPPORTED_EXTENSIONS = {".py", ".md", ".txt", ".json", ".yaml", ".yml", ".ini", ".conf", ".toml"}

def generate_markdown_bundle(repo_path: Path, output_path: Path):
    with open(output_path, "w", encoding="utf-8") as outfile:
        outfile.write(f"# Codebase Bundle: {repo_path.resolve().name}\n\n")
        
        # 1. Generate a Folder Structure Visual First
        outfile.write("## Project Structure\n```text\n")
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            level = len(Path(root).relative_to(repo_path).parts)
            indent = "  " * level
            outfile.write(f"{indent}📁 {os.path.basename(root)}/\n")
            sub_indent = "  " * (level + 1)
            for f in files:
                if f not in IGNORE_FILES and Path(f).suffix in SUPPORTED_EXTENSIONS:
                    outfile.write(f"{sub_indent}📄 {f}\n")
        outfile.write("```\n\n---\n\n")

        # 2. Pack File Contents
        outfile.write("## File Contents\n\n")
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file in IGNORE_FILES:
                    continue
                    
                file_path = Path(root) / file
                relative_path = file_path.relative_to(repo_path)
                
                if file_path.suffix in SUPPORTED_EXTENSIONS:
                    # Determine markdown syntax highlighting language
                    lang = file_path.suffix.lstrip('.')
                    if lang in ["yml", "yaml"]: lang = "yaml"
                    elif lang in ["md", "txt"]: lang = "markdown"

                    outfile.write(f"### File: `{relative_path}`\n\n")
                    outfile.write(f"```{lang}\n")
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="replace") as infile:
                            outfile.write(infile.read())
                    except Exception as e:
                        outfile.write(f"[Error reading file: {e}]")
                    outfile.write("\n```\n\n---\n\n")

    print(f" Successfully packed repository into {output_path}")

if __name__ == "__main__":
    generate_markdown_bundle(Path("."), Path(OUTPUT_FILE))
```

---

### File: `reference_code/tournament.py`

```py
import os
import gc
import json
import itertools
import logging
from typing import Tuple, List, Optional, Any, Dict, Generator

import numpy as np
import pandas as pd
import dask.dataframe as dd
import pyarrow.parquet as pq
import xgboost as xgb
from itertools import combinations
from numba import njit
import scipy.cluster.hierarchy as sch
from scipy.spatial.distance import squareform

import config

logger = logging.getLogger(__name__)

# ==============================================================================
# 1. OUT-OF-CORE PYARROW ITERATOR & RISK SIMULATOR
# ==============================================================================
class ParquetDataIter(xgb.DataIter):
    """Zero-copy out-of-core XGBoost Data Iterator via PyArrow."""
    def __init__(self, file_path: str, features: List[str], target_col: str):
        super().__init__(on_host=True)
        self.file_path = file_path
        self.features = features
        self.target_col = target_col
        self.pf = pq.ParquetFile(file_path)
        self.num_row_groups = self.pf.num_row_groups
        self.it = 0

    def reset(self) -> None:
        self.it = 0

    def next(self, input_data: Any) -> int:
        if self.it == self.num_row_groups:
            return 0
        chunk_table = self.pf.read_row_group(self.it, columns=self.features + [self.target_col])
        input_data(data=chunk_table.select(self.features), label=chunk_table.select([self.target_col]))
        self.it += 1
        return 1

@njit(fastmath=True)
def simulate_risk_manager_njit(signals, closes, lows, atrs, atr_multiplier, max_risk_pct):
    n = len(signals)
    returns = np.zeros(n)
    for i in range(n - 1):
        if signals[i] == 1 and atrs[i] > 0:
            entry = closes[i]
            stop = entry - (atr_multiplier * atrs[i])
            risk_distance = (entry - stop) / entry
            size = max_risk_pct / risk_distance if risk_distance > 0 else 0.0
            size = min(size, 1.0) 
            if lows[i+1] <= stop:
                returns[i] = -risk_distance * size
            else:
                returns[i] = ((closes[i+1] - entry) / entry) * size
    return returns

def asymmetric_financial_loss(preds: np.ndarray, dtrain: xgb.DMatrix) -> Tuple[np.ndarray, np.ndarray]:
    """
    Custom objective: Penalizes False Positives (Capital Loss) 5x more than False Negatives (Opportunity Loss).
    """
    labels = dtrain.get_label()
    preds_prob = 1.0 / (1.0 + np.exp(-preds))
    
    # Gradient and Hessian of logloss
    grad = preds_prob - labels
    hess = preds_prob * (1.0 - preds_prob)
    
    # Asymmetric penalty multiplier
    penalty_fp = 5.0
    penalty_fn = 1.0
    
    grad = np.where(labels == 0, grad * penalty_fp, grad * penalty_fn)
    hess = np.where(labels == 0, hess * penalty_fp, hess * penalty_fn)
    
    return grad, hess

# ==============================================================================
# 2. TOURNAMENT PIPELINE & CLUSTERED FEATURE SELECTION
# ==============================================================================
class ModularTournamentDirector:
    def __init__(self) -> None:
        self.ddf: dd.DataFrame = dd.read_parquet(config.PROCESSED_VAULT_DIR, **config.DASK_READ_KWARGS)

    def generate_cpcv_splits(self, df: pd.DataFrame, n_groups: int = 6, test_groups: int = 2) -> Generator[Tuple[pd.DataFrame, pd.DataFrame], None, None]:
        indices = np.array_split(df.index, n_groups)
        group_ids = list(range(n_groups))
        
        for test_combo in combinations(group_ids, test_groups):
            test_indices = []
            for i in test_combo:
                test_indices.extend(indices[i])
                
            test_df = df.loc[test_indices]
            train_df = df.drop(index=test_indices)
            
            purge_gap = pd.Timedelta(days=config.MAX_HOLD_DAYS)
            embargo_gap = pd.Timedelta(days=5) 
            
            for test_idx in test_combo:
                boundary_start = indices[test_idx] - purge_gap
                boundary_end = indices[test_idx][-1] + purge_gap + embargo_gap
                train_df = train_df.loc[~((train_df.index >= boundary_start) & (train_df.index <= boundary_end))]
                
            yield train_df, test_df

    def tune_sector_grid(self, sector_name: str) -> None:
        logger.info(f"--- CPCV Tournament for {sector_name} ---")
        sector_df = self.ddf[self.ddf['sector'] == sector_name].compute().sort_values('date')
        if len(sector_df) < 1000: return

        target_col = 'target_label'
        features = [c for c in sector_df.columns if c not in config.METADATA_COLS]

        param_grid = {'max_depth': [1, 2], 'learning_rate': [0.01, 0.05]}
        keys, values = zip(*param_grid.items())
        grid_combinations = [dict(zip(keys, v)) for v in itertools.product(*values)]
        
        returns_matrix = {}
        benchmark_returns = []
        best_sr, best_params = -1.0, None
        
        temp_train_path = f"temp_train_{sector_name}.parquet"
        
        for trial_idx, params in enumerate(grid_combinations):
            params.update({'tree_method': 'hist', 'device': 'cuda', 'disable_default_eval_metric': 1})
            trial_oos_returns = []
            
            try:
                for train_df, test_df in self.generate_cpcv_splits(sector_df):
                    # FIX 1: Dynamically size the disk chunks based on hardware limits
                    train_df.to_parquet(
                        temp_train_path, 
                        engine='pyarrow', 
                        row_group_size=config.ROW_GROUP_SIZE 
                    )
                    train_iter = ParquetDataIter(temp_train_path, features, target_col)
                    
                    # FIX 2: Enable Adaptive VRAM Caching to prevent CUDA OOM on smaller GPUs
                    # cache_host_ratio=0.75 forces XGBoost to keep 75% of the histogram cache in RAM,
                    # prioritizing structural safety and continuous execution over pure VRAM speed.
                    dtrain = xgb.ExtMemQuantileDMatrix(train_iter, cache_host_ratio=0.75) 
                    
                    # Materialize the smaller test split directly into host RAM
                    dtest = xgb.DMatrix(test_df[features], label=test_df[target_col])
                    
                    bst = xgb.train(
                        params, dtrain, num_boost_round=300,
                        obj=asymmetric_financial_loss,
                        evals=[(dtrain, 'train'), (dtest, 'eval')],
                        early_stopping_rounds=25, verbose_eval=False,
                        custom_metric=lambda p, d: ('error', np.mean((1.0 / (1.0 + np.exp(-p)) > 0.5) != d.get_label()))
                    )
                    
                    preds = 1.0 / (1.0 + np.exp(-bst.predict(dtest, iteration_range=(0, bst.best_iteration + 1))))
                    signals = (preds > config.CONFIDENCE_THRESHOLD).astype(int)
                    
                    if config.RISK_MANAGER_ENABLED:
                        returns = simulate_risk_manager_njit(
                            signals, test_df['close'].values, test_df['low'].values, test_df['atr'].values,
                            config.ATR_STOP_MULTIPLIER, config.MAX_RISK_PER_TRADE
                        )
                    else:
                        returns = signals * test_df['close'].pct_change().fillna(0).values
                    trial_oos_returns.extend(returns)
                    
                    if trial_idx == 0: benchmark_returns.extend(test_df['close'].pct_change().fillna(0).values)
                    del dtrain, dtest, train_iter
                    
            finally:
                if os.path.exists(temp_train_path): os.remove(temp_train_path)
            
            trial_oos_returns = np.array(trial_oos_returns)
            returns_matrix[f"trial_{trial_idx}"] = trial_oos_returns
            trial_sr = np.mean(trial_oos_returns) / np.std(trial_oos_returns) if np.std(trial_oos_returns) > 0 else 0.0
                
            if trial_sr > best_sr:
                best_sr = trial_sr
                best_params = params

        # -------------------------------------------------------------------------
        # GLOBAL CLUSTERED FEATURE SELECTION (CFS)
        # -------------------------------------------------------------------------
        split_idx = int(len(sector_df) * 0.8)
        cfi_train, cfi_test = sector_df.iloc[:split_idx], sector_df.iloc[split_idx:]
        
        d_cfi_train = xgb.DMatrix(cfi_train[features], label=cfi_train[target_col])
        d_cfi_test = xgb.DMatrix(cfi_test[features], label=cfi_test[target_col])
        cfi_bst = xgb.train(best_params, d_cfi_train, obj=asymmetric_financial_loss, num_boost_round=100)
        
        base_preds = 1.0 / (1.0 + np.exp(-cfi_bst.predict(d_cfi_test)))
        base_returns = (base_preds > config.CONFIDENCE_THRESHOLD).astype(int) * cfi_test['close'].pct_change().fillna(0).values
        base_sharpe = np.mean(base_returns) / np.std(base_returns) if np.std(base_returns) > 0 else 0.0

        # Correlation distance matrix & Ward linkage
        corr_matrix = cfi_train[features].corr(method='spearman').fillna(0).values
        dist_matrix = np.sqrt(np.clip(0.5 * (1 - corr_matrix), 0, 1))
        condensed_dist = squareform(dist_matrix, checks=False)
        linkage_matrix = sch.linkage(condensed_dist, method='ward')
        clusters = sch.fcluster(linkage_matrix, t=0.5, criterion='distance')
        
        surviving_features = []
        for cluster_id in np.unique(clusters):
            cluster_features = [features[i] for i, c in enumerate(clusters) if c == cluster_id]
            X_test_perm = cfi_test[features].copy()
            shuffle_idx = np.random.permutation(len(X_test_perm))
            X_test_perm[cluster_features] = X_test_perm[cluster_features].values[shuffle_idx]
            
            perm_preds = 1.0 / (1.0 + np.exp(-cfi_bst.predict(xgb.DMatrix(X_test_perm))))
            perm_returns = (perm_preds > config.CONFIDENCE_THRESHOLD).astype(int) * cfi_test['close'].pct_change().fillna(0).values
            perm_sharpe = np.mean(perm_returns) / np.std(perm_returns) if np.std(perm_returns) > 0 else 0.0
            
            if (base_sharpe - perm_sharpe) > 0.02: # Feature group contains orthogonal alpha
                surviving_features.extend(cluster_features)

        if not surviving_features: surviving_features = features # Fallback if all decay
        
        logger.info(f"[{sector_name}] CFS pruned feature space from {len(features)} to {len(surviving_features)}.")

        # Train final candidate on orthogonalized feature subset
        d_full = xgb.DMatrix(sector_df[surviving_features], label=sector_df[target_col])
        candidate_booster = xgb.train(best_params, d_full, obj=asymmetric_financial_loss, num_boost_round=150)
        
        os.makedirs(config.PROD_MODELS_DIR, exist_ok=True)
        candidate_booster.save_model(os.path.join(config.PROD_MODELS_DIR, f"{sector_name}_candidate.json"))
        with open(os.path.join(config.PROD_MODELS_DIR, f"{sector_name}_candidate_features.json"), "w") as f:
            json.dump(surviving_features, f)
            
        pd.DataFrame(returns_matrix).to_parquet(f"returns_matrix_{sector_name}.parquet", engine='pyarrow')
        pd.DataFrame({"benchmark": benchmark_returns, "champion": returns_matrix[f"trial_{np.argmax([np.mean(returns_matrix[k])/np.std(returns_matrix[k]) if np.std(returns_matrix[k])>0 else 0 for k in returns_matrix])}"]}).to_parquet(f"benchmark_{sector_name}.parquet", engine='pyarrow')
        gc.collect()

    def execute_gauntlet(self) -> None:
        if not os.path.exists(config.PROCESSED_VAULT_DIR): return
        unique_sectors = self.ddf['sector'].unique().compute()
        for sector in unique_sectors:
            if not pd.isna(sector): self.tune_sector_grid(str(sector))
```

---

### File: `reference_code/main.py`

```py
import os
import argparse
import logging
import pandas as pd
from dask.distributed import Client, LocalCluster

# ==============================================================================
# 1. ARGPARSE & GLOBAL STATE INJECTION
# ==============================================================================
parser = argparse.ArgumentParser(description="Quantum Sentinel V6 - Multi-Agent Engine")
parser.add_argument("--refresh-raw", action="store_true", help="Refresh raw market data")
parser.add_argument("--fusion", action="store_true", help="Enable LLM Sentiment Fusion Agent")
parser.add_argument("--disable-risk-manager", action="store_true", help="Disable the Risk Manager Agent")

# New Lifecycle Execution Flags
parser.add_argument("--evaluate", action="store_true", help="Run the statistical Evaluator to promote models")
parser.add_argument("--live", action="store_true", help="Launch the Live Trading Sandbox")
args = parser.parse_args()

# Inject the toggled states into config BEFORE other modules load
import config
config.FUSION_ENABLED = args.fusion
config.RISK_MANAGER_ENABLED = not args.disable_risk_manager

# ==============================================================================
# 2. CENTRALIZED LOGGING CONFIGURATION
# ==============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(config.SYSTEM_LOG_FILE),  
        logging.StreamHandler()                       
    ]
)
logger = logging.getLogger(__name__)

# ==============================================================================
# 3. DOWNSTREAM MODULE IMPORTS
# ==============================================================================
import data_ingestion
import feature_compiler
import tournament
import evaluator
import live_trader

def initialize_dask_cluster() -> Client:
    """
    Initializes a dynamic Dask cluster. Reserves cores for the LLM/GPU orchestrators 
    and enforces strict memory limits to trigger graceful NVMe disk spilling on low RAM.
    """
    allocated_workers = max(1, os.cpu_count() - 2)
    
    cluster = LocalCluster(
        n_workers=allocated_workers,
        threads_per_worker=1,
        memory_limit='auto'  # Guarantees the system slows down (spills) instead of crashing
    )
    return Client(cluster)

def main():
    client = initialize_dask_cluster()

    logger.info(f"=== QUANTUM SENTINEL ORCHESTRATOR [{config.RUN_MODE} MODE] ===")
    logger.info(f"LLM Fusion Agent: {'ONLINE' if config.FUSION_ENABLED else 'OFFLINE'}")
    logger.info(f"Risk Manager Agent: {'ONLINE' if config.RISK_MANAGER_ENABLED else 'OFFLINE'}")
    
    # PHASE 1: DATA PIPELINE & TRAINING
    if args.refresh_raw:
        universe = data_ingestion.get_survivorship_adjusted_universe()
        data_ingestion.build_raw_vault(universe)
        feature_compiler.compile_features_from_raw()
        
        director = tournament.ModularTournamentDirector()
        director.execute_gauntlet()

    # PHASE 2: STATISTICAL EVALUATION
    if args.evaluate:
        stat_evaluator = evaluator.QuantitativeEvaluator()
        stat_evaluator.run_evaluation_gauntlet()

    # PHASE 3: LIVE MARKET EXECUTION
    if args.live:
        logger.info("Initializing Live Trading Sandbox via Alpaca...")
        sandbox = live_trader.LiveTradingSandbox(is_paper=True)
        
        # In a true deployment, this block would pull today's live OHLCV data. 
        # For testing, we load the most recent data from the processed vault.
        logger.info("Sourcing live market data for active champions...")
        live_market_df = pd.read_parquet(config.PROCESSED_VAULT_DIR, engine="pyarrow")
        
        # Filter for the most recent trading day to simulate the live feed
        latest_date = live_market_df['date'].max()
        current_data = live_market_df[live_market_df['date'] == latest_date].copy()
        
        sandbox.execute_live_cycle(current_data)

if __name__ == "__main__":
    main()
```

---

### File: `reference_code/live_trader.py`

```py
import os
import re
import gc
import math
import json
import time
import requests
import logging
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import xgboost as xgb

from numba import njit # FIX: Removed unused numba_config to prevent TBB dependency crash
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.requests import LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

import config

def fetch_live_sentiment(ticker: str) -> float:
    if not config.FUSION_ENABLED:
        return 0.0

    live_headline = f"Breaking pre-market developments expected to impact {ticker} today."
    anonymized_headline = re.sub(rf'\b{ticker}\b', 'the company', live_headline, flags=re.IGNORECASE)

    payload = {
        "model": config.LLM_MODEL_NAME,
        "prompt": f"{config.LLM_SYSTEM_PROMPT}\n\nHeadline: {anonymized_headline}",
        "format": "json",
        "stream": False
    }

    try:
        response = requests.post(config.OLLAMA_ENDPOINT, json=payload, timeout=3.0)
        if response.status_code == 200:
            data = json.loads(response.json().get("response", "{}"))
            return float(data.get("sentiment_score", 0.0))

# ==============================================================================
# 0. CENTRALIZED LOGGING & INTEL TBB CONFIGURATION
# ==============================================================================
logger = logging.getLogger(__name__)

# FIX: Delete the orphaned numba_config.THREADING_LAYER = 'tbb'

# ==============================================================================
# 1. THE SENSOR AGENT: LIVE LLM SENTIMENT
# ==============================================================================
def fetch_live_sentiment(ticker: str) -> float:
    """
    Scrapes live market news, anonymizes the ticker to prevent LLM hallucination/bias,
    and requests a strictly formatted JSON sentiment score from the local Llama 3 model.
    """
    if not config.FUSION_ENABLED:
        return 0.0

    live_headline = f"Breaking pre-market developments expected to impact {ticker} today."
    anonymized_headline = re.sub(rf'\b{ticker}\b', 'the company', live_headline, flags=re.IGNORECASE)

    payload = {
        "model": config.LLM_MODEL_NAME,
        "prompt": f"{config.LLM_SYSTEM_PROMPT}\n\nHeadline: {anonymized_headline}",
        "format": "json",
        "stream": False
    }

    try:
        response = requests.post(config.OLLAMA_ENDPOINT, json=payload, timeout=3.0)
        if response.status_code == 200:
            data = json.loads(response.json().get("response", "{}"))
            return float(data.get("sentiment_score", 0.0))
    except Exception as e:
        logger.warning(f"LLM Sensor timeout for {ticker}. Defaulting to neutral sentiment.")
        
    return 0.0

# ==============================================================================
# 2. THE SHIELD AGENT: CPU-PARALLELIZED RISK MANAGER
# ==============================================================================
@njit(fastmath=True)
def evaluate_risk_veto_gates(entry_price: float, atr: float, atr_multiplier: float, 
                             account_capital: float, max_risk_pct: float) -> tuple:
    """
    Intel TBB Parallelized Risk Manager.
    Evaluates sizing and volatility stops. Returns (Is_Approved, Position_Size).
    """
    stop_loss = entry_price - (atr_multiplier * atr)
    risk_per_share = entry_price - stop_loss
    
    if risk_per_share <= 0:
        return False, 0.0 # Veto: Invalid Volatility Profile
        
    capital_at_risk = account_capital * max_risk_pct
    position_size = capital_at_risk / risk_per_share
    
    max_allowable_shares = account_capital / entry_price
    position_size = min(position_size, max_allowable_shares)
    
    # FIX: Hard force floor rounding to avoid Alpaca fractional share rejections entirely
    position_size = math.floor(position_size)
    
    if position_size < 1.0: 
        return False, 0.0 # Veto: Account too small for safe risk profile on this asset
        
    return True, float(position_size)

# ==============================================================================
# 3. LIVE SANDBOX EXECUTION CYCLE
# ==============================================================================
class LiveTradingSandbox:
    def __init__(self, is_paper: bool = True):
        self.is_paper = is_paper
        # Initialize Alpaca client for secure execution [1]
        self.client = TradingClient(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY, paper=is_paper)
        logger.info(f"LiveTradingSandbox Initialized (Paper: {is_paper}).")

    def sync_portfolio_state(self) -> dict:
        """
        Polls the broker to map current inventory, preventing recursive over-allocation.
        """
        try:
            positions = self.client.get_all_positions()
            return {p.symbol: float(p.qty) for p in positions}
        except Exception as e:
            logger.error(f"Failed to synchronize portfolio state: {e}")
            return {}

    def load_champion_model(self, sector_name: str) -> tuple:
        model_path = os.path.join(config.PROD_MODELS_DIR, f"{sector_name}_champion.json")
        features_path = os.path.join(config.PROD_MODELS_DIR, f"{sector_name}_champion_features.json")
        
        if not os.path.exists(model_path) or not os.path.exists(features_path):
            return None, None
            
        booster = xgb.Booster()
        booster.load_model(model_path)
        
        with open(features_path, "r") as f:
            features = json.load(f)
            
        return booster, features

    def execute_live_cycle(self, current_data: pd.DataFrame, booster: xgb.Booster) -> None:
        """
        The terminal execution loop. Processes the feature manifold, queries the LLM,
        validates risk, and dispatches dynamic limit orders.
        """
        logger.info("Initiating Live Execution Cycle...")
        current_inventory = self.sync_portfolio_state()
        account = self.client.get_account()
        available_capital = float(account.buying_power)

        for index, row in current_data.iterrows():
            ticker = row['ticker']
            
            # 1. XGBoost & LLM Inference Handoff
            features = [c for c in current_data.columns if c not in config.METADATA_COLS]
            dmatrix = xgb.DMatrix(current_data.loc[[index]][features])
            probability = booster.predict(dmatrix)
            
            if probability > config.CONFIDENCE_THRESHOLD:
                # 2. Risk Management Gate
                is_approved, target_size = evaluate_risk_veto_gates(
                    entry_price=row['close'], 
                    atr=row['atr'], 
                    atr_multiplier=config.ATR_STOP_MULTIPLIER, 
                    account_capital=available_capital, 
                    max_risk_pct=config.MAX_RISK_PER_TRADE
                )
                
                if is_approved:
                    # 3. Portfolio Delta Calculation
                    current_qty = current_inventory.get(ticker, 0.0)
                    delta_qty = target_size - current_qty
                    
                    if delta_qty > 0:
                        # 4. Dynamic Limit Order Routing
                        # Protects against adverse execution using local microstructure volatility
                        limit_price = row['close'] + (0.1 * row['atr'])
                        
                        order_data = LimitOrderRequest(
                            symbol=ticker,
                            qty=delta_qty,
                            side=OrderSide.BUY,
                            time_in_force=TimeInForce.DAY,
                            limit_price=round(limit_price, 2)
                        )
                        
                        try:
                            order = self.client.submit_order(order_data)
                            logger.info(f"[{ticker}] ORDER DISPATCHED: {delta_qty} shares @ {limit_price:.2f} Limit.")
                            
                            # Log to PyArrow Ledger
                            self._log_to_ledger(ticker, "BUY", delta_qty, limit_price)
                        except Exception as e:
                            logger.error(f"[{ticker}] Execution rejected by broker: {e}")
                    else:
                        logger.info(f"[{ticker}] Target size met. Current inventory sufficient.")
                else:
                    logger.warning(f"[{ticker}] VETO: Risk parameters exceeded.")
```

---

### File: `reference_code/data_ingestion.py`

```py
import os
import shutil
import pandas as pd
import yfinance as yf
import pyarrow as pa
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from typing import Dict
import config

logger = logging.getLogger(__name__)

def raw_vault_is_populated() -> bool:
    if not os.path.exists(config.RAW_VAULT_DIR):
        return False
    subdirs = [d for d in os.listdir(config.RAW_VAULT_DIR) if os.path.isdir(os.path.join(config.RAW_VAULT_DIR, d))]
    return len(subdirs) > 0

def reset_raw_vault() -> None:
    if os.path.exists(config.RAW_VAULT_DIR):
        shutil.rmtree(config.RAW_VAULT_DIR)
    os.makedirs(config.RAW_VAULT_DIR, exist_ok=True)

def get_survivorship_adjusted_universe() -> Dict[str, str]:
    """
    TEMPORARY BYPASS: Fetches current S&P 500 constituents from Wikipedia.
    """
    logger.warning("EODHD API bypassed. Fetching static S&P 500 list from Wikipedia.")
    
    try:
        url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
        tables = pd.read_html(url)
        # FIX: pd.read_html returns a list of DataFrames. Index the first table.
        df = tables 
        
        universe = {}
        for _, row in df.iterrows():
            ticker = str(row['Symbol']).replace('.', '-')
            sector = str(row['GICS Sector'])
            universe[ticker] = sector
            
        return universe

    except Exception as e:
        logger.error("Failed to map sector universe from Wikipedia.", exc_info=True)
        return {}

def fetch_point_in_time_news(ticker: str, dates: pd.DatetimeIndex) -> pd.DataFrame:
    news_data = {
        "date": dates,
        "raw_news_headline": [f"Standard pre-market conditions persist for {ticker}."] * len(dates)
    }
    news_df = pd.DataFrame(news_data)
    news_df.set_index("date", inplace=True)
    return news_df

def ingest_raw_ticker(ticker: str, sector: str) -> bool:
    try:
        df = yf.download(
            ticker, 
            start=config.START_DATE, 
            end=config.END_DATE, 
            interval="1d", 
            progress=False, 
            multi_level_index=False
        )
        
        if df.empty or len(df) < 252:
            return False
            
        df.index = pd.to_datetime(df.index)
        df['ticker'] = ticker
        df['sector'] = sector
        
        if config.FUSION_ENABLED:
            news_df = fetch_point_in_time_news(ticker, df.index)
            df = df.join(news_df, how='left')
        
        df = df.convert_dtypes(dtype_backend="pyarrow")
        
        out_dir = os.path.join(config.RAW_VAULT_DIR, f"sector={sector}")
        os.makedirs(out_dir, exist_ok=True)
        
        df.to_parquet(os.path.join(out_dir, f"{ticker}.parquet"), engine='pyarrow')
        return True
        
    except Exception as e:
        logger.error(f"Ingestion failed for {ticker} in sector {sector}.", exc_info=True)
        return False

def build_raw_vault(universe_map: Dict[str, str]) -> None:
    logger.info(f"Executing raw data acquisition layer (Fusion Mode: {'ON' if config.FUSION_ENABLED else 'OFF'})...")
    reset_raw_vault()
    
    success_count = 0
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = {executor.submit(ingest_raw_ticker, ticker, sector): ticker for ticker, sector in universe_map.items()}
        for future in as_completed(futures):
            if future.result():
                success_count += 1
                
    logger.info(f"Raw data acquisition complete. Successfully ingested {success_count} tickers.")
```

---

### File: `reference_code/requirements.txt`

```markdown
# ==========================================
# QUANTUM SENTINEL V6 - MULTI-AGENT STACK
# ==========================================

# Core Data & Mathematics
numpy
pandas
scipy

# Out-of-Core Processing & Zero-Copy Memory
dask[dataframe]
pyarrow

# Machine Learning & Microstructure Sensors
xgboost
numba
tbb
pandas_ta

# Institutional Quantitative Evaluation
jsharpe          # Required for Bailey and Lopez de Prado's Deflated Sharpe Ratio [1, 2]
hmmlearn         # Required for the Gaussian Hidden Markov Model synthesis
scipy            # Required for Ward linkage and Spearman rank-order clustering
nest_asyncio     # Required to prevent Dask worker event loop collisions
quantstats       # Required for HTML tearsheet generation

# Data Acquisition & Broker Routing
yfinance
requests
alpaca-py
aiohttp
asyncio
nest_asyncio

# Telemetry & Dashboard Interface
streamlit
plotly
```

---

### File: `reference_code/config.py`

```py
import os
import argparse
import logging
import psutil
import pyarrow as pa
from datetime import datetime, timedelta
import pandas as pd

# ==============================================================================
# 1. ARGPARSE & GLOBAL STATE INJECTION
# ==============================================================================
parser = argparse.ArgumentParser(description="Quantum Sentinel V6 - Multi-Agent Engine")
parser.add_argument("--refresh-raw", action="store_true", help="Refresh raw market data")
parser.add_argument("--fusion", action="store_true", help="Enable LLM Sentiment Fusion Agent")
parser.add_argument("--disable-risk-manager", action="store_true", help="Disable the Risk Manager Agent")
parser.add_argument("--evaluate", action="store_true", help="Run the statistical Evaluator to promote models")
parser.add_argument("--live", action="store_true", help="Launch the Live Trading Sandbox")
args = parser.parse_args()

import config
config.FUSION_ENABLED = args.fusion
config.RISK_MANAGER_ENABLED = not args.disable_risk_manager

# ==============================================================================
# 2. CENTRALIZED LOGGING CONFIGURATION
# ==============================================================================
# FIX: Logging MUST be configured before importing dependent modules
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(config.SYSTEM_LOG_FILE),  
        logging.StreamHandler()                       
    ]
)
logger = logging.getLogger(__name__)

# ==============================================================================
# 3. DOWNSTREAM MODULE IMPORTS
# ==============================================================================
import data_ingestion
import feature_compiler
import tournament
import evaluator
import live_trader

def main():
    logger.info(f"=== QUANTUM SENTINEL ORCHESTRATOR [{config.RUN_MODE} MODE] ===")
    logger.info(f"LLM Fusion Agent: {'ONLINE' if config.FUSION_ENABLED else 'OFFLINE'}")
    logger.info(f"Risk Manager Agent: {'ONLINE' if config.RISK_MANAGER_ENABLED else 'OFFLINE'}")
    
    # PHASE 1: DATA PIPELINE & TRAINING
    if args.refresh_raw:
        universe = data_ingestion.get_survivorship_adjusted_universe()
        data_ingestion.build_raw_vault(universe)
        feature_compiler.compile_features_from_raw()
        
        director = tournament.ModularTournamentDirector()
        director.execute_gauntlet()

    # PHASE 2: STATISTICAL EVALUATION
    if args.evaluate:
        stat_evaluator = evaluator.QuantitativeEvaluator()
        stat_evaluator.run_evaluation_gauntlet()

    # PHASE 3: LIVE MARKET EXECUTION
    if args.live:
        logger.info("Initializing Live Trading Sandbox via Alpaca...")
        sandbox = live_trader.LiveTradingSandbox(is_paper=True)
        
        logger.info("Sourcing live market data for active champions...")
        live_market_df = pd.read_parquet(config.PROCESSED_VAULT_DIR, engine="pyarrow")
        
        latest_date = live_market_df['date'].max()
        current_data = live_market_df[live_market_df['date'] == latest_date].copy()
        
        sandbox.execute_live_cycle(current_data)

# ==============================================================================
# 6. DYNAMIC HARDWARE ALLOCATION & OUT-OF-CORE CONFIGURATION
# ==============================================================================
# Dynamically scale data chunks based on available physical RAM
SYSTEM_RAM_GB = psutil.virtual_memory().total / (1024 ** 3)

if SYSTEM_RAM_GB <= 16.0:
    PARQUET_BLOCKSIZE = "64MiB"
    ROW_GROUP_SIZE = 50000        # Smaller chunks, slows execution but guarantees safety
elif SYSTEM_RAM_GB <= 32.0:
    PARQUET_BLOCKSIZE = "128MiB"
    ROW_GROUP_SIZE = 100000
else:
    PARQUET_BLOCKSIZE = "256MiB"
    ROW_GROUP_SIZE = 250000       # Maximum throughput for High-Performance Workstations

DASK_READ_KWARGS = {
    "engine": "pyarrow",
    "blocksize": PARQUET_BLOCKSIZE,
    "split_row_groups": "infer",
    "dtype_backend": "pyarrow"  
}

if __name__ == "__main__":
    main()
```

---

### File: `reference_code/evaluator.py`

```py
import os
import glob
import logging
import numpy as np
import pandas as pd
import scipy.stats as stats
import quantstats as qs
from hmmlearn import hmm
import xgboost as xgb
import json

import config

logger = logging.getLogger(__name__)

class QuantitativeEvaluator:
    def __init__(self) -> None:
        self.min_dsr_threshold = 0.95
        
    def compute_deflated_sharpe_ratio(self, trial_matrix: pd.DataFrame, champion_returns: pd.Series) -> float:
        """
        Calculates the Deflated Sharpe Ratio (DSR) using Bailey and Lopez de Prado's framework.
        Corrects for non-normality and selection bias under multiple testing.
        """
        # 1. Base Sharpe & Moments
        champ_sr = champion_returns.mean() / champion_returns.std() if champion_returns.std() > 0 else 0.0
        skew = stats.skew(champion_returns)
        kurt = stats.kurtosis(champion_returns, fisher=True)
        
        # 2. Variance of trials
        trial_srs = trial_matrix.mean() / trial_matrix.std().replace(0, 1e-9)
        var_trials = np.var(trial_srs)
        N = trial_matrix.shape[3]
        
        # 3. Expected Maximum Sharpe Ratio
        euler_mascheroni = 0.5772156649
        expected_max_sr = np.sqrt(var_trials) * ((1.0 - euler_mascheroni) * stats.norm.ppf(1 - 1.0/N) + euler_mascheroni * stats.norm.ppf(1 - 1.0/(N * np.e)))
        
        # 4. Deflation Calculation
        T = len(champion_returns)
        denominator = np.sqrt(1 - skew * champ_sr + ((kurt - 1) / 4.0) * champ_sr**2)
        dsr_stat = (champ_sr - expected_max_sr) * np.sqrt(T - 1) / denominator
        
        return stats.norm.cdf(dsr_stat)

    def run_hmm_synthetic_gauntlet(self, sector_name: str, benchmark_returns: pd.Series) -> float:
        """
        Fits a Gaussian HMM to extract market regimes, simulates synthetic Monte Carlo paths, 
        and evaluates the champion model against data it has mathematically never seen.
        """
        model_path = os.path.join(config.PROD_MODELS_DIR, f"{sector_name}_candidate.json")
        features_path = os.path.join(config.PROD_MODELS_DIR, f"{sector_name}_candidate_features.json")
        
        if not os.path.exists(model_path): return 0.0
        
        booster = xgb.Booster()
        booster.load_model(model_path)
        with open(features_path, "r") as f: features = json.load(f)

        # 1. Extract underlying Market Regimes via HMM
        X_hmm = benchmark_returns.values.reshape(-1, 1)
        hmm_model = hmm.GaussianHMM(n_components=3, covariance_type="full", n_iter=100)
        hmm_model.fit(X_hmm)
        
        # 2. Generate Synthetic Returns Matrix
        synthetic_returns, _ = hmm_model.sample(n_samples=len(benchmark_returns))
        
        # 3. FIX: Eliminate Target Leakage via Historical Feature Bootstrapping
        # We randomly sample rows from the historical features (with replacement) to match 
        # the length of the synthetic returns, destroying any chronological look-ahead bias.
        historical_features_df = pd.read_parquet(config.PROCESSED_VAULT_DIR, columns=features)
        synthetic_df = historical_features_df.sample(n=len(synthetic_returns), replace=True).reset_index(drop=True)
        
        d_synth = xgb.DMatrix(synthetic_df)
        preds = 1.0 / (1.0 + np.exp(-booster.predict(d_synth)))
        signals = (preds > config.CONFIDENCE_THRESHOLD).astype(int)
        
        strategy_returns = signals * synthetic_returns.flatten()
        return np.mean(strategy_returns) / np.std(strategy_returns) if np.std(strategy_returns) > 0 else 0.0

    def assess_sector(self, sector_name: str) -> None:
        matrix_file = f"returns_matrix_{sector_name}.parquet"
        bench_file = f"benchmark_{sector_name}.parquet"
        
        if not os.path.exists(matrix_file) or not os.path.exists(bench_file): return
        
        trial_matrix = pd.read_parquet(matrix_file)
        bench_df = pd.read_parquet(bench_file)
        champion_returns = bench_df['champion']
        benchmark_returns = bench_df['benchmark']
        
        # Apply Business Date indexing for proper QuantStats annualization
        dummy_index = pd.bdate_range(end=config.END_DATE, periods=len(champion_returns))
        champion_returns.index = dummy_index
        benchmark_returns.index = dummy_index
        
        dsr = self.compute_deflated_sharpe_ratio(trial_matrix, champion_returns)
        synthetic_sr = self.run_hmm_synthetic_gauntlet(sector_name, benchmark_returns)
        
        logger.info(f"[{sector_name}] Probabilistic DSR: {dsr:.4f} | Synthetic HMM Sharpe: {synthetic_sr:.4f}")
        
        if dsr >= self.min_dsr_threshold and synthetic_sr > 0:
            logger.info(f"[{sector_name}] TRUE ALPHA DETECTED. Generalization proven. Promoting to production.")
            
            os.rename(
                os.path.join(config.PROD_MODELS_DIR, f"{sector_name}_candidate.json"),
                os.path.join(config.PROD_MODELS_DIR, f"{sector_name}_champion.json")
            )
            os.rename(
                os.path.join(config.PROD_MODELS_DIR, f"{sector_name}_candidate_features.json"),
                os.path.join(config.PROD_MODELS_DIR, f"{sector_name}_champion_features.json")
            )
            
            qs.reports.html(
                returns=champion_returns, benchmark=benchmark_returns, 
                title=f'Quantum Sentinel - {sector_name} Champion Profile (DSR: {dsr:.2f})', 
                output=f"tearsheet_{sector_name}.html"
            )
        else:
            logger.warning(f"[{sector_name}] REJECTED. Model failed quantitative rigors (Overfit or Memorization Trap).")
            
        os.remove(matrix_file)
        os.remove(bench_file)

    def run_evaluation_gauntlet(self) -> None:
        logger.info("=== COMMENCING DSR & SYNTHETIC GENERALIZATION EVALUATION ===")
        for matrix_file in glob.glob("returns_matrix_*.parquet"):
            sector = matrix_file.replace("returns_matrix_", "").replace(".parquet", "")
            self.assess_sector(sector)
```

---

### File: `reference_code/dashboard.py`

```py
import os
import pandas as pd
import pyarrow.parquet as pq
import streamlit as st
import plotly.express as px

import config

# ==============================================================================
# 1. PAGE CONFIGURATION & SECURITY GATE
# ==============================================================================
st.set_page_config(page_title="Quantum Sentinel Analytics Hub", layout="wide", page_icon="🛡️")

# Force strict HTTP verification layers directly within session allocations
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Quantum Workspace Security Gate")
    user_input = st.text_input("Username Identification Profile:")
    pass_input = st.text_input("Secret Clearance Authentication Key:", type="password")
    
    valid_user = os.environ.get("DASHBOARD_USER") 
    valid_pass = os.environ.get("DASHBOARD_PASS")
    
    if not valid_user or not valid_pass:
        st.error("CRITICAL: Security environment variables (DASHBOARD_USER / DASHBOARD_PASS) are missing.")
        st.stop()
        
    if st.button("Authenticate"):
        if user_input == valid_user and pass_input == valid_pass: 
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Authentication failed. Unauthorized access attempt logged.")
    st.stop()

# ==============================================================================
# 2. DATA INGESTION (PYARROW MEMORY MAPPING)
# ==============================================================================
@st.cache_data(ttl=30)
def fetch_live_ledger() -> pd.DataFrame:
    """Reads the partitioned live execution log utilizing PyArrow zero-copy backends."""
    if not os.path.exists(config.LIVE_LOG_DIR):
        return pd.DataFrame()
    try:
        dataset = pq.ParquetDataset(config.LIVE_LOG_DIR)
        return dataset.read().to_pandas()
    except Exception as e:
        st.error(f"Failed to read live ledger: {e}")
        return pd.DataFrame()

live_df = fetch_live_ledger()

# ==============================================================================
# 3. INTERACTIVE TABS & WORKSPACE
# ==============================================================================
st.title("🛡️ Quantum Sentinel Strategy Workspace")

# Dynamic Badges based on Argparse config
fusion_status = "🟢 ONLINE" if config.FUSION_ENABLED else "🔴 OFFLINE"
risk_status = "🟢 ONLINE" if config.RISK_MANAGER_ENABLED else "🔴 OFFLINE"
st.markdown(f"**LLM Fusion Agent:** {fusion_status} | **Risk Manager Agent:** {risk_status}")
st.markdown("---")

tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Executive Summary", 
    "🏆 Tournament Standings", 
    "📡 Live Activity & Veto Ledger", 
    "⚙️ System Health"
])

# ------------------------------------------------------------------------------
# TAB 1: EXECUTIVE SUMMARY (Dynamic Metrics)
# ------------------------------------------------------------------------------
with tab1:
    st.header("Executive Summary")
    if not live_df.empty:
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Market Evaluations", len(live_df))
        
        # Conditionally render LLM Sensor metrics
        if config.FUSION_ENABLED and 'sentiment' in live_df.columns:
            avg_sentiment = live_df['sentiment'].mean()
            col2.metric("Average LLM Sentiment", f"{avg_sentiment:.3f}")
        else:
            col2.metric("Average LLM Sentiment", "N/A (Fusion Offline)")

        # Conditionally render Risk Manager Veto metrics
        if config.RISK_MANAGER_ENABLED and 'signal' in live_df.columns:
            veto_count = len(live_df[live_df['signal'] == 'VETO'])
            col3.metric("Trades Intercepted by Shield", veto_count)
        else:
            col3.metric("Trades Intercepted by Shield", "N/A (Shield Offline)")
    else:
        st.info("Live execution ledger is currently empty. Awaiting market data.")

# ------------------------------------------------------------------------------
# TAB 2: TOURNAMENT STANDINGS & TEARSHEETS
# ------------------------------------------------------------------------------
with tab2:
    st.header("Quantitative Model Leaderboard")
    st.info("Champion models, feature manifolds, and DSR tearsheets are staged in the `production_models` directory.")

# ------------------------------------------------------------------------------
# TAB 3: LIVE ACTIVITY & VETO LEDGER
# ------------------------------------------------------------------------------
with tab3:
    st.header("Live Agent Telemetry Ledger")
    if not live_df.empty:
        # Sub-tab structure to clearly separate accepted vs blocked trades
        log_tab1, log_tab2 = st.tabs(["🟢 Executed Orders", "🛑 Veto Ledger"])
        
        with log_tab1:
            executed_df = live_df[live_df['signal'] == 'BUY']
            st.dataframe(executed_df, use_container_width=True)
            
        with log_tab2:
            if config.RISK_MANAGER_ENABLED:
                vetoed_df = live_df[live_df['signal'] == 'VETO']
                if not vetoed_df.empty:
                    st.warning("The following predictions were intercepted and canceled by the Risk Manager.")
                    # Only show relevant columns for clarity
                    st.dataframe(vetoed_df[['timestamp', 'ticker', 'probability', 'veto_reason']], use_container_width=True)
                else:
                    st.success("No trades have been vetoed today.")
            else:
                st.error("⚠️ Shield Agent is OFFLINE. Veto logic is bypassed.")
    else:
        st.info("No live telemetry found. Initiate live_trader.py to populate the ledger.")

# ------------------------------------------------------------------------------
# TAB 4: SYSTEM HEALTH
# ------------------------------------------------------------------------------
with tab4:
    st.header("System Orchestration & Environment Parameters")
    st.json({
        "Run Mode": config.RUN_MODE,
        "LLM Fusion Agent": config.FUSION_ENABLED,
        "Risk Manager Agent": config.RISK_MANAGER_ENABLED,
        "Max Drawdown Limit": f"{config.MAX_DAILY_DRAWDOWN * 100}%",
        "Target Premium Gain": f"{config.TARGET_PREMIUM_GAIN * 100}%",
        "Data Engine": "PyArrow Zero-Copy",
        "Parallelization": "Intel TBB + CUDA"
    })
```

---

### File: `reference_code/feature_compiler.py`

```py
import os
import re
import math
import json
import shutil
import asyncio
import aiohttp
import nest_asyncio
import logging
import numpy as np
import pandas as pd
import dask.dataframe as dd
import pandas_ta as ta
from numba import cuda

import config

# FIX: Allow asyncio.run() to operate securely inside Dask's existing worker event loops
nest_asyncio.apply()

logger = logging.getLogger(__name__)

# ==============================================================================
# 1. ASYNCHRONOUS ENTITY ANONYMIZATION & LLM INFERENCE (THE SENSOR)
# ==============================================================================
async def fetch_sentiment_async(semaphore: asyncio.Semaphore, session: aiohttp.ClientSession, headline: str, ticker: str) -> float:
    """
    Asynchronously queries the local LLM.
    Crucially utilizes Entity Anonymization to scrub the ticker from the text, 
    preventing the LLM from relying on memorized historical look-ahead bias.
    """
    if pd.isna(headline) or not str(headline).strip():
        return 0.0

    anonymized_headline = re.sub(rf'\b{ticker}\b', 'the company', str(headline), flags=re.IGNORECASE)

    payload = {
        "model": config.LLM_MODEL_NAME,
        "prompt": f"{config.LLM_SYSTEM_PROMPT}\n\nHeadline: {anonymized_headline}",
        "format": "json",
        "stream": False
    }

    # The semaphore acts as a traffic controller to prevent local GPU queue overflow
    async with semaphore:
        try:
            # Timeout increased slightly to accommodate local queuing
            async with session.post(config.OLLAMA_ENDPOINT, json=payload, timeout=10.0) as response:
                if response.status == 200:
                    result = await response.json()
                    data = json.loads(result.get("response", "{}"))
                    return float(data.get("sentiment_score", 0.0))
        except Exception:
            pass
            
    return 0.0

async def process_llm_batch_async(df: pd.DataFrame) -> list:
    """
    Batches HTTP requests to the local LLM concurrently across the pandas partition.
    """
    # Limit concurrent requests to 20 to protect the local Ollama server from crashing
    semaphore = asyncio.Semaphore(20)
    
    # TCPConnector limits the total active connections pooling
    connector = aiohttp.TCPConnector(limit=20, force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [
            fetch_sentiment_async(semaphore, session, str(row['raw_news_headline']), str(row['ticker']))
            for _, row in df.iterrows()
        ]
        return await asyncio.gather(*tasks)

# ==============================================================================
# 2. CUDA JIT KERNELS (VRAM FAST-MATH EXECUTION)
# ==============================================================================
# ... [Keep all existing @cuda.jit math kernels unchanged] ...

# ==============================================================================
# 3. DASK WORKER EXECUTION MAPPING
# ==============================================================================

def compute_partition_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies massive mechanical sensors to a localized data chunk. 
    Routes text to the CPU-bound LLM asynchronously before mapping structural math to the GPU.
    """
    if df.empty or len(df) < 252:
        return pd.DataFrame(columns=df.columns)
        
    df.columns = [c.lower() for c in df.columns]
    
    # -------------------------------------------------------------------------
    # STEP 1: BASE CPU ANALYTICS
    # -------------------------------------------------------------------------
    df['returns'] = df['close'].pct_change().fillna(0)
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
    df['adv_20'] = df['volume'].rolling(window=20).mean()
    
    # -------------------------------------------------------------------------
    # STEP 2: NaN PURGE
    # -------------------------------------------------------------------------
    # FIX: Purge NaNs BEFORE the LLM evaluation to prevent wasting API inference
    # compute on lookback rows that will be deleted anyway.
    df = df.dropna()

    # -------------------------------------------------------------------------
    # STEP 3: MULTI-AGENT HANDOFF: CPU-Bound Asynchronous LLM Sentiment
    # -------------------------------------------------------------------------
    if config.FUSION_ENABLED and 'raw_news_headline' in df.columns:
        sentiment_results = asyncio.run(process_llm_batch_async(df))
        df['sentiment_score'] = np.array(sentiment_results, dtype=np.float32)

    # -------------------------------------------------------------------------
    # STEP 4: VRAM MEMORY STAGING
    # -------------------------------------------------------------------------
    # Safely serialize PyArrow Extension Arrays into strict contiguous C-arrays for Numba VRAM 
    closes = np.ascontiguousarray(df['close'].to_numpy(dtype=np.float64))
    highs = np.ascontiguousarray(df['high'].to_numpy(dtype=np.float64))
    lows = np.ascontiguousarray(df['low'].to_numpy(dtype=np.float64))
    volumes = np.ascontiguousarray(df['volume'].to_numpy(dtype=np.float64))
    returns = np.ascontiguousarray(df['returns'].to_numpy(dtype=np.float64))
    atrs = np.ascontiguousarray(df['atr'].to_numpy(dtype=np.float64))
    advs = np.ascontiguousarray(df['adv_20'].to_numpy(dtype=np.float64))
    
    n = len(closes)
    
    spreads = np.zeros(n, dtype=np.float64)
    amihud = np.zeros(n, dtype=np.float64)
    ncskew = np.zeros(n, dtype=np.float64)
    duvol = np.zeros(n, dtype=np.float64)
    labels = np.zeros(n, dtype=np.int8)

    # PUSH MEMORY TO VRAM
    d_closes = cuda.to_device(closes)
    d_highs = cuda.to_device(highs)
    d_lows = cuda.to_device(lows)
    d_volumes = cuda.to_device(volumes)
    d_returns = cuda.to_device(returns)
    d_atrs = cuda.to_device(atrs)
    d_advs = cuda.to_device(advs)
    
    d_spreads = cuda.to_device(spreads)
    d_amihud = cuda.to_device(amihud)
    d_ncskew = cuda.to_device(ncskew)
    d_duvol = cuda.to_device(duvol)
    d_labels = cuda.to_device(labels)

    # KERNEL THREAD CONFIGURATION
    threads_per_block = 256
    blocks_per_grid = math.ceil(n / threads_per_block)

    # DISPATCH ASYNCHRONOUS KERNELS
    compute_roll_spread_cuda[blocks_per_grid, threads_per_block](d_closes, d_spreads, 20)
    compute_amihud_illiquidity_cuda[blocks_per_grid, threads_per_block](d_returns, d_closes, d_volumes, d_amihud, 20)
    compute_crash_risk_cuda[blocks_per_grid, threads_per_block](d_returns, d_ncskew, d_duvol, 60)
    
    cuda.synchronize()

    if config.RUN_MODE == "STANDARD":
        compute_friction_labels_cuda[blocks_per_grid, threads_per_block](
            d_closes, d_highs, d_lows, d_atrs, d_spreads, d_volumes, d_advs, d_labels, 2.0, 20
        )
        df['target_label'] = d_labels.copy_to_host()
    else:
        compute_options_labels_cuda[blocks_per_grid, threads_per_block](
            d_closes, d_atrs, d_labels, 21, 0.50
        )
        df['option_target_label'] = d_labels.copy_to_host()

    # PULL VRAM DATA BACK TO HOST RAM
    df['roll_spread'] = d_spreads.copy_to_host()
    df['amihud_illiq'] = d_amihud.copy_to_host()
    df['ncskew'] = d_ncskew.copy_to_host()
    df['duvol'] = d_duvol.copy_to_host()

    # If the LLM wasn't triggered, safely drop the raw text column so PyArrow Parquet doesn't bloat
    if 'raw_news_headline' in df.columns:
        df = df.drop(columns=['raw_news_headline'])

    return df

def compile_features_from_raw() -> None:
    """
    Orchestrates the offline Dask-powered transformation pipeline.
    """
    if not os.path.exists(config.RAW_VAULT_DIR):
        logger.error("Raw storage vault missing. Run ingestion sequence first.")
        return
        
    logger.info(f"Engaging CUDA compilation... (Fusion Mode: {'ON' if config.FUSION_ENABLED else 'OFF'})")
    reset_processed_vault()

    ddf = dd.read_parquet(config.RAW_VAULT_DIR, **config.DASK_READ_KWARGS)
    
    ddf_processed = ddf.map_partitions(compute_partition_features)

    ddf_processed.to_parquet(
        config.PROCESSED_VAULT_DIR,
        engine="pyarrow",
        partition_on=['sector'],
        write_metadata_file=False
    )
    logger.info(f"Data arrays safely exported to {config.PROCESSED_VAULT_DIR}.")
```

---

### File: `new_pipeline/main.py`

```py
import argparse
import json
from pathlib import Path

from new_pipeline.config import get_config
from new_pipeline.core.logging import configure_logging
from new_pipeline.data.vaults import VaultManager
from new_pipeline.monitoring.health import HealthCheck


def run_show_config() -> None:
    print(get_config().model_dump_json(indent=2))


def run_init_vaults() -> None:
    manager = VaultManager()
    raw, processed = manager.ensure_vaults()
    print(f"Raw vault: {raw}")
    print(f"Processed vault: {processed}")


def run_health() -> None:
    print(HealthCheck().status())


def run_pipeline() -> None:
    # Lazy import so the lightweight commands don't pull xgboost/hmmlearn.
    from new_pipeline.tournament.pipeline import run_offline_pipeline

    summary = run_offline_pipeline(get_config().models.candidate_models_dir)
    print(json.dumps(summary, indent=2))


def run_trade() -> None:
    """Drive promoted champions through the whole trade graph (training first if needed)."""
    from dataclasses import asdict

    from new_pipeline.evaluation.promotion import PromotionRegistry
    from new_pipeline.execution.runner import run_trading_session
    from new_pipeline.tournament.pipeline import run_offline_pipeline

    candidates = get_config().models.candidate_models_dir
    registry = PromotionRegistry(Path(candidates) / "promotion_registry.json")
    if not registry.active_champions():
        print("No champions yet — running the offline pipeline to produce them...")
        run_offline_pipeline(candidates)
    summary = run_trading_session(candidates)
    print(json.dumps(asdict(summary), indent=2))


_COMMANDS = {
    "show-config": run_show_config,
    "init-vaults": run_init_vaults,
    "health": run_health,
    "pipeline": run_pipeline,
    "trade": run_trade,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quantum Avenger CLI")
    parser.add_argument("command", choices=list(_COMMANDS), help="CLI command to execute")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    configure_logging()
    _COMMANDS[args.command]()

```

---

### File: `new_pipeline/requirements-dashboard.txt`

```markdown
# Dashboard tooling (Phase 6). Deliberately NOT installed by the SessionStart
# hook so remote-session startup stays lean. Install for the dashboard with:
#   pip install -r new_pipeline/requirements-dashboard.txt
streamlit>=1.36

```

---

### File: `new_pipeline/requirements-gpu.txt`

```markdown
# GPU-only dependencies for the production CUDA runtime.
# NOT installed by the SessionStart hook (these require a CUDA toolkit/driver
# and will not install on the CPU-only sandbox or CI). Install on a GPU box:
#   pip install -r new_pipeline/requirements-gpu.txt
# numba (CPU + CUDA dispatch) is already in requirements.txt; cupy is the GPU
# array library used by the feature kernels.
cupy-cuda12x>=13.0

```

---

### File: `new_pipeline/__init__.py`

```py
"""Quantum Avenger Phase 1 core pipeline package."""

__all__ = []

```

---

### File: `new_pipeline/setup.py`

```py
from setuptools import find_packages, setup

setup(
    name="quantum_avenger",
    version="0.1.0",
    packages=find_packages(include=["new_pipeline", "new_pipeline.*"]),
    install_requires=[
        "pydantic>=2.0",
        "pyyaml>=6.0",
        "numpy>=1.25",
    ],
    python_requires=">=3.11",
)

```

---

### File: `new_pipeline/requirements.txt`

```markdown
pydantic>=2.0
pytest>=8.0
pyyaml>=6.0
numpy>=1.25
pandas>=2.0
polars>=1.0
numba>=0.60
pyarrow>=15.0
xgboost>=2.0
scipy>=1.11
hmmlearn>=0.3
langgraph>=0.2
rank-bm25>=0.2
psutil>=5.9
dask[dataframe]>=2024.1

```

---

### File: `new_pipeline/README.md`

```markdown
# Quantum Avenger Phase 1 Pipeline

This directory contains the Phase 1 implementation scaffold for the Quantum Avenger hybrid trading system.

## Overview

Phase 1 builds the foundational pipeline infrastructure: configuration management, core utilities, data layer skeletons, logging, and test scaffolding.

## Getting Started

1. Create a Python virtual environment.
2. Install dependencies in `requirements.txt`.
3. Run `python -m pytest new_pipeline/tests`.

```

---

### File: `new_pipeline/requirements-dev.txt`

```markdown
# Development tooling for Quantum Avenger.
# Installed by the SessionStart hook (.claude/hooks/session-start.sh) so that
# linters work out of the box in Claude Code on the web sessions.
ruff>=0.15
pytest-cov>=5.0
matplotlib>=3.8  # backtest performance visualization (analysis/backtest.py)

```

---

### File: `new_pipeline/requirements-live.txt`

```markdown
# Live integration dependencies (Alpaca paper/live trading + market data + news).
# Deliberately NOT installed by the SessionStart hook — the offline dev/CI
# sandbox runs entirely on deterministic fakes and has no egress to Alpaca.
# Install on a host that is allowlisted for paper-api.alpaca.markets and
# data.alpaca.markets:
#   pip install -r new_pipeline/requirements-live.txt
# Credentials are provided via QA_ALPACA__API_KEY / QA_ALPACA__SECRET_KEY env
# vars and are never committed.
alpaca-py>=0.33

```

---

### File: `new_pipeline/pyproject.toml`

```toml
[project]
name = "quantum_avenger"
version = "0.1.0"
description = "Phase 1 core pipeline infrastructure for Quantum Avenger."
readme = "README.md"
requires-python = ">=3.11"

[project.dependencies]
pydantic = "^2.0"
pytest = "^8.0"
pyyaml = "^6.0"
numpy = "^1.25"

[project.urls]
homepage = "https://github.com/andrewweasel1/Quantum_Avenger"

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "W", "B", "UP"]
ignore = [
    # ValidationMode / RunMode intentionally subclass (str, Enum) for stable
    # JSON/YAML serialization; StrEnum would change str() output semantics.
    "UP042",
]

[tool.coverage.run]
source = ["new_pipeline"]
branch = true
omit = [
    # Live integrations: require alpaca-py + egress, absent from the offline CI
    # image, so they are exercised by mock-injected unit tests here but excluded
    # from the coverage gate (cf. the @pytest.mark.gpu kernels).
    "new_pipeline/adapters/market_alpaca.py",
    "new_pipeline/adapters/news_alpaca.py",
    "new_pipeline/adapters/broker_alpaca.py",
    "new_pipeline/scripts/live_smoke.py",
    "new_pipeline/scripts/ingest_training_data.py",
]

[tool.coverage.report]
show_missing = true
# A hard ">= 85%" gate is enforced in CI during Phase 7; left unset here so the
# suite stays green while later-phase modules are still being built.

```

---

### File: `new_pipeline/features/shields.py`

```py
"""The Shield Agent: a deterministic, Numba-compiled risk veto.

``evaluate_risk_veto_gates`` is the project's risk gate *of record*. It is
imported unchanged by three call sites — the Phase 3 t+1 backtest simulator,
the Phase 5 LangGraph Risk-Veto node, and the Phase 5 MCP risk tool — so risk
logic can never drift between backtest and live (the roadmap "central
invariant").

Five gates, evaluated in order; any failure vetoes the trade and returns a
zero position size:

  1. Stop validity   — a positive ATR stop distance exists.
  2. Position sizing — risk-based size rounds down to >= 1 share (Kelly-style).
  3. Liquidity       — order notional <= ``max_adv_coverage`` * ADV20.
  4. Slippage        — hydrodynamic estimate <= ``max_slippage_bps``.
  5. Reconciliation  — the order strictly increases the position.
"""

import math

from numba import njit

from new_pipeline.features.slippage import hydrodynamic_slippage_bps

DEFAULT_MAX_ADV_COVERAGE = 0.25
DEFAULT_SLIPPAGE_CONSTANT = 0.5
DEFAULT_MAX_SLIPPAGE_BPS = 50.0
DEFAULT_BPS_SCALER = 10000.0


@njit(fastmath=True, cache=True)
def calculate_kelly_position_size(
    entry_price, atr, atr_multiplier, account_capital, max_risk_pct
):
    """Risk-based share count: capital_at_risk / risk_per_share, capped by the
    affordable share count and floored to a whole number. 0 means "no trade"."""
    if entry_price <= 0.0 or atr <= 0.0 or atr_multiplier <= 0.0:
        return 0.0
    if account_capital <= 0.0 or max_risk_pct <= 0.0:
        return 0.0
    risk_per_share = atr_multiplier * atr
    size = (account_capital * max_risk_pct) / risk_per_share
    max_allowable = account_capital / entry_price
    if size > max_allowable:
        size = max_allowable
    size = math.floor(size)
    return size if size >= 1.0 else 0.0


@njit(fastmath=True, cache=True)
def enforce_volatility_stop(
    entry_price, atr, atr_multiplier, current_price, highest_price
):
    """Effective stop = max(hard ATR stop, trailing ATR stop). Returns
    ``(stop_level, triggered)`` where ``triggered`` is current_price <= stop."""
    hard_stop = entry_price - atr_multiplier * atr
    trailing_stop = highest_price - atr_multiplier * atr
    stop = hard_stop if hard_stop > trailing_stop else trailing_stop
    return stop, current_price <= stop


@njit(fastmath=True, cache=True)
def evaluate_risk_veto_gates(
    entry_price,
    atr,
    atr_multiplier,
    account_capital,
    max_risk_pct,
    current_qty,
    adv_20,
    volume_today,
    volatility,
    max_adv_coverage=DEFAULT_MAX_ADV_COVERAGE,
    slippage_constant=DEFAULT_SLIPPAGE_CONSTANT,
    max_slippage_bps=DEFAULT_MAX_SLIPPAGE_BPS,
    bps_scaler=DEFAULT_BPS_SCALER,
):
    """Run the five veto gates. Returns ``(approved, position_size)``."""
    # Gate 1: stop-loss validity.
    if entry_price <= 0.0 or atr <= 0.0 or atr_multiplier <= 0.0:
        return False, 0.0
    risk_per_share = atr_multiplier * atr
    stop_price = entry_price - risk_per_share
    if stop_price <= 0.0:
        return False, 0.0

    # Gate 2: risk-based (Kelly-style) position sizing.
    position_size = calculate_kelly_position_size(
        entry_price, atr, atr_multiplier, account_capital, max_risk_pct
    )
    if position_size < 1.0:
        return False, 0.0

    # Gate 3: liquidity — cap order notional at a fraction of ADV.
    order_notional = position_size * entry_price
    if adv_20 <= 0.0 or order_notional > adv_20 * max_adv_coverage:
        return False, 0.0

    # Gate 4: dynamic (hydrodynamic) slippage ceiling.
    slippage_bps = hydrodynamic_slippage_bps(
        order_notional, volatility, volume_today, slippage_constant, bps_scaler
    )
    if slippage_bps > max_slippage_bps:
        return False, 0.0

    # Gate 5: portfolio reconciliation — only add to the position.
    if position_size - current_qty <= 0.0:
        return False, 0.0

    return True, position_size

```

---

### File: `new_pipeline/features/slippage.py`

```py
"""Dynamic hydrodynamic slippage model:  S = c · σ · sqrt(Q / V).

Numba-compiled so the Shield Agent (also ``@njit``) can call it inside its veto
gates. ``Q`` is the order notional, ``V`` the traded volume over the same unit,
``σ`` the (annualized) volatility, and ``c`` a calibrated market-impact
constant. The result is scaled to basis points.
"""

import math

from numba import njit

DEFAULT_SLIPPAGE_CONSTANT = 0.5
DEFAULT_BPS_SCALER = 10000.0
HIGH_VOL_MULTIPLIER = 2.0
_NO_LIQUIDITY_BPS = 1.0e18  # forces a downstream veto when there is no volume


@njit(fastmath=True, cache=True)
def hydrodynamic_slippage_bps(
    order_notional,
    volatility,
    volume,
    constant=DEFAULT_SLIPPAGE_CONSTANT,
    bps_scaler=DEFAULT_BPS_SCALER,
):
    """Estimated slippage in basis points for an order of ``order_notional``."""
    if volume <= 0.0:
        return _NO_LIQUIDITY_BPS
    if order_notional <= 0.0 or volatility <= 0.0:
        return 0.0
    impact = constant * volatility * math.sqrt(order_notional / volume)
    return impact * bps_scaler


@njit(fastmath=True, cache=True)
def adjust_slippage_by_regime(
    base_bps,
    regime,
    normal_multiplier=1.0,
    high_vol_multiplier=HIGH_VOL_MULTIPLIER,
):
    """Scale slippage up in a high-volatility regime (``regime == 1``)."""
    if regime == 1:
        return base_bps * high_vol_multiplier
    return base_bps * normal_multiplier

```

---

### File: `new_pipeline/features/polars_engine.py`

```py
"""Vectorized feature engine built on Polars frames.

Computes the Phase 2 technical + microstructure feature set with no Python
loops (principle G2). Operates per ticker so rolling windows never bleed across
symbols. Required input columns: date, ticker, open, high, low, close, volume.

Scale (Tier 2): :meth:`PolarsFeatureEngine.compile` is out-of-core — it scans
the vault lazily and streams one ticker at a time, writing psutil-sized row
groups, so memory stays bounded. :func:`compile_features_dask` parallelizes a
pre-partitioned (one-file-per-ticker) vault via Dask.

Hygiene (G5): purge NaNs from bad *inputs* before calling this; the leading
nulls that rolling windows legitimately produce are left for the caller to drop.
"""

import math
from pathlib import Path

import polars as pl
import pyarrow.parquet as pq

from new_pipeline.core.exceptions import SchemaValidationError
from new_pipeline.data.sizing import dynamic_row_group_size
from new_pipeline.features.base import FeatureEngine
from new_pipeline.features.gpu_kernels import rolling_duvol, rolling_ncskew
from new_pipeline.features.registry import FeatureMetadata, feature_registry

ATR_PERIOD = 14
ADV_WINDOW = 20
VOL_WINDOW = 20
AMIHUD_WINDOW = 20
SPREAD_WINDOW = 20
CRASH_WINDOW = 60
TRADING_DAYS = 252
REGIME_QUANTILE = 0.8

FEATURE_NAMES = (
    "returns",
    "atr",
    "adv_20",
    "volatility",
    "spread_pct",
    "roll_spread",
    "amihud",
    "regime",
    "ncskew",
    "duvol",
    "sentiment_score",
)
_REQUIRED_COLUMNS = ("date", "ticker", "open", "high", "low", "close", "volume")


def _feature_metadata() -> dict[str, FeatureMetadata]:
    return {
        "returns": FeatureMetadata("returns", "Arithmetic daily return.", "price", "1d"),
        "atr": FeatureMetadata("atr", "Wilder ATR (RMA of true range).", "price", f"{ATR_PERIOD}d"),
        "adv_20": FeatureMetadata("adv_20", "Average dollar volume.", "volume", f"{ADV_WINDOW}d"),
        "volatility": FeatureMetadata(
            "volatility", "Annualized rolling volatility.", "price", f"{VOL_WINDOW}d"
        ),
        "spread_pct": FeatureMetadata("spread_pct", "High-low spread over mid.", "price", "1d"),
        "roll_spread": FeatureMetadata(
            "roll_spread", "Rolling mean high-low spread.", "price", f"{SPREAD_WINDOW}d"
        ),
        "amihud": FeatureMetadata("amihud", "Amihud illiquidity.", "volume", f"{AMIHUD_WINDOW}d"),
        "regime": FeatureMetadata(
            "regime", "High-volatility regime flag.", "price", f"{VOL_WINDOW}d", "int"
        ),
        "ncskew": FeatureMetadata(
            "ncskew", "Rolling NCSKEW crash-risk skewness.", "price", f"{CRASH_WINDOW}d"
        ),
        "duvol": FeatureMetadata(
            "duvol", "Rolling down-to-up volatility.", "price", f"{CRASH_WINDOW}d"
        ),
        "sentiment_score": FeatureMetadata(
            "sentiment_score", "LLM sentiment (neutral default until fusion runs).", "fusion", "1d"
        ),
    }


def add_features(frame: pl.DataFrame) -> pl.DataFrame:
    """Add the Phase 2 features to a single ticker's frame (sorted by date)."""
    prev_close = pl.col("close").shift(1)
    true_range = pl.max_horizontal(
        pl.col("high") - pl.col("low"),
        (pl.col("high") - prev_close).abs(),
        (pl.col("low") - prev_close).abs(),
    )
    mid = (pl.col("high") + pl.col("low")) / 2.0

    out = frame.sort("date").with_columns(
        pl.col("close").pct_change().alias("returns"),
        true_range.alias("_tr"),
        mid.alias("_mid"),
    )
    out = out.with_columns(
        pl.col("_tr").ewm_mean(alpha=1.0 / ATR_PERIOD, adjust=False).alias("atr"),
        (pl.col("_mid") * pl.col("volume")).rolling_mean(window_size=ADV_WINDOW).alias("adv_20"),
        (
            pl.col("returns").rolling_std(window_size=VOL_WINDOW) * math.sqrt(TRADING_DAYS)
        ).alias("volatility"),
        ((pl.col("high") - pl.col("low")) / pl.col("_mid")).alias("spread_pct"),
    )
    out = out.with_columns(
        pl.col("spread_pct").rolling_mean(window_size=SPREAD_WINDOW).alias("roll_spread"),
        (pl.col("returns").abs() / (pl.col("close") * pl.col("volume")))
        .rolling_mean(window_size=AMIHUD_WINDOW)
        .alias("amihud"),
        (pl.col("volatility") > pl.col("volatility").quantile(REGIME_QUANTILE))
        .cast(pl.Int8)
        .alias("regime"),
    )
    returns_np = out["returns"].fill_null(0.0).to_numpy()
    out = out.with_columns(
        pl.Series("ncskew", rolling_ncskew(returns_np, CRASH_WINDOW)),
        pl.Series("duvol", rolling_duvol(returns_np, CRASH_WINDOW)),
        pl.lit(0.0).alias("sentiment_score"),
    )
    return out.drop("_tr", "_mid")


def compile_features(frame: pl.DataFrame) -> pl.DataFrame:
    """Add features per ticker and recombine. Validates required columns first."""
    missing = [column for column in _REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise SchemaValidationError(f"Missing required columns: {missing}")
    groups = [
        add_features(group) for _, group in frame.group_by("ticker", maintain_order=True)
    ]
    return pl.concat(groups) if groups else frame


def _compile_file(path: str) -> pl.DataFrame:
    return add_features(pl.read_parquet(path))


def compile_features_dask(input_dir, output_path) -> None:
    """Parallel per-file feature compilation via Dask (each file = one ticker)."""
    import dask

    files = sorted(Path(input_dir).glob("*.parquet"))
    if not files:
        return
    frames = dask.compute(*[dask.delayed(_compile_file)(str(path)) for path in files])
    _stream_write(frames, output_path)


def _stream_write(frames, output_path) -> None:
    row_group_size = dynamic_row_group_size()
    writer = None
    try:
        for frame in frames:
            table = frame.to_arrow()
            if writer is None:
                writer = pq.ParquetWriter(str(output_path), table.schema)
            writer.write_table(table, row_group_size=row_group_size)
    finally:
        if writer is not None:
            writer.close()


class PolarsFeatureEngine(FeatureEngine):
    """FeatureEngine implementation backed by :func:`compile_features`."""

    def __init__(self) -> None:
        self._register_features()

    def compile(self, raw_path, processed_path) -> None:
        """Out-of-core: scan lazily and stream one ticker at a time to disk."""
        lazy = pl.scan_parquet(raw_path)
        tickers = lazy.select("ticker").unique().collect().to_series().to_list()
        featured = (
            add_features(lazy.filter(pl.col("ticker") == ticker).collect()) for ticker in tickers
        )
        _stream_write(featured, processed_path)

    def list_available_features(self) -> list[str]:
        return list(FEATURE_NAMES)

    def _register_features(self) -> None:
        # persist=False: keep the tracked registry YAML stable during runs/tests.
        for name, meta in _feature_metadata().items():
            if feature_registry.get(name) is None:
                feature_registry.register(name, meta, persist=False)

```

---

### File: `new_pipeline/features/gpu_kernels.py`

```py
"""GPU-targeted microstructure kernels with correct CPU fallbacks.

The production target is CUDA (``@cuda.jit`` + CuPy); this module also provides
NumPy CPU implementations so the metrics are correct and testable on a machine
with no GPU (CI / this sandbox). Host dispatchers use the GPU when it is
available and requested, otherwise the CPU path.

Metrics: per-bar spread, Amihud illiquidity, and the crash-risk pair NCSKEW
(negative coefficient of skewness) and DUVOL (down-to-up volatility) — provided
both as whole-series scalars and as vectorized rolling-window series. The
elementwise pair ship with ``@cuda.jit`` kernels; the reductions are vectorized
NumPy (GPU reductions are a follow-up to be validated on a GPU box).
"""

import math

import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

try:
    from numba import cuda

    _CUDA_IMPORTABLE = True
except Exception:  # pragma: no cover - import guard for environments w/o numba.cuda
    cuda = None
    _CUDA_IMPORTABLE = False


def gpu_available() -> bool:
    """True only when numba.cuda is importable AND a CUDA device is present."""
    if not _CUDA_IMPORTABLE:
        return False
    try:
        return bool(cuda.is_available())
    except Exception:  # pragma: no cover - driver probing
        return False


# --- CPU implementations (correct, tested) --------------------------------
def cpu_spread_pct(high: np.ndarray, low: np.ndarray) -> np.ndarray:
    high = np.asarray(high, dtype=np.float64)
    low = np.asarray(low, dtype=np.float64)
    mid = (high + low) / 2.0
    result = np.zeros_like(mid)
    np.divide(high - low, mid, out=result, where=mid > 0.0)
    return result


def cpu_amihud(returns: np.ndarray, close: np.ndarray, volume: np.ndarray) -> np.ndarray:
    returns = np.asarray(returns, dtype=np.float64)
    close = np.asarray(close, dtype=np.float64)
    volume = np.asarray(volume, dtype=np.float64)
    dollar_volume = close * volume
    result = np.zeros_like(dollar_volume)
    np.divide(np.abs(returns), dollar_volume, out=result, where=dollar_volume > 0.0)
    return result


def ncskew(returns: np.ndarray) -> float:
    """Negative coefficient of skewness (Chen-Hong-Stein crash-risk measure)."""
    values = np.asarray(returns, dtype=np.float64)
    n = values.size
    if n < 3:
        return 0.0
    centered = values - values.mean()
    sum_sq = float(np.sum(centered**2))
    if sum_sq <= 0.0:
        return 0.0
    sum_cube = float(np.sum(centered**3))
    numerator = n * (n - 1) ** 1.5 * sum_cube
    denominator = (n - 1) * (n - 2) * sum_sq**1.5
    return -numerator / denominator


def duvol(returns: np.ndarray) -> float:
    """Down-to-up volatility: log ratio of down-day vs up-day return variance."""
    values = np.asarray(returns, dtype=np.float64)
    centered = values - values.mean()
    down = centered[centered < 0.0]
    up = centered[centered >= 0.0]
    if down.size < 2 or up.size < 2:
        return 0.0
    down_var = float(np.sum(down**2))
    up_var = float(np.sum(up**2))
    if down_var <= 0.0 or up_var <= 0.0:
        return 0.0
    return math.log(((up.size - 1) * down_var) / ((down.size - 1) * up_var))


# --- Rolling crash-risk (vectorized; leading window-1 bars are NaN) --------
def rolling_ncskew(returns: np.ndarray, window: int) -> np.ndarray:
    values = np.asarray(returns, dtype=np.float64)
    n = values.size
    out = np.full(n, np.nan)
    if n < window or window < 3:
        return out
    windows = sliding_window_view(values, window)
    centered = windows - windows.mean(axis=1, keepdims=True)
    sum_sq = (centered**2).sum(axis=1)
    sum_cube = (centered**3).sum(axis=1)
    numerator = window * (window - 1) ** 1.5 * sum_cube
    denominator = (window - 1) * (window - 2) * np.power(sum_sq, 1.5)
    skew = np.divide(-numerator, denominator, out=np.zeros_like(sum_sq), where=sum_sq > 0.0)
    out[window - 1 :] = skew
    return out


def rolling_duvol(returns: np.ndarray, window: int) -> np.ndarray:
    values = np.asarray(returns, dtype=np.float64)
    n = values.size
    out = np.full(n, np.nan)
    if n < window or window < 4:
        return out
    windows = sliding_window_view(values, window)
    centered = windows - windows.mean(axis=1, keepdims=True)
    is_down = centered < 0.0
    down_count = is_down.sum(axis=1)
    up_count = window - down_count
    down_sum = (np.where(is_down, centered, 0.0) ** 2).sum(axis=1)
    up_sum = (np.where(~is_down, centered, 0.0) ** 2).sum(axis=1)
    valid = (down_count >= 2) & (up_count >= 2) & (down_sum > 0.0) & (up_sum > 0.0)
    ratio = np.divide(
        (up_count - 1) * down_sum,
        (down_count - 1) * up_sum,
        out=np.ones_like(down_sum),
        where=valid,
    )
    out[window - 1 :] = np.where(valid, np.log(ratio), 0.0)
    return out


# --- CUDA kernels (compiled lazily; exercised on a GPU box) ----------------
if _CUDA_IMPORTABLE:

    @cuda.jit
    def _spread_kernel(high, low, out):  # pragma: no cover - requires a GPU
        i = cuda.grid(1)
        if i < high.size:
            mid = (high[i] + low[i]) / 2.0
            out[i] = (high[i] - low[i]) / mid if mid > 0.0 else 0.0

    @cuda.jit
    def _amihud_kernel(returns, close, volume, out):  # pragma: no cover - requires a GPU
        i = cuda.grid(1)
        if i < returns.size:
            dollar_volume = close[i] * volume[i]
            out[i] = abs(returns[i]) / dollar_volume if dollar_volume > 0.0 else 0.0

    @cuda.jit
    def _rolling_ncskew_kernel(returns, window, out):  # pragma: no cover - requires a GPU
        i = cuda.grid(1)
        if i < window - 1 or i >= returns.size:
            return
        start = i - window + 1
        mean = 0.0
        for k in range(start, i + 1):
            mean += returns[k]
        mean /= window
        s2 = 0.0
        s3 = 0.0
        for k in range(start, i + 1):
            d = returns[k] - mean
            s2 += d * d
            s3 += d * d * d
        if s2 <= 0.0:
            out[i] = 0.0
        else:
            out[i] = -(window * (window - 1) ** 1.5 * s3) / ((window - 1) * (window - 2) * s2**1.5)

    @cuda.jit
    def _rolling_duvol_kernel(returns, window, out):  # pragma: no cover - requires a GPU
        i = cuda.grid(1)
        if i < window - 1 or i >= returns.size:
            return
        start = i - window + 1
        mean = 0.0
        for k in range(start, i + 1):
            mean += returns[k]
        mean /= window
        down_sum = 0.0
        up_sum = 0.0
        down_count = 0
        up_count = 0
        for k in range(start, i + 1):
            d = returns[k] - mean
            if d < 0.0:
                down_sum += d * d
                down_count += 1
            else:
                up_sum += d * d
                up_count += 1
        if down_count < 2 or up_count < 2 or down_sum <= 0.0 or up_sum <= 0.0:
            out[i] = 0.0
        else:
            out[i] = math.log(((up_count - 1) * down_sum) / ((down_count - 1) * up_sum))


def compute_rolling_ncskew(returns, window: int, use_gpu: bool = False) -> np.ndarray:
    if use_gpu and gpu_available():  # pragma: no cover - requires a GPU
        values = np.ascontiguousarray(returns, dtype=np.float64)
        out = np.full(values.size, np.nan)
        threads = 256
        blocks = (values.size + threads - 1) // threads
        device_out = cuda.to_device(out)
        _rolling_ncskew_kernel[blocks, threads](cuda.to_device(values), window, device_out)
        return device_out.copy_to_host()
    return rolling_ncskew(returns, window)


def compute_rolling_duvol(returns, window: int, use_gpu: bool = False) -> np.ndarray:
    if use_gpu and gpu_available():  # pragma: no cover - requires a GPU
        values = np.ascontiguousarray(returns, dtype=np.float64)
        out = np.full(values.size, np.nan)
        threads = 256
        blocks = (values.size + threads - 1) // threads
        device_out = cuda.to_device(out)
        _rolling_duvol_kernel[blocks, threads](cuda.to_device(values), window, device_out)
        return device_out.copy_to_host()
    return rolling_duvol(returns, window)


def _launch(kernel, size, *arrays):  # pragma: no cover - requires a GPU
    out = np.empty(size, dtype=np.float64)
    threads = 256
    blocks = (size + threads - 1) // threads
    device_args = [cuda.to_device(np.ascontiguousarray(a, dtype=np.float64)) for a in arrays]
    device_out = cuda.to_device(out)
    kernel[blocks, threads](*device_args, device_out)
    return device_out.copy_to_host()


def compute_spread_pct(high: np.ndarray, low: np.ndarray, use_gpu: bool = False) -> np.ndarray:
    if use_gpu and gpu_available():  # pragma: no cover - requires a GPU
        return _launch(_spread_kernel, high.size, high, low)
    return cpu_spread_pct(high, low)


def compute_amihud(
    returns: np.ndarray, close: np.ndarray, volume: np.ndarray, use_gpu: bool = False
) -> np.ndarray:
    if use_gpu and gpu_available():  # pragma: no cover - requires a GPU
        return _launch(_amihud_kernel, returns.size, returns, close, volume)
    return cpu_amihud(returns, close, volume)

```

---

### File: `new_pipeline/features/__init__.py`

```py
from .base import FeatureEngine
from .compiler import PandasFeatureCompiler
from .registry import FeatureRegistry

__all__ = ["FeatureEngine", "FeatureRegistry", "PandasFeatureCompiler"]

```

---

### File: `new_pipeline/features/compiler.py`

```py
from pathlib import Path

import pandas as pd

from new_pipeline.config import get_config
from new_pipeline.core.exceptions import IngestionError
from new_pipeline.data.vaults import VaultManager
from new_pipeline.features.base import FeatureEngine
from new_pipeline.features.registry import FeatureMetadata, feature_registry


class PandasFeatureCompiler(FeatureEngine):
    def __init__(self) -> None:
        self.config = get_config()
        self.vaults = VaultManager()
        self._register_features()

    def compile(self, raw_path: Path, processed_path: Path) -> None:
        if not raw_path.exists():
            raise IngestionError(f"Raw path does not exist: {raw_path}")

        processed_path.mkdir(parents=True, exist_ok=True)
        raw_files = list(raw_path.glob("*.csv"))

        for raw_file in raw_files:
            df = pd.read_csv(raw_file, parse_dates=["date"])
            df = self._validate_dataframe(df)
            df = self._compute_features(df)

            output_file = processed_path / raw_file.name
            df.to_csv(output_file, index=False)

    def list_available_features(self) -> list[str]:
        return feature_registry.list_features()

    def _register_features(self) -> None:
        for name, metadata in self._feature_definitions().items():
            if feature_registry.get(name) is None:
                feature_registry.register(name, metadata)

    @staticmethod
    def _feature_definitions() -> dict[str, FeatureMetadata]:
        return {
            "returns": FeatureMetadata(
                name="returns",
                description="Daily price return computed from close prices.",
                source="price",
                window="1d",
                dtype="float",
            ),
            "atr_14": FeatureMetadata(
                name="atr_14",
                description="14-day average true range for volatility scaling.",
                source="price",
                window="14d",
                dtype="float",
            ),
            "volatility_20": FeatureMetadata(
                name="volatility_20",
                description="20-day rolling standard deviation of returns.",
                source="price",
                window="20d",
                dtype="float",
            ),
            "average_volume_20": FeatureMetadata(
                name="average_volume_20",
                description="20-day moving average volume.",
                source="volume",
                window="20d",
                dtype="float",
            ),
        }

    def _validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        expected = {"date", "open", "high", "low", "close", "volume"}
        missing = expected.difference(df.columns)
        if missing:
            raise IngestionError(f"Missing required columns: {sorted(missing)}")
        return df.sort_values("date").reset_index(drop=True)

    def _compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df["returns"] = df["close"].pct_change().fillna(0.0)

        high_low = df["high"] - df["low"]
        high_close = (df["high"] - df["close"].shift(1)).abs()
        low_close = (df["low"] - df["close"].shift(1)).abs()
        df["atr_14"] = (
            pd.concat([high_low, high_close, low_close], axis=1)
            .max(axis=1)
            .rolling(14)
            .mean()
            .fillna(0.0)
        )

        df["volatility_20"] = df["returns"].rolling(window=20).std().fillna(0.0)
        df["average_volume_20"] = df["volume"].rolling(window=20).mean().fillna(0.0)

        return df

```

---

### File: `new_pipeline/features/registry.py`

```py
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml

from new_pipeline.config import get_config


@dataclass
class FeatureMetadata:
    name: str
    description: str
    source: str
    window: str | None = None
    dtype: str = "float"


class FeatureRegistry:
    METADATA_FILENAME = "feature_registry.yaml"

    def __init__(self) -> None:
        self._registry: dict[str, FeatureMetadata] = {}
        self._metadata_path = self._resolve_metadata_path()
        self._load_persistent_registry()

    def _resolve_metadata_path(self) -> Path:
        config = get_config()
        metadata_dir = Path(config.features.metadata_dir)
        metadata_dir.mkdir(parents=True, exist_ok=True)
        return metadata_dir / self.METADATA_FILENAME

    def _load_persistent_registry(self) -> None:
        if not self._metadata_path.exists():
            return

        with self._metadata_path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}

        for feature_name, metadata in payload.items():
            self.register(feature_name, metadata, persist=False)

    def register(
        self,
        feature_name: str,
        metadata: FeatureMetadata | dict[str, Any],
        persist: bool = True,
    ) -> None:
        if isinstance(metadata, dict):
            metadata = FeatureMetadata(**metadata)
        self._registry[feature_name] = metadata
        if persist:
            self.save()

    def get(self, feature_name: str) -> dict[str, Any] | None:
        metadata = self._registry.get(feature_name)
        return asdict(metadata) if metadata is not None else None

    def list_features(self) -> list[str]:
        return list(self._registry.keys())

    def clear(self) -> None:
        self._registry.clear()

    def save(self, path: Path | None = None) -> None:
        destination = path or self._metadata_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        payload = {name: asdict(metadata) for name, metadata in self._registry.items()}

        with destination.open("w", encoding="utf-8") as handle:
            yaml.safe_dump(payload, handle)

    def load(self, path: Path | None = None) -> None:
        source = path or self._metadata_path
        if not source.exists():
            return

        with source.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or {}

        self.clear()
        for feature_name, metadata in payload.items():
            self.register(feature_name, metadata, persist=False)


feature_registry = FeatureRegistry()

```

---

### File: `new_pipeline/features/base.py`

```py
from abc import ABC, abstractmethod
from pathlib import Path


class FeatureEngine(ABC):
    @abstractmethod
    def compile(self, raw_path: Path, processed_path: Path) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_available_features(self) -> list[str]:
        raise NotImplementedError

```

---

### File: `new_pipeline/features/labels.py`

```py
"""Friction-aware target-label generation (Phase 2/3).

``label[t] = 1`` if the forward return from ``t`` to ``t+horizon`` exceeds the
round-trip trading cost (in bps), else ``0``. The final ``horizon`` rows have no
forward window and are returned as NaN for the caller to drop.

The label is the supervised *target* (forward-looking by definition); feature
look-ahead hygiene is handled separately in the feature engine, and signal-side
look-ahead is handled by the t+1 backtest simulator.
"""

import numpy as np
import polars as pl


def friction_aware_labels(close, horizon: int = 1, cost_bps: float = 10.0) -> np.ndarray:
    """Binary label array: forward return over ``horizon`` beats round-trip cost."""
    prices = np.asarray(close, dtype=np.float64)
    n = prices.size
    labels = np.full(n, np.nan, dtype=np.float64)
    if horizon < 1 or n <= horizon:
        return labels
    forward_return = prices[horizon:] / prices[:-horizon] - 1.0
    labels[:-horizon] = (forward_return > cost_bps / 10000.0).astype(np.float64)
    return labels


def add_labels(frame: pl.DataFrame, horizon: int = 1, cost_bps: float = 10.0) -> pl.DataFrame:
    """Add a ``target_label`` column per ticker (sorted by date)."""
    groups = []
    for _, group in frame.sort("date").group_by("ticker", maintain_order=True):
        labels = friction_aware_labels(group["close"].to_numpy(), horizon, cost_bps)
        groups.append(group.with_columns(pl.Series("target_label", labels)))
    return pl.concat(groups) if groups else frame

```

---

### File: `new_pipeline/tournament/director.py`

```py
"""Per-sector tournament director — the Phase 3 end-to-end orchestration.

For each sector in the processed feature frame it (optionally) prunes features
with Clustered Feature Selection, runs the CPCV grid search, trains an
early-stopped candidate, and writes the candidate booster + feature manifest +
returns matrix under the candidates directory. Sectors are independent, so they
run in parallel on a thread pool (XGBoost releases the GIL during training) when
``max_workers > 1``. Restores the legacy ``execute_gauntlet`` loop.
"""

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

from new_pipeline.config import get_config
from new_pipeline.core.seeding import active_seed
from new_pipeline.tournament.feature_selection import select_orthogonal_features
from new_pipeline.tournament.grid_search import run_grid_search
from new_pipeline.tournament.simulator import sharpe_ratio, simulate_t1_returns
from new_pipeline.tournament.trainer import predict_proba, save_candidate, train_booster

_PRICE_COLUMNS = ("close", "low", "atr")
_MIN_ROWS = 40


def _slug(sector: str) -> str:
    return sector.lower().replace(" ", "_").replace("/", "_")


def _sharpe_score_fn(labels, prices, cfg):
    """A score_fn(feature_matrix) -> Sharpe used for CFS permutation importance."""
    rounds = min(40, cfg.tournament.num_boost_round)

    def score(matrix):
        booster = train_booster(
            matrix,
            labels,
            num_boost_round=rounds,
            penalty_fp=cfg.tournament.penalty_fp,
            penalty_fn=cfg.tournament.penalty_fn,
        )
        proba = predict_proba(booster, matrix)
        signals = (proba > cfg.execution.confidence_threshold).astype(np.int64)
        returns = simulate_t1_returns(
            signals,
            prices["close"],
            prices["low"],
            prices["atr"],
            cfg.execution.atr_stop_multiplier,
            cfg.execution.max_risk_per_trade,
        )
        return sharpe_ratio(returns)

    return score


def run_sector_tournament(frame, feature_cols, output_dir, use_cfs=True, max_workers=None):
    """Run the tournament per sector; returns a {sector: result} summary dict."""
    cfg = get_config()
    workers = max_workers if max_workers is not None else cfg.tournament.max_workers
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    required = [*feature_cols, "target_label", *_PRICE_COLUMNS]

    sectors = []
    for _, group in frame.group_by("sector", maintain_order=True):
        # Polars treats NaN as distinct from null; coerce so rolling/label NaNs drop.
        clean = group.with_columns(pl.col(required).fill_nan(None)).drop_nulls(subset=required)
        if clean.height >= _MIN_ROWS:
            sectors.append(clean)

    def work(clean):
        return _process_sector(clean, feature_cols, output, cfg, use_cfs)

    if workers and workers > 1 and len(sectors) > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            outcomes = list(pool.map(work, sectors))
    else:
        outcomes = [work(clean) for clean in sectors]
    return {sector: result for sector, result in outcomes}


def _process_sector(clean, feature_cols, output, cfg, use_cfs):
    sector = clean["sector"][0]
    labels = clean["target_label"].to_numpy().astype(np.float64)
    prices = {col: clean[col].to_numpy().astype(np.float64) for col in _PRICE_COLUMNS}
    matrix = clean.select(feature_cols).to_numpy()

    selected = list(feature_cols)
    if use_cfs and matrix.shape[1] > 1:
        selected = select_orthogonal_features(
            matrix,
            list(feature_cols),
            _sharpe_score_fn(labels, prices, cfg),
            distance_threshold=cfg.tournament.cfs_distance_threshold,
            min_importance=cfg.tournament.cfs_min_importance,
            seed=active_seed(),
        )
    selected_matrix = clean.select(selected).to_numpy()

    search = run_grid_search(selected_matrix, labels, prices)
    booster = _train_candidate(selected_matrix, labels, cfg)
    return sector, _persist(output, sector, booster, selected, search)


def _train_candidate(matrix, labels, cfg):
    split = int(len(labels) * 0.8)
    use_eval = len(labels) - split >= 10
    return train_booster(
        matrix[:split] if use_eval else matrix,
        labels[:split] if use_eval else labels,
        num_boost_round=cfg.tournament.num_boost_round,
        penalty_fp=cfg.tournament.penalty_fp,
        penalty_fn=cfg.tournament.penalty_fn,
        eval_features=matrix[split:] if use_eval else None,
        eval_labels=labels[split:] if use_eval else None,
        early_stopping_rounds=cfg.tournament.early_stopping_rounds,
    )


def _persist(output: Path, sector: str, booster, selected, search) -> dict:
    slug = _slug(sector)
    candidate_path = output / f"{slug}_candidate.json"
    features_path = output / f"{slug}_candidate_features.json"
    returns_path = output / f"{slug}_returns_matrix.parquet"

    save_candidate(booster, candidate_path)
    features_path.write_text(
        json.dumps(
            {"features": selected, "metadata": {"sector": sector, "params": search.best_params}},
            indent=2,
        ),
        encoding="utf-8",
    )
    matrix = search.returns_matrix
    pl.DataFrame(
        matrix.T, schema=[f"trial_{i}" for i in range(matrix.shape[0])]
    ).write_parquet(returns_path)

    return {
        "selected_features": selected,
        "best_params": search.best_params,
        "best_sharpe": search.best_sharpe,
        "trial_sharpes": search.trial_sharpes,
        "candidate_path": str(candidate_path),
    }

```

---

### File: `new_pipeline/tournament/objectives.py`

```py
"""Custom XGBoost objective: asymmetric financial loss.

False positives (wrong buys that lose capital) are penalized ``penalty_fp``x
relative to false negatives (missed trades). Gradient/Hessian are the standard
logistic ones scaled by the per-sample penalty.
"""

import numpy as np


def asymmetric_financial_loss(preds, dtrain, penalty_fp=5.0, penalty_fn=1.0):
    """XGBoost objective -> (grad, hess). ``preds`` are raw margins."""
    labels = dtrain.get_label()
    proba = 1.0 / (1.0 + np.exp(-preds))
    weight = np.where(labels == 0.0, penalty_fp, penalty_fn)
    grad = (proba - labels) * weight
    hess = proba * (1.0 - proba) * weight
    return grad, hess


def asymmetric_loss_factory(penalty_fp=5.0, penalty_fn=1.0):
    """Return a 2-arg XGBoost objective with the given penalties bound."""

    def _objective(preds, dtrain):
        return asymmetric_financial_loss(preds, dtrain, penalty_fp, penalty_fn)

    return _objective

```

---

### File: `new_pipeline/tournament/data_iterator.py`

```py
"""Zero-copy out-of-core feeding of Parquet row-groups to XGBoost.

Streams one Parquet row-group at a time into an ``xgb.QuantileDMatrix`` /
``xgb.ExtMemQuantileDMatrix`` so training never materializes the whole vault in
memory — the basis for the GPU out-of-core path (``cache_host_ratio``). Columns
are converted Arrow -> NumPy directly (no pandas materialization).
"""

import numpy as np
import pyarrow.parquet as pq
import xgboost as xgb


class ParquetDataIter(xgb.DataIter):
    def __init__(self, path, feature_columns, label_column):
        self._parquet = pq.ParquetFile(str(path))
        self._features = list(feature_columns)
        self._label = label_column
        self._row_group = 0
        super().__init__()

    def reset(self) -> None:
        self._row_group = 0

    def next(self, input_data) -> int:
        if self._row_group >= self._parquet.num_row_groups:
            return 0
        table = self._parquet.read_row_group(
            self._row_group, columns=[*self._features, self._label]
        )
        features = np.column_stack(
            [table.column(name).to_numpy(zero_copy_only=False) for name in self._features]
        ).astype(np.float64, copy=False)
        labels = table.column(self._label).to_numpy(zero_copy_only=False).astype(
            np.float64, copy=False
        )
        input_data(data=features, label=labels)
        self._row_group += 1
        return 1

```

---

### File: `new_pipeline/tournament/pipeline.py`

```py
"""Offline end-to-end pipeline orchestration (Phase 3 glue).

Assembles the full chain with no network: synthetic market data -> vectorized
features -> sector join + friction labels -> per-sector tournament -> Deflated
Sharpe + HMM promotion. The legacy multi-phase ``main`` flow, rebuilt offline.
"""

from datetime import date
from pathlib import Path

import numpy as np
import polars as pl

from new_pipeline.adapters import FakeMarketDataSource, StaticUniverseProvider
from new_pipeline.config import get_config
from new_pipeline.evaluation.dsr import compute_deflated_sharpe_ratio, probabilistic_sharpe_ratio
from new_pipeline.evaluation.haircut import haircut_sharpe_ratio
from new_pipeline.evaluation.hmm_gauntlet import run_hmm_synthetic_gauntlet
from new_pipeline.evaluation.minbtl import backtest_length_is_sufficient
from new_pipeline.evaluation.pbo import probability_of_backtest_overfitting
from new_pipeline.evaluation.promotion import PromotionRegistry, assess_promotion
from new_pipeline.features.labels import add_labels
from new_pipeline.features.polars_engine import compile_features
from new_pipeline.tournament.director import run_sector_tournament
from new_pipeline.tournament.simulator import sharpe_ratio
from new_pipeline.tournament.trainer import load_booster, predict_proba

FEATURE_COLS = [
    "returns", "atr", "adv_20", "volatility", "spread_pct", "roll_spread",
    "amihud", "ncskew", "duvol",
]


def build_training_frame(symbols, sectors, start, end, source=None, cfg=None) -> pl.DataFrame:
    """Synthetic OHLCV -> features -> sector join + target_label, one frame."""
    source = source or FakeMarketDataSource()
    cfg = cfg or get_config()
    rows = [
        {
            "date": bar.day, "ticker": symbol, "open": bar.open, "high": bar.high,
            "low": bar.low, "close": bar.close, "volume": bar.volume,
        }
        for symbol in symbols
        for bar in source.history(symbol, start, end)
    ]
    features = compile_features(pl.DataFrame(rows))
    labeled = add_labels(features, cfg.features.label_horizon, cfg.features.label_cost_bps)
    sector_df = pl.DataFrame(
        {"ticker": list(sectors), "sector": [sectors[t] for t in sectors]}
    )
    return labeled.join(sector_df, on="ticker", how="left")


def run_offline_pipeline(
    output_dir, start=date(2021, 1, 1), end=date(2022, 12, 31), max_symbols=None, source=None
) -> dict:
    cfg = get_config()
    sectors = StaticUniverseProvider().sectors()
    symbols = list(sectors)[: max_symbols] if max_symbols else list(sectors)
    frame = build_training_frame(symbols, sectors, start, end, source, cfg)
    results = run_sector_tournament(frame, FEATURE_COLS, output_dir)
    promotions = _evaluate_and_promote(frame, results, output_dir, cfg)
    return {"sectors": list(results), "promotions": promotions}


def _evaluate_and_promote(frame: pl.DataFrame, results: dict, output_dir, cfg) -> dict:
    registry = PromotionRegistry(Path(output_dir) / "promotion_registry.json")
    decisions: dict[str, bool] = {}
    for sector, result in results.items():
        trials = result["trial_sharpes"]
        if not trials:
            continue
        best = int(np.argmax(trials))
        returns_matrix = pl.read_parquet(result["candidate_path"].replace(
            "_candidate.json", "_returns_matrix.parquet"
        ))
        champion_returns = returns_matrix[:, best].to_numpy()

        dsr = compute_deflated_sharpe_ratio(champion_returns, trials)
        synthetic_sr = _synthetic_sharpe(frame, sector, result, champion_returns)
        # Overfitting/selection diagnostics over the full (n_obs x n_trials) matrix.
        champion_sharpe = sharpe_ratio(champion_returns)
        pbo = probability_of_backtest_overfitting(
            returns_matrix.to_numpy(), cfg.evaluation.pbo_partitions
        )
        psr = probabilistic_sharpe_ratio(champion_returns, cfg.evaluation.psr_benchmark_sr)
        haircut = haircut_sharpe_ratio(
            champion_sharpe, champion_returns.size, len(trials), cfg.evaluation.mt_method,
        ).adjusted_sharpe
        minbtl_ok = None
        if cfg.evaluation.enforce_minbtl:
            minbtl_ok = backtest_length_is_sufficient(
                champion_returns.size, len(trials), champion_sharpe
            )
        decision = assess_promotion(
            sector, dsr, synthetic_sr,
            cfg.evaluation.dsr_promotion_threshold, cfg.evaluation.synthetic_sr_min,
            pbo=pbo, pbo_threshold=cfg.evaluation.pbo_threshold,
            psr=psr, haircut_sharpe=haircut, minbtl_satisfied=minbtl_ok,
        )
        model_path = result["candidate_path"] if decision.promoted else None
        registry.record(decision, model_path=model_path)
        decisions[sector] = decision.promoted
    return decisions


def _synthetic_sharpe(frame, sector, result, champion_returns) -> float:
    booster = load_booster(result["candidate_path"])
    features = (
        frame.filter(pl.col("sector") == sector)
        .with_columns(pl.col(result["selected_features"]).fill_nan(None))
        .drop_nulls(subset=result["selected_features"])
        .select(result["selected_features"])
        .to_numpy()
    )
    if features.shape[0] < 10:
        return 0.0
    return run_hmm_synthetic_gauntlet(
        champion_returns, features, lambda matrix: predict_proba(booster, matrix), n_iter=20
    )

```

---

### File: `new_pipeline/tournament/__init__.py`

```py
from .cpcv import CPCVSplitGenerator
from .objectives import asymmetric_financial_loss, asymmetric_loss_factory
from .simulator import sharpe_ratio, simulate_t1_returns

__all__ = [
    "CPCVSplitGenerator",
    "asymmetric_financial_loss",
    "asymmetric_loss_factory",
    "sharpe_ratio",
    "simulate_t1_returns",
]

```

---

### File: `new_pipeline/tournament/simulator.py`

```py
"""t+1 risk-managed return simulation (no look-ahead).

Enters at ``close[i]`` when ``signal[i] == 1``, places an ATR stop, and realizes
the trade on the *next* bar: a stop-out returns the (negative) risk distance,
otherwise the close-to-close move — both scaled by the risk-based position
fraction. Shares the Shield Agent's stop/sizing math (``features.shields``) so
backtest and live risk stay consistent (the roadmap "central invariant").
"""

import numpy as np
from numba import njit


@njit(fastmath=True, cache=True)
def simulate_t1_returns(signals, close, low, atr, atr_multiplier, max_risk_pct):
    """Per-bar strategy returns; 0.0 on bars with no (or vetoed) entry."""
    n = close.shape[0]
    out = np.zeros(n, dtype=np.float64)
    for i in range(n - 1):
        if signals[i] != 1:
            continue
        entry = close[i]
        if entry <= 0.0 or atr[i] <= 0.0:
            continue
        stop = entry - atr_multiplier * atr[i]
        risk_distance = (entry - stop) / entry
        if risk_distance <= 0.0:
            continue
        size_fraction = max_risk_pct / risk_distance
        if size_fraction > 1.0:
            size_fraction = 1.0
        if low[i + 1] <= stop:
            out[i] = -risk_distance * size_fraction
        else:
            out[i] = (close[i + 1] - entry) / entry * size_fraction
    return out


def sharpe_ratio(returns: np.ndarray, periods: int = 252) -> float:
    """Annualized Sharpe of a per-bar return series (0 risk-free)."""
    series = np.asarray(returns, dtype=np.float64)
    if series.size < 2:
        return 0.0
    std = series.std(ddof=1)
    if std <= 0.0:
        return 0.0
    return float(series.mean() / std * np.sqrt(periods))

```

---

### File: `new_pipeline/tournament/feature_selection.py`

```py
"""Clustered Feature Selection (CFS) — keep orthogonal alpha, drop redundancy.

Restores the legacy pruning step: Spearman correlation -> correlation distance
-> Ward hierarchical clustering groups collinear features; within each cluster we
keep the single feature whose permutation drops the out-of-sample score the most,
provided that drop clears ``min_importance``. This removes redundant inputs while
preserving genuinely independent signal.
"""

from collections.abc import Callable

import numpy as np
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import squareform
from scipy.stats import spearmanr


def cluster_features(
    feature_matrix: np.ndarray, feature_names: list[str], distance_threshold: float = 0.5
) -> list[list[str]]:
    """Group features into clusters by Ward linkage on correlation distance."""
    matrix = np.asarray(feature_matrix, dtype=np.float64)
    if matrix.shape[1] <= 1:
        return [list(feature_names)]
    corr = np.atleast_2d(spearmanr(matrix).statistic)
    corr = np.nan_to_num(corr, nan=0.0)
    distance = np.sqrt(np.clip(0.5 * (1.0 - corr), 0.0, None))
    np.fill_diagonal(distance, 0.0)
    linkage_matrix = linkage(squareform(distance, checks=False), method="ward")
    cluster_ids = fcluster(linkage_matrix, t=distance_threshold, criterion="distance")
    clusters: dict[int, list[str]] = {}
    for name, cluster_id in zip(feature_names, cluster_ids, strict=True):
        clusters.setdefault(int(cluster_id), []).append(name)
    return list(clusters.values())


def select_orthogonal_features(
    feature_matrix: np.ndarray,
    feature_names: list[str],
    score_fn: Callable[[np.ndarray], float],
    distance_threshold: float = 0.5,
    min_importance: float = 0.0,
    seed: int = 0,
) -> list[str]:
    """Return surviving feature names: best per cluster by permutation importance.

    ``score_fn`` maps a feature matrix to an out-of-sample score (e.g. Sharpe);
    a feature's importance is the score drop when its column is shuffled.
    Falls back to all features if nothing clears ``min_importance``.
    """
    matrix = np.asarray(feature_matrix, dtype=np.float64)
    names = list(feature_names)
    base_score = score_fn(matrix)
    rng = np.random.default_rng(seed)

    survivors: list[str] = []
    for cluster in cluster_features(matrix, names, distance_threshold):
        best_name, best_importance = None, -np.inf
        for name in cluster:
            column = names.index(name)
            permuted = matrix.copy()
            permuted[:, column] = rng.permutation(permuted[:, column])
            importance = base_score - score_fn(permuted)
            if importance > best_importance:
                best_name, best_importance = name, importance
        if best_name is not None and best_importance >= min_importance:
            survivors.append(best_name)

    return survivors or names

```

---

### File: `new_pipeline/tournament/cpcv.py`

```py
"""Combinatorial Purged Cross-Validation (López de Prado).

Splits a time-ordered index into ``n_groups`` contiguous blocks and forms every
C(n_groups, test_groups) combination as a test set. Training rows within
``purge`` positions before, or ``embargo`` positions after, any test block are
dropped to kill look-ahead leakage. With the defaults (6 groups, 2 test) this
yields the canonical 15 folds.
"""

import itertools
import math
from dataclasses import dataclass

import numpy as np

from new_pipeline.core.exceptions import CPCVSplitError


@dataclass
class CPCVSplitGenerator:
    n_groups: int = 6
    test_groups: int = 2
    purge: int = 5
    embargo: int = 5

    @property
    def n_folds(self) -> int:
        return math.comb(self.n_groups, self.test_groups)

    def split(self, n_samples: int) -> list[tuple[np.ndarray, np.ndarray]]:
        """Return ``n_folds`` (train_idx, test_idx) integer-position pairs."""
        if n_samples < self.n_groups:
            raise CPCVSplitError(f"n_samples={n_samples} < n_groups={self.n_groups}")
        groups = np.array_split(np.arange(n_samples), self.n_groups)
        folds: list[tuple[np.ndarray, np.ndarray]] = []
        for combo in itertools.combinations(range(self.n_groups), self.test_groups):
            test_idx = np.concatenate([groups[g] for g in combo])
            forbidden = set(test_idx.tolist())
            for g in combo:
                block = groups[g]
                start, end = int(block[0]), int(block[-1])
                forbidden.update(range(max(0, start - self.purge), start))
                forbidden.update(range(end + 1, min(n_samples, end + 1 + self.embargo)))
            train_idx = np.array(
                [i for i in range(n_samples) if i not in forbidden], dtype=np.int64
            )
            self._validate(train_idx, np.sort(test_idx))
            folds.append((train_idx, np.sort(test_idx)))
        return folds

    @staticmethod
    def _validate(train_idx: np.ndarray, test_idx: np.ndarray) -> None:
        if np.intersect1d(train_idx, test_idx).size > 0:
            raise CPCVSplitError("CPCV produced overlapping train/test indices")

```

---

### File: `new_pipeline/tournament/trainer.py`

```py
"""XGBoost trainer for the tournament.

Targets the GPU in production (``device='cuda'`` + ``tree_method='hist'``) with
a one-line CPU fallback via config; trains with the asymmetric financial
objective. ``predict_proba`` applies the sigmoid the custom objective implies.
Early stopping is used when an eval set is supplied (a custom error metric is
needed because the custom objective has no built-in metric).
"""

import numpy as np
import xgboost as xgb

from new_pipeline.config import get_config
from new_pipeline.core.seeding import active_seed
from new_pipeline.tournament.objectives import asymmetric_loss_factory


def default_params(
    max_depth: int = 2,
    learning_rate: float = 0.05,
    device: str = "cpu",
    tree_method: str = "hist",
) -> dict:
    return {
        "max_depth": max_depth,
        "eta": learning_rate,
        "tree_method": tree_method,
        "device": device,
        "seed": active_seed(),
    }


def _error_metric(preds, dtrain):
    labels = dtrain.get_label()
    proba = 1.0 / (1.0 + np.exp(-preds))
    return "error", float(np.mean((proba > 0.5) != (labels > 0.5)))


def train_booster(
    features,
    labels,
    params=None,
    num_boost_round=100,
    penalty_fp=5.0,
    penalty_fn=1.0,
    eval_features=None,
    eval_labels=None,
    early_stopping_rounds=None,
):
    cfg = get_config().tournament
    if params is None:
        params = default_params(device=cfg.device, tree_method=cfg.tree_method)
    dtrain = xgb.DMatrix(
        np.asarray(features, dtype=np.float64), label=np.asarray(labels, dtype=np.float64)
    )
    objective = asymmetric_loss_factory(penalty_fp, penalty_fn)

    kwargs = {}
    if eval_features is not None and eval_labels is not None and early_stopping_rounds:
        dvalid = xgb.DMatrix(
            np.asarray(eval_features, dtype=np.float64),
            label=np.asarray(eval_labels, dtype=np.float64),
        )
        kwargs = {
            "evals": [(dvalid, "valid")],
            "custom_metric": _error_metric,
            "early_stopping_rounds": early_stopping_rounds,
            "verbose_eval": False,
        }
    return xgb.train(params, dtrain, num_boost_round=num_boost_round, obj=objective, **kwargs)


def predict_proba(booster, features) -> np.ndarray:
    margins = booster.predict(xgb.DMatrix(np.asarray(features, dtype=np.float64)))
    return 1.0 / (1.0 + np.exp(-margins))


def save_candidate(booster, path) -> None:
    booster.save_model(str(path))


def load_booster(path):
    booster = xgb.Booster()
    booster.load_model(str(path))
    return booster

```

---

### File: `new_pipeline/tournament/grid_search.py`

```py
"""Per-sector hyperparameter grid search over CPCV folds.

For each parameter combo, trains across all CPCV folds, simulates t+1 returns on
each out-of-sample test fold (via the Shield-consistent simulator), and scores
by out-of-sample Sharpe. Returns the best combo plus the stacked OOS returns
matrix (one row per combo) consumed downstream by the Deflated Sharpe Ratio.
"""

import itertools
from dataclasses import dataclass, field

import numpy as np

from new_pipeline.config import get_config
from new_pipeline.tournament.cpcv import CPCVSplitGenerator
from new_pipeline.tournament.simulator import sharpe_ratio, simulate_t1_returns
from new_pipeline.tournament.trainer import default_params, predict_proba, train_booster

_DEFAULT_GRID = {"max_depth": [1, 2], "learning_rate": [0.01, 0.05]}


@dataclass
class GridSearchResult:
    best_params: dict
    best_sharpe: float
    returns_matrix: np.ndarray  # shape (n_trials, n_samples)
    trial_sharpes: list[float] = field(default_factory=list)


def run_grid_search(features, labels, prices, grid=None, confidence_threshold=0.5):
    """``prices`` is a dict of equal-length 'close'/'low'/'atr' arrays."""
    cfg = get_config()
    grid = grid or _DEFAULT_GRID
    splitter = CPCVSplitGenerator(
        n_groups=cfg.tournament.n_groups,
        test_groups=cfg.tournament.test_groups,
        purge=cfg.tournament.purge_days,
        embargo=cfg.tournament.embargo_days,
    )
    folds = splitter.split(len(labels))
    combos = [dict(zip(grid, values, strict=True)) for values in itertools.product(*grid.values())]

    rows: list[np.ndarray] = []
    sharpes: list[float] = []
    for combo in combos:
        oos_sum = np.zeros(len(labels), dtype=np.float64)
        oos_count = np.zeros(len(labels), dtype=np.float64)
        for train_idx, test_idx in folds:
            params = default_params(
                max_depth=combo["max_depth"],
                learning_rate=combo["learning_rate"],
                device=cfg.tournament.device,
                tree_method=cfg.tournament.tree_method,
            )
            booster = train_booster(
                features[train_idx],
                labels[train_idx],
                params=params,
                num_boost_round=cfg.tournament.num_boost_round,
                penalty_fp=cfg.tournament.penalty_fp,
                penalty_fn=cfg.tournament.penalty_fn,
            )
            proba = predict_proba(booster, features[test_idx])
            signals = (proba > confidence_threshold).astype(np.int64)
            fold_returns = simulate_t1_returns(
                signals,
                prices["close"][test_idx],
                prices["low"][test_idx],
                prices["atr"][test_idx],
                cfg.execution.atr_stop_multiplier,
                cfg.execution.max_risk_per_trade,
            )
            oos_sum[test_idx] += fold_returns
            oos_count[test_idx] += 1.0
        oos = np.where(oos_count > 0.0, oos_sum / np.maximum(oos_count, 1.0), 0.0)
        rows.append(oos)
        sharpes.append(sharpe_ratio(oos))

    matrix = np.vstack(rows)
    best = int(np.argmax(sharpes))
    return GridSearchResult(
        best_params=combos[best],
        best_sharpe=sharpes[best],
        returns_matrix=matrix,
        trial_sharpes=sharpes,
    )

```

---

### File: `new_pipeline/adapters/news_alpaca.py`

```py
"""Live Alpaca news adapter (``NewsSource``).

Wraps alpaca-py's ``NewsClient`` behind the project's ABC, mapping Alpaca news
articles to the internal :class:`NewsItem` (timestamp + headline). Loaded lazily
by the adapter factory for a live ``run_mode``; requires egress to
``data.alpaca.markets``.
"""

from datetime import date, datetime, time

from alpaca.data.historical.news import NewsClient
from alpaca.data.requests import NewsRequest

from new_pipeline.adapters.base import NewsItem, NewsSource


class AlpacaNewsSource(NewsSource):
    def __init__(self, api_key, secret_key, limit: int = 10, client=None):
        self._client = client or NewsClient(api_key, secret_key)
        self._limit = limit

    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        request = NewsRequest(
            symbols=symbol,
            start=datetime.combine(on, time.min),
            end=datetime.combine(on, time.max),
            limit=self._limit,
            sort="desc",
        )
        newsset = self._client.get_news(request)
        articles = newsset.data.get("news", []) if hasattr(newsset, "data") else list(newsset)
        return [
            NewsItem(timestamp=article.created_at, symbol=symbol, headline=article.headline)
            for article in articles
        ]

```

---

### File: `new_pipeline/adapters/factory.py`

```py
"""Composition root: assemble the external adapters for a run (principle G4).

``build_adapters`` is the single place that decides whether the engine talks to
deterministic fakes or live SDKs, keyed off ``system.run_mode``. Today only the
offline modes are wired; the live modes raise a clear error pointing at the
adapters that still need implementing. The runner and orchestrator depend on the
returned bundle, never on a concrete client — so going live is a config flip
plus three adapter implementations, no change to the trade loop.
"""

from dataclasses import dataclass

from new_pipeline.adapters.base import LLMClient, MarketDataSource, NewsSource, UniverseProvider
from new_pipeline.adapters.fakes import (
    FakeBroker,
    FakeLLMClient,
    FakeMarketDataSource,
    FakeNewsSource,
)
from new_pipeline.adapters.universe_static import StaticUniverseProvider
from new_pipeline.execution.broker import BrokerAdapter

# Offline, network-free modes that resolve to deterministic fakes.
OFFLINE_MODES = frozenset({"offline", "backtest", "replay", "sim", "development", "testing"})
# Modes that require the live SDK adapters (not yet implemented).
LIVE_MODES = frozenset({"live", "paper", "production"})


@dataclass(frozen=True)
class AdapterBundle:
    market_data: MarketDataSource
    news: NewsSource
    llm: LLMClient
    broker: BrokerAdapter
    universe: UniverseProvider


def build_adapters(cfg) -> AdapterBundle:
    """Return the adapter bundle for ``cfg.system.run_mode``."""
    mode = (cfg.system.run_mode or "offline").lower()
    if mode in OFFLINE_MODES:
        return AdapterBundle(
            market_data=FakeMarketDataSource(),
            news=FakeNewsSource(),
            llm=FakeLLMClient(),
            broker=FakeBroker(),
            universe=StaticUniverseProvider(),
        )
    if mode in LIVE_MODES:
        if not (cfg.alpaca.api_key and cfg.alpaca.secret_key):
            raise ValueError(
                f"run_mode={mode!r} requires QA_ALPACA__API_KEY and "
                "QA_ALPACA__SECRET_KEY (never commit them)."
            )
        return _build_live_adapters(cfg)
    raise ValueError(f"unknown run_mode: {mode!r}")


def _build_live_adapters(cfg) -> AdapterBundle:  # pragma: no cover - needs the live SDK + egress
    """Assemble the live Alpaca adapters (lazy SDK import keeps offline runs clean).

    The LLM stays the deterministic fake until an Ollama endpoint is configured —
    Alpaca covers market data, news, and order execution. Going fully live is a
    drop-in LLM client here, no change elsewhere.
    """
    from new_pipeline.adapters.broker_alpaca import AlpacaBroker
    from new_pipeline.adapters.market_alpaca import AlpacaMarketDataSource
    from new_pipeline.adapters.news_alpaca import AlpacaNewsSource

    creds = (cfg.alpaca.api_key, cfg.alpaca.secret_key)
    return AdapterBundle(
        market_data=AlpacaMarketDataSource(*creds, feed=cfg.alpaca.data_feed),
        news=AlpacaNewsSource(*creds),
        llm=FakeLLMClient(),
        broker=AlpacaBroker(*creds, paper=cfg.alpaca.paper),
        universe=StaticUniverseProvider(),
    )

```

---

### File: `new_pipeline/adapters/fakes.py`

```py
"""Deterministic, offline implementations of the adapter interfaces.

Used by dev and the entire test suite so no phase needs a network or live
credentials (G4). Every output is a pure function of its inputs — same call,
same result — which keeps tests reproducible (G6).
"""

import math
from datetime import date, datetime, timedelta

from new_pipeline.adapters.base import (
    Bar,
    LLMClient,
    MarketDataSource,
    NewsItem,
    NewsSource,
    SentimentResult,
    Verdict,
)
from new_pipeline.execution.broker import BrokerAdapter

_STANCE_BY_LABEL = {"bullish": "BULLISH", "bearish": "BEARISH", "neutral": "NEUTRAL"}


def _stable_unit(text: str) -> float:
    """Map text to a deterministic value in [-1.0, 1.0]."""
    total = sum(ord(char) for char in text)
    return ((total % 2001) - 1000) / 1000.0


class FakeLLMClient(LLMClient):
    def sentiment(self, text: str) -> SentimentResult:
        score = _stable_unit(text)
        if score > 0.1:
            label = "bullish"
        elif score < -0.1:
            label = "bearish"
        else:
            label = "neutral"
        return SentimentResult(score=score, label=label)

    def verdict(self, prompt: str) -> Verdict:
        stance = _STANCE_BY_LABEL[self.sentiment(prompt).label]
        return Verdict(stance=stance, rationale="deterministic fake verdict")


class FakeMarketDataSource(MarketDataSource):
    """Synthetic but well-formed OHLCV: a smooth sinusoid + drift, fully
    deterministic in the symbol and date (no RNG)."""

    def __init__(self, base_price: float = 100.0) -> None:
        self._base_price = base_price

    def history(self, symbol: str, start: date, end: date) -> list[Bar]:
        if end < start:
            return []
        anchor = (sum(ord(char) for char in symbol) % 50) + self._base_price
        bars: list[Bar] = []
        day = start
        i = 0
        while day <= end:
            close = anchor + 5.0 * math.sin(i / 7.0) + 0.05 * i
            open_ = anchor + 5.0 * math.sin((i - 1) / 7.0) + 0.05 * (i - 1)
            high = max(open_, close) + 1.0
            low = min(open_, close) - 1.0
            bars.append(
                Bar(
                    day=day,
                    open=round(open_, 4),
                    high=round(high, 4),
                    low=round(low, 4),
                    close=round(close, 4),
                    volume=1_000_000 + (i % 13) * 10_000,
                )
            )
            day += timedelta(days=1)
            i += 1
        return bars


class FakeNewsSource(NewsSource):
    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        return [
            NewsItem(
                timestamp=datetime(on.year, on.month, on.day),
                symbol=symbol,
                headline=f"{symbol} steady as markets digest data on {on.isoformat()}.",
            )
        ]


class FakeBroker(BrokerAdapter):
    """In-memory broker: records orders and tracks net positions."""

    def __init__(self) -> None:
        self._orders: list[dict] = []
        self._positions: dict[str, float] = {}

    def submit_order(self, order: dict) -> dict:
        symbol = str(order.get("symbol", ""))
        qty = float(order.get("qty", 0.0))
        side = str(order.get("side", "buy")).lower()
        signed = qty if side == "buy" else -qty
        self._positions[symbol] = self._positions.get(symbol, 0.0) + signed
        receipt = {
            "status": "filled",
            "order_id": f"fake-{len(self._orders) + 1}",
            **order,
        }
        self._orders.append(receipt)
        return receipt

    def get_positions(self) -> dict[str, float]:
        return dict(self._positions)

    @property
    def orders(self) -> list[dict]:
        return list(self._orders)

```

---

### File: `new_pipeline/adapters/broker_alpaca.py`

```py
"""Live Alpaca broker adapter (``BrokerAdapter``).

Wraps alpaca-py's ``TradingClient`` (paper by default) behind the project's
broker ABC. ``submit_order`` builds a market or limit order from the same dict
the orchestrator hands the fake broker and maps the Alpaca ``Order`` back to the
receipt shape the orchestrator/trade-log expect. Loaded lazily for a live
``run_mode``; requires egress to ``paper-api.alpaca.markets``.
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.trading.requests import LimitOrderRequest, MarketOrderRequest

from new_pipeline.execution.broker import BrokerAdapter

_SIDE = {"buy": OrderSide.BUY, "sell": OrderSide.SELL}
_TIF = {
    "day": TimeInForce.DAY,
    "gtc": TimeInForce.GTC,
    "ioc": TimeInForce.IOC,
    "fok": TimeInForce.FOK,
    "opg": TimeInForce.OPG,
    "cls": TimeInForce.CLS,
}


class AlpacaBroker(BrokerAdapter):
    def __init__(self, api_key, secret_key, paper: bool = True, client=None):
        self._client = client or TradingClient(api_key, secret_key, paper=paper)

    def submit_order(self, order: dict) -> dict:
        symbol = str(order["symbol"])
        qty = int(order.get("qty", 0))
        side = _SIDE[str(order.get("side", "buy")).lower()]
        tif = _TIF.get(str(order.get("tif", "day")).lower(), TimeInForce.DAY)
        limit_price = order.get("limit_price")
        if limit_price is not None:
            request = LimitOrderRequest(
                symbol=symbol, qty=qty, side=side, time_in_force=tif,
                limit_price=round(float(limit_price), 2),
            )
        else:
            request = MarketOrderRequest(symbol=symbol, qty=qty, side=side, time_in_force=tif)

        placed = self._client.submit_order(order_data=request)
        return {
            "status": _value(placed.status),
            "order_id": str(placed.id),
            "symbol": placed.symbol,
            "qty": float(placed.qty) if placed.qty is not None else float(qty),
            "side": _value(placed.side),
            "limit_price": float(placed.limit_price) if placed.limit_price is not None else None,
            "filled_avg_price": float(placed.filled_avg_price) if placed.filled_avg_price else 0.0,
        }

    def get_positions(self) -> dict[str, float]:
        positions: dict[str, float] = {}
        for pos in self._client.get_all_positions():
            qty = float(pos.qty)
            positions[pos.symbol] = qty if _value(pos.side).lower() == "long" else -qty
        return positions

    def account(self) -> dict:
        """Account snapshot — confirms connectivity and that it's the paper account."""
        acct = self._client.get_account()
        return {
            "status": _value(acct.status),
            "cash": float(acct.cash),
            "equity": float(acct.equity),
            "buying_power": float(acct.buying_power),
        }


def _value(enum_or_str) -> str:
    """Unwrap an Alpaca enum (``.value``) or pass a plain string through."""
    return getattr(enum_or_str, "value", str(enum_or_str))

```

---

### File: `new_pipeline/adapters/__init__.py`

```py
from .base import (
    Bar,
    LLMClient,
    MarketDataSource,
    NewsItem,
    NewsSource,
    SentimentResult,
    UniverseMember,
    UniverseProvider,
    Verdict,
)
from .fakes import FakeBroker, FakeLLMClient, FakeMarketDataSource, FakeNewsSource
from .universe_static import StaticUniverseProvider

__all__ = [
    "Bar",
    "FakeBroker",
    "FakeLLMClient",
    "FakeMarketDataSource",
    "FakeNewsSource",
    "LLMClient",
    "MarketDataSource",
    "NewsItem",
    "NewsSource",
    "SentimentResult",
    "StaticUniverseProvider",
    "UniverseMember",
    "UniverseProvider",
    "Verdict",
]

```

---

### File: `new_pipeline/adapters/universe_static.py`

```py
"""Offline, survivorship-safe universe loaded from a point-in-time CSV fixture.

Implements :class:`UniverseProvider` over ``data/universe/membership.csv``
(`ticker, gics_sector, start_date, end_date`). A licensed real point-in-time
membership dataset can replace the fixture with no code change.
"""

import csv
from datetime import date
from pathlib import Path

from new_pipeline.adapters.base import UniverseMember, UniverseProvider
from new_pipeline.core.exceptions import UniverseError
from new_pipeline.core.paths import data_dir

DEFAULT_MEMBERSHIP_PATH = data_dir() / "universe" / "membership.csv"


def _parse_optional_date(value: str | None) -> date | None:
    if value is None:
        return None
    value = value.strip()
    return date.fromisoformat(value) if value else None


class StaticUniverseProvider(UniverseProvider):
    def __init__(self, membership_path: Path | None = None) -> None:
        self._path = membership_path or DEFAULT_MEMBERSHIP_PATH
        self._members = self._load()

    def _load(self) -> list[UniverseMember]:
        if not self._path.exists():
            raise UniverseError(f"Universe membership fixture not found: {self._path}")
        members: list[UniverseMember] = []
        with open(self._path, encoding="utf-8", newline="") as handle:
            for row in csv.DictReader(handle):
                members.append(
                    UniverseMember(
                        ticker=row["ticker"].strip(),
                        gics_sector=row["gics_sector"].strip(),
                        start_date=date.fromisoformat(row["start_date"].strip()),
                        end_date=_parse_optional_date(row.get("end_date")),
                    )
                )
        if not members:
            raise UniverseError(f"Universe membership fixture is empty: {self._path}")
        return members

    def members(self, as_of: date | None = None) -> list[UniverseMember]:
        if as_of is None:
            return list(self._members)
        return [member for member in self._members if member.active_on(as_of)]

```

---

### File: `new_pipeline/adapters/base.py`

```py
"""Adapter interfaces for every external boundary (principle G4).

The pipeline never imports a live SDK directly; it depends on these ABCs and is
handed a concrete implementation — a deterministic fake in dev/tests, a live
client in production. This keeps all 7 phases unit-testable with no network.

``BrokerAdapter`` deliberately stays in :mod:`new_pipeline.execution.broker`
(its original home); the fakes/live brokers implement that interface.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True)
class SentimentResult:
    score: float  # normalized to [-1.0, 1.0]
    label: str  # "bullish" | "bearish" | "neutral"


@dataclass(frozen=True)
class Verdict:
    stance: str  # "BULLISH" | "BEARISH" | "NEUTRAL"
    rationale: str


@dataclass(frozen=True)
class NewsItem:
    timestamp: datetime
    symbol: str
    headline: str


@dataclass(frozen=True)
class Bar:
    day: date
    open: float
    high: float
    low: float
    close: float
    volume: int


@dataclass(frozen=True)
class UniverseMember:
    ticker: str
    gics_sector: str
    start_date: date
    end_date: date | None = None

    def active_on(self, as_of: date) -> bool:
        """True if the member is in the index on ``as_of`` (end is exclusive)."""
        return self.start_date <= as_of and (self.end_date is None or as_of < self.end_date)


class LLMClient(ABC):
    """Sentiment + verdict generation. The LLM never computes risk/quant
    numbers (G1) — those go through deterministic tools."""

    @abstractmethod
    def sentiment(self, text: str) -> SentimentResult:
        raise NotImplementedError

    @abstractmethod
    def verdict(self, prompt: str) -> Verdict:
        raise NotImplementedError


class MarketDataSource(ABC):
    @abstractmethod
    def history(self, symbol: str, start: date, end: date) -> list[Bar]:
        raise NotImplementedError


class NewsSource(ABC):
    @abstractmethod
    def headlines(self, symbol: str, on: date) -> list[NewsItem]:
        raise NotImplementedError


class UniverseProvider(ABC):
    """Point-in-time, survivorship-safe trading universe."""

    @abstractmethod
    def members(self, as_of: date | None = None) -> list[UniverseMember]:
        raise NotImplementedError

    def symbols(self, as_of: date | None = None) -> list[str]:
        return [member.ticker for member in self.members(as_of)]

    def sectors(self, as_of: date | None = None) -> dict[str, str]:
        return {member.ticker: member.gics_sector for member in self.members(as_of)}

```

---

### File: `new_pipeline/adapters/market_alpaca.py`

```py
"""Live Alpaca market-data adapter (``MarketDataSource``).

Wraps alpaca-py's ``StockHistoricalDataClient`` behind the project's ABC, mapping
Alpaca daily bars to the internal :class:`Bar`. Built only for a live
``run_mode`` (offline runs use the deterministic fake), so this module — and the
``alpaca`` import — is loaded lazily by the adapter factory. Requires egress to
``data.alpaca.markets`` at call time; the free IEX feed is the default.
"""

from datetime import date, datetime, time

from alpaca.data.enums import Adjustment, DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from new_pipeline.adapters.base import Bar, MarketDataSource


class AlpacaMarketDataSource(MarketDataSource):
    def __init__(self, api_key, secret_key, feed="iex", adjustment="all", client=None):
        self._client = client or StockHistoricalDataClient(api_key, secret_key)
        self._feed = DataFeed(feed)
        self._adjustment = Adjustment(adjustment)

    def history(self, symbol: str, start: date, end: date) -> list[Bar]:
        request = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=TimeFrame.Day,
            start=datetime.combine(start, time.min),
            end=datetime.combine(end, time.max),
            feed=self._feed,
            adjustment=self._adjustment,
        )
        barset = self._client.get_stock_bars(request)
        bars = barset.data.get(symbol, []) if hasattr(barset, "data") else list(barset[symbol])
        return [
            Bar(
                day=bar.timestamp.date(),
                open=float(bar.open),
                high=float(bar.high),
                low=float(bar.low),
                close=float(bar.close),
                volume=int(bar.volume),
            )
            for bar in bars
        ]

```

---

### File: `new_pipeline/core/circuit_breaker.py`

```py
"""Circuit breaker for guarding flaky external calls (LLM, broker, market data).

Complements :mod:`new_pipeline.utils.retry`: retries handle transient blips,
while the breaker fails fast and stops hammering a dependency that is hard-down
until a recovery window has elapsed.
"""

import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, TypeVar

from new_pipeline.core.exceptions import CircuitBreakerError

T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Three-state breaker.

    CLOSED → OPEN once ``failure_threshold`` consecutive failures occur → after
    ``recovery_timeout`` seconds the next call is allowed as HALF_OPEN → success
    closes the circuit, another failure re-opens it. ``clock`` is injectable for
    deterministic testing.
    """

    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    name: str = "circuit"
    clock: Callable[[], float] = time.monotonic
    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failures: int = field(default=0, init=False)
    _opened_at: float = field(default=0.0, init=False)

    @property
    def state(self) -> CircuitState:
        return self._state

    @property
    def failure_count(self) -> int:
        return self._failures

    def call(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Invoke ``func`` through the breaker, enforcing the current state."""
        if self._state is CircuitState.OPEN:
            if (self.clock() - self._opened_at) >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerError(f"Circuit '{self.name}' is open")

        try:
            result = func(*args, **kwargs)
        except Exception:
            self._record_failure()
            raise
        self._record_success()
        return result

    def _record_success(self) -> None:
        self._failures = 0
        self._state = CircuitState.CLOSED

    def _record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.failure_threshold:
            self._state = CircuitState.OPEN
            self._opened_at = self.clock()

```

---

### File: `new_pipeline/core/seeding.py`

```py
"""Central reproducibility helper.

A single :func:`seed_everything` call seeds every RNG source the pipeline uses
so backtests, model training, and tests are deterministic (principle G6). Heavy
optional libraries (e.g. ``torch``) are seeded only when importable, keeping the
offline / CPU-only sandbox lightweight.
"""

import os
import random

import numpy as np

DEFAULT_SEED = 42

_active_seed = DEFAULT_SEED


def seed_everything(seed: int = DEFAULT_SEED) -> int:
    """Seed all known RNG sources and return the seed that was applied."""
    global _active_seed
    _active_seed = seed
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    _seed_torch(seed)
    return seed


def active_seed() -> int:
    """Return the most recently applied seed."""
    return _active_seed


def _seed_torch(seed: int) -> None:
    """Seed torch if it is installed; a no-op otherwise."""
    try:
        import torch
    except ImportError:
        return
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

```

---

### File: `new_pipeline/core/paths.py`

```py
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def project_root() -> Path:
    return PROJECT_ROOT


def data_dir() -> Path:
    return PROJECT_ROOT / "data"


def logs_dir() -> Path:
    return PROJECT_ROOT / "logs"

```

---

### File: `new_pipeline/core/exceptions.py`

```py
"""Exception hierarchy for Quantum Avenger.

Everything derives from :class:`QuantumAvengerError` so callers can catch the
whole family. Leaves are grouped by pipeline area; risk/broker/order failures
derive from :class:`ExecutionError` so the execution layer can catch them as a
group.
"""


class QuantumAvengerError(Exception):
    """Base exception for Quantum Avenger."""


# --- Configuration & reproducibility --------------------------------------
class ConfigurationError(QuantumAvengerError):
    """Raised when configuration validation or loading fails."""


class SeedingError(QuantumAvengerError):
    """Raised when reproducibility seeding fails."""


# --- Data layer ------------------------------------------------------------
class DataError(QuantumAvengerError):
    """Base for data-layer failures."""


class DataValidationError(DataError):
    """Raised when data quality checks fail."""


class IngestionError(DataError):
    """Raised when data ingestion fails."""


class VaultError(DataError):
    """Raised when a data vault cannot be read or written."""


class SchemaValidationError(DataError):
    """Raised when a dataframe/parquet does not match its declared schema."""


# --- Adapters (external boundaries) ---------------------------------------
class AdapterError(QuantumAvengerError):
    """Base for external-adapter failures."""


class MarketDataError(AdapterError):
    """Raised when a market-data source fails."""


class NewsSourceError(AdapterError):
    """Raised when a news source fails."""


class UniverseError(AdapterError):
    """Raised when the trading universe cannot be resolved."""


class LLMClientError(AdapterError):
    """Raised when the LLM client fails or returns an unparseable response."""


# --- Feature engineering ---------------------------------------------------
class FeatureError(QuantumAvengerError):
    """Base for feature-engineering failures."""


class FeatureRegistryError(FeatureError):
    """Raised when feature registration or lookup fails."""


class SlippageError(FeatureError):
    """Raised when the slippage model receives invalid inputs."""


# --- Tournament / training -------------------------------------------------
class TournamentError(QuantumAvengerError):
    """Base for backtesting-tournament failures."""


class CPCVSplitError(TournamentError):
    """Raised when a CPCV split is invalid (e.g. train/test overlap)."""


class ModelTrainingError(TournamentError):
    """Raised when model training fails."""


# --- Evaluation / promotion ------------------------------------------------
class EvaluationError(QuantumAvengerError):
    """Base for statistical-evaluation failures."""


class DeflatedSharpeError(EvaluationError):
    """Raised when the Deflated Sharpe Ratio cannot be computed."""


class PromotionError(EvaluationError):
    """Raised when model promotion fails or violates the registry contract."""


# --- Execution / orchestration --------------------------------------------
class ExecutionError(QuantumAvengerError):
    """Raised for execution or risk-evaluation failures."""


class ShieldVetoError(ExecutionError):
    """Raised when the Shield Agent rejects a trade."""


class RiskLimitError(ExecutionError):
    """Raised when a risk limit would be breached."""


class PositionSizingError(ExecutionError):
    """Raised when position sizing produces an invalid result."""


class BrokerError(ExecutionError):
    """Raised when the broker adapter fails."""


class OrderRoutingError(ExecutionError):
    """Raised when an order cannot be routed or is rejected."""


class MCPToolError(ExecutionError):
    """Raised when an MCP tool invocation fails."""


class AnonymizationError(ExecutionError):
    """Raised when entity anonymization fails."""


class RAGError(ExecutionError):
    """Raised when retrieval-augmented generation fails."""


# --- Resilience / monitoring ----------------------------------------------
class CircuitBreakerError(QuantumAvengerError):
    """Raised when a call is rejected because a circuit breaker is open."""


class MonitoringError(QuantumAvengerError):
    """Raised when monitoring or telemetry export fails."""

```

---

### File: `new_pipeline/core/__init__.py`

```py
from .circuit_breaker import CircuitBreaker, CircuitState
from .logging import (
    configure_logging,
    get_trace_id,
    new_trace_id,
    set_trace_id,
    trace_context,
)
from .paths import project_root
from .seeding import active_seed, seed_everything

__all__ = [
    "CircuitBreaker",
    "CircuitState",
    "active_seed",
    "configure_logging",
    "get_trace_id",
    "new_trace_id",
    "project_root",
    "seed_everything",
    "set_trace_id",
    "trace_context",
]

```

---

### File: `new_pipeline/core/logging.py`

```py
"""Structured logging with trace-id propagation.

:func:`configure_logging` honours ``logging.json_logs`` (emit one JSON object
per line) and ``logging.trace_enabled`` (attach the current trace id to every
record). Wrap a unit of work in :func:`trace_context` so every log line it
emits shares one correlating ``trace_id``.
"""

import json
import logging
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar, Token
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any

from new_pipeline.config import get_config

_LOGGER_NAME = "quantum_avenger"
_TRACE_ID: ContextVar[str | None] = ContextVar("qa_trace_id", default=None)


def new_trace_id() -> str:
    return uuid.uuid4().hex


def get_trace_id() -> str | None:
    return _TRACE_ID.get()


def set_trace_id(trace_id: str | None) -> Token:
    return _TRACE_ID.set(trace_id)


@contextmanager
def trace_context(trace_id: str | None = None) -> Iterator[str]:
    """Bind a trace id for the duration of the block (auto-generated if None)."""
    resolved = trace_id or new_trace_id()
    token = _TRACE_ID.set(resolved)
    try:
        yield resolved
    finally:
        _TRACE_ID.reset(token)


class TraceIdFilter(logging.Filter):
    """Inject the current trace id onto every record as ``trace_id``."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = _TRACE_ID.get() or "-"
        return True


class JsonFormatter(logging.Formatter):
    """Render log records as single-line JSON, including the trace id."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None) or _TRACE_ID.get() or "-",
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging() -> logging.Logger:
    config = get_config()
    log_file_path = Path(config.logging.log_file).resolve()
    log_file_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(getattr(logging, config.logging.level.upper(), logging.INFO))

    if not logger.handlers:
        if config.logging.json_logs:
            formatter: logging.Formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(config.logging.format)

        handler = RotatingFileHandler(
            filename=log_file_path,
            maxBytes=config.logging.max_bytes,
            backupCount=5,
            encoding="utf-8",
        )
        handler.setFormatter(formatter)
        if config.logging.trace_enabled:
            handler.addFilter(TraceIdFilter())
        logger.addHandler(handler)

    return logger

```

---

### File: `new_pipeline/core/constants.py`

```py
from enum import Enum


class RunMode(str, Enum):
    BACKTEST = "backtest"
    EVALUATE = "evaluate"
    LIVE = "live"


class ValidationMode(str, Enum):
    STRICT = "strict"
    WARN = "warn"
    SKIP = "skip"

```

---

### File: `new_pipeline/execution/mcp_tools.py`

```py
"""Deterministic quant tool registry (the FastMCP surface, G1).

The LLM is forbidden from doing math; every quantity it needs comes from one of
these tools, which simply wrap the project's existing deterministic functions
(no logic duplication) and return structured JSON-shaped dicts. ``to_jsonrpc``
emits the JSON-RPC tool schema an MCP server (or a live FastMCP adapter)
advertises. Building the registry needs no network, so it is fully testable
offline.
"""

from collections.abc import Callable
from dataclasses import dataclass, field

from new_pipeline.evaluation.dsr import (
    compute_deflated_sharpe_ratio,
    expected_max_sharpe,
    interpret_dsr,
)
from new_pipeline.evaluation.tearsheet import summary_metrics
from new_pipeline.features.shields import (
    calculate_kelly_position_size,
    enforce_volatility_stop,
    evaluate_risk_veto_gates,
)
from new_pipeline.features.slippage import hydrodynamic_slippage_bps
from new_pipeline.tournament.simulator import sharpe_ratio

_JSON_NUMBER = "number"
_JSON_ARRAY = "array"


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, str]
    handler: Callable[..., dict]

    def __call__(self, **kwargs) -> dict:
        return self.handler(**kwargs)

    def to_jsonrpc(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": {key: {"type": kind} for key, kind in self.parameters.items()},
                "required": list(self.parameters),
            },
        }


@dataclass
class ToolRegistry:
    _tools: dict[str, Tool] = field(default_factory=dict)

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools[name]

    def call(self, name: str, **kwargs) -> dict:
        return self._tools[name](**kwargs)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def schemas(self) -> list[dict]:
        return [tool.to_jsonrpc() for tool in self._tools.values()]

    def __len__(self) -> int:
        return len(self._tools)


def _veto_gates_tool(**kw) -> dict:
    approved, size = evaluate_risk_veto_gates(
        kw["entry_price"],
        kw["atr"],
        kw["atr_multiplier"],
        kw["account_capital"],
        kw["max_risk_pct"],
        kw["current_qty"],
        kw["adv_20"],
        kw["volume_today"],
        kw["volatility"],
    )
    return {"approved": bool(approved), "position_size": float(size)}


def _kelly_tool(**kw) -> dict:
    size = calculate_kelly_position_size(
        kw["entry_price"], kw["atr"], kw["atr_multiplier"],
        kw["account_capital"], kw["max_risk_pct"],
    )
    return {"position_size": float(size)}


def _vol_stop_tool(**kw) -> dict:
    stop, triggered = enforce_volatility_stop(
        kw["entry_price"], kw["atr"], kw["atr_multiplier"],
        kw["current_price"], kw["highest_price"],
    )
    return {"stop_level": float(stop), "triggered": bool(triggered)}


def _slippage_tool(**kw) -> dict:
    bps = hydrodynamic_slippage_bps(
        kw["order_notional"], kw["volatility"], kw["volume_today"],
        kw.get("slippage_constant", 0.5), kw.get("bps_scaler", 10000.0),
    )
    ceiling = kw.get("max_slippage_bps", 50.0)
    return {"slippage_bps": float(bps), "approval": bool(bps <= ceiling)}


def _sharpe_tool(**kw) -> dict:
    return {"sharpe": sharpe_ratio(kw["returns"])}


def _dsr_tool(**kw) -> dict:
    dsr = compute_deflated_sharpe_ratio(kw["returns"], kw["trial_sharpes"])
    return {"dsr": dsr, "verdict": interpret_dsr(dsr)}


def _expected_max_sharpe_tool(**kw) -> dict:
    return {"expected_max_sharpe": expected_max_sharpe(kw["var_trials"], kw["n_trials"])}


def _summary_tool(**kw) -> dict:
    return summary_metrics(kw["returns"])


def build_default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    _risk = {
        "entry_price": _JSON_NUMBER,
        "atr": _JSON_NUMBER,
        "atr_multiplier": _JSON_NUMBER,
        "account_capital": _JSON_NUMBER,
        "max_risk_pct": _JSON_NUMBER,
    }
    registry.register(
        Tool(
            "evaluate_risk_veto_gates",
            "Run the Shield Agent's five veto gates.",
            {**_risk, "current_qty": _JSON_NUMBER, "adv_20": _JSON_NUMBER,
             "volume_today": _JSON_NUMBER, "volatility": _JSON_NUMBER},
            _veto_gates_tool,
        )
    )
    registry.register(
        Tool("calculate_kelly_position_size", "Risk-based share count.", _risk, _kelly_tool)
    )
    registry.register(
        Tool(
            "enforce_volatility_stop",
            "Hard + trailing ATR stop and whether it is triggered.",
            {"entry_price": _JSON_NUMBER, "atr": _JSON_NUMBER, "atr_multiplier": _JSON_NUMBER,
             "current_price": _JSON_NUMBER, "highest_price": _JSON_NUMBER},
            _vol_stop_tool,
        )
    )
    registry.register(
        Tool(
            "calculate_dynamic_slippage",
            "Hydrodynamic slippage (bps) and whether it clears the ceiling.",
            {"order_notional": _JSON_NUMBER, "volatility": _JSON_NUMBER,
             "volume_today": _JSON_NUMBER},
            _slippage_tool,
        )
    )
    registry.register(Tool("sharpe_ratio", "Annualized Sharpe of a return series.",
                           {"returns": _JSON_ARRAY}, _sharpe_tool))
    registry.register(Tool("deflated_sharpe_ratio", "Deflated Sharpe probability + verdict.",
                           {"returns": _JSON_ARRAY, "trial_sharpes": _JSON_ARRAY}, _dsr_tool))
    registry.register(Tool("expected_max_sharpe", "Expected max Sharpe under the null.",
                           {"var_trials": _JSON_NUMBER, "n_trials": _JSON_NUMBER},
                           _expected_max_sharpe_tool))
    registry.register(Tool("summary_metrics", "Sharpe/drawdown/win-rate/profit-factor summary.",
                           {"returns": _JSON_ARRAY}, _summary_tool))
    return registry

```

---

### File: `new_pipeline/execution/grader.py`

```py
"""Grader node: does the verdict hold up against the retrieved context?

A second LLM pass returning approve/reject. The orchestrator retries the verdict
up to ``max_retries`` on rejection. Offline, the ``FakeLLMClient`` makes the
decision deterministic; tests inject scripted clients to drive the retry path.
"""

from dataclasses import dataclass

from new_pipeline.adapters.base import LLMClient, Verdict


@dataclass
class GraderResult:
    approved: bool
    feedback: str


@dataclass
class Grader:
    llm: LLMClient

    def grade(self, verdict: Verdict, context: list[str]) -> GraderResult:
        joined = "\n".join(f"- {item}" for item in context)
        prompt = (
            f"Verdict: {verdict.stance} ({verdict.rationale})\nContext:\n{joined}\n"
            "Is the verdict supported by the context? Answer YES or NO."
        )
        response = self.llm.verdict(prompt)
        # A decisive (non-neutral) grader stance counts as support.
        return GraderResult(approved=response.stance != "NEUTRAL", feedback=response.rationale)

```

---

### File: `new_pipeline/execution/runner.py`

```py
"""Whole-engine trading runner: champions -> walk-forward replay -> trade graph.

The composition root that drives the engine end to end. For each promoted
champion it pulls the sector's bars from the market-data adapter, computes
features, walks the bars forward, and at every signal builds a ``TradeRequest``
and runs the LangGraph ``TradeOrchestrator`` (Verdict -> Grader -> Shield veto ->
Execute/Fallback). Decisions land in the veto ledger; executed trades realize a
t+1 return via the backtest simulator and land in the trade log — the two
parquet files the dashboard reads.

Offline this runs over the deterministic fakes with no network. The *same* loop
runs live the moment ``build_adapters`` returns live clients for a live
``run_mode`` — only the adapters change, not the orchestration.
"""

import json
import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl

from new_pipeline.adapters.factory import build_adapters
from new_pipeline.config import get_config
from new_pipeline.evaluation.promotion import PromotionRegistry
from new_pipeline.execution.orchestrator import TradeOrchestrator, TradeRequest
from new_pipeline.execution.trade_log import TradeLog, TradeRecord
from new_pipeline.execution.veto_ledger import VetoLedger
from new_pipeline.features.polars_engine import compile_features
from new_pipeline.tournament.simulator import simulate_t1_returns
from new_pipeline.tournament.trainer import load_booster, predict_proba

_PRICE_COLS = ("close", "low", "atr", "adv_20", "volatility", "volume")
_logger = logging.getLogger(__name__)


@dataclass
class SessionSummary:
    sectors: list[str]
    decisions: int
    executed: int
    vetoed: int
    realized_pnl: float


def run_trading_session(
    candidates_dir,
    start: date = date(2021, 1, 1),
    end: date = date(2021, 12, 31),
    adapters=None,
    cfg=None,
    registry_path=None,
) -> SessionSummary:
    """Drive promoted champions through the live trade graph over a bar replay."""
    cfg = cfg or get_config()
    adapters = adapters or build_adapters(cfg)
    candidates = Path(candidates_dir)
    registry = PromotionRegistry(registry_path or candidates / "promotion_registry.json")
    champions = registry.active_champions()
    if not champions:
        _logger.info("no active champions; nothing to trade")
        return SessionSummary([], 0, 0, 0, 0.0)

    ledger_dir = Path(cfg.execution.ledger_dir)
    ledger = VetoLedger(ledger_dir / "veto_ledger.parquet")
    trade_log = TradeLog(ledger_dir / "trade_log.parquet")
    orchestrator = TradeOrchestrator(
        adapters.llm,
        adapters.broker,
        ledger,
        max_retries=cfg.execution.max_retries,
        tif=cfg.execution.tif,
    )
    dsr_by_sector = _champion_dsr(registry)
    sector_of = adapters.universe.sectors()

    counters = {"decisions": 0, "executed": 0, "vetoed": 0, "pnl": 0.0}
    for sector, model_path in champions.items():
        booster = load_booster(model_path)
        selected = _selected_features(model_path)
        symbols = [ticker for ticker, sec in sector_of.items() if sec == sector]
        for symbol in symbols:
            _replay_symbol(
                symbol, dsr_by_sector.get(sector, 0.0), booster, selected,
                adapters, orchestrator, trade_log, start, end, cfg, counters,
            )

    return SessionSummary(
        sectors=list(champions),
        decisions=counters["decisions"],
        executed=counters["executed"],
        vetoed=counters["vetoed"],
        realized_pnl=round(counters["pnl"], 6),
    )


def _replay_symbol(
    symbol, dsr, booster, selected, adapters, orchestrator, trade_log, start, end, cfg, counters
):
    bars = adapters.market_data.history(symbol, start, end)
    if len(bars) < 2:
        return
    frame = pl.DataFrame(
        [
            {
                "date": bar.day, "ticker": symbol, "open": bar.open, "high": bar.high,
                "low": bar.low, "close": bar.close, "volume": bar.volume,
            }
            for bar in bars
        ]
    )
    features = compile_features(frame)
    required = [*selected, *_PRICE_COLS]
    clean = features.with_columns(pl.col(required).fill_nan(None)).drop_nulls(subset=required)
    if clean.height < 2:
        return

    matrix = clean.select(selected).to_numpy()
    proba = predict_proba(booster, matrix)
    signals = proba > cfg.execution.confidence_threshold
    prices = {col: clean[col].to_numpy().astype(np.float64) for col in _PRICE_COLS}
    dates = clean["date"].to_list()

    for i in range(clean.height - 1):
        if not signals[i]:
            continue
        counters["decisions"] += 1
        request = _build_request(symbol, dsr, prices, i, cfg, adapters, dates[i])
        state = orchestrator.run(request)
        if state.get("outcome") == "executed":
            counters["executed"] += 1
            pnl = _realized_return(prices, i, cfg)
            counters["pnl"] += pnl
            _record_fill(trade_log, request, state, prices["close"][i], pnl)
        else:
            counters["vetoed"] += 1


def _build_request(symbol, dsr, prices, i, cfg, adapters, day) -> TradeRequest:
    context = [item.headline for item in adapters.news.headlines(symbol, day)]
    current_qty = adapters.broker.get_positions().get(symbol, 0.0)
    return TradeRequest(
        signal="BUY",
        symbol=symbol,
        entry_price=float(prices["close"][i]),
        atr=float(prices["atr"][i]),
        atr_multiplier=cfg.execution.atr_stop_multiplier,
        account_capital=cfg.execution.account_capital,
        max_risk_pct=cfg.execution.max_risk_per_trade,
        current_qty=current_qty,
        adv_20=float(prices["adv_20"][i]),
        volume_today=float(prices["volume"][i]),
        volatility=float(prices["volatility"][i]),
        context=context,
        dsr=dsr,
    )


def _realized_return(prices, i, cfg) -> float:
    """t+1 realized return of the entry, reusing the backtest simulator's math."""
    window = simulate_t1_returns(
        np.array([1, 0], dtype=np.int64),
        prices["close"][i : i + 2],
        prices["low"][i : i + 2],
        prices["atr"][i : i + 2],
        cfg.execution.atr_stop_multiplier,
        cfg.execution.max_risk_per_trade,
    )
    return float(window[0])


def _record_fill(trade_log, request, state, fill_price, pnl) -> None:
    limit_price = round(request.entry_price + 0.1 * request.atr, 2)
    trade_log.append(
        TradeRecord(
            symbol=request.symbol,
            side="buy",
            qty=int(state.get("position_size", 0)),
            limit_price=limit_price,
            status="filled",
            order_id=str(state.get("execution_id", "")),
            fill_price=float(fill_price),
            pnl=pnl,
        )
    )


def _selected_features(model_path) -> list[str]:
    features_path = str(model_path).replace("_candidate.json", "_candidate_features.json")
    return json.loads(Path(features_path).read_text(encoding="utf-8"))["features"]


def _champion_dsr(registry: PromotionRegistry) -> dict[str, float]:
    """Most recent promoted DSR per sector, for the ledger's audit column."""
    dsr: dict[str, float] = {}
    for entry in registry.promotions:
        if entry.get("promoted"):
            dsr[entry["sector"]] = entry.get("dsr", 0.0)
    return dsr

```

---

### File: `new_pipeline/execution/orchestrator.py`

```py
"""LangGraph trade orchestrator: Verdict -> Grader -> Risk-Veto -> Execute/Fallback.

The deterministic vs. probabilistic boundary in one place: the LLM nodes
(verdict, grader) produce only narrative stances; the Risk-Veto node calls the
Shield Agent (the exact function the backtest uses); execution goes through the
broker adapter. Every terminal outcome is appended to the veto ledger. A
rejected verdict is retried up to ``max_retries`` times before falling back.
"""

from dataclasses import dataclass, field
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from new_pipeline.adapters.base import LLMClient, Verdict
from new_pipeline.core.logging import new_trace_id
from new_pipeline.execution.broker import BrokerAdapter
from new_pipeline.execution.grader import Grader
from new_pipeline.execution.verdict_engine import VerdictEngine
from new_pipeline.execution.veto_ledger import VetoLedger, VetoRecord
from new_pipeline.features.shields import evaluate_risk_veto_gates


@dataclass
class TradeRequest:
    signal: str
    symbol: str
    entry_price: float
    atr: float
    atr_multiplier: float
    account_capital: float
    max_risk_pct: float
    current_qty: float
    adv_20: float
    volume_today: float
    volatility: float
    context: list[str] = field(default_factory=list)
    dsr: float = 0.0


class _State(TypedDict, total=False):
    request: TradeRequest
    verdict: str
    grader_approved: bool
    grader_feedback: str
    shield_approved: bool
    position_size: float
    execution_id: str
    attempts: int
    outcome: str


class TradeOrchestrator:
    def __init__(
        self,
        llm: LLMClient,
        broker: BrokerAdapter,
        ledger: VetoLedger,
        max_retries: int = 3,
        tif: str = "day",
    ):
        self._verdict_engine = VerdictEngine(llm)
        self._grader = Grader(llm)
        self._broker = broker
        self._ledger = ledger
        self._max_retries = max_retries
        self._tif = tif
        self._app = self._build_graph()

    def run(self, request: TradeRequest) -> _State:
        return self._app.invoke({"request": request, "attempts": 0})

    def _build_graph(self):
        graph = StateGraph(_State)
        graph.add_node("verdict", self._verdict_node)
        graph.add_node("grader", self._grader_node)
        graph.add_node("risk_veto", self._risk_veto_node)
        graph.add_node("execute", self._execute_node)
        graph.add_node("fallback", self._fallback_node)
        graph.add_edge(START, "verdict")
        graph.add_edge("verdict", "grader")
        graph.add_conditional_edges(
            "grader",
            self._route_after_grader,
            {"approved": "risk_veto", "retry": "verdict", "reject": "fallback"},
        )
        graph.add_conditional_edges(
            "risk_veto",
            self._route_after_veto,
            {"execute": "execute", "veto": "fallback"},
        )
        graph.add_edge("execute", END)
        graph.add_edge("fallback", END)
        return graph.compile()

    # --- nodes -------------------------------------------------------------
    def _verdict_node(self, state: _State) -> dict:
        request = state["request"]
        verdict = self._verdict_engine.generate(request.signal, request.symbol, request.context)
        return {"verdict": verdict.stance, "attempts": state.get("attempts", 0) + 1}

    def _grader_node(self, state: _State) -> dict:
        request = state["request"]
        result = self._grader.grade(Verdict(state["verdict"], ""), request.context)
        return {"grader_approved": result.approved, "grader_feedback": result.feedback}

    def _risk_veto_node(self, state: _State) -> dict:
        request = state["request"]
        approved, size = evaluate_risk_veto_gates(
            request.entry_price,
            request.atr,
            request.atr_multiplier,
            request.account_capital,
            request.max_risk_pct,
            request.current_qty,
            request.adv_20,
            request.volume_today,
            request.volatility,
        )
        return {"shield_approved": bool(approved), "position_size": float(size)}

    def _execute_node(self, state: _State) -> dict:
        request = state["request"]
        limit_price = round(request.entry_price + 0.1 * request.atr, 2)
        receipt = self._broker.submit_order(
            {
                "symbol": request.symbol,
                "qty": int(state["position_size"]),
                "side": "buy",
                "limit_price": limit_price,
                "tif": self._tif,
            }
        )
        execution_id = str(receipt.get("order_id", new_trace_id()))
        self._ledger.append(
            VetoRecord(
                symbol=request.symbol,
                signal=request.signal,
                entry_price=request.entry_price,
                veto_reason="executed",
                veto_gate="none",
                dsr=request.dsr,
                position_size=int(state["position_size"]),
                execution_id=execution_id,
            )
        )
        return {"execution_id": execution_id, "outcome": "executed"}

    def _fallback_node(self, state: _State) -> dict:
        request = state["request"]
        if not state.get("grader_approved", False):
            gate, reason = "grader", "grader rejected after retries"
        else:
            gate, reason = "shield", "risk veto"
        self._ledger.append(
            VetoRecord(
                symbol=request.symbol,
                signal=request.signal,
                entry_price=request.entry_price,
                veto_reason=reason,
                veto_gate=gate,
                dsr=request.dsr,
                position_size=0,
                execution_id="",
            )
        )
        return {"outcome": "vetoed"}

    # --- routers -----------------------------------------------------------
    def _route_after_grader(self, state: _State) -> str:
        if state.get("grader_approved"):
            return "approved"
        if state.get("attempts", 0) < self._max_retries:
            return "retry"
        return "reject"

    def _route_after_veto(self, state: _State) -> str:
        return "execute" if state.get("shield_approved") else "veto"

```

---

### File: `new_pipeline/execution/verdict_engine.py`

```py
"""Verdict generation: turn a signal + retrieved context into a stance.

Delegates entirely to an ``LLMClient`` (the offline ``FakeLLMClient`` in dev and
tests). The LLM only produces a narrative stance — it performs no math (G1);
all quantities flow through deterministic tools / the Shield.
"""

from dataclasses import dataclass

from new_pipeline.adapters.base import LLMClient, Verdict


@dataclass
class VerdictEngine:
    llm: LLMClient

    def generate(self, signal: str, symbol: str, context: list[str]) -> Verdict:
        return self.llm.verdict(self._build_prompt(signal, symbol, context))

    @staticmethod
    def _build_prompt(signal: str, symbol: str, context: list[str]) -> str:
        joined = "\n".join(f"- {item}" for item in context)
        return (
            f"Signal: {signal}\nSymbol: {symbol}\nContext:\n{joined}\n"
            "Generate a BULLISH/BEARISH/NEUTRAL verdict with a one-line rationale."
        )

```

---

### File: `new_pipeline/execution/async_sentiment.py`

```py
"""Asyncio-batched LLM sentiment (restores the legacy Semaphore(20) pattern).

Scores many texts concurrently through a (sync) ``LLMClient``, bounding in-flight
calls with an ``asyncio.Semaphore``. Sync client calls run in the default
executor so a slow/network-bound LLM never blocks the event loop. Order is
preserved; offline + deterministic with ``FakeLLMClient``.
"""

import asyncio

from new_pipeline.adapters.base import LLMClient, SentimentResult


async def _score_one(client, text, semaphore, loop):
    async with semaphore:
        return await loop.run_in_executor(None, client.sentiment, text)


async def batch_sentiment_async(
    client: LLMClient, texts, concurrency: int = 20
) -> list[SentimentResult]:
    semaphore = asyncio.Semaphore(concurrency)
    loop = asyncio.get_running_loop()
    return list(
        await asyncio.gather(*[_score_one(client, text, semaphore, loop) for text in texts])
    )


def batch_sentiment(client: LLMClient, texts, concurrency: int = 20) -> list[SentimentResult]:
    """Sync entry point: score texts concurrently, preserving input order."""
    return asyncio.run(batch_sentiment_async(client, list(texts), concurrency))

```

---

### File: `new_pipeline/execution/__init__.py`

```py
from .broker import BrokerAdapter
from .entity_anonymizer import AnonymizationResult, EntityAnonymizer
from .grader import Grader, GraderResult
from .mcp_tools import Tool, ToolRegistry, build_default_registry
from .rag_engine import HashingEmbedder, RagEngine, RetrievedChunk, late_chunk
from .risk import RiskManager
from .trade_log import TRADE_LOG_SCHEMA, TradeLog, TradeRecord
from .verdict_engine import VerdictEngine
from .veto_ledger import LEDGER_SCHEMA, VetoLedger, VetoRecord

__all__ = [
    "LEDGER_SCHEMA",
    "TRADE_LOG_SCHEMA",
    "AnonymizationResult",
    "BrokerAdapter",
    "EntityAnonymizer",
    "Grader",
    "GraderResult",
    "HashingEmbedder",
    "RagEngine",
    "RetrievedChunk",
    "RiskManager",
    "Tool",
    "ToolRegistry",
    "TradeLog",
    "TradeRecord",
    "VerdictEngine",
    "VetoLedger",
    "VetoRecord",
    "build_default_registry",
    "late_chunk",
]

```

---

### File: `new_pipeline/execution/entity_anonymizer.py`

```py
"""Entity anonymization for the LLM verdict pipeline (G1 defense).

Tradable entities (tickers and company names) are masked to opaque placeholders
("[COMPANY_A]") before any text reaches the LLM, defeating name memorization /
look-ahead. Offline by default: it masks a supplied vocabulary (e.g. the
universe's tickers and names) with deterministic regex — no spaCy model download
needed. A spaCy NER pass for open-vocabulary entities can layer on later behind
the same interface.
"""

import re
from dataclasses import dataclass, field


@dataclass
class AnonymizationResult:
    text: str
    mapping: dict[str, str]  # placeholder -> original


def _placeholder(index: int) -> str:
    suffix = chr(ord("A") + index) if index < 26 else str(index)
    return f"[COMPANY_{suffix}]"


@dataclass
class EntityAnonymizer:
    vocabulary: list[str] = field(default_factory=list)

    def anonymize(self, text: str) -> AnonymizationResult:
        mapping: dict[str, str] = {}
        assigned: dict[str, str] = {}  # original -> placeholder
        result = text
        # Longest term first so "Apple Inc" is masked before "Apple".
        for term in sorted({t for t in self.vocabulary if t}, key=len, reverse=True):
            pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
            if not pattern.search(result):
                continue
            if term not in assigned:
                placeholder = _placeholder(len(assigned))
                assigned[term] = placeholder
                mapping[placeholder] = term
            result = pattern.sub(assigned[term], result)
        return AnonymizationResult(text=result, mapping=mapping)

    @staticmethod
    def deanonymize(text: str, mapping: dict[str, str]) -> str:
        result = text
        for placeholder, original in mapping.items():
            result = result.replace(placeholder, original)
        return result

```

---

### File: `new_pipeline/execution/rag_engine.py`

```py
"""Retrieval-Augmented context for the LLM, offline by default.

"Late chunking": split a document on sentence boundaries with character overlap
so semantic units stay intact. Retrieval blends a lexical score (BM25) with a
dense cosine score from a pluggable embedder; the offline default is a
deterministic hashing embedder (no model download). A sentence-transformers
embedder can be swapped in behind the same ``embed`` interface later.
"""

import hashlib
import re
from dataclasses import dataclass

import numpy as np
from rank_bm25 import BM25Okapi


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _stable_hash(token: str) -> int:
    return int.from_bytes(hashlib.blake2b(token.encode(), digest_size=8).digest(), "big")


def late_chunk(text: str, chunk_size: int = 512, overlap: int = 100) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > chunk_size:
            chunks.append(current.strip())
            current = current[-overlap:] if overlap else ""
        current = f"{current} {sentence}".strip()
    if current.strip():
        chunks.append(current.strip())
    return chunks


class HashingEmbedder:
    """Deterministic bag-of-hashed-tokens embedder (offline; no weights)."""

    def __init__(self, dim: int = 256):
        self.dim = dim

    def embed(self, texts: list[str]) -> np.ndarray:
        vectors = np.zeros((len(texts), self.dim), dtype=np.float64)
        for i, text in enumerate(texts):
            for token in _tokenize(text):
                vectors[i, _stable_hash(token) % self.dim] += 1.0
            norm = np.linalg.norm(vectors[i])
            if norm > 0.0:
                vectors[i] /= norm
        return vectors


@dataclass
class RetrievedChunk:
    text: str
    score: float


class RagEngine:
    def __init__(self, embedder=None, top_k: int = 5, chunk_size: int = 512, overlap: int = 100):
        self.embedder = embedder or HashingEmbedder()
        self.top_k = top_k
        self.chunk_size = chunk_size
        self.overlap = overlap
        self._chunks: list[str] = []
        self._embeddings: np.ndarray | None = None
        self._bm25: BM25Okapi | None = None

    def index(self, documents: list[str]) -> None:
        chunks: list[str] = []
        for document in documents:
            chunks.extend(late_chunk(document, self.chunk_size, self.overlap))
        self._chunks = chunks
        if not chunks:
            return
        self._embeddings = self.embedder.embed(chunks)
        self._bm25 = BM25Okapi([_tokenize(chunk) for chunk in chunks])

    def retrieve(self, query: str, top_k: int | None = None) -> list[RetrievedChunk]:
        if not self._chunks:
            return []
        k = top_k or self.top_k
        query_vector = self.embedder.embed([query])[0]
        dense = self._embeddings @ query_vector  # cosine (rows are unit-normalized)
        lexical = np.asarray(self._bm25.get_scores(_tokenize(query)), dtype=np.float64)
        if lexical.max() > 0.0:
            lexical = lexical / lexical.max()
        combined = 0.5 * dense + 0.5 * lexical
        order = np.argsort(combined)[::-1][:k]
        return [RetrievedChunk(self._chunks[i], float(combined[i])) for i in order]

```

---

### File: `new_pipeline/execution/risk.py`

```py
from dataclasses import dataclass


@dataclass
class RiskManager:
    max_risk_per_trade: float
    atr_multiplier: float

    def compute_position_size(
        self, account_balance: float, entry_price: float, atr: float
    ) -> float:
        if atr <= 0 or entry_price <= 0:
            return 0.0

        stop = entry_price - (self.atr_multiplier * atr)
        risk_per_share = entry_price - stop
        if risk_per_share <= 0:
            return 0.0

        capital_at_risk = account_balance * self.max_risk_per_trade
        position_size = capital_at_risk / risk_per_share
        return max(0.0, position_size)

```

---

### File: `new_pipeline/execution/veto_ledger.py`

```py
"""Append-only decision ledger (Parquet).

Every orchestrator outcome — executed or vetoed — is appended with the
nine-column schema the Phase 6 dashboard reads. ``veto_gate`` is "none" for
executed trades, otherwise the gate that rejected the trade
("grader" | "shield" | "execution").
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

LEDGER_SCHEMA = pa.schema(
    [
        ("timestamp", pa.timestamp("ns")),
        ("symbol", pa.string()),
        ("signal", pa.string()),
        ("entry_price", pa.float64()),
        ("veto_reason", pa.string()),
        ("veto_gate", pa.string()),
        ("dsr", pa.float64()),
        ("position_size", pa.int32()),
        ("execution_id", pa.string()),
    ]
)


@dataclass
class VetoRecord:
    symbol: str
    signal: str
    entry_price: float
    veto_reason: str
    veto_gate: str
    dsr: float
    position_size: int
    execution_id: str
    timestamp: datetime | None = None


class VetoLedger:
    def __init__(self, path):
        self._path = Path(path)

    def append(self, record: VetoRecord) -> None:
        moment = record.timestamp or datetime.now(UTC)
        table = pa.table(
            {
                "timestamp": pa.array([moment.replace(tzinfo=None)], type=pa.timestamp("ns")),
                "symbol": [record.symbol],
                "signal": [record.signal],
                "entry_price": [float(record.entry_price)],
                "veto_reason": [record.veto_reason],
                "veto_gate": [record.veto_gate],
                "dsr": [float(record.dsr)],
                "position_size": [int(record.position_size)],
                "execution_id": [record.execution_id],
            },
            schema=LEDGER_SCHEMA,
        )
        if self._path.exists():
            table = pa.concat_tables([pq.read_table(self._path), table])
        self._path.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, self._path)

    def read(self) -> pa.Table:
        if not self._path.exists():
            return LEDGER_SCHEMA.empty_table()
        return pq.read_table(self._path)

    def __len__(self) -> int:
        return self.read().num_rows

```

---

### File: `new_pipeline/execution/broker.py`

```py
from abc import ABC, abstractmethod


class BrokerAdapter(ABC):
    @abstractmethod
    def submit_order(self, order: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def get_positions(self) -> dict[str, float]:
        raise NotImplementedError

```

---

### File: `new_pipeline/execution/trade_log.py`

```py
"""Append-only trade log (Parquet) — the realized-fill record (Phase 6 contract).

Separate from the veto ledger (which records *decisions*): this captures order /
fill details and realized P&L for executed trades, and is the source of the
dashboard's performance KPIs. ``pnl`` is the per-trade fractional return.
"""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

TRADE_LOG_SCHEMA = pa.schema(
    [
        ("timestamp", pa.timestamp("ns")),
        ("symbol", pa.string()),
        ("side", pa.string()),
        ("qty", pa.int32()),
        ("limit_price", pa.float64()),
        ("status", pa.string()),
        ("order_id", pa.string()),
        ("fill_price", pa.float64()),
        ("pnl", pa.float64()),
    ]
)


@dataclass
class TradeRecord:
    symbol: str
    side: str
    qty: int
    limit_price: float
    status: str
    order_id: str
    fill_price: float = 0.0
    pnl: float = 0.0
    timestamp: datetime | None = None


class TradeLog:
    def __init__(self, path):
        self._path = Path(path)

    def append(self, record: TradeRecord) -> None:
        moment = (record.timestamp or datetime.now(UTC)).replace(tzinfo=None)
        table = pa.table(
            {
                "timestamp": pa.array([moment], type=pa.timestamp("ns")),
                "symbol": [record.symbol],
                "side": [record.side],
                "qty": [int(record.qty)],
                "limit_price": [float(record.limit_price)],
                "status": [record.status],
                "order_id": [record.order_id],
                "fill_price": [float(record.fill_price)],
                "pnl": [float(record.pnl)],
            },
            schema=TRADE_LOG_SCHEMA,
        )
        if self._path.exists():
            table = pa.concat_tables([pq.read_table(self._path), table])
        self._path.parent.mkdir(parents=True, exist_ok=True)
        pq.write_table(table, self._path)

    def read(self) -> pa.Table:
        if not self._path.exists():
            return TRADE_LOG_SCHEMA.empty_table()
        return pq.read_table(self._path)

    def __len__(self) -> int:
        return self.read().num_rows

```

---

### File: `new_pipeline/evaluation/haircut.py`

```py
"""Haircut Sharpe Ratio & multiple-testing adjustment (Harvey & Liu).

Harvey & Liu (2015), "Backtesting" + "...and the Cross-Section of Expected
Returns". A Sharpe ratio that survived a search over ``n_trials`` candidates is
inflated by selection bias. We turn the reported Sharpe into a t-stat, convert
to a p-value, inflate that p-value for the multiplicity of trials (Bonferroni /
Holm / Benjamini-Hochberg-Yekutieli), then map the adjusted p-value back to a
"haircut" Sharpe — what is left once the multiple-testing discount is applied.
"""

import math
from dataclasses import dataclass

import numpy as np
from scipy import stats


def _harmonic(n: int) -> float:
    """c(N) = Σ_{i=1}^{N} 1/i — the BHY dependency-correction constant."""
    return float(np.sum(1.0 / np.arange(1, n + 1)))


def multiple_testing_adjust(p_values, method: str = "bhy") -> np.ndarray:
    """Adjusted p-values (original order) controlling for multiplicity.

    ``bonferroni`` / ``holm`` control the family-wise error rate; ``bhy``
    (Benjamini-Yekutieli) controls the FDR under arbitrary dependence.
    """
    p = np.asarray(p_values, dtype=np.float64)
    m = p.size
    if m == 0:
        return p
    method = method.lower()
    if method == "bonferroni":
        return np.minimum(p * m, 1.0)

    order = np.argsort(p)
    p_sorted = p[order]
    adj_sorted = np.empty(m)
    if method == "holm":  # step-down, enforce non-decreasing
        running = 0.0
        for k in range(m):  # rank k+1
            running = max(running, (m - k) * p_sorted[k])
            adj_sorted[k] = min(running, 1.0)
    elif method == "bhy":  # step-up with Σ1/i correction, non-decreasing from top
        c_m = _harmonic(m)
        running = 1.0
        for k in range(m - 1, -1, -1):  # rank k+1 from M down to 1
            running = min(running, c_m * m / (k + 1) * p_sorted[k])
            adj_sorted[k] = min(running, 1.0)
    else:
        raise ValueError(f"unknown method: {method!r}")

    adj = np.empty(m)
    adj[order] = adj_sorted
    return adj


def _single_test_pvalue_factor(n_trials: int, method: str) -> float:
    """Multiplier turning a single p-value into its rank-1 adjusted p-value."""
    method = method.lower()
    if method in ("bonferroni", "holm"):
        return float(n_trials)
    if method == "bhy":
        return n_trials * _harmonic(n_trials)
    raise ValueError(f"unknown method: {method!r}")


@dataclass
class HaircutResult:
    adjusted_sharpe: float
    haircut_fraction: float
    adjusted_pvalue: float
    observed_tstat: float
    adjusted_tstat: float


def haircut_sharpe_ratio(
    observed_sr: float,
    n_obs: int,
    n_trials: int,
    method: str = "bhy",
    periods_per_year: float = 252.0,
) -> HaircutResult:
    """Discount an annualized Sharpe for having been the best of ``n_trials``."""
    years = n_obs / periods_per_year
    if observed_sr <= 0.0 or years <= 0.0 or n_obs < 2:
        return HaircutResult(max(observed_sr, 0.0), 0.0, 1.0, 0.0, 0.0)

    t_stat = observed_sr * math.sqrt(years)
    p_single = 2.0 * (1.0 - stats.norm.cdf(t_stat))  # two-sided
    p_adj = min(p_single * _single_test_pvalue_factor(n_trials, method), 1.0)
    p_adj = min(max(p_adj, 1e-16), 1.0)
    t_adj = float(stats.norm.ppf(1.0 - p_adj / 2.0))

    ratio = max(t_adj / t_stat, 0.0)
    return HaircutResult(
        adjusted_sharpe=observed_sr * ratio,
        haircut_fraction=max(1.0 - ratio, 0.0),
        adjusted_pvalue=p_adj,
        observed_tstat=t_stat,
        adjusted_tstat=t_adj,
    )


def minimum_profit_hurdle(
    n_obs: int,
    n_trials: int,
    method: str = "bhy",
    significance: float = 0.05,
    periods_per_year: float = 252.0,
) -> float:
    """Minimum annualized Sharpe that stays significant after the adjustment."""
    years = n_obs / periods_per_year
    if years <= 0.0:
        return float("inf")
    p_single = significance / _single_test_pvalue_factor(n_trials, method)
    t_required = float(stats.norm.ppf(1.0 - p_single / 2.0))
    return t_required / math.sqrt(years)

```

---

### File: `new_pipeline/evaluation/minbtl.py`

```py
"""Minimum Backtest Length (MinBTL).

Bailey, Borwein, López de Prado & Zhu (2014), "Pseudo-Mathematics and Financial
Charlatanism", eq. for the minimum sample needed to keep a claimed Sharpe out of
the no-skill regime. Under ``n_trials`` independent skill-less strategies the
expected maximum (annualized) Sharpe over ``y`` years is

    E[max SR] ≈ (1/√y) · [(1-γ)·Z⁻¹(1-1/N) + γ·Z⁻¹(1-1/(N·e))]

(the bracket is exactly ``dsr.expected_max_sharpe`` with unit trial variance).
Setting that equal to the reported Sharpe and solving for ``y`` gives MinBTL: a
backtest shorter than this *expects* the reported Sharpe from luck alone.
"""

from new_pipeline.evaluation.dsr import expected_max_sharpe


def min_backtest_length(
    n_trials: int, target_sharpe: float, periods_per_year: float = 1.0
) -> float:
    """Minimum backtest length for ``target_sharpe`` to clear the no-skill bound.

    Returns years by default; pass ``periods_per_year`` (e.g. 252) to express the
    result in observations instead. ``target_sharpe`` is annualized.
    """
    if target_sharpe <= 0.0:
        return float("inf")
    if n_trials < 2:
        return 0.0
    bound = expected_max_sharpe(1.0, n_trials)  # E[max SR] at unit trial variance
    return (bound / target_sharpe) ** 2 * periods_per_year


def backtest_length_is_sufficient(
    n_obs: int, n_trials: int, target_sharpe: float, periods_per_year: float = 252.0
) -> bool:
    """True when ``n_obs`` observations clear the MinBTL for the trial count."""
    required = min_backtest_length(n_trials, target_sharpe, periods_per_year)
    return n_obs >= required

```

---

### File: `new_pipeline/evaluation/promotion.py`

```py
"""Champion promotion gate + immutable registry.

A candidate is promoted only if it clears every gate: Deflated Sharpe >=
threshold, HMM synthetic Sharpe > minimum, and (when supplied) Probability of
Backtest Overfitting <= threshold. PSR and the haircut Sharpe ride along as
recorded diagnostics. The registry is an append-only JSON audit:
``{"promotions": [...], "active_champions": {sector: model_path}}``.
"""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from new_pipeline.core.exceptions import PromotionError


@dataclass
class PromotionDecision:
    sector: str
    dsr: float
    synthetic_sharpe: float
    promoted: bool
    reason: str
    pbo: float | None = None
    psr: float | None = None
    haircut_sharpe: float | None = None


def assess_promotion(
    sector,
    dsr,
    synthetic_sharpe,
    dsr_threshold=0.95,
    synthetic_min=0.0,
    pbo=None,
    pbo_threshold=0.5,
    psr=None,
    haircut_sharpe=None,
    minbtl_satisfied=None,
) -> PromotionDecision:
    """Apply every promotion gate; the first failure names the rejection reason."""
    gates = {
        "low DSR": dsr < dsr_threshold,
        "failed synthetic gauntlet": synthetic_sharpe <= synthetic_min,
        "overfit (high PBO)": pbo is not None and pbo > pbo_threshold,
        "backtest shorter than MinBTL": minbtl_satisfied is False,
    }
    failed = [reason for reason, tripped in gates.items() if tripped]
    promoted = not failed
    return PromotionDecision(
        sector,
        dsr,
        synthetic_sharpe,
        promoted,
        "true alpha" if promoted else failed[0],
        pbo=pbo,
        psr=psr,
        haircut_sharpe=haircut_sharpe,
    )


class PromotionRegistry:
    def __init__(self, path):
        self._path = Path(path)
        self._data = self._load()

    def _load(self) -> dict:
        if self._path.exists():
            return json.loads(self._path.read_text(encoding="utf-8"))
        return {"promotions": [], "active_champions": {}}

    def record(self, decision: PromotionDecision, model_path: str | None = None) -> dict:
        if decision.promoted and model_path is None:
            raise PromotionError("a promoted decision requires a model_path")
        entry = {
            "sector": decision.sector,
            "dsr": decision.dsr,
            "synthetic_sharpe": decision.synthetic_sharpe,
            "pbo": decision.pbo,
            "psr": decision.psr,
            "haircut_sharpe": decision.haircut_sharpe,
            "promoted": decision.promoted,
            "reason": decision.reason,
            "timestamp": datetime.now(UTC).isoformat(),
            "model_path": model_path,
        }
        self._data["promotions"].append(entry)  # append-only audit trail
        if decision.promoted:
            self._data["active_champions"][decision.sector] = model_path
        self._save()
        return entry

    def is_champion(self, sector) -> bool:
        return sector in self._data["active_champions"]

    def active_champions(self) -> dict:
        return dict(self._data["active_champions"])

    @property
    def promotions(self) -> list:
        return list(self._data["promotions"])

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(self._data, indent=2), encoding="utf-8")

```

---

### File: `new_pipeline/evaluation/tearsheet.py`

```py
"""Lightweight performance summary (+ optional quantstats HTML tearsheet)."""

import numpy as np

from new_pipeline.tournament.simulator import sharpe_ratio


def summary_metrics(returns) -> dict:
    series = np.asarray(returns, dtype=np.float64)
    if series.size == 0:
        return {"sharpe": 0.0, "max_drawdown": 0.0, "win_rate": 0.0, "profit_factor": 0.0}
    equity = np.cumprod(1.0 + series)
    running_max = np.maximum.accumulate(equity)
    drawdown = (equity - running_max) / running_max
    wins = series[series > 0.0]
    losses = series[series < 0.0]
    gross_loss = float(-losses.sum())
    traded = series[series != 0.0]
    return {
        "sharpe": sharpe_ratio(series),
        "max_drawdown": float(drawdown.min()),
        "win_rate": float(wins.size / traded.size) if traded.size else 0.0,
        "profit_factor": float(wins.sum()) / gross_loss if gross_loss > 0.0 else 0.0,
    }


def write_html_tearsheet(returns, path) -> bool:
    """Write a quantstats HTML tearsheet if quantstats is installed, else False."""
    try:
        import pandas as pd
        import quantstats as qs
    except ImportError:
        return False
    series = pd.Series(np.asarray(returns, dtype=np.float64))
    qs.reports.html(series, output=str(path))  # pragma: no cover - optional dep
    return True

```

---

### File: `new_pipeline/evaluation/__init__.py`

```py
from .cscv import cscv_partition_indices, cscv_splits, n_cscv_splits
from .dsr import (
    compute_deflated_sharpe_ratio,
    expected_max_sharpe,
    interpret_dsr,
    min_track_record_length,
    probabilistic_sharpe_ratio,
)
from .haircut import (
    HaircutResult,
    haircut_sharpe_ratio,
    minimum_profit_hurdle,
    multiple_testing_adjust,
)
from .hmm_gauntlet import fit_regime_hmm, run_hmm_synthetic_gauntlet
from .minbtl import backtest_length_is_sufficient, min_backtest_length
from .pbo import CSCVResult, evaluate_cscv, probability_of_backtest_overfitting
from .promotion import PromotionDecision, PromotionRegistry, assess_promotion
from .tearsheet import summary_metrics, write_html_tearsheet

__all__ = [
    "CSCVResult",
    "HaircutResult",
    "PromotionDecision",
    "PromotionRegistry",
    "assess_promotion",
    "backtest_length_is_sufficient",
    "compute_deflated_sharpe_ratio",
    "cscv_partition_indices",
    "cscv_splits",
    "evaluate_cscv",
    "expected_max_sharpe",
    "fit_regime_hmm",
    "haircut_sharpe_ratio",
    "interpret_dsr",
    "min_backtest_length",
    "min_track_record_length",
    "minimum_profit_hurdle",
    "multiple_testing_adjust",
    "n_cscv_splits",
    "probabilistic_sharpe_ratio",
    "probability_of_backtest_overfitting",
    "run_hmm_synthetic_gauntlet",
    "summary_metrics",
    "write_html_tearsheet",
]

```

---

### File: `new_pipeline/evaluation/hmm_gauntlet.py`

```py
"""HMM synthetic-data gauntlet: does the model survive regimes it never saw?

Fit a 3-state Gaussian HMM to benchmark returns, sample a *synthetic* return
path, evaluate the model's signals on bootstrapped feature rows (whole rows, to
preserve cross-feature correlation — the legacy bug resampled per column), and
require a positive Sharpe on the synthetic path.
"""

import numpy as np
from hmmlearn.hmm import GaussianHMM

from new_pipeline.core.seeding import active_seed
from new_pipeline.tournament.simulator import sharpe_ratio


def fit_regime_hmm(benchmark_returns, n_states=3, n_iter=100, seed=None):
    series = np.asarray(benchmark_returns, dtype=np.float64).reshape(-1, 1)
    model = GaussianHMM(
        n_components=n_states,
        covariance_type="full",
        n_iter=n_iter,
        random_state=active_seed() if seed is None else seed,
    )
    model.fit(series)
    return model


def run_hmm_synthetic_gauntlet(
    benchmark_returns,
    features,
    predict_fn,
    n_states=3,
    n_iter=100,
    confidence_threshold=0.5,
    seed=None,
):
    """``predict_fn`` maps a feature matrix to per-row probabilities."""
    rng_seed = active_seed() if seed is None else seed
    model = fit_regime_hmm(benchmark_returns, n_states, n_iter, rng_seed)

    n_samples = len(benchmark_returns)
    synthetic_returns, _ = model.sample(n_samples, random_state=rng_seed)
    synthetic_returns = synthetic_returns.ravel()

    feature_matrix = np.asarray(features, dtype=np.float64)
    rng = np.random.default_rng(rng_seed)
    rows = rng.integers(0, feature_matrix.shape[0], size=n_samples)  # whole-row bootstrap
    sampled = feature_matrix[rows]

    proba = np.asarray(predict_fn(sampled), dtype=np.float64)
    signals = (proba > confidence_threshold).astype(np.float64)
    return sharpe_ratio(signals * synthetic_returns)

```

---

### File: `new_pipeline/evaluation/pbo.py`

```py
"""Probability of Backtest Overfitting (PBO) via CSCV.

Bailey, Borwein, López de Prado & Zhu (2014). Over every CSCV in-sample /
out-of-sample split we pick the trial that looks best in-sample and ask where it
ranks out-of-sample. If skill is real the IS winner keeps winning OOS; if the
backtest is overfit the IS winner is no better than a coin flip OOS, so its OOS
rank lands below the median. PBO is the fraction of splits where the IS-best
configuration underperforms the OOS median (rank logit <= 0).

Pure NumPy over the ``(n_obs, n_trials)`` matrix the tournament already emits.
"""

from dataclasses import dataclass

import numpy as np

from new_pipeline.evaluation.cscv import cscv_splits


def _sharpe_per_trial(block: np.ndarray) -> np.ndarray:
    """Column-wise Sharpe of a ``(n_obs, n_trials)`` block (0 rf, unscaled).

    Ranking is invariant to the annualization factor, so we skip the √periods
    term that ``simulator.sharpe_ratio`` applies — only the cross-trial order
    matters here.
    """
    mean = block.mean(axis=0)
    std = block.std(axis=0, ddof=1)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(std > 0.0, mean / std, 0.0)


def _even_partitions(n_obs: int, n_partitions: int) -> int:
    """Largest usable even partition count <= request and <= n_obs (0 if none)."""
    usable = min(n_partitions, n_obs)
    if usable % 2 != 0:
        usable -= 1
    return usable if usable >= 2 else 0


@dataclass
class CSCVResult:
    pbo: float
    probability_of_loss: float
    performance_degradation: float
    n_splits: int


def evaluate_cscv(returns_matrix, n_partitions: int = 10, score_fn=None) -> CSCVResult:
    """Run CSCV over the matrix and return PBO + degradation diagnostics."""
    matrix = np.asarray(returns_matrix, dtype=np.float64)
    if matrix.ndim != 2 or matrix.shape[1] < 2:
        return CSCVResult(0.0, 0.0, 0.0, 0)
    partitions = _even_partitions(matrix.shape[0], n_partitions)
    if partitions == 0:
        return CSCVResult(0.0, 0.0, 0.0, 0)

    score = score_fn or _sharpe_per_trial
    n_trials = matrix.shape[1]
    logits, is_best, oos_best = [], [], []
    for is_index, oos_index in cscv_splits(matrix.shape[0], partitions):
        is_perf = score(matrix[is_index])
        oos_perf = score(matrix[oos_index])
        best = int(np.argmax(is_perf))
        # Relative OOS rank of the IS-best trial in (0, 1); rank 1..N -> /(N+1).
        rank = float(np.sum(oos_perf <= oos_perf[best])) / (n_trials + 1)
        rank = min(max(rank, 1e-9), 1.0 - 1e-9)
        logits.append(np.log(rank / (1.0 - rank)))
        is_best.append(is_perf[best])
        oos_best.append(oos_perf[best])

    logits = np.asarray(logits)
    is_best = np.asarray(is_best)
    oos_best = np.asarray(oos_best)
    pbo = float(np.mean(logits <= 0.0))
    prob_loss = float(np.mean(oos_best < 0.0))
    degradation = _degradation_slope(is_best, oos_best)
    return CSCVResult(pbo, prob_loss, degradation, logits.size)


def _degradation_slope(is_best: np.ndarray, oos_best: np.ndarray) -> float:
    """Slope of OOS-on-IS performance for the selected trials (<0 = decay)."""
    if is_best.size < 2 or np.ptp(is_best) == 0.0:
        return 0.0
    return float(np.polyfit(is_best, oos_best, 1)[0])


def probability_of_backtest_overfitting(
    returns_matrix, n_partitions: int = 10, score_fn=None
) -> float:
    """PBO over a ``(n_obs, n_trials)`` matrix; each column is one trial's PnL."""
    return evaluate_cscv(returns_matrix, n_partitions, score_fn).pbo

```

---

### File: `new_pipeline/evaluation/cscv.py`

```py
"""Combinatorially Symmetric Cross-Validation (CSCV) splitter.

Bailey, Borwein, López de Prado & Zhu (2014), "Pseudo-Mathematics and Financial
Charlatanism". Partition the observation axis of a (n_obs x n_trials) returns
matrix into ``S`` disjoint, contiguous submatrices, then enumerate every
C(S, S/2) way of choosing half the partitions as in-sample (IS); the complement
is out-of-sample (OOS). Because each split's complement is *also* enumerated,
the construction is symmetric — the property that makes the downstream
overfitting estimate (PBO) unbiased.
"""

import math
from itertools import combinations

import numpy as np


def cscv_partition_indices(n_obs: int, n_partitions: int) -> list[np.ndarray]:
    """Split ``range(n_obs)`` into ``n_partitions`` contiguous index blocks."""
    if n_partitions < 2 or n_partitions % 2 != 0:
        raise ValueError("n_partitions must be an even integer >= 2")
    if n_obs < n_partitions:
        raise ValueError("need at least one observation per partition")
    return [block.astype(np.int64) for block in np.array_split(np.arange(n_obs), n_partitions)]


def n_cscv_splits(n_partitions: int) -> int:
    """Number of IS/OOS splits = C(S, S/2)."""
    return math.comb(n_partitions, n_partitions // 2)


def cscv_splits(n_obs: int, n_partitions: int):
    """Yield ``(is_index, oos_index)`` arrays over every C(S, S/2) IS/OOS choice."""
    blocks = cscv_partition_indices(n_obs, n_partitions)
    half = n_partitions // 2
    for chosen in combinations(range(n_partitions), half):
        is_set = set(chosen)
        is_index = np.concatenate([blocks[i] for i in range(n_partitions) if i in is_set])
        oos_index = np.concatenate([blocks[i] for i in range(n_partitions) if i not in is_set])
        yield np.sort(is_index), np.sort(oos_index)

```

---

### File: `new_pipeline/evaluation/dsr.py`

```py
"""Deflated & Probabilistic Sharpe Ratio (Bailey & López de Prado).

The Probabilistic Sharpe Ratio (PSR) is the probability the true Sharpe exceeds
a benchmark, adjusting for sample length and non-normal returns (skew + excess
kurtosis). The Deflated Sharpe Ratio (DSR) is PSR with the benchmark set to the
*expected maximum* Sharpe under ``n_trials`` skill-less strategies — i.e. it also
corrects for selection bias / multiple testing.

Note: the deflation term uses *non-excess* kurtosis (normal = 3).
"""

import math

import numpy as np
from scipy import stats

EULER_MASCHERONI = 0.5772156649


def expected_max_sharpe(var_trials: float, n_trials: int) -> float:
    """E[max SR] under the null of zero true skill across ``n_trials``."""
    if n_trials < 2 or var_trials <= 0.0:
        return 0.0
    sigma = math.sqrt(var_trials)
    z_high = stats.norm.ppf(1.0 - 1.0 / n_trials)
    z_low = stats.norm.ppf(1.0 - 1.0 / (n_trials * math.e))
    return sigma * ((1.0 - EULER_MASCHERONI) * z_high + EULER_MASCHERONI * z_low)


def _moments(series: np.ndarray):
    sharpe = series.mean() / series.std(ddof=1)
    skew = float(stats.skew(series))
    kurtosis = float(stats.kurtosis(series, fisher=False))  # non-excess (normal = 3)
    return sharpe, skew, kurtosis


def _deflation_term(sharpe: float, skew: float, kurtosis: float) -> float:
    """1 - γ₃·SR + (γ₄-1)/4·SR² — the variance factor of the SR estimator."""
    return 1.0 - skew * sharpe + (kurtosis - 1.0) / 4.0 * sharpe**2


def _psr_statistic(sharpe, skew, kurtosis, n_obs, benchmark_sr) -> float:
    denominator = math.sqrt(max(1e-12, _deflation_term(sharpe, skew, kurtosis)))
    return float(stats.norm.cdf((sharpe - benchmark_sr) * math.sqrt(n_obs - 1) / denominator))


def probabilistic_sharpe_ratio(returns, benchmark_sr: float = 0.0) -> float:
    """Probability the true (per-observation) Sharpe exceeds ``benchmark_sr``."""
    series = np.asarray(returns, dtype=np.float64)
    if series.size < 3 or series.std(ddof=1) <= 0.0:
        return 0.0
    return _psr_statistic(*_moments(series), series.size, benchmark_sr)


def min_track_record_length(returns, benchmark_sr: float = 0.0, prob: float = 0.95) -> float:
    """Minimum observations for PSR(benchmark_sr) to reach ``prob`` confidence."""
    series = np.asarray(returns, dtype=np.float64)
    if series.size < 3 or series.std(ddof=1) <= 0.0:
        return float("inf")
    sharpe, skew, kurtosis = _moments(series)
    if sharpe <= benchmark_sr:
        return float("inf")
    z = stats.norm.ppf(prob)
    return 1.0 + _deflation_term(sharpe, skew, kurtosis) * (z / (sharpe - benchmark_sr)) ** 2


def compute_deflated_sharpe_ratio(returns, trial_sharpes) -> float:
    """Probability the strategy's true Sharpe beats the expected max under the
    null of ``len(trial_sharpes)`` skill-less trials. Returns 0..1."""
    series = np.asarray(returns, dtype=np.float64)
    if series.size < 3 or series.std(ddof=1) <= 0.0:
        return 0.0
    trials = np.asarray(trial_sharpes, dtype=np.float64)
    var_trials = float(np.var(trials, ddof=1)) if trials.size > 1 else 0.0
    sr0 = expected_max_sharpe(var_trials, trials.size)
    return _psr_statistic(*_moments(series), series.size, sr0)


def interpret_dsr(dsr: float, threshold: float = 0.95) -> str:
    if dsr < 0.5:
        return "overfit"
    if dsr < threshold:
        return "insignificant"
    return "promote"

```

---

### File: `new_pipeline/models/metadata.py`

```py
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class ModelMetadata(BaseModel):
    model_name: str
    version: str
    created_at: datetime
    feature_set: list[str]
    path: Path

    class Config:
        arbitrary_types_allowed = True

```

---

### File: `new_pipeline/models/__init__.py`

```py
from .metadata import ModelMetadata
from .registry import ModelRegistry

__all__ = ["ModelRegistry", "ModelMetadata"]

```

---

### File: `new_pipeline/models/registry.py`

```py

from .metadata import ModelMetadata


class ModelRegistry:
    def __init__(self) -> None:
        self._registry: dict[str, ModelMetadata] = {}

    def register(self, model_name: str, metadata: ModelMetadata) -> None:
        self._registry[model_name] = metadata

    def get(self, model_name: str) -> ModelMetadata | None:
        return self._registry.get(model_name)

    def list_models(self) -> list[str]:
        return list(self._registry.keys())

```

---

### File: `new_pipeline/config/defaults.yaml`

```yaml
data:
  raw_vault_dir: "./data/raw"
  processed_vault_dir: "./data/processed"
  parquet_blocksize: "128MiB"
  row_group_size: 100000
  validation_mode: "strict"

features:
  cache_enabled: true
  gpu_enabled: false
  batch_size: 1024
  metadata_dir: "./data/metadata"
  slippage_constant: 0.5
  regime_percentile: 0.8
  bps_scaler: 10000.0
  max_slippage_bps: 50.0

models:
  prod_models_dir: "./models/prod"
  candidate_models_dir: "./models/candidates"
  model_version: "v0.1"

execution:
  max_risk_per_trade: 0.02
  atr_stop_multiplier: 2.0
  confidence_threshold: 0.65
  max_adv_coverage: 0.25
  ledger_dir: "./data/ledger"
  max_retries: 3
  tif: "day"
  account_capital: 100000.0

logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  log_file: "./logs/system.log"
  max_bytes: 10485760
  json_logs: false
  trace_enabled: true

fusion:
  enabled: false
  ollama_endpoint: "http://localhost:11434"
  llm_model_name: "qwen-3"
  sentiment_timeout: 5.0
  semaphore_limit: 20
  verdict_model: "qwen-3"

system:
  run_mode: "backtest"
  dask_enabled: false
  num_workers: 1
  memory_limit: "8GB"

gpu:
  cuda_enabled: false
  device: "cpu"
  fallback_to_cpu: true

tournament:
  n_groups: 6
  test_groups: 2
  purge_days: 5
  embargo_days: 5
  penalty_fp: 5.0
  penalty_fn: 1.0
  num_boost_round: 100
  cache_host_ratio: 0.75
  tree_method: "hist"
  device: "cpu"
  sectors:
    - "Information Technology"
    - "Health Care"
    - "Financials"
    - "Consumer Discretionary"
    - "Communication Services"
    - "Industrials"
    - "Consumer Staples"
    - "Energy"
    - "Utilities"
    - "Real Estate"
    - "Materials"

evaluation:
  dsr_promotion_threshold: 0.95
  hmm_states: 3
  hmm_n_iter: 100
  synthetic_sr_min: 0.0
  registry_path: "./models/prod/promotion_registry.json"
  psr_benchmark_sr: 0.0
  pbo_threshold: 0.5
  pbo_partitions: 10
  mt_method: "bhy"
  enforce_minbtl: false

mcp:
  transport: "stdio"

rag:
  embedder: "hashing"
  top_k: 5
  chunk_size: 512
  chunk_overlap: 100

dashboard:
  veto_ledger_path: "./data/ledger/veto_ledger.parquet"
  trade_log_path: "./data/ledger/trade_log.parquet"
  refresh_seconds: 5
  max_drawdown_alert: 0.15
  min_sharpe_alert: 0.0
  max_veto_rate_alert: 0.5

alpaca:
  # Credentials are injected via QA_ALPACA__API_KEY / QA_ALPACA__SECRET_KEY env
  # vars (never committed). Paper trading + the free IEX data feed by default.
  api_key: ""
  secret_key: ""
  paper: true
  data_feed: "iex"

```

---

### File: `new_pipeline/config/schema.py`

```py
from pydantic import BaseModel, Field


class DataConfig(BaseModel):
    raw_vault_dir: str
    processed_vault_dir: str
    parquet_blocksize: str
    row_group_size: int
    validation_mode: str


class FeatureConfig(BaseModel):
    cache_enabled: bool
    gpu_enabled: bool
    batch_size: int
    metadata_dir: str
    slippage_constant: float = 0.5
    regime_percentile: float = 0.8
    bps_scaler: float = 10000.0
    max_slippage_bps: float = 50.0
    crash_window: int = 60
    label_horizon: int = 1
    label_cost_bps: float = 10.0


class ModelConfig(BaseModel):
    prod_models_dir: str
    candidate_models_dir: str
    model_version: str


class ExecutionConfig(BaseModel):
    max_risk_per_trade: float
    atr_stop_multiplier: float
    confidence_threshold: float
    max_adv_coverage: float = 0.25
    ledger_dir: str = "./data/ledger"
    max_retries: int = 3
    tif: str = "day"
    account_capital: float = 100_000.0


class LoggingConfig(BaseModel):
    level: str
    format: str
    log_file: str
    max_bytes: int
    json_logs: bool = False
    trace_enabled: bool = True


class FusionConfig(BaseModel):
    enabled: bool
    ollama_endpoint: str
    llm_model_name: str
    sentiment_timeout: float
    semaphore_limit: int
    verdict_model: str = "qwen-3"


class GPUConfig(BaseModel):
    cuda_enabled: bool = False
    device: str = "cpu"
    fallback_to_cpu: bool = True


class TournamentConfig(BaseModel):
    n_groups: int = 6
    test_groups: int = 2
    purge_days: int = 5
    embargo_days: int = 5
    penalty_fp: float = 5.0
    penalty_fn: float = 1.0
    num_boost_round: int = 100
    early_stopping_rounds: int = 25
    cache_host_ratio: float = 0.75
    tree_method: str = "hist"
    device: str = "cpu"
    max_workers: int = 1
    cfs_distance_threshold: float = 0.5
    cfs_min_importance: float = 0.0
    sectors: list[str] = Field(default_factory=list)


class EvaluationConfig(BaseModel):
    dsr_promotion_threshold: float = 0.95
    hmm_states: int = 3
    hmm_n_iter: int = 100
    synthetic_sr_min: float = 0.0
    registry_path: str = "./models/prod/promotion_registry.json"
    psr_benchmark_sr: float = 0.0
    pbo_threshold: float = 0.5
    pbo_partitions: int = 10
    mt_method: str = "bhy"
    enforce_minbtl: bool = False


class MCPConfig(BaseModel):
    transport: str = "stdio"


class RAGConfig(BaseModel):
    embedder: str = "hashing"
    top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 100


class DashboardConfig(BaseModel):
    veto_ledger_path: str = "./data/ledger/veto_ledger.parquet"
    trade_log_path: str = "./data/ledger/trade_log.parquet"
    refresh_seconds: int = 5
    max_drawdown_alert: float = 0.15
    min_sharpe_alert: float = 0.0
    max_veto_rate_alert: float = 0.5
    auth_enabled: bool = False


class SystemConfig(BaseModel):
    run_mode: str
    dask_enabled: bool
    num_workers: int
    memory_limit: str


class AlpacaConfig(BaseModel):
    """Live Alpaca credentials/settings. Keys come from QA_ALPACA__* env vars and
    are never committed; dev/test/backtest run on fakes and ignore these."""

    api_key: str = ""
    secret_key: str = ""
    paper: bool = True
    data_feed: str = "iex"  # free feed; "sip" needs a paid subscription


class AppConfig(BaseModel):
    data: DataConfig
    features: FeatureConfig
    models: ModelConfig
    execution: ExecutionConfig
    logging: LoggingConfig
    fusion: FusionConfig
    system: SystemConfig
    gpu: GPUConfig = Field(default_factory=GPUConfig)
    tournament: TournamentConfig = Field(default_factory=TournamentConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    alpaca: AlpacaConfig = Field(default_factory=AlpacaConfig)

```

---

### File: `new_pipeline/config/testing.yaml`

```yaml
# Testing overlay — isolated vault paths, quiet logs, deterministic and offline.
# Layered over defaults.yaml, then any QA_-prefixed env vars win.
data:
  raw_vault_dir: "./data/test/raw"
  processed_vault_dir: "./data/test/processed"
logging:
  level: "WARNING"
  json_logs: false
features:
  gpu_enabled: false
  cache_enabled: false
gpu:
  cuda_enabled: false
  device: "cpu"
fusion:
  enabled: false
system:
  run_mode: "backtest"
  dask_enabled: false

```

---

### File: `new_pipeline/config/__init__.py`

```py
from .base import build_config, get_config, reload_config

__all__ = ["build_config", "get_config", "reload_config"]

```

---

### File: `new_pipeline/config/development.py`

```py
from .base import build_config
from .schema import AppConfig


def development_config() -> AppConfig:
    return build_config(env="development")

```

---

### File: `new_pipeline/config/base.py`

```py
import copy
import os
from pathlib import Path
from typing import Any

import yaml

from .schema import AppConfig

_CONFIG_DIR = Path(__file__).resolve().parent
_DEFAULTS_PATH = _CONFIG_DIR / "defaults.yaml"

# Recognized deployment environments and their overlay files (layered over
# defaults.yaml, then any QA_-prefixed env vars win).
_ENV_OVERLAYS = {
    "development": _CONFIG_DIR / "development.yaml",
    "testing": _CONFIG_DIR / "testing.yaml",
    "production": _CONFIG_DIR / "production.yaml",
}

_CONFIG_INSTANCE: AppConfig | None = None


def load_defaults() -> dict[str, Any]:
    with open(_DEFAULTS_PATH, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def _load_overlay(env: str) -> dict[str, Any]:
    path = _ENV_OVERLAYS.get(env)
    if path is None or not path.exists():
        return {}
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


class ConfigManager:
    def __init__(self, env: str | None = None) -> None:
        self._env = env if env is not None else os.environ.get("QA_ENV")
        self._defaults = load_defaults()
        self._config = self._build_config()

    def _build_config(self) -> AppConfig:
        merged = copy.deepcopy(self._defaults)
        if self._env:
            merged = _deep_merge(merged, _load_overlay(self._env))

        for key, value in os.environ.items():
            # QA_ENV selects the overlay; it is not a config key itself.
            if key.startswith("QA_") and key != "QA_ENV":
                parts = key[3:].lower().split("__")
                target = merged
                for part in parts[:-1]:
                    if part not in target or not isinstance(target[part], dict):
                        target[part] = {}
                    target = target[part]
                target[parts[-1]] = self._parse_env_value(value)

        return AppConfig.model_validate(merged)

    @staticmethod
    def _parse_env_value(value: str) -> Any:
        if value.lower() in {"true", "false"}:
            return value.lower() == "true"
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            return value

    def get_config(self) -> AppConfig:
        return self._config


def get_config() -> AppConfig:
    global _CONFIG_INSTANCE
    if _CONFIG_INSTANCE is None:
        _CONFIG_INSTANCE = ConfigManager().get_config()
    return _CONFIG_INSTANCE


def reload_config() -> AppConfig:
    global _CONFIG_INSTANCE
    _CONFIG_INSTANCE = None
    return get_config()


def build_config(env: str | None = None) -> AppConfig:
    """Build a fresh (non-singleton) config for a specific environment overlay."""
    return ConfigManager(env=env).get_config()

```

---

### File: `new_pipeline/config/production.yaml`

```yaml
# Production overlay — GPU on, structured JSON logs, live fusion.
# Layered over defaults.yaml, then any QA_-prefixed env vars (incl. secrets) win.
logging:
  level: "INFO"
  json_logs: true
features:
  gpu_enabled: true
gpu:
  cuda_enabled: true
  device: "cuda"
  fallback_to_cpu: true
fusion:
  enabled: true
tournament:
  device: "cuda"
system:
  run_mode: "live"

```

---

### File: `new_pipeline/config/testing.py`

```py
from .base import build_config
from .schema import AppConfig


def testing_config() -> AppConfig:
    return build_config(env="testing")

```

---

### File: `new_pipeline/config/development.yaml`

```yaml
# Development overlay — verbose logging, everything local and offline.
# Layered over defaults.yaml, then any QA_-prefixed env vars win.
logging:
  level: "DEBUG"
  json_logs: false
features:
  gpu_enabled: false
gpu:
  cuda_enabled: false
  device: "cpu"
fusion:
  enabled: false
system:
  run_mode: "backtest"

```

---

### File: `new_pipeline/config/production.py`

```py
from .base import build_config
from .schema import AppConfig


def production_config() -> AppConfig:
    return build_config(env="production")

```

---

### File: `new_pipeline/docs/LOGGING_GUIDE.md`

```markdown
# Logging Guide

The core logging setup is implemented in `core/logging.py`. It creates a `RotatingFileHandler` and formats logs using settings from config.

```

---

### File: `new_pipeline/docs/API_REFERENCE.md`

```markdown
# API Reference

This file will document the public interfaces for Phase 1 modules.

## Config
- `get_config()`

## Core
- `configure_logging()`
- `project_root()`

## Data
- `DataIngestion`
- `VaultManager`
- `DataValidator`

## Execution
- `RiskManager`
- `BrokerAdapter`

```

---

### File: `new_pipeline/docs/ARCHITECTURE.md`

```markdown
# Phase 1 Architecture

This document describes the Phase 1 architecture for the Quantum Avenger pipeline.

## Goals
- Establish configuration and core infrastructure
- Create data vault management and feature layer skeletons
- Provide a stable basis for future Phase 2 and beyond

```

---

### File: `new_pipeline/docs/ERROR_HANDLING.md`

```markdown
# Error Handling

All custom domain exceptions are defined under `core/exceptions.py`.

- `QuantumAvengerError`: base class
- `ConfigurationError`: config validation failures
- `DataValidationError`: data quality issues
- `IngestionError`: ingestion failures
- `ExecutionError`: runtime execution problems

```

---

### File: `new_pipeline/docs/CONFIG_GUIDE.md`

```markdown
# Configuration Guide

The `config` package exposes `get_config()` which loads defaults from `config/defaults.yaml` and applies `QA__` environment variable overrides.

Example usage:

```python
from config import get_config
config = get_config()
print(config.data.raw_vault_dir)
```

```

---

### File: `new_pipeline/docs/TESTING_GUIDE.md`

```markdown
# Testing Guide

Phase 1 includes unit tests for config, logging, exceptions, and retry utilities, as well as a sample integration test for vault path creation.

Run tests with:

```bash
pytest new_pipeline/tests
```

```

---

### File: `new_pipeline/data/training_db.py`

```py
"""Training-database builder: historical stock (+ optional news) -> feature vault.

Reuses the offline training-frame assembly (bars -> production features ->
friction-aware labels -> sector join) but is source-agnostic: hand it the live
``AlpacaMarketDataSource`` to materialize a real training database, or the fake
for an offline dry run. Optionally enriches each ``(ticker, date)`` row with a
news ``sentiment_score`` via a ``NewsSource`` + ``LLMClient``.
"""

from datetime import date
from pathlib import Path

import polars as pl

from new_pipeline.adapters import StaticUniverseProvider
from new_pipeline.config import get_config
from new_pipeline.tournament.pipeline import build_training_frame


def add_news_sentiment(frame: pl.DataFrame, news_source, llm) -> pl.DataFrame:
    """Add a per-(ticker, date) ``sentiment_score`` in [-1, 1] from news headlines."""
    scores = []
    for ticker, day in zip(frame["ticker"].to_list(), frame["date"].to_list(), strict=True):
        items = news_source.headlines(ticker, day)
        if items:
            values = [llm.sentiment(item.headline).score for item in items]
            scores.append(sum(values) / len(values))
        else:
            scores.append(0.0)
    return frame.with_columns(pl.Series("sentiment_score", scores))


def build_training_database(
    output_path,
    source,
    universe=None,
    start: date = date(2023, 1, 1),
    end: date = date(2023, 12, 31),
    cfg=None,
    news_source=None,
    llm=None,
) -> dict:
    """Materialize a labeled feature parquet for the universe over the date range."""
    cfg = cfg or get_config()
    universe = universe or StaticUniverseProvider()
    sectors = universe.sectors()
    symbols = list(sectors)

    frame = build_training_frame(symbols, sectors, start, end, source, cfg)
    if news_source is not None and llm is not None:
        frame = add_news_sentiment(frame, news_source, llm)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(out)
    return {
        "rows": frame.height,
        "symbols": len(symbols),
        "columns": frame.columns,
        "path": str(out),
        "start": start.isoformat(),
        "end": end.isoformat(),
    }

```

---

### File: `new_pipeline/data/validation.py`

```py
from pathlib import Path

import pandas as pd

from new_pipeline.config import get_config
from new_pipeline.core.exceptions import DataValidationError


class DataValidator:
    def __init__(self) -> None:
        self.config = get_config()

    def validate_dataframe(self, df: pd.DataFrame) -> bool:
        missing = df.isna().sum().sum()
        if missing > 0 and self.config.data.validation_mode == "strict":
            raise DataValidationError("Data contains missing values")
        return missing == 0

    def validate_file(self, path: Path) -> bool:
        if not path.exists():
            raise DataValidationError(f"Data file missing: {path}")
        return True

```

---

### File: `new_pipeline/data/__init__.py`

```py
from .base import BaseDataHandler
from .ingestion import DataIngestion
from .validation import DataValidator
from .vaults import VaultManager

__all__ = ["BaseDataHandler", "DataIngestion", "VaultManager", "DataValidator"]

```

---

### File: `new_pipeline/data/ingestion.py`

```py
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd

from new_pipeline.config import get_config
from new_pipeline.core.exceptions import IngestionError


class DataIngestion:
    def __init__(self) -> None:
        self.config = get_config()

    def ensure_raw_vault(self) -> Path:
        raw_dir = Path(self.config.data.raw_vault_dir)
        raw_dir.mkdir(parents=True, exist_ok=True)
        return raw_dir

    def stage_source_file(self, source_path: Path, destination_name: str) -> Path:
        raw_dir = self.ensure_raw_vault()
        target_path = raw_dir / destination_name
        try:
            if not source_path.exists():
                raise IngestionError(f"Source file does not exist: {source_path}")
            with source_path.open("rb") as source, target_path.open("wb") as dest:
                dest.write(source.read())
            return target_path
        except Exception as exc:
            raise IngestionError(f"Failed to stage source file: {exc}") from exc

    def stage_dataframe(self, df: pd.DataFrame, destination_name: str) -> Path:
        raw_dir = self.ensure_raw_vault()
        target_path = raw_dir / destination_name
        try:
            if target_path.suffix == ".parquet":
                try:
                    df.to_parquet(target_path, index=False)
                except ImportError as exc:
                    raise IngestionError(
                        "Parquet support requires pyarrow or fastparquet. "
                        "Install it before using .parquet output."
                    ) from exc
            else:
                df.to_csv(target_path, index=False)
            return target_path
        except Exception as exc:
            raise IngestionError(f"Failed to persist dataframe: {exc}") from exc

    def load_raw_dataframe(self, source_name: str) -> pd.DataFrame:
        raw_dir = self.ensure_raw_vault()
        source_path = raw_dir / source_name
        if not source_path.exists():
            raise IngestionError(f"Raw file missing: {source_path}")

        try:
            if source_path.suffix == ".parquet":
                return pd.read_parquet(source_path)
            return pd.read_csv(source_path, parse_dates=["date"])
        except Exception as exc:
            raise IngestionError(f"Failed to load raw dataframe: {exc}") from exc

    def load_many(self, source_names, max_workers: int = 4) -> dict[str, pd.DataFrame]:
        """Load multiple raw files concurrently (I/O-bound ThreadPool)."""
        names = list(source_names)
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            frames = list(pool.map(self.load_raw_dataframe, names))
        return dict(zip(names, frames, strict=True))

```

---

### File: `new_pipeline/data/base.py`

```py
from abc import ABC, abstractmethod
from pathlib import Path


class BaseDataHandler(ABC):
    @abstractmethod
    def load(self, path: Path):
        raise NotImplementedError

    @abstractmethod
    def save(self, path: Path):
        raise NotImplementedError

    @abstractmethod
    def validate(self) -> bool:
        raise NotImplementedError

```

---

### File: `new_pipeline/data/sizing.py`

```py
"""Dynamic, RAM-aware Parquet sizing (claude.md mandate).

Picks a Parquet block size and row-group size from available physical RAM
(psutil) — 64-256 MiB blocks — so large vaults stream without OOM instead of a
hardcoded constant. ``available_bytes`` is injectable for deterministic tests.
"""

import psutil

MIN_BLOCK_BYTES = 64 * 1024 * 1024
MAX_BLOCK_BYTES = 256 * 1024 * 1024


def dynamic_block_bytes(fraction: float = 0.05, available_bytes: int | None = None) -> int:
    if available_bytes is None:
        available_bytes = psutil.virtual_memory().available
    target = int(available_bytes * fraction)
    return max(MIN_BLOCK_BYTES, min(MAX_BLOCK_BYTES, target))


def dynamic_row_group_size(
    avg_row_bytes: int = 512,
    fraction: float = 0.05,
    max_rows: int = 500_000,
    available_bytes: int | None = None,
) -> int:
    block = dynamic_block_bytes(fraction, available_bytes)
    rows = block // max(1, avg_row_bytes)
    return max(1000, min(max_rows, rows))

```

---

### File: `new_pipeline/data/vaults.py`

```py
from pathlib import Path

from new_pipeline.config import get_config


class VaultManager:
    def __init__(self) -> None:
        self.config = get_config()

    def raw_vault_path(self) -> Path:
        path = Path(self.config.data.raw_vault_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def processed_vault_path(self) -> Path:
        path = Path(self.config.data.processed_vault_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def ensure_vaults(self) -> tuple[Path, Path]:
        return self.raw_vault_path(), self.processed_vault_path()

```

---

### File: `new_pipeline/scripts/check_health.py`

```py
from new_pipeline.monitoring.health import HealthCheck

if __name__ == "__main__":
    status = HealthCheck().status()
    print(status)

```

---

### File: `new_pipeline/scripts/serve_mcp.py`

```py
"""Offline stand-in entrypoint for the MCP tool server (Phase 7 container image).

Prints the deterministic quant-tool registry as JSON-RPC tool schemas. The live
FastMCP stdio server is wired here at the live cutover; until then this is a
runnable inventory entrypoint for the MCP image.
"""

import json

from new_pipeline.execution.mcp_tools import build_default_registry


def main() -> None:
    registry = build_default_registry()
    print(json.dumps({"tools": registry.schemas()}, indent=2))


if __name__ == "__main__":
    main()

```

---

### File: `new_pipeline/scripts/ingest_training_data.py`

```py
"""Build a training database from Alpaca historical data (live) or fakes (offline).

  PYTHONPATH=. QA_SYSTEM__RUN_MODE=live QA_ALPACA__API_KEY=... QA_ALPACA__SECRET_KEY=... \
      python new_pipeline/scripts/ingest_training_data.py \
      --start 2023-06-01 --end 2023-12-31 --out data/processed/training.parquet --news

Live mode pulls real bars (+ optional news sentiment) from Alpaca and needs an
allowlisted host; any offline run_mode uses the deterministic fakes.
"""

import argparse
import json
from datetime import date

from new_pipeline.adapters.factory import build_adapters
from new_pipeline.config import get_config
from new_pipeline.core.logging import configure_logging
from new_pipeline.data.training_db import build_training_database


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Quantum Avenger training database")
    parser.add_argument("--start", default="2023-06-01")
    parser.add_argument("--end", default="2023-12-31")
    parser.add_argument("--out", default="data/processed/training.parquet")
    parser.add_argument("--news", action="store_true", help="enrich rows with news sentiment")
    args = parser.parse_args()

    configure_logging()
    cfg = get_config()
    bundle = build_adapters(cfg)
    summary = build_training_database(
        args.out,
        bundle.market_data,
        bundle.universe,
        start=date.fromisoformat(args.start),
        end=date.fromisoformat(args.end),
        cfg=cfg,
        news_source=bundle.news if args.news else None,
        llm=bundle.llm if args.news else None,
    )
    summary["columns"] = len(summary["columns"])
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()

```

---

### File: `new_pipeline/scripts/live_smoke.py`

```py
"""Live Alpaca paper-trading smoke test.

Confirms connectivity + order submission end to end: prints the account, submits
a tiny order for one symbol, and prints the resulting positions. Requires
QA_ALPACA__API_KEY / QA_ALPACA__SECRET_KEY and egress to
paper-api.alpaca.markets. Paper only.

  QA_ALPACA__API_KEY=... QA_ALPACA__SECRET_KEY=... PYTHONPATH=. \
      python new_pipeline/scripts/live_smoke.py --symbol AAPL --qty 1
"""

import argparse
import json

from new_pipeline.config import get_config


def main() -> None:
    parser = argparse.ArgumentParser(description="Alpaca paper-trading smoke test")
    parser.add_argument("--symbol", default="AAPL")
    parser.add_argument("--qty", type=int, default=1)
    parser.add_argument("--limit-price", type=float, default=None)
    args = parser.parse_args()

    cfg = get_config()
    if not (cfg.alpaca.api_key and cfg.alpaca.secret_key):
        raise SystemExit("Set QA_ALPACA__API_KEY and QA_ALPACA__SECRET_KEY first.")
    if not cfg.alpaca.paper:
        raise SystemExit("Refusing to run the smoke test against a live-money account.")

    from new_pipeline.adapters.broker_alpaca import AlpacaBroker

    broker = AlpacaBroker(cfg.alpaca.api_key, cfg.alpaca.secret_key, paper=True)
    print("account:", json.dumps(broker.account(), indent=2))
    print("positions before:", broker.get_positions())
    order = {"symbol": args.symbol, "qty": args.qty, "side": "buy", "tif": "day"}
    if args.limit_price is not None:
        order["limit_price"] = args.limit_price
    print("order receipt:", json.dumps(broker.submit_order(order), indent=2))
    print("positions after:", broker.get_positions())


if __name__ == "__main__":
    main()

```

---

### File: `new_pipeline/monitoring/telemetry.py`

```py
"""Telemetry export in Prometheus text exposition format (Phase 7).

No ``prometheus_client`` dependency — the scrape payload is rendered as plain
text so a ``/metrics`` endpoint works anywhere and stays unit-testable offline.
Numeric values become gauges; the metric names the roadmap calls out
(``trade_rate``, ``veto_rate``, ``execution_latency_ms``, ``dsr_value``, …) are
simply keys in the payload.
"""

from typing import Any

from new_pipeline.monitoring.metrics import MetricsCollector

DEFAULT_PREFIX = "quantum_avenger"


def render_prometheus(metrics: dict[str, float], prefix: str = DEFAULT_PREFIX) -> str:
    """Render a ``{name: value}`` mapping as Prometheus text exposition format."""
    lines: list[str] = []
    for name in sorted(metrics):
        metric_name = f"{prefix}_{name}"
        lines.append(f"# TYPE {metric_name} gauge")
        lines.append(f"{metric_name} {float(metrics[name])}")
    return "\n".join(lines) + "\n" if lines else ""


class TelemetryExporter:
    def __init__(self, prefix: str = DEFAULT_PREFIX) -> None:
        self._prefix = prefix
        self._last_render = ""

    def export(self, payload: dict[str, Any]) -> str:
        numeric = {
            key: float(value)
            for key, value in payload.items()
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        }
        self._last_render = render_prometheus(numeric, self._prefix)
        return self._last_render

    def from_collector(self, collector: MetricsCollector) -> str:
        return self.export(dict(collector.counters))

    @property
    def last_render(self) -> str:
        return self._last_render

```

---

### File: `new_pipeline/monitoring/metrics_endpoint.py`

```py
"""Prometheus ``/metrics`` HTTP exposition (Phase 7 observability).

Frameworkless: :func:`render_metrics_response` returns ``(status, content_type,
body)`` so it is unit-testable, and :func:`serve_metrics` binds a tiny
``http.server`` for real use (Prometheus scrapes the body the exporter renders).
"""

from new_pipeline.monitoring.metrics import MetricsCollector
from new_pipeline.monitoring.telemetry import TelemetryExporter

CONTENT_TYPE = "text/plain; version=0.0.4"


def render_metrics_response(collector: MetricsCollector) -> tuple[int, str, str]:
    return 200, CONTENT_TYPE, TelemetryExporter().from_collector(collector)


def serve_metrics(collector, host="0.0.0.0", port=9090):  # pragma: no cover - binds a socket
    from http.server import BaseHTTPRequestHandler, HTTPServer

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            status, content_type, body = render_metrics_response(collector)
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))

        def log_message(self, *args):
            pass

    HTTPServer((host, port), _Handler).serve_forever()

```

---

### File: `new_pipeline/monitoring/__init__.py`

```py
from .health import HealthCheck
from .metrics import MetricsCollector
from .telemetry import TelemetryExporter, render_prometheus

__all__ = ["HealthCheck", "MetricsCollector", "TelemetryExporter", "render_prometheus"]

```

---

### File: `new_pipeline/monitoring/metrics.py`

```py
from dataclasses import dataclass


@dataclass
class MetricsCollector:
    counters: dict[str, int] = None

    def __post_init__(self) -> None:
        self.counters = self.counters or {}

    def increment(self, name: str, amount: int = 1) -> None:
        self.counters[name] = self.counters.get(name, 0) + amount

    def get(self, name: str) -> int:
        return self.counters.get(name, 0)

```

---

### File: `new_pipeline/monitoring/health.py`

```py
class HealthCheck:
    def status(self) -> dict[str, str]:
        return {"status": "healthy"}

```

---

### File: `new_pipeline/monitoring/dashboard/auth.py`

```py
"""Dashboard auth gate (restored from the legacy dashboard).

Credentials come from env vars (``DASHBOARD_USER`` / ``DASHBOARD_PASS``) — never
stored in config or code. ``verify_credentials`` is a pure, constant-time check
so it is testable without Streamlit; ``require_login`` wires it into the app.
"""

import hmac
import os


def verify_credentials(
    username, password, expected_user=None, expected_password=None
) -> bool:
    expected_user = (
        expected_user if expected_user is not None else os.environ.get("DASHBOARD_USER", "")
    )
    expected_password = (
        expected_password
        if expected_password is not None
        else os.environ.get("DASHBOARD_PASS", "")
    )
    if not expected_user or not expected_password:
        return False  # fail closed when no credentials are configured
    return hmac.compare_digest(str(username), expected_user) and hmac.compare_digest(
        str(password), expected_password
    )


def require_login(st) -> bool:  # pragma: no cover - exercised via the Streamlit app
    """Render a login gate; return True once authenticated."""
    if st.session_state.get("authenticated"):
        return True
    st.title("🛡️ Quantum Avenger — Sign in")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Sign in"):
        if verify_credentials(username, password):
            st.session_state["authenticated"] = True
            return True
        st.error("Invalid credentials.")
    return False

```

---

### File: `new_pipeline/monitoring/dashboard/alerts.py`

```py
"""Threshold alert engine for the dashboard (Phase 6).

Pure function over the computed KPIs so it is unit-testable without a UI.
"""

from dataclasses import dataclass

from new_pipeline.monitoring.dashboard.realtime import Performance, VetoSummary


@dataclass
class Alert:
    severity: str  # "warning" | "critical"
    message: str


def check_alerts(
    performance: Performance,
    veto_summary: VetoSummary,
    *,
    max_drawdown: float = 0.15,
    min_sharpe: float = 0.0,
    max_veto_rate: float = 0.5,
) -> list[Alert]:
    alerts: list[Alert] = []
    if performance.max_drawdown < -abs(max_drawdown):
        alerts.append(
            Alert("critical", f"Max drawdown {performance.max_drawdown:.1%} breached "
                              f"the {abs(max_drawdown):.0%} limit")
        )
    if performance.sharpe < min_sharpe:
        alerts.append(Alert("warning", f"Sharpe {performance.sharpe:.2f} below {min_sharpe:.2f}"))
    if veto_summary.veto_rate > max_veto_rate:
        alerts.append(
            Alert("warning", f"Veto rate {veto_summary.veto_rate:.0%} exceeds "
                            f"{max_veto_rate:.0%}")
        )
    return alerts

```

---

### File: `new_pipeline/monitoring/dashboard/__init__.py`

```py
from .alerts import Alert, check_alerts
from .realtime import Performance, RealtimeDataManager, VetoSummary

__all__ = ["Alert", "Performance", "RealtimeDataManager", "VetoSummary", "check_alerts"]

```

---

### File: `new_pipeline/monitoring/dashboard/views.py`

```py
"""Dashboard data views for the model-registry and risk pages (Phase 6).

Pure data over the promotion registry (JSON) and the trade log (Parquet), so the
pages stay thin and the logic is unit-testable offline.
"""

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq


def model_registry_view(registry_path) -> dict:
    """Active champions + promotion history from the immutable registry JSON."""
    path = Path(registry_path)
    if not path.exists():
        return {"active_champions": {}, "promotions": []}
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass
class RiskView:
    gross_exposure: float
    position_count: int
    largest_position: float
    concentration: float  # largest position notional / gross exposure


def risk_view(trade_log_path) -> RiskView:
    """Net per-symbol notional exposure and concentration from the trade log."""
    path = Path(trade_log_path)
    if not path.exists():
        return RiskView(0.0, 0, 0.0, 0.0)
    table = pq.read_table(path)
    if table.num_rows == 0:
        return RiskView(0.0, 0, 0.0, 0.0)

    symbols = table.column("symbol").to_pylist()
    qty = np.asarray(table.column("qty").to_pylist(), dtype=np.float64)
    price = np.asarray(table.column("limit_price").to_pylist(), dtype=np.float64)
    sign = np.where(np.array(table.column("side").to_pylist()) == "buy", 1.0, -1.0)
    signed_notional = sign * qty * price

    exposure: dict[str, float] = {}
    for symbol, value in zip(symbols, signed_notional, strict=True):
        exposure[symbol] = exposure.get(symbol, 0.0) + float(value)

    notionals = np.array([abs(v) for v in exposure.values()])
    gross = float(notionals.sum())
    largest = float(notionals.max()) if notionals.size else 0.0
    open_positions = int((notionals > 0.0).sum())
    return RiskView(gross, open_positions, largest, largest / gross if gross > 0.0 else 0.0)

```

---

### File: `new_pipeline/monitoring/dashboard/app.py`

```py
"""Quantum Avenger — Streamlit monitoring dashboard (Phase 6).

Run: ``streamlit run new_pipeline/monitoring/dashboard/app.py``
Reads the veto ledger + trade log via RealtimeDataManager (offline, no network).
When ``dashboard.auth_enabled`` is set, a login gate guards the app
(credentials from DASHBOARD_USER / DASHBOARD_PASS).
"""

import streamlit as st

from new_pipeline.config import get_config
from new_pipeline.monitoring.dashboard.alerts import check_alerts
from new_pipeline.monitoring.dashboard.auth import require_login
from new_pipeline.monitoring.dashboard.realtime import RealtimeDataManager


def build_manager() -> RealtimeDataManager:
    cfg = get_config().dashboard
    return RealtimeDataManager(cfg.veto_ledger_path, cfg.trade_log_path)


def main() -> None:
    cfg = get_config().dashboard
    st.set_page_config(page_title="Quantum Avenger", layout="wide", page_icon="🛡️")
    if cfg.auth_enabled and not require_login(st):
        return
    st.title("🛡️ Quantum Avenger — Monitoring")

    manager = build_manager()
    kpis = manager.kpis()
    performance = manager.performance()
    veto = manager.veto_summary()

    columns = st.columns(4)
    columns[0].metric("Total P&L", f"{kpis['total_pnl']:.2%}")
    columns[1].metric("Sharpe", f"{kpis['sharpe']:.2f}")
    columns[2].metric("Max Drawdown", f"{kpis['max_drawdown']:.1%}")
    columns[3].metric("Veto Rate", f"{kpis['veto_rate']:.0%}")

    for alert in check_alerts(
        performance,
        veto,
        max_drawdown=cfg.max_drawdown_alert,
        min_sharpe=cfg.min_sharpe_alert,
        max_veto_rate=cfg.max_veto_rate_alert,
    ):
        (st.error if alert.severity == "critical" else st.warning)(alert.message)

    if performance.equity_curve:
        st.subheader("Equity curve")
        st.line_chart(performance.equity_curve)

    if veto.by_gate:
        st.subheader("Vetoes by gate")
        st.bar_chart(veto.by_gate)


if __name__ == "__main__":
    main()

```

---

### File: `new_pipeline/monitoring/dashboard/notifications.py`

```py
"""Alert delivery channels for the dashboard alert engine (Phase 6/7).

Dispatch ``Alert``s to one or more channels. Offline-friendly: ``ConsoleChannel``
writes to an injectable sink, ``WebhookChannel`` posts JSON via an injectable
transport (a fake in tests; a real HTTP client when wired live). No network in
dev/tests.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from new_pipeline.monitoring.dashboard.alerts import Alert


class Channel(Protocol):
    def send(self, alert: Alert) -> None: ...


@dataclass
class ConsoleChannel:
    sink: Callable[[str], None] = print

    def send(self, alert: Alert) -> None:
        self.sink(f"[{alert.severity.upper()}] {alert.message}")


@dataclass
class WebhookChannel:
    url: str
    transport: Callable[[str, dict], None]

    def send(self, alert: Alert) -> None:
        self.transport(self.url, {"severity": alert.severity, "message": alert.message})


@dataclass
class RecordingChannel:
    """In-memory channel for tests."""

    sent: list = field(default_factory=list)

    def send(self, alert: Alert) -> None:
        self.sent.append(alert)


def dispatch(alerts, channels) -> int:
    """Send every alert to every channel; returns the number of deliveries."""
    deliveries = 0
    for alert in alerts:
        for channel in channels:
            channel.send(alert)
            deliveries += 1
    return deliveries

```

---

### File: `new_pipeline/monitoring/dashboard/realtime.py`

```py
"""Dashboard data layer: load the ledgers and compute KPIs (Phase 6).

Pure data + math (no Streamlit) so it is fully unit-testable offline. Reads the
append-only veto ledger (decision analytics) and trade log (performance), and
derives the KPI dict + equity curve the UI renders. ``pnl`` rows are treated as
per-trade fractional returns.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

from new_pipeline.evaluation.tearsheet import summary_metrics


@dataclass
class VetoSummary:
    total: int
    executed: int
    vetoed: int
    veto_rate: float
    by_gate: dict[str, int]


@dataclass
class Performance:
    total_pnl: float
    sharpe: float
    max_drawdown: float
    win_rate: float
    profit_factor: float
    equity_curve: list[float]


class RealtimeDataManager:
    def __init__(self, veto_ledger_path, trade_log_path):
        self._veto_path = Path(veto_ledger_path)
        self._trade_path = Path(trade_log_path)

    def veto_summary(self) -> VetoSummary:
        if not self._veto_path.exists():
            return VetoSummary(0, 0, 0, 0.0, {})
        gates = pq.read_table(self._veto_path).column("veto_gate").to_pylist()
        total = len(gates)
        executed = sum(1 for gate in gates if gate == "none")
        vetoed = total - executed
        by_gate: dict[str, int] = {}
        for gate in gates:
            if gate != "none":
                by_gate[gate] = by_gate.get(gate, 0) + 1
        return VetoSummary(total, executed, vetoed, vetoed / total if total else 0.0, by_gate)

    def performance(self) -> Performance:
        empty = Performance(0.0, 0.0, 0.0, 0.0, 0.0, [])
        if not self._trade_path.exists():
            return empty
        pnl = np.asarray(
            pq.read_table(self._trade_path).column("pnl").to_pylist(), dtype=np.float64
        )
        if pnl.size == 0:
            return empty
        metrics = summary_metrics(pnl)
        return Performance(
            total_pnl=float(pnl.sum()),
            sharpe=metrics["sharpe"],
            max_drawdown=metrics["max_drawdown"],
            win_rate=metrics["win_rate"],
            profit_factor=metrics["profit_factor"],
            equity_curve=np.cumprod(1.0 + pnl).tolist(),
        )

    def kpis(self) -> dict:
        veto = self.veto_summary()
        perf = self.performance()
        return {
            "total_decisions": veto.total,
            "executed": veto.executed,
            "vetoed": veto.vetoed,
            "veto_rate": veto.veto_rate,
            "total_pnl": perf.total_pnl,
            "sharpe": perf.sharpe,
            "max_drawdown": perf.max_drawdown,
            "win_rate": perf.win_rate,
            "profit_factor": perf.profit_factor,
        }

```

---

### File: `new_pipeline/monitoring/dashboard/pages/06_settings.py`

```py
"""Settings page — current configuration and alert thresholds (read-only)."""

import streamlit as st
from new_pipeline.config import get_config

st.title("Settings")

cfg = get_config()
st.subheader("Risk & execution")
st.json(cfg.execution.model_dump())
st.subheader("Alert thresholds")
st.json(cfg.dashboard.model_dump())
st.caption("Edit via config overlays / QA_ env vars. Auth: DASHBOARD_USER / DASHBOARD_PASS.")

```

---

### File: `new_pipeline/monitoring/dashboard/pages/03_trade_log.py`

```py
"""Trade log page — recent fills and realized P&L."""

import streamlit as st
from new_pipeline.config import get_config
from new_pipeline.execution.trade_log import TradeLog

st.title("Trade Log")

table = TradeLog(get_config().dashboard.trade_log_path).read()
if table.num_rows:
    st.dataframe(table.to_pandas())
else:
    st.info("No trades logged yet.")

```

---

### File: `new_pipeline/monitoring/dashboard/pages/02_veto_analysis.py`

```py
"""Veto analysis page — rejection breakdown by gate."""

import streamlit as st
from new_pipeline.monitoring.dashboard.app import build_manager

st.title("Veto Analysis")

veto = build_manager().veto_summary()
st.metric("Veto rate", f"{veto.veto_rate:.0%}")
if veto.by_gate:
    st.bar_chart(veto.by_gate)
else:
    st.info("No vetoes recorded yet.")

```

---

### File: `new_pipeline/monitoring/dashboard/pages/05_risk_dashboard.py`

```py
"""Risk dashboard page — exposure and concentration."""

import streamlit as st
from new_pipeline.config import get_config
from new_pipeline.monitoring.dashboard.views import risk_view

st.title("Risk Dashboard")

view = risk_view(get_config().dashboard.trade_log_path)
columns = st.columns(4)
columns[0].metric("Gross exposure", f"${view.gross_exposure:,.0f}")
columns[1].metric("Open positions", view.position_count)
columns[2].metric("Largest position", f"${view.largest_position:,.0f}")
columns[3].metric("Concentration", f"{view.concentration:.0%}")

```

---

### File: `new_pipeline/monitoring/dashboard/pages/01_live_monitor.py`

```py
"""Live monitor page — execution counts, win rate, and the equity curve."""

import streamlit as st
from new_pipeline.monitoring.dashboard.app import build_manager

st.title("Live Monitor")

manager = build_manager()
kpis = manager.kpis()
columns = st.columns(3)
columns[0].metric("Executed", kpis["executed"])
columns[1].metric("Vetoed", kpis["vetoed"])
columns[2].metric("Win Rate", f"{kpis['win_rate']:.0%}")

performance = manager.performance()
if performance.equity_curve:
    st.line_chart(performance.equity_curve)
else:
    st.info("No trades logged yet.")

```

---

### File: `new_pipeline/monitoring/dashboard/pages/04_model_registry.py`

```py
"""Model registry page — active champions and promotion history."""

import streamlit as st
from new_pipeline.config import get_config
from new_pipeline.monitoring.dashboard.views import model_registry_view

st.title("Model Registry")

view = model_registry_view(get_config().evaluation.registry_path)
st.subheader("Active champions")
st.json(view["active_champions"])
st.subheader("Promotion history")
if view["promotions"]:
    st.dataframe(view["promotions"])
else:
    st.info("No promotions recorded yet.")

```

---

### File: `new_pipeline/utils/time.py`

```py
from datetime import datetime


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"

```

---

### File: `new_pipeline/utils/retry.py`

```py
from dataclasses import dataclass


@dataclass
class RetryPolicy:
    max_retries: int = 3
    backoff_seconds: float = 0.5

```

---

### File: `new_pipeline/utils/decorators.py`

```py
import time
from functools import wraps

from .retry import RetryPolicy


def retry(policy: RetryPolicy):
    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            attempt = 0
            while attempt <= policy.max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception:
                    attempt += 1
                    if attempt > policy.max_retries:
                        raise
                    time.sleep(policy.backoff_seconds)
        return inner
    return wrapper

```

---

### File: `new_pipeline/utils/serialization.py`

```py
import json
from pathlib import Path
from typing import Any


def to_json(obj: Any, path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2)


def from_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)

```

---

### File: `new_pipeline/utils/__init__.py`

```py
from .decorators import retry
from .retry import RetryPolicy
from .serialization import from_json, to_json
from .time import now_iso

__all__ = ["retry", "RetryPolicy", "to_json", "from_json", "now_iso"]

```

---

### File: `new_pipeline/tests/conftest.py`

```py
from pathlib import Path

import pytest

from new_pipeline.config import base


@pytest.fixture(scope="session")
def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _reset_config_singleton():
    """Keep the cached config from leaking between tests (env overlays / QA_ vars)."""
    base._CONFIG_INSTANCE = None
    yield
    base._CONFIG_INSTANCE = None


@pytest.fixture(autouse=True)
def _isolate_feature_registry(tmp_path):
    """Redirect the feature-registry singleton to a throwaway path so no test
    mutates the tracked data/metadata/feature_registry.yaml artifact."""
    from new_pipeline.features.registry import feature_registry

    original_path = feature_registry._metadata_path
    feature_registry._metadata_path = tmp_path / "feature_registry.yaml"
    feature_registry.clear()
    yield
    feature_registry._metadata_path = original_path

```

---

### File: `new_pipeline/tests/__init__.py`

```py

```

---

### File: `new_pipeline/tests/unit/test_tournament_core.py`

```py
import numpy as np
from new_pipeline.tournament.objectives import (
    asymmetric_financial_loss,
    asymmetric_loss_factory,
)
from new_pipeline.tournament.simulator import sharpe_ratio, simulate_t1_returns


class _DMatrix:
    def __init__(self, labels):
        self._labels = np.asarray(labels, dtype=np.float64)

    def get_label(self):
        return self._labels


def test_asymmetric_loss_penalizes_false_positives_5x():
    grad, hess = asymmetric_financial_loss(np.array([0.0, 0.0]), _DMatrix([0.0, 1.0]))
    np.testing.assert_allclose(grad, [2.5, -0.5])  # p=0.5: (0.5-0)*5, (0.5-1)*1
    np.testing.assert_allclose(hess, [1.25, 0.25])  # 0.25*5, 0.25*1


def test_loss_factory_binds_penalties():
    objective = asymmetric_loss_factory(penalty_fp=3.0, penalty_fn=1.0)
    grad, _ = objective(np.array([0.0]), _DMatrix([0.0]))
    np.testing.assert_allclose(grad, [1.5])  # (0.5-0)*3


def test_simulator_stop_out_returns_negative():
    close = np.array([100.0, 100.0])
    low = np.array([100.0, 90.0])  # next-bar low pierces the stop at 98
    atr = np.array([1.0, 1.0])
    out = simulate_t1_returns(np.array([1, 0]), close, low, atr, 2.0, 0.02)
    assert out[0] < 0.0


def test_simulator_winning_trade_positive():
    close = np.array([100.0, 103.0])
    low = np.array([100.0, 102.0])
    atr = np.array([1.0, 1.0])
    out = simulate_t1_returns(np.array([1, 0]), close, low, atr, 2.0, 0.02)
    assert out[0] > 0.0


def test_simulator_no_lookahead_on_last_bar():
    close = np.array([100.0, 101.0])
    low = close - 1.0
    atr = np.full(2, 1.0)
    out = simulate_t1_returns(np.array([0, 1]), close, low, atr, 2.0, 0.02)
    assert out[-1] == 0.0  # a signal on the final bar has no t+1 -> no trade


def test_sharpe_zero_for_flat_series():
    assert sharpe_ratio(np.zeros(10)) == 0.0

```

---

### File: `new_pipeline/tests/unit/test_psr_mintrl.py`

```py
import numpy as np
from new_pipeline.evaluation.dsr import (
    compute_deflated_sharpe_ratio,
    expected_max_sharpe,
    min_track_record_length,
    probabilistic_sharpe_ratio,
)


def _series(mean: float, n: int = 1000, seed: int = 0):
    return np.random.default_rng(seed).normal(mean, 0.01, n)


def test_psr_is_a_probability():
    assert 0.0 <= probabilistic_sharpe_ratio(_series(0.002)) <= 1.0


def test_psr_rises_with_sample_length():
    short = probabilistic_sharpe_ratio(_series(0.0015, n=120))
    long = probabilistic_sharpe_ratio(_series(0.0015, n=1500))
    assert long > short


def test_psr_drops_as_benchmark_rises():
    returns = _series(0.003)
    assert probabilistic_sharpe_ratio(returns, 0.0) > probabilistic_sharpe_ratio(returns, 0.2)


def test_dsr_equals_psr_at_expected_max_benchmark():
    # The plan's golden identity: DSR is PSR with the benchmark set to E[max SR].
    returns = _series(0.002)
    trials = list(np.linspace(0.0, 0.1, 9))
    sr0 = expected_max_sharpe(float(np.var(trials, ddof=1)), len(trials))
    psr_at_max = probabilistic_sharpe_ratio(returns, sr0)
    assert psr_at_max == compute_deflated_sharpe_ratio(returns, trials)


def test_mintrl_infinite_when_sharpe_below_benchmark():
    returns = _series(0.001)
    sharpe = returns.mean() / returns.std(ddof=1)
    assert min_track_record_length(returns, benchmark_sr=sharpe + 0.5) == float("inf")


def test_mintrl_finite_and_grows_with_confidence():
    returns = _series(0.003)
    lo = min_track_record_length(returns, 0.0, prob=0.90)
    hi = min_track_record_length(returns, 0.0, prob=0.99)
    assert 0.0 < lo < hi < float("inf")


def test_degenerate_inputs_are_safe():
    assert probabilistic_sharpe_ratio([0.01, 0.01]) == 0.0  # < 3 observations
    assert min_track_record_length([0.01, 0.01]) == float("inf")

```

---

### File: `new_pipeline/tests/unit/test_telemetry.py`

```py
from new_pipeline.monitoring.metrics import MetricsCollector
from new_pipeline.monitoring.telemetry import TelemetryExporter, render_prometheus


def test_render_prometheus_format():
    text = render_prometheus({"veto_rate": 0.25, "dsr_value": 0.96})
    assert "# TYPE quantum_avenger_veto_rate gauge" in text
    assert "quantum_avenger_veto_rate 0.25" in text
    assert "quantum_avenger_dsr_value 0.96" in text


def test_render_empty():
    assert render_prometheus({}) == ""


def test_exporter_filters_non_numeric_and_bool():
    text = TelemetryExporter().export(
        {"trades": 3, "ok": True, "label": "x", "latency_ms": 12.5}
    )
    assert "quantum_avenger_trades 3.0" in text
    assert "quantum_avenger_latency_ms 12.5" in text
    assert "ok" not in text
    assert "label" not in text


def test_from_collector():
    collector = MetricsCollector()
    collector.increment("orders", 2)
    collector.increment("vetoes")
    text = TelemetryExporter().from_collector(collector)
    assert "quantum_avenger_orders 2.0" in text
    assert "quantum_avenger_vetoes 1.0" in text

```

---

### File: `new_pipeline/tests/unit/test_adapters_fakes.py`

```py
from datetime import date

from new_pipeline.adapters import (
    FakeBroker,
    FakeLLMClient,
    FakeMarketDataSource,
    FakeNewsSource,
)


def test_fake_llm_is_deterministic():
    llm = FakeLLMClient()
    first = llm.sentiment("Apple beats earnings")
    second = llm.sentiment("Apple beats earnings")
    assert first == second
    assert -1.0 <= first.score <= 1.0
    assert first.label in {"bullish", "bearish", "neutral"}


def test_fake_llm_verdict_stance():
    verdict = FakeLLMClient().verdict("some prompt")
    assert verdict.stance in {"BULLISH", "BEARISH", "NEUTRAL"}


def test_fake_market_data_well_formed_ohlc():
    bars = FakeMarketDataSource().history("AAPL", date(2024, 1, 1), date(2024, 1, 10))
    assert len(bars) == 10
    for bar in bars:
        assert bar.high >= max(bar.open, bar.close)
        assert bar.low <= min(bar.open, bar.close)
        assert bar.volume > 0


def test_fake_market_data_empty_for_reversed_range():
    bars = FakeMarketDataSource().history("AAPL", date(2024, 1, 10), date(2024, 1, 1))
    assert bars == []


def test_fake_news_returns_headline():
    items = FakeNewsSource().headlines("MSFT", date(2024, 6, 1))
    assert len(items) == 1
    assert "MSFT" in items[0].headline


def test_fake_broker_tracks_positions():
    broker = FakeBroker()
    receipt = broker.submit_order({"symbol": "AAPL", "qty": 10, "side": "buy"})
    assert receipt["status"] == "filled"
    broker.submit_order({"symbol": "AAPL", "qty": 4, "side": "sell"})
    assert broker.get_positions()["AAPL"] == 6.0
    assert len(broker.orders) == 2

```

---

### File: `new_pipeline/tests/unit/test_dsr.py`

```py
import numpy as np
from new_pipeline.evaluation.dsr import (
    compute_deflated_sharpe_ratio,
    expected_max_sharpe,
    interpret_dsr,
)


def _series(mean: float, n: int = 1000, seed: int = 0):
    return np.random.default_rng(seed).normal(mean, 0.01, n)


def test_dsr_is_a_probability():
    dsr = compute_deflated_sharpe_ratio(_series(0.002), [0.1, 0.12, 0.09, 0.11])
    assert 0.0 <= dsr <= 1.0


def test_strong_alpha_promotes():
    # champion Sharpe well above a low-variance trial cluster -> DSR ~ 1
    dsr = compute_deflated_sharpe_ratio(_series(0.005), list(np.linspace(0.0, 0.1, 9)))
    assert dsr > 0.95
    assert interpret_dsr(dsr) == "promote"


def test_flat_returns_not_significant():
    dsr = compute_deflated_sharpe_ratio(_series(0.0), list(np.linspace(0.0, 0.1, 9)))
    assert dsr < 0.5


def test_dsr_monotonic_in_sharpe():
    trials = list(np.linspace(0.0, 0.1, 9))
    low = compute_deflated_sharpe_ratio(_series(0.001, seed=1), trials)
    high = compute_deflated_sharpe_ratio(_series(0.004, seed=1), trials)
    assert high >= low


def test_expected_max_sharpe_increases_with_trials():
    assert expected_max_sharpe(0.01, 50) > expected_max_sharpe(0.01, 5)


def test_interpret_thresholds():
    assert interpret_dsr(0.3) == "overfit"
    assert interpret_dsr(0.8) == "insignificant"
    assert interpret_dsr(0.96) == "promote"

```

---

### File: `new_pipeline/tests/unit/test_feature_selection.py`

```py
import numpy as np
from new_pipeline.tournament.feature_selection import (
    cluster_features,
    select_orthogonal_features,
)


def test_cluster_groups_collinear_features():
    rng = np.random.default_rng(0)
    base = rng.normal(size=200)
    matrix = np.column_stack([base, base + rng.normal(0, 0.01, 200), rng.normal(size=200)])
    clusters = cluster_features(matrix, ["f0", "f1", "f2"], distance_threshold=0.5)
    assert sorted(len(c) for c in clusters) == [1, 2]  # f0+f1 together, f2 alone


def test_select_prunes_unimportant_features():
    rng = np.random.default_rng(1)
    target = rng.normal(size=150)
    informative = target + rng.normal(0, 0.1, 150)
    matrix = np.column_stack([informative, rng.normal(size=150), rng.normal(size=150)])

    def score(candidate):
        return abs(float(np.corrcoef(candidate[:, 0], target)[0, 1]))

    kept = select_orthogonal_features(
        matrix, ["f0", "f1", "f2"], score, distance_threshold=0.5, min_importance=0.1, seed=0
    )
    assert kept == ["f0"]


def test_select_falls_back_to_all_when_nothing_clears_threshold():
    rng = np.random.default_rng(2)
    matrix = rng.normal(size=(80, 3))
    kept = select_orthogonal_features(
        matrix, ["a", "b", "c"], lambda _m: 1.0, min_importance=0.5, seed=0
    )
    assert kept == ["a", "b", "c"]  # constant score -> zero importance -> fallback

```

---

### File: `new_pipeline/tests/unit/test_trade_log.py`

```py
from new_pipeline.execution.trade_log import TRADE_LOG_SCHEMA, TradeLog, TradeRecord


def _record(pnl=0.05, exec_id="o1"):
    return TradeRecord("AAPL", "buy", 10, 100.0, "filled", exec_id, fill_price=100.1, pnl=pnl)


def test_append_and_read(tmp_path):
    log = TradeLog(tmp_path / "trades.parquet")
    log.append(_record())
    table = log.read()
    assert table.num_rows == 1
    assert table.schema.names == TRADE_LOG_SCHEMA.names
    assert table.column("pnl").to_pylist() == [0.05]


def test_append_only_accumulates(tmp_path):
    log = TradeLog(tmp_path / "trades.parquet")
    log.append(_record(exec_id="a"))
    log.append(_record(pnl=-0.02, exec_id="b"))
    assert len(log) == 2


def test_read_empty(tmp_path):
    assert TradeLog(tmp_path / "missing.parquet").read().num_rows == 0

```

---

### File: `new_pipeline/tests/unit/test_feature_registry.py`

```py
from new_pipeline.features.compiler import PandasFeatureCompiler
from new_pipeline.features.registry import FeatureMetadata, feature_registry


def test_feature_registry_can_register_and_query():
    feature_registry.clear()

    metadata = FeatureMetadata(
        name="test_feature",
        description="A synthetic test feature.",
        source="test",
        window="1d",
        dtype="float",
    )
    feature_registry.register("test_feature", metadata)

    assert "test_feature" in feature_registry.list_features()
    assert feature_registry.get("test_feature")["name"] == "test_feature"
    assert feature_registry.get("test_feature")["description"] == "A synthetic test feature."


def test_feature_compiler_registers_feature_metadata():
    feature_registry.clear()
    PandasFeatureCompiler()

    assert "returns" in feature_registry.list_features()
    assert feature_registry.get("atr_14")["window"] == "14d"
    assert feature_registry.get("average_volume_20")["dtype"] == "float"


def test_feature_registry_persists_and_loads(tmp_path):
    feature_registry.clear()

    metadata = FeatureMetadata(
        name="persist_feature",
        description="Persisted test feature.",
        source="test",
        window="1d",
        dtype="float",
    )
    feature_registry.register("persist_feature", metadata)

    path = tmp_path / "feature_registry_test.yaml"
    feature_registry.save(path)

    feature_registry.clear()
    assert feature_registry.list_features() == []

    feature_registry.load(path)
    assert "persist_feature" in feature_registry.list_features()
    assert feature_registry.get("persist_feature")["description"] == "Persisted test feature."

```

---

### File: `new_pipeline/tests/unit/test_serve_mcp.py`

```py
import json

from new_pipeline.scripts import serve_mcp


def test_serve_mcp_prints_tool_schemas(capsys):
    serve_mcp.main()
    payload = json.loads(capsys.readouterr().out)
    assert "tools" in payload
    assert len(payload["tools"]) >= 8
    assert all("inputSchema" in tool for tool in payload["tools"])

```

---

### File: `new_pipeline/tests/unit/test_evaluation.py`

```py
import numpy as np
from new_pipeline.core.seeding import seed_everything
from new_pipeline.evaluation.hmm_gauntlet import run_hmm_synthetic_gauntlet
from new_pipeline.evaluation.tearsheet import summary_metrics, write_html_tearsheet


def _predict(features):
    return 1.0 / (1.0 + np.exp(-features[:, 0]))


def test_hmm_gauntlet_returns_float_and_is_reproducible():
    seed_everything(7)
    rng = np.random.default_rng(0)
    benchmark = rng.normal(0.0, 0.01, 200)
    features = rng.normal(size=(200, 3))
    first = run_hmm_synthetic_gauntlet(benchmark, features, _predict, n_iter=20, seed=7)
    second = run_hmm_synthetic_gauntlet(benchmark, features, _predict, n_iter=20, seed=7)
    assert isinstance(first, float)
    assert first == second  # deterministic under a fixed seed


def test_summary_metrics_on_known_series():
    metrics = summary_metrics(np.array([0.1, -0.05, 0.2, 0.0, -0.1]))
    assert set(metrics) == {"sharpe", "max_drawdown", "win_rate", "profit_factor"}
    assert metrics["win_rate"] == 0.5  # 2 wins out of 4 traded bars
    assert metrics["max_drawdown"] <= 0.0


def test_write_html_tearsheet_degrades_without_quantstats():
    result = write_html_tearsheet(np.array([0.01, -0.02]), "/tmp/qa_tearsheet.html")
    assert isinstance(result, bool)

```

---

### File: `new_pipeline/tests/unit/test_polars_engine.py`

```py
from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest
from new_pipeline.core.exceptions import SchemaValidationError
from new_pipeline.features.polars_engine import (
    ATR_PERIOD,
    FEATURE_NAMES,
    PolarsFeatureEngine,
    add_features,
    compile_features,
)


def _frame(ticker: str = "AAPL", n: int = 30, seed: int = 0):
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0.0, 1.0, n))
    high = close + rng.uniform(0.5, 1.5, n)
    low = close - rng.uniform(0.5, 1.5, n)
    volume = rng.integers(1_000_000, 2_000_000, n).astype(float)
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(n)]
    frame = pl.DataFrame(
        {
            "date": dates,
            "ticker": [ticker] * n,
            "open": close,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )
    return frame, close, high, low


def _expected_atr_last(close, high, low) -> float:
    n = len(close)
    tr = np.empty(n)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        tr[i] = max(
            high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])
        )
    alpha = 1.0 / ATR_PERIOD
    atr = tr[0]
    for i in range(1, n):
        atr = atr * (1.0 - alpha) + tr[i] * alpha
    return atr


def test_returns_and_spread_match_numpy():
    frame, close, high, low = _frame()
    out = add_features(frame).sort("date")
    assert out["returns"].to_list()[-1] == pytest.approx(close[-1] / close[-2] - 1.0, rel=1e-9)
    mid = (high[-1] + low[-1]) / 2.0
    assert out["spread_pct"].to_list()[-1] == pytest.approx((high[-1] - low[-1]) / mid, rel=1e-9)


def test_atr_matches_wilder_rma():
    frame, close, high, low = _frame()
    out = add_features(frame).sort("date")
    assert out["atr"].to_list()[-1] == pytest.approx(_expected_atr_last(close, high, low), rel=1e-9)


def test_volatility_matches_rolling_std():
    frame, close, _, _ = _frame()
    out = add_features(frame).sort("date")
    ret = close[1:] / close[:-1] - 1.0
    expected = ret[-20:].std(ddof=1) * np.sqrt(252)
    assert out["volatility"].to_list()[-1] == pytest.approx(expected, rel=1e-9)


def test_multi_ticker_isolation():
    a, *_ = _frame("AAPL", seed=1)
    b, *_ = _frame("MSFT", seed=2)
    out = compile_features(pl.concat([a, b]))
    for ticker in ("AAPL", "MSFT"):
        first_return = out.filter(pl.col("ticker") == ticker).sort("date")["returns"].to_list()[0]
        assert first_return is None  # no bleed across tickers
    assert set(out["ticker"].unique().to_list()) == {"AAPL", "MSFT"}


def test_missing_columns_raise():
    bad = pl.DataFrame({"date": [date(2024, 1, 1)], "ticker": ["AAPL"], "close": [100.0]})
    with pytest.raises(SchemaValidationError):
        compile_features(bad)


def test_engine_registers_features():
    engine = PolarsFeatureEngine()
    assert set(FEATURE_NAMES).issubset(set(engine.list_available_features()))

```

---

### File: `new_pipeline/tests/unit/test_logging.py`

```py
import logging

from new_pipeline.core.logging import configure_logging


def test_logging_configures_logger(tmp_path):
    logger = configure_logging()
    assert isinstance(logger, logging.Logger)

```

---

### File: `new_pipeline/tests/unit/test_dashboard_auth.py`

```py
from new_pipeline.monitoring.dashboard.auth import verify_credentials


def test_valid_credentials():
    assert verify_credentials("admin", "secret", expected_user="admin", expected_password="secret")


def test_invalid_password():
    assert not verify_credentials(
        "admin", "wrong", expected_user="admin", expected_password="secret"
    )


def test_fail_closed_when_unconfigured():
    assert not verify_credentials("admin", "secret", expected_user="", expected_password="")


def test_reads_from_env(monkeypatch):
    monkeypatch.setenv("DASHBOARD_USER", "quant")
    monkeypatch.setenv("DASHBOARD_PASS", "shield")
    assert verify_credentials("quant", "shield")
    assert not verify_credentials("quant", "nope")

```

---

### File: `new_pipeline/tests/unit/test_haircut.py`

```py
import numpy as np
import pytest
from new_pipeline.evaluation.haircut import (
    haircut_sharpe_ratio,
    minimum_profit_hurdle,
    multiple_testing_adjust,
)


def test_bonferroni_scales_by_count():
    assert np.allclose(multiple_testing_adjust([0.01, 0.02], "bonferroni"), [0.02, 0.04])


def test_adjusted_pvalues_stay_in_range_and_never_shrink():
    p = np.array([0.001, 0.02, 0.03, 0.04])
    for method in ("holm", "bhy"):
        adj = multiple_testing_adjust(p, method)
        assert np.all(adj >= p - 1e-12)  # adjustment only inflates p-values
        assert np.all((adj >= 0.0) & (adj <= 1.0))


def test_haircut_never_exceeds_observed_and_decays_with_trials():
    base = haircut_sharpe_ratio(1.5, n_obs=2520, n_trials=1)
    few = haircut_sharpe_ratio(1.5, n_obs=2520, n_trials=10)
    many = haircut_sharpe_ratio(1.5, n_obs=2520, n_trials=200)
    assert base.adjusted_sharpe <= 1.5 + 1e-9
    assert many.adjusted_sharpe < few.adjusted_sharpe < base.adjusted_sharpe
    assert 0.0 <= many.haircut_fraction <= 1.0


def test_haircut_handles_nonpositive_sharpe():
    res = haircut_sharpe_ratio(-0.5, n_obs=2520, n_trials=10)
    assert res.adjusted_sharpe == 0.0
    assert res.haircut_fraction == 0.0


def test_minimum_hurdle_rises_with_trials():
    one = minimum_profit_hurdle(2520, n_trials=1)
    many = minimum_profit_hurdle(2520, n_trials=100)
    assert many > one > 0.0


def test_unknown_method_raises():
    with pytest.raises(ValueError):
        multiple_testing_adjust([0.1], "bogus")

```

---

### File: `new_pipeline/tests/unit/test_verdict_grader.py`

```py
from new_pipeline.adapters.base import LLMClient, SentimentResult, Verdict
from new_pipeline.execution.grader import Grader
from new_pipeline.execution.verdict_engine import VerdictEngine


class _StubLLM(LLMClient):
    def __init__(self, stance: str):
        self._stance = stance

    def sentiment(self, text):
        return SentimentResult(0.0, "neutral")

    def verdict(self, prompt):
        return Verdict(self._stance, "because")


def test_verdict_engine_returns_stance():
    verdict = VerdictEngine(_StubLLM("BULLISH")).generate("BUY", "AAPL", ["ctx"])
    assert verdict.stance == "BULLISH"


def test_grader_approves_decisive_stance():
    result = Grader(_StubLLM("BULLISH")).grade(Verdict("BULLISH", ""), ["ctx"])
    assert result.approved is True


def test_grader_rejects_neutral():
    result = Grader(_StubLLM("NEUTRAL")).grade(Verdict("BULLISH", ""), ["ctx"])
    assert result.approved is False

```

---

### File: `new_pipeline/tests/unit/test_alerts.py`

```py
from new_pipeline.monitoring.dashboard.alerts import check_alerts
from new_pipeline.monitoring.dashboard.realtime import Performance, VetoSummary


def _perf(sharpe=1.0, drawdown=-0.05):
    return Performance(
        total_pnl=0.1,
        sharpe=sharpe,
        max_drawdown=drawdown,
        win_rate=0.6,
        profit_factor=2.0,
        equity_curve=[1.0],
    )


def _veto(rate=0.1):
    return VetoSummary(total=10, executed=9, vetoed=1, veto_rate=rate, by_gate={"shield": 1})


def test_no_alerts_when_healthy():
    assert check_alerts(_perf(), _veto()) == []


def test_drawdown_breach_is_critical():
    alerts = check_alerts(_perf(drawdown=-0.25), _veto(), max_drawdown=0.15)
    assert any(alert.severity == "critical" for alert in alerts)


def test_low_sharpe_warns():
    alerts = check_alerts(_perf(sharpe=-0.5), _veto(), min_sharpe=0.0)
    assert any("Sharpe" in alert.message for alert in alerts)


def test_high_veto_rate_warns():
    alerts = check_alerts(_perf(), _veto(rate=0.8), max_veto_rate=0.5)
    assert any("Veto rate" in alert.message for alert in alerts)

```

---

### File: `new_pipeline/tests/unit/test_exceptions_hierarchy.py`

```py
from new_pipeline.core.exceptions import (
    BrokerError,
    CircuitBreakerError,
    ExecutionError,
    IngestionError,
    QuantumAvengerError,
    ShieldVetoError,
    UniverseError,
)


def test_execution_leaves_share_execution_base():
    for exc in (ShieldVetoError, BrokerError):
        assert issubclass(exc, ExecutionError)
        assert issubclass(exc, QuantumAvengerError)


def test_all_errors_share_root():
    for exc in (IngestionError, UniverseError, CircuitBreakerError):
        assert issubclass(exc, QuantumAvengerError)

```

---

### File: `new_pipeline/tests/unit/test_veto_ledger.py`

```py
from new_pipeline.execution.veto_ledger import LEDGER_SCHEMA, VetoLedger, VetoRecord


def _record(reason="executed", gate="none", size=10, exec_id="x1"):
    return VetoRecord("AAPL", "BUY", 100.0, reason, gate, 0.96, size, exec_id)


def test_append_and_read(tmp_path):
    ledger = VetoLedger(tmp_path / "veto.parquet")
    ledger.append(_record())
    table = ledger.read()
    assert table.num_rows == 1
    assert table.schema.names == LEDGER_SCHEMA.names
    assert table.column("symbol").to_pylist() == ["AAPL"]


def test_append_only_accumulates(tmp_path):
    ledger = VetoLedger(tmp_path / "veto.parquet")
    ledger.append(_record(exec_id="a"))
    ledger.append(_record(reason="risk veto", gate="shield", size=0, exec_id=""))
    assert len(ledger) == 2
    assert ledger.read().column("veto_gate").to_pylist() == ["none", "shield"]


def test_read_empty_ledger(tmp_path):
    assert VetoLedger(tmp_path / "missing.parquet").read().num_rows == 0

```

---

### File: `new_pipeline/tests/unit/test_retry.py`

```py
from new_pipeline.utils.retry import RetryPolicy


def test_retry_policy_defaults():
    policy = RetryPolicy()
    assert policy.max_retries == 3
    assert policy.backoff_seconds == 0.5

```

---

### File: `new_pipeline/tests/unit/test_data_ingestion.py`

```py
import pandas as pd
from new_pipeline.config import reload_config
from new_pipeline.data.ingestion import DataIngestion


def test_stage_and_load_dataframe(monkeypatch, tmp_path):
    monkeypatch.setenv("QA_DATA__RAW_VAULT_DIR", str(tmp_path / "raw"))
    reload_config()

    ingestion = DataIngestion()
    df = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02"],
            "open": [100.0, 101.0],
            "high": [101.0, 102.0],
            "low": [99.0, 100.0],
            "close": [100.5, 101.5],
            "volume": [1000, 1100],
        }
    )

    target = ingestion.stage_dataframe(df, "sample.csv")
    loaded = ingestion.load_raw_dataframe("sample.csv")

    assert target.exists()
    assert list(loaded.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert len(loaded) == 2

```

---

### File: `new_pipeline/tests/unit/test_seeding.py`

```py
import numpy as np
from new_pipeline.core.seeding import DEFAULT_SEED, active_seed, seed_everything


def test_seed_everything_is_deterministic():
    seed_everything(123)
    first = np.random.rand(5).tolist()
    seed_everything(123)
    second = np.random.rand(5).tolist()
    assert first == second


def test_seed_everything_returns_and_records_seed():
    assert seed_everything(7) == 7
    assert active_seed() == 7


def test_default_seed_applied():
    assert seed_everything() == DEFAULT_SEED

```

---

### File: `new_pipeline/tests/unit/test_adapter_factory.py`

```py
import pytest
from new_pipeline.adapters.factory import AdapterBundle, build_adapters
from new_pipeline.adapters.fakes import FakeBroker, FakeLLMClient, FakeMarketDataSource
from new_pipeline.config import get_config


def _cfg_with_mode(mode):
    cfg = get_config().model_copy(deep=True)
    cfg.system.run_mode = mode
    return cfg


def test_offline_mode_returns_fakes():
    bundle = build_adapters(_cfg_with_mode("backtest"))
    assert isinstance(bundle, AdapterBundle)
    assert isinstance(bundle.market_data, FakeMarketDataSource)
    assert isinstance(bundle.llm, FakeLLMClient)
    assert isinstance(bundle.broker, FakeBroker)


def test_live_mode_requires_credentials():
    cfg = _cfg_with_mode("live")  # default config has empty Alpaca keys
    with pytest.raises(ValueError, match="QA_ALPACA"):
        build_adapters(cfg)


def test_live_mode_builds_alpaca_adapters():
    pytest.importorskip("alpaca")  # live SDK; skipped in the offline CI image
    from new_pipeline.adapters.broker_alpaca import AlpacaBroker
    from new_pipeline.adapters.market_alpaca import AlpacaMarketDataSource
    from new_pipeline.adapters.news_alpaca import AlpacaNewsSource

    cfg = _cfg_with_mode("paper")
    cfg.alpaca.api_key = "dummy_key"
    cfg.alpaca.secret_key = "dummy_secret"
    bundle = build_adapters(cfg)

    assert isinstance(bundle.market_data, AlpacaMarketDataSource)
    assert isinstance(bundle.news, AlpacaNewsSource)
    assert isinstance(bundle.broker, AlpacaBroker)
    assert isinstance(bundle.llm, FakeLLMClient)  # LLM stays fake until Ollama is configured


def test_unknown_mode_raises():
    with pytest.raises(ValueError, match="unknown run_mode"):
        build_adapters(_cfg_with_mode("banana"))

```

---

### File: `new_pipeline/tests/unit/test_gpu_rolling_dispatch.py`

```py
import numpy as np
from new_pipeline.features.gpu_kernels import (
    compute_rolling_duvol,
    compute_rolling_ncskew,
    rolling_duvol,
    rolling_ncskew,
)


def test_rolling_ncskew_cpu_dispatch_matches():
    returns = np.random.default_rng(0).normal(size=100)
    np.testing.assert_allclose(
        compute_rolling_ncskew(returns, 60, use_gpu=False),
        rolling_ncskew(returns, 60),
        equal_nan=True,
    )


def test_rolling_duvol_cpu_dispatch_matches():
    returns = np.random.default_rng(1).normal(size=100)
    np.testing.assert_allclose(
        compute_rolling_duvol(returns, 60, use_gpu=False),
        rolling_duvol(returns, 60),
        equal_nan=True,
    )

```

---

### File: `new_pipeline/tests/unit/test_config.py`

```py

from new_pipeline.config import reload_config


def test_config_loads_defaults():
    config = reload_config()
    assert config.data.raw_vault_dir == "./data/raw"
    assert config.execution.max_risk_per_trade == 0.02
    assert config.logging.level == "INFO"


def test_config_environment_override(monkeypatch):
    monkeypatch.setenv("QA_DATA__RAW_VAULT_DIR", "/tmp/test_raw")
    monkeypatch.setenv("QA_EXECUTION__MAX_RISK_PER_TRADE", "0.05")
    config = reload_config()

    assert config.data.raw_vault_dir == "/tmp/test_raw"
    assert config.execution.max_risk_per_trade == 0.05

```

---

### File: `new_pipeline/tests/unit/test_cscv_pbo.py`

```py
import numpy as np
import pytest
from new_pipeline.evaluation.cscv import cscv_partition_indices, cscv_splits, n_cscv_splits
from new_pipeline.evaluation.pbo import evaluate_cscv, probability_of_backtest_overfitting


def test_partition_count_and_coverage():
    assert n_cscv_splits(10) == 252  # C(10, 5)
    blocks = cscv_partition_indices(100, 10)
    assert len(blocks) == 10
    assert sum(b.size for b in blocks) == 100


def test_odd_partitions_rejected():
    with pytest.raises(ValueError):
        cscv_partition_indices(100, 5)


def test_splits_partition_the_axis():
    for is_idx, oos_idx in cscv_splits(60, 6):
        assert set(is_idx.tolist()).isdisjoint(oos_idx.tolist())
        assert np.array_equal(np.sort(np.concatenate([is_idx, oos_idx])), np.arange(60))


def test_pbo_low_for_genuine_skill():
    rng = np.random.default_rng(0)
    matrix = rng.normal(0.0, 0.01, size=(500, 12))
    matrix[:, 0] += 0.01  # one trial carries a persistent edge across every row
    assert probability_of_backtest_overfitting(matrix, n_partitions=10) < 0.2


def test_pbo_high_for_overfit_matrix():
    rng = np.random.default_rng(1)
    matrix = rng.normal(0.0, 0.01, size=(500, 40))
    matrix -= matrix.mean(axis=0, keepdims=True)  # zero true edge -> IS gains revert OOS
    result = evaluate_cscv(matrix, n_partitions=10)
    assert result.pbo > 0.8
    assert result.performance_degradation < 0.0
    assert result.n_splits == 252


def test_degenerate_matrices_are_safe():
    assert probability_of_backtest_overfitting(np.zeros((4, 1))) == 0.0  # single trial
    assert probability_of_backtest_overfitting(np.zeros((1, 5))) == 0.0  # too few observations

```

---

### File: `new_pipeline/tests/unit/test_realtime.py`

```py
from new_pipeline.execution.trade_log import TradeLog, TradeRecord
from new_pipeline.execution.veto_ledger import VetoLedger, VetoRecord
from new_pipeline.monitoring.dashboard.realtime import RealtimeDataManager


def _seed_veto(path):
    ledger = VetoLedger(path)
    ledger.append(VetoRecord("AAPL", "BUY", 100.0, "executed", "none", 0.96, 10, "o1"))
    ledger.append(VetoRecord("MSFT", "BUY", 100.0, "risk veto", "shield", 0.96, 0, ""))
    ledger.append(VetoRecord("NVDA", "BUY", 100.0, "grader rejected", "grader", 0.96, 0, ""))


def _seed_trades(path):
    log = TradeLog(path)
    for pnl, order_id in [(0.10, "a"), (-0.05, "b"), (0.08, "c")]:
        log.append(TradeRecord("AAPL", "buy", 10, 100.0, "filled", order_id, pnl=pnl))


def test_veto_summary(tmp_path):
    veto_path = tmp_path / "v.parquet"
    _seed_veto(veto_path)
    summary = RealtimeDataManager(veto_path, tmp_path / "t.parquet").veto_summary()
    assert summary.total == 3
    assert summary.executed == 1
    assert summary.vetoed == 2
    assert abs(summary.veto_rate - 2 / 3) < 1e-9
    assert summary.by_gate == {"shield": 1, "grader": 1}


def test_performance(tmp_path):
    trade_path = tmp_path / "t.parquet"
    _seed_trades(trade_path)
    perf = RealtimeDataManager(tmp_path / "v.parquet", trade_path).performance()
    assert abs(perf.total_pnl - 0.13) < 1e-9
    assert perf.win_rate == 2 / 3
    assert len(perf.equity_curve) == 3
    assert perf.max_drawdown <= 0.0


def test_kpis_combines_both(tmp_path):
    veto_path = tmp_path / "v.parquet"
    trade_path = tmp_path / "t.parquet"
    _seed_veto(veto_path)
    _seed_trades(trade_path)
    kpis = RealtimeDataManager(veto_path, trade_path).kpis()
    assert kpis["executed"] == 1
    assert kpis["vetoed"] == 2
    assert "sharpe" in kpis
    assert "total_pnl" in kpis


def test_missing_files_return_zeros(tmp_path):
    manager = RealtimeDataManager(tmp_path / "nope_v.parquet", tmp_path / "nope_t.parquet")
    assert manager.veto_summary().total == 0
    assert manager.performance().total_pnl == 0.0
    assert manager.kpis()["veto_rate"] == 0.0

```

---

### File: `new_pipeline/tests/unit/test_gpu_kernels.py`

```py
import numpy as np
import pytest
from new_pipeline.features.gpu_kernels import (
    compute_amihud,
    compute_spread_pct,
    cpu_amihud,
    cpu_spread_pct,
    duvol,
    gpu_available,
    ncskew,
)


def test_cpu_spread_pct_golden():
    high = np.array([2.0, 3.0])
    low = np.array([1.0, 1.0])
    np.testing.assert_allclose(cpu_spread_pct(high, low), [1.0 / 1.5, 2.0 / 2.0])


def test_cpu_amihud_golden():
    out = cpu_amihud(np.array([0.02]), np.array([100.0]), np.array([1000.0]))
    np.testing.assert_allclose(out, [0.02 / 100_000.0])


def test_amihud_zero_volume_is_zero():
    out = cpu_amihud(np.array([0.02]), np.array([100.0]), np.array([0.0]))
    assert out[0] == 0.0


def test_ncskew_symmetric_is_zero():
    assert abs(ncskew(np.array([1.0, -1.0, 2.0, -2.0, 3.0, -3.0]))) < 1e-9


def test_ncskew_positive_for_crashy_returns():
    crashy = np.array([0.01, 0.012, 0.009, 0.011, -0.10, 0.01, 0.008])
    assert ncskew(crashy) > 0.0  # left tail -> negative skew -> NCSKEW > 0


def test_duvol_positive_when_downside_more_volatile():
    returns = np.array([0.01, 0.01, 0.01, -0.05, -0.06, -0.04])
    assert duvol(returns) > 0.0


def test_dispatch_uses_cpu_when_gpu_not_requested():
    high = np.array([2.0, 3.0, 4.0])
    low = np.array([1.0, 1.5, 2.0])
    np.testing.assert_allclose(
        compute_spread_pct(high, low, use_gpu=False), cpu_spread_pct(high, low)
    )
    returns, close, volume = np.array([0.01]), np.array([100.0]), np.array([1e6])
    np.testing.assert_allclose(
        compute_amihud(returns, close, volume, use_gpu=False),
        cpu_amihud(returns, close, volume),
    )


def test_gpu_available_returns_bool():
    assert isinstance(gpu_available(), bool)


@pytest.mark.skipif(not gpu_available(), reason="no CUDA device")
def test_gpu_matches_cpu():  # pragma: no cover - runs only on a GPU box
    high, low = np.array([2.0, 3.0, 4.0]), np.array([1.0, 1.5, 2.0])
    np.testing.assert_allclose(
        compute_spread_pct(high, low, use_gpu=True), cpu_spread_pct(high, low)
    )

```

---

### File: `new_pipeline/tests/unit/test_notifications.py`

```py
from new_pipeline.monitoring.dashboard.alerts import Alert
from new_pipeline.monitoring.dashboard.notifications import (
    ConsoleChannel,
    RecordingChannel,
    WebhookChannel,
    dispatch,
)


def test_dispatch_to_multiple_channels():
    alerts = [Alert("critical", "drawdown"), Alert("warning", "veto rate")]
    recorder = RecordingChannel()
    posted = []
    webhook = WebhookChannel("http://hook", lambda url, payload: posted.append((url, payload)))

    deliveries = dispatch(alerts, [recorder, webhook])

    assert deliveries == 4  # 2 alerts x 2 channels
    assert len(recorder.sent) == 2
    assert posted[0] == ("http://hook", {"severity": "critical", "message": "drawdown"})


def test_console_channel_uses_sink():
    lines = []
    ConsoleChannel(sink=lines.append).send(Alert("warning", "hi"))
    assert lines == ["[WARNING] hi"]

```

---

### File: `new_pipeline/tests/unit/test_trainer.py`

```py
import numpy as np
import polars as pl
import xgboost as xgb
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.data_iterator import ParquetDataIter
from new_pipeline.tournament.trainer import (
    load_booster,
    predict_proba,
    save_candidate,
    train_booster,
)


def _xy(n: int = 120, seed: int = 0):
    rng = np.random.default_rng(seed)
    features = rng.normal(size=(n, 4))
    labels = (features[:, 0] > 0).astype(np.float64)
    return features, labels


def test_train_and_predict_proba_in_unit_interval():
    seed_everything(0)
    features, labels = _xy()
    booster = train_booster(features, labels, num_boost_round=20)
    proba = predict_proba(booster, features)
    assert proba.shape == (len(labels),)
    assert proba.min() >= 0.0
    assert proba.max() <= 1.0


def test_save_load_roundtrip(tmp_path):
    features, labels = _xy()
    booster = train_booster(features, labels, num_boost_round=10)
    path = tmp_path / "candidate.json"
    save_candidate(booster, path)
    reloaded = load_booster(path)
    np.testing.assert_allclose(predict_proba(booster, features), predict_proba(reloaded, features))


def test_parquet_data_iter_feeds_xgboost(tmp_path):
    features, labels = _xy(n=200)
    columns = {f"f{i}": features[:, i] for i in range(4)}
    frame = pl.DataFrame({**columns, "label": labels})
    path = tmp_path / "data.parquet"
    frame.write_parquet(path, row_group_size=50)  # -> 4 row-groups
    iterator = ParquetDataIter(path, [f"f{i}" for i in range(4)], "label")
    dmatrix = xgb.QuantileDMatrix(iterator)
    assert dmatrix.num_row() == 200
    assert dmatrix.num_col() == 4

```

---

### File: `new_pipeline/tests/unit/test_shields.py`

```py
import math

from new_pipeline.execution.risk import RiskManager
from new_pipeline.features.shields import (
    calculate_kelly_position_size,
    enforce_volatility_stop,
    evaluate_risk_veto_gates,
)

# A baseline trade that passes all five gates.
_APPROVE = {
    "entry_price": 100.0,
    "atr": 2.0,
    "atr_multiplier": 2.0,
    "account_capital": 100_000.0,
    "max_risk_pct": 0.02,
    "current_qty": 0.0,
    "adv_20": 10_000_000.0,
    "volume_today": 100_000_000.0,
    "volatility": 0.2,
}


def _call(**overrides):
    args = {**_APPROVE, **overrides}
    return evaluate_risk_veto_gates(
        args["entry_price"],
        args["atr"],
        args["atr_multiplier"],
        args["account_capital"],
        args["max_risk_pct"],
        args["current_qty"],
        args["adv_20"],
        args["volume_today"],
        args["volatility"],
    )


def test_baseline_trade_approved():
    approved, size = _call()
    assert approved is True
    assert size == 500.0


def test_gate1_invalid_atr_vetoes():
    assert _call(atr=0.0) == (False, 0.0)


def test_gate2_account_too_small_vetoes():
    assert _call(account_capital=10.0) == (False, 0.0)


def test_gate3_illiquid_vetoes():
    assert _call(adv_20=1_000.0) == (False, 0.0)


def test_gate4_high_slippage_vetoes():
    assert _call(volume_today=100_000.0, volatility=0.6) == (False, 0.0)


def test_gate5_already_at_target_vetoes():
    assert _call(current_qty=600.0) == (False, 0.0)


def test_invariant_veto_implies_zero_size():
    for override in ({"atr": 0.0}, {"adv_20": 1.0}, {"current_qty": 10_000.0}):
        approved, size = _call(**override)
        assert approved is False
        assert size == 0.0


def test_invariant_size_never_negative():
    for capital in (1.0, 100.0, 1_000.0, 1_000_000.0):
        _, size = _call(account_capital=capital)
        assert size >= 0.0


def test_kelly_matches_riskmanager_oracle():
    rm = RiskManager(max_risk_per_trade=0.02, atr_multiplier=2.0)
    kelly = calculate_kelly_position_size(100.0, 2.0, 2.0, 100_000.0, 0.02)
    assert kelly == math.floor(rm.compute_position_size(100_000.0, 100.0, 2.0))


def test_enforce_volatility_stop_uses_trailing_and_flags_trigger():
    stop, triggered = enforce_volatility_stop(100.0, 2.0, 2.0, 95.0, 110.0)
    assert stop == 106.0  # trailing: 110 - 2*2 beats hard stop 96
    assert triggered is True  # current 95 <= 106
    _, not_triggered = enforce_volatility_stop(100.0, 2.0, 2.0, 108.0, 110.0)
    assert not_triggered is False

```

---

### File: `new_pipeline/tests/unit/test_ingestion_parallel.py`

```py
import pandas as pd
from new_pipeline.config import reload_config
from new_pipeline.data.ingestion import DataIngestion


def test_load_many_concurrent(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_DATA__RAW_VAULT_DIR", str(tmp_path / "raw"))
    reload_config()
    ingestion = DataIngestion()
    names = ["a.csv", "b.csv", "c.csv"]
    for name in names:
        ingestion.stage_dataframe(pd.DataFrame({"date": ["2024-01-01"], "close": [1.0]}), name)

    frames = ingestion.load_many(names)

    assert set(frames) == set(names)
    assert all(len(frame) == 1 for frame in frames.values())

```

---

### File: `new_pipeline/tests/unit/test_metrics_endpoint.py`

```py
from new_pipeline.monitoring.metrics import MetricsCollector
from new_pipeline.monitoring.metrics_endpoint import CONTENT_TYPE, render_metrics_response


def test_render_metrics_response():
    collector = MetricsCollector()
    collector.increment("orders", 3)
    status, content_type, body = render_metrics_response(collector)
    assert status == 200
    assert content_type == CONTENT_TYPE
    assert "quantum_avenger_orders 3.0" in body

```

---

### File: `new_pipeline/tests/unit/test_crash_risk.py`

```py
import numpy as np
from new_pipeline.features.gpu_kernels import ncskew, rolling_duvol, rolling_ncskew


def test_rolling_ncskew_shape_and_leading_nan():
    returns = np.random.default_rng(0).normal(size=100)
    out = rolling_ncskew(returns, 60)
    assert out.shape == (100,)
    assert np.isnan(out[:59]).all()
    assert np.isfinite(out[59:]).all()


def test_rolling_duvol_shape_and_leading_nan():
    returns = np.random.default_rng(0).normal(size=100)
    out = rolling_duvol(returns, 60)
    assert out.shape == (100,)
    assert np.isnan(out[:59]).all()
    assert np.isfinite(out[59:]).all()


def test_rolling_ncskew_matches_scalar_on_full_window():
    returns = np.random.default_rng(2).normal(size=60)
    out = rolling_ncskew(returns, 60)
    assert abs(out[-1] - ncskew(returns)) < 1e-9


def test_rolling_too_short_is_all_nan():
    assert np.isnan(rolling_ncskew(np.zeros(10), 60)).all()

```

---

### File: `new_pipeline/tests/unit/test_orchestrator.py`

```py
from new_pipeline.adapters import FakeBroker
from new_pipeline.adapters.base import LLMClient, SentimentResult, Verdict
from new_pipeline.execution.orchestrator import TradeOrchestrator, TradeRequest
from new_pipeline.execution.veto_ledger import VetoLedger


class _ScriptedLLM(LLMClient):
    def __init__(self, stance: str):
        self._stance = stance

    def sentiment(self, text):
        return SentimentResult(0.0, "neutral")

    def verdict(self, prompt):
        return Verdict(self._stance, "rationale")


def _executable_request():
    return TradeRequest(
        "BUY", "AAPL", 100.0, 1.0, 2.0, 100000.0, 0.02, 0.0, 5e6, 5e6, 0.02, ["ctx"]
    )


def test_happy_path_executes(tmp_path):
    ledger = VetoLedger(tmp_path / "v.parquet")
    out = TradeOrchestrator(_ScriptedLLM("BULLISH"), FakeBroker(), ledger).run(
        _executable_request()
    )
    assert out["outcome"] == "executed"
    assert out["position_size"] == 1000.0
    assert out["execution_id"]
    assert ledger.read().column("veto_gate").to_pylist() == ["none"]


def test_grader_veto_after_retries(tmp_path):
    ledger = VetoLedger(tmp_path / "v.parquet")
    out = TradeOrchestrator(_ScriptedLLM("NEUTRAL"), FakeBroker(), ledger, max_retries=3).run(
        _executable_request()
    )
    assert out["outcome"] == "vetoed"
    assert out["attempts"] == 3  # retried up to the limit before falling back
    assert ledger.read().column("veto_gate").to_pylist() == ["grader"]


def test_shield_veto_when_account_too_small(tmp_path):
    ledger = VetoLedger(tmp_path / "v.parquet")
    tiny = TradeRequest("BUY", "AAPL", 100.0, 1.0, 2.0, 50.0, 0.02, 0.0, 5e6, 5e6, 0.02, ["ctx"])
    out = TradeOrchestrator(_ScriptedLLM("BULLISH"), FakeBroker(), ledger).run(tiny)
    assert out["outcome"] == "vetoed"
    assert ledger.read().column("veto_gate").to_pylist() == ["shield"]


def test_broker_records_executed_order(tmp_path):
    broker = FakeBroker()
    TradeOrchestrator(_ScriptedLLM("BULLISH"), broker, VetoLedger(tmp_path / "v.parquet")).run(
        _executable_request()
    )
    assert broker.get_positions()["AAPL"] == 1000.0
    assert broker.orders[0]["tif"] == "day"

```

---

### File: `new_pipeline/tests/unit/test_logging_structured.py`

```py
import json
import logging

from new_pipeline.core.logging import (
    JsonFormatter,
    TraceIdFilter,
    configure_logging,
    get_trace_id,
    trace_context,
)


def _record(msg: str = "hello") -> logging.LogRecord:
    return logging.LogRecord("quantum_avenger", logging.INFO, __file__, 1, msg, None, None)


def test_json_formatter_emits_valid_json_with_trace_id():
    formatter = JsonFormatter()
    with trace_context("abc123"):
        payload = json.loads(formatter.format(_record("hi")))
    assert payload["message"] == "hi"
    assert payload["level"] == "INFO"
    assert payload["trace_id"] == "abc123"


def test_trace_context_sets_and_resets():
    assert get_trace_id() is None
    with trace_context("xyz") as tid:
        assert tid == "xyz"
        assert get_trace_id() == "xyz"
    assert get_trace_id() is None


def test_trace_filter_injects_default_dash():
    record = _record()
    assert TraceIdFilter().filter(record) is True
    assert record.trace_id == "-"


def test_configure_logging_returns_logger():
    assert isinstance(configure_logging(), logging.Logger)

```

---

### File: `new_pipeline/tests/unit/test_minbtl.py`

```py
import numpy as np
from new_pipeline.evaluation.minbtl import backtest_length_is_sufficient, min_backtest_length


def test_minbtl_increases_with_trials():
    few = min_backtest_length(5, target_sharpe=1.0)
    many = min_backtest_length(500, target_sharpe=1.0)
    assert many > few > 0.0


def test_minbtl_decreases_with_higher_target_sharpe():
    easy = min_backtest_length(100, target_sharpe=2.0)
    hard = min_backtest_length(100, target_sharpe=0.5)
    assert hard > easy


def test_minbtl_guards():
    assert min_backtest_length(100, target_sharpe=0.0) == float("inf")
    assert min_backtest_length(1, target_sharpe=1.0) == 0.0  # no multiplicity with < 2 trials


def test_periods_per_year_scales_to_observations():
    years = min_backtest_length(50, 1.0)
    observations = min_backtest_length(50, 1.0, periods_per_year=252)
    assert np.isclose(observations, years * 252)


def test_sufficiency_check():
    required = min_backtest_length(50, 1.0, periods_per_year=252)
    assert backtest_length_is_sufficient(int(required) + 1, 50, 1.0)
    assert not backtest_length_is_sufficient(int(required) - 1, 50, 1.0)

```

---

### File: `new_pipeline/tests/unit/test_sizing.py`

```py
from new_pipeline.data.sizing import (
    MAX_BLOCK_BYTES,
    MIN_BLOCK_BYTES,
    dynamic_block_bytes,
    dynamic_row_group_size,
)

_GB = 1024**3


def test_block_bytes_clamped_to_max():
    assert dynamic_block_bytes(0.05, available_bytes=10 * _GB) == MAX_BLOCK_BYTES


def test_block_bytes_clamped_to_min():
    assert dynamic_block_bytes(0.05, available_bytes=100 * 1024**2) == MIN_BLOCK_BYTES


def test_block_bytes_within_range():
    block = dynamic_block_bytes(0.05, available_bytes=2 * _GB)
    assert block == int(2 * _GB * 0.05)
    assert MIN_BLOCK_BYTES <= block <= MAX_BLOCK_BYTES


def test_row_group_size_bounds():
    rows = dynamic_row_group_size(avg_row_bytes=512, available_bytes=2 * _GB)
    assert 1000 <= rows <= 500_000


def test_row_group_size_uses_psutil_by_default():
    assert dynamic_row_group_size() >= 1000

```

---

### File: `new_pipeline/tests/unit/test_universe.py`

```py
from datetime import date

from new_pipeline.adapters import StaticUniverseProvider

_EXPECTED_SECTORS = {
    "Information Technology",
    "Health Care",
    "Financials",
    "Consumer Discretionary",
    "Communication Services",
    "Industrials",
    "Consumer Staples",
    "Energy",
    "Utilities",
    "Real Estate",
    "Materials",
}


def test_loads_all_eleven_gics_sectors():
    provider = StaticUniverseProvider()
    assert set(provider.sectors().values()) == _EXPECTED_SECTORS


def test_point_in_time_membership_is_survivorship_safe():
    provider = StaticUniverseProvider()
    # Lehman was in the index in 2007 but delisted by 2020.
    assert "LEH" in provider.symbols(date(2007, 6, 1))
    assert "LEH" not in provider.symbols(date(2020, 1, 1))
    # Alphabet class A only entered the universe in 2014.
    assert "GOOGL" not in provider.symbols(date(2007, 6, 1))
    assert "GOOGL" in provider.symbols(date(2020, 1, 1))


def test_members_without_as_of_returns_everything():
    provider = StaticUniverseProvider()
    assert len(provider.members()) == len(provider.symbols())
    assert len(provider.members()) >= 40

```

---

### File: `new_pipeline/tests/unit/test_circuit_breaker.py`

```py
import pytest
from new_pipeline.core.circuit_breaker import CircuitBreaker, CircuitState
from new_pipeline.core.exceptions import CircuitBreakerError


def _boom() -> None:
    raise ValueError("boom")


def test_starts_closed_and_passes_through():
    breaker = CircuitBreaker(failure_threshold=2)
    assert breaker.state is CircuitState.CLOSED
    assert breaker.call(lambda: 42) == 42


def test_opens_after_threshold_failures():
    breaker = CircuitBreaker(failure_threshold=2)
    for _ in range(2):
        with pytest.raises(ValueError):
            breaker.call(_boom)
    assert breaker.state is CircuitState.OPEN
    with pytest.raises(CircuitBreakerError):
        breaker.call(lambda: 1)


def test_half_open_then_closes_on_success():
    clock = {"t": 0.0}
    breaker = CircuitBreaker(
        failure_threshold=1, recovery_timeout=10.0, clock=lambda: clock["t"]
    )
    with pytest.raises(ValueError):
        breaker.call(_boom)
    assert breaker.state is CircuitState.OPEN

    clock["t"] = 11.0  # past the recovery window
    assert breaker.call(lambda: "ok") == "ok"
    assert breaker.state is CircuitState.CLOSED


def test_success_resets_failure_count():
    breaker = CircuitBreaker(failure_threshold=3)
    with pytest.raises(ValueError):
        breaker.call(_boom)
    breaker.call(lambda: 1)
    assert breaker.failure_count == 0

```

---

### File: `new_pipeline/tests/unit/test_entity_anonymizer.py`

```py
from new_pipeline.execution.entity_anonymizer import EntityAnonymizer


def test_masks_known_entities_and_roundtrips():
    anon = EntityAnonymizer(["Apple", "AAPL", "Microsoft"])
    original = "Apple and AAPL rose; Microsoft fell."
    result = anon.anonymize(original)
    assert "Apple" not in result.text
    assert "AAPL" not in result.text
    assert "[COMPANY_" in result.text
    assert EntityAnonymizer.deanonymize(result.text, result.mapping) == original


def test_longest_match_first():
    anon = EntityAnonymizer(["Apple", "Apple Inc"])
    result = anon.anonymize("Apple Inc reported earnings.")
    assert result.text.count("[COMPANY_") == 1  # "Apple Inc" masked as one entity
    assert "Inc" not in result.text


def test_case_insensitive():
    anon = EntityAnonymizer(["apple"])
    assert "Apple" not in anon.anonymize("Apple surged").text


def test_unknown_terms_untouched():
    result = EntityAnonymizer(["Apple"]).anonymize("Banana prices rose")
    assert result.text == "Banana prices rose"
    assert result.mapping == {}

```

---

### File: `new_pipeline/tests/unit/test_async_sentiment.py`

```py
from new_pipeline.adapters import FakeLLMClient
from new_pipeline.execution.async_sentiment import batch_sentiment


def test_batch_preserves_order_and_matches_sync():
    client = FakeLLMClient()
    texts = ["Apple beats earnings", "Oil slumps", "Neutral note", "Rally continues"]
    results = batch_sentiment(client, texts, concurrency=2)
    assert len(results) == len(texts)
    assert results == [client.sentiment(text) for text in texts]


def test_empty_batch():
    assert batch_sentiment(FakeLLMClient(), []) == []

```

---

### File: `new_pipeline/tests/unit/test_mcp_tools.py`

```py
from new_pipeline.execution.mcp_tools import build_default_registry


def test_registry_builds_tools():
    registry = build_default_registry()
    assert len(registry) >= 8
    assert "evaluate_risk_veto_gates" in registry.names()


def test_tool_call_returns_structured_dict():
    out = build_default_registry().call(
        "calculate_kelly_position_size",
        entry_price=100.0,
        atr=1.0,
        atr_multiplier=2.0,
        account_capital=100000.0,
        max_risk_pct=0.02,
    )
    assert out["position_size"] == 1000.0


def test_jsonrpc_schema_shape():
    schema = build_default_registry().get("calculate_dynamic_slippage").to_jsonrpc()
    assert schema["name"] == "calculate_dynamic_slippage"
    assert schema["inputSchema"]["type"] == "object"
    assert "order_notional" in schema["inputSchema"]["properties"]


def test_dsr_tool_matches_function():
    out = build_default_registry().call(
        "deflated_sharpe_ratio",
        returns=[0.01, -0.005, 0.02, 0.0, 0.015] * 20,
        trial_sharpes=[0.1, 0.2, 0.15],
    )
    assert 0.0 <= out["dsr"] <= 1.0
    assert out["verdict"] in {"overfit", "insignificant", "promote"}

```

---

### File: `new_pipeline/tests/unit/test_training_db.py`

```py
from datetime import date

import polars as pl
from new_pipeline.adapters.fakes import FakeLLMClient, FakeMarketDataSource, FakeNewsSource
from new_pipeline.adapters.universe_static import StaticUniverseProvider
from new_pipeline.config import reload_config
from new_pipeline.data.training_db import build_training_database


def test_build_training_database_with_news(tmp_path):
    reload_config()
    out = tmp_path / "training.parquet"
    summary = build_training_database(
        out, FakeMarketDataSource(), StaticUniverseProvider(),
        start=date(2023, 1, 1), end=date(2023, 4, 30),
        news_source=FakeNewsSource(), llm=FakeLLMClient(),
    )

    assert out.exists() and summary["rows"] > 0
    df = pl.read_parquet(out)
    assert {"target_label", "sentiment_score"} <= set(df.columns)
    assert df["sentiment_score"].is_between(-1.0, 1.0).all()
    assert df["sentiment_score"].n_unique() > 1  # news enrichment varies the score


def test_build_training_database_without_news(tmp_path):
    reload_config()
    out = tmp_path / "t.parquet"
    summary = build_training_database(
        out, FakeMarketDataSource(), StaticUniverseProvider(),
        start=date(2023, 1, 1), end=date(2023, 3, 31),
    )
    assert out.exists() and summary["rows"] > 0
    # sentiment_score is part of the feature contract; without news it stays the placeholder.
    assert pl.read_parquet(out)["sentiment_score"].n_unique() == 1

```

---

### File: `new_pipeline/tests/unit/test_exceptions.py`

```py
from new_pipeline.core.exceptions import ConfigurationError, QuantumAvengerError


def test_custom_exception_hierarchy():
    exc = ConfigurationError("config failed")
    assert isinstance(exc, QuantumAvengerError)
    assert str(exc) == "config failed"

```

---

### File: `new_pipeline/tests/unit/test_feature_compiler.py`

```py
import pandas as pd
from new_pipeline.config import reload_config
from new_pipeline.features.compiler import PandasFeatureCompiler


def test_feature_compiler_generates_feature_columns(monkeypatch, tmp_path):
    monkeypatch.setenv("QA_DATA__RAW_VAULT_DIR", str(tmp_path / "raw"))
    monkeypatch.setenv("QA_DATA__PROCESSED_VAULT_DIR", str(tmp_path / "processed"))
    reload_config()

    raw_path = tmp_path / "raw"
    processed_path = tmp_path / "processed"
    raw_path.mkdir(parents=True)
    processed_path.mkdir(parents=True)

    df = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04", "2026-01-05"],
            "open": [100.0, 101.0, 102.0, 103.0, 104.0],
            "high": [101.0, 102.0, 103.0, 104.0, 105.0],
            "low": [99.0, 100.0, 101.0, 102.0, 103.0],
            "close": [100.5, 101.5, 102.5, 103.5, 104.5],
            "volume": [1000, 1100, 1200, 1300, 1400],
        }
    )
    source_file = raw_path / "sample.csv"
    df.to_csv(source_file, index=False)

    compiler = PandasFeatureCompiler()
    compiler.compile(raw_path, processed_path)

    output_file = processed_path / "sample.csv"
    assert output_file.exists()

    output_df = pd.read_csv(output_file, parse_dates=["date"])
    assert "returns" in output_df.columns
    assert "atr_14" in output_df.columns
    assert "volatility_20" in output_df.columns
    assert "average_volume_20" in output_df.columns

```

---

### File: `new_pipeline/tests/unit/test_slippage.py`

```py
import math

from new_pipeline.features.slippage import (
    adjust_slippage_by_regime,
    hydrodynamic_slippage_bps,
)


def test_slippage_matches_formula():
    bps = hydrodynamic_slippage_bps(50_000.0, 0.2, 100_000_000.0, 0.5, 10_000.0)
    expected = 0.5 * 0.2 * math.sqrt(50_000.0 / 100_000_000.0) * 10_000.0
    assert math.isclose(bps, expected, rel_tol=1e-9)


def test_no_volume_forces_veto_value():
    assert hydrodynamic_slippage_bps(50_000.0, 0.2, 0.0) > 1e17


def test_zero_volatility_is_zero_slippage():
    assert hydrodynamic_slippage_bps(50_000.0, 0.0, 1_000.0) == 0.0


def test_regime_doubles_slippage_in_high_vol():
    assert adjust_slippage_by_regime(30.0, 1) == 60.0
    assert adjust_slippage_by_regime(30.0, 0) == 30.0

```

---

### File: `new_pipeline/tests/unit/test_trainer_early_stopping.py`

```py
import numpy as np
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.trainer import train_booster


def test_early_stopping_sets_best_iteration():
    seed_everything(0)
    rng = np.random.default_rng(0)
    features = rng.normal(size=(200, 4))
    labels = (features[:, 0] > 0).astype(float)
    booster = train_booster(
        features[:160],
        labels[:160],
        num_boost_round=80,
        eval_features=features[160:],
        eval_labels=labels[160:],
        early_stopping_rounds=5,
    )
    assert isinstance(booster.best_iteration, int)
    assert 0 <= booster.best_iteration <= 79

```

---

### File: `new_pipeline/tests/unit/test_rag_engine.py`

```py
from new_pipeline.execution.rag_engine import RagEngine, late_chunk


def test_late_chunk_splits_on_sentences():
    chunks = late_chunk("First sentence. Second sentence. Third one.", chunk_size=20, overlap=0)
    assert len(chunks) >= 2
    assert all(chunk for chunk in chunks)


def test_retrieve_returns_relevant_chunk_first():
    rag = RagEngine(top_k=1)
    rag.index(
        [
            "Apple expanded its AI workforce. Earnings beat estimates.",
            "Oil prices fell on demand worries. Energy stocks dropped.",
        ]
    )
    hits = rag.retrieve("AI workforce earnings")
    assert len(hits) == 1
    assert "AI workforce" in hits[0].text


def test_retrieve_on_empty_index():
    assert RagEngine().retrieve("anything") == []


def test_top_k_caps_results():
    rag = RagEngine(top_k=5)
    rag.index(["A cat sat.", "A dog ran.", "Birds fly high.", "Fish swim deep."])
    assert len(rag.retrieve("animals", top_k=2)) == 2

```

---

### File: `new_pipeline/tests/unit/test_promotion.py`

```py
import pytest
from new_pipeline.core.exceptions import PromotionError
from new_pipeline.evaluation.promotion import PromotionRegistry, assess_promotion


def test_promote_when_both_gates_pass():
    decision = assess_promotion("Energy", 0.97, 0.2)
    assert decision.promoted is True
    assert decision.reason == "true alpha"


def test_reject_low_dsr():
    decision = assess_promotion("Energy", 0.80, 0.5)
    assert decision.promoted is False
    assert decision.reason == "low DSR"


def test_reject_failed_gauntlet():
    decision = assess_promotion("Energy", 0.97, -0.1)
    assert decision.promoted is False
    assert decision.reason == "failed synthetic gauntlet"


def test_registry_records_persists_and_is_append_only(tmp_path):
    path = tmp_path / "reg.json"
    registry = PromotionRegistry(path)
    registry.record(assess_promotion("Energy", 0.97, 0.2), model_path="/m/energy.json")
    registry.record(assess_promotion("Tech", 0.80, 0.1))  # rejected, still recorded
    assert registry.is_champion("Energy")
    assert not registry.is_champion("Tech")
    assert len(registry.promotions) == 2
    # reload from disk -> persisted active champions
    reloaded = PromotionRegistry(path)
    assert reloaded.active_champions() == {"Energy": "/m/energy.json"}


def test_promoted_without_model_path_raises(tmp_path):
    registry = PromotionRegistry(tmp_path / "reg.json")
    with pytest.raises(PromotionError):
        registry.record(assess_promotion("Energy", 0.97, 0.2))


def test_pbo_gate_blocks_overfit_candidate():
    decision = assess_promotion("Energy", 0.97, 0.2, pbo=0.8, pbo_threshold=0.5)
    assert decision.promoted is False
    assert decision.reason == "overfit (high PBO)"


def test_pbo_within_threshold_still_promotes():
    decision = assess_promotion("Energy", 0.97, 0.2, pbo=0.3, pbo_threshold=0.5)
    assert decision.promoted is True
    assert decision.pbo == 0.3


def test_omitted_pbo_leaves_gate_disabled():
    # Back-compat: callers that pass no PBO are gated on DSR + synthetic only.
    assert assess_promotion("Energy", 0.97, 0.2).promoted is True


def test_minbtl_gate_blocks_short_backtest():
    decision = assess_promotion("Energy", 0.97, 0.2, minbtl_satisfied=False)
    assert decision.promoted is False
    assert decision.reason == "backtest shorter than MinBTL"


def test_minbtl_gate_disabled_by_default():
    # minbtl_satisfied=None (the default) must not gate.
    assert assess_promotion("Energy", 0.97, 0.2, minbtl_satisfied=True).promoted is True
    assert assess_promotion("Energy", 0.97, 0.2).promoted is True


def test_diagnostics_are_recorded(tmp_path):
    registry = PromotionRegistry(tmp_path / "reg.json")
    decision = assess_promotion("Energy", 0.97, 0.2, pbo=0.1, psr=0.99, haircut_sharpe=1.1)
    entry = registry.record(decision, model_path="/m/e.json")
    assert entry["pbo"] == 0.1
    assert entry["psr"] == 0.99
    assert entry["haircut_sharpe"] == 1.1

```

---

### File: `new_pipeline/tests/unit/test_dashboard_views.py`

```py
from new_pipeline.evaluation.promotion import PromotionRegistry, assess_promotion
from new_pipeline.execution.trade_log import TradeLog, TradeRecord
from new_pipeline.monitoring.dashboard.views import model_registry_view, risk_view


def test_model_registry_view(tmp_path):
    path = tmp_path / "reg.json"
    registry = PromotionRegistry(path)
    registry.record(assess_promotion("Energy", 0.97, 0.2), model_path="/m/e.json")
    view = model_registry_view(path)
    assert view["active_champions"] == {"Energy": "/m/e.json"}
    assert len(view["promotions"]) == 1


def test_model_registry_view_missing(tmp_path):
    assert model_registry_view(tmp_path / "none.json") == {
        "active_champions": {},
        "promotions": [],
    }


def test_risk_view(tmp_path):
    path = tmp_path / "trades.parquet"
    log = TradeLog(path)
    log.append(TradeRecord("AAPL", "buy", 10, 100.0, "filled", "o1"))  # +1000
    log.append(TradeRecord("MSFT", "buy", 5, 100.0, "filled", "o2"))  # +500
    log.append(TradeRecord("AAPL", "sell", 2, 100.0, "filled", "o3"))  # -200 -> AAPL 800

    view = risk_view(path)
    assert view.position_count == 2
    assert abs(view.gross_exposure - 1300.0) < 1e-6
    assert abs(view.largest_position - 800.0) < 1e-6
    assert abs(view.concentration - 800.0 / 1300.0) < 1e-9


def test_risk_view_empty(tmp_path):
    assert risk_view(tmp_path / "none.parquet").gross_exposure == 0.0

```

---

### File: `new_pipeline/tests/unit/test_alpaca_adapters.py`

```py
from datetime import date, datetime
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

pytest.importorskip("alpaca")  # live SDK; skipped in the offline CI image

from new_pipeline.adapters.broker_alpaca import AlpacaBroker  # noqa: E402
from new_pipeline.adapters.market_alpaca import AlpacaMarketDataSource  # noqa: E402
from new_pipeline.adapters.news_alpaca import AlpacaNewsSource  # noqa: E402


def _bar(ts, close):
    return SimpleNamespace(
        timestamp=ts, open=close - 1, high=close + 1, low=close - 2, close=close, volume=1000
    )


def test_market_history_maps_bars_and_builds_request():
    client = MagicMock()
    client.get_stock_bars.return_value = SimpleNamespace(
        data={"AAPL": [_bar(datetime(2024, 1, 2, 9, 30), 100.0),
                       _bar(datetime(2024, 1, 3, 9, 30), 101.0)]}
    )
    source = AlpacaMarketDataSource("k", "s", client=client)
    bars = source.history("AAPL", date(2024, 1, 1), date(2024, 1, 31))

    assert [b.day for b in bars] == [date(2024, 1, 2), date(2024, 1, 3)]
    assert bars[0].close == 100.0 and bars[1].volume == 1000
    assert client.get_stock_bars.call_args.args[0].symbol_or_symbols == "AAPL"


def test_news_headlines_maps_articles():
    client = MagicMock()
    client.get_news.return_value = SimpleNamespace(
        data={"news": [SimpleNamespace(created_at=datetime(2024, 1, 2), headline="AAPL rallies")]}
    )
    source = AlpacaNewsSource("k", "s", client=client)
    items = source.headlines("AAPL", date(2024, 1, 2))

    assert items[0].headline == "AAPL rallies" and items[0].symbol == "AAPL"


def test_broker_market_order_and_positions():
    from alpaca.trading.requests import MarketOrderRequest

    client = MagicMock()
    client.submit_order.return_value = SimpleNamespace(
        status=SimpleNamespace(value="accepted"), id="abc-1", symbol="AAPL",
        qty="3", side=SimpleNamespace(value="buy"), limit_price=None, filled_avg_price=None,
    )
    client.get_all_positions.return_value = [
        SimpleNamespace(symbol="AAPL", qty="3", side=SimpleNamespace(value="long")),
        SimpleNamespace(symbol="TSLA", qty="2", side=SimpleNamespace(value="short")),
    ]
    broker = AlpacaBroker("k", "s", client=client)
    receipt = broker.submit_order({"symbol": "AAPL", "qty": 3, "side": "buy", "tif": "day"})

    assert receipt["order_id"] == "abc-1" and receipt["status"] == "accepted"
    assert receipt["qty"] == 3.0 and receipt["filled_avg_price"] == 0.0
    assert isinstance(client.submit_order.call_args.kwargs["order_data"], MarketOrderRequest)
    assert broker.get_positions() == {"AAPL": 3.0, "TSLA": -2.0}


def test_broker_limit_order():
    from alpaca.trading.requests import LimitOrderRequest

    client = MagicMock()
    client.submit_order.return_value = SimpleNamespace(
        status="accepted", id="abc-2", symbol="AAPL", qty="1",
        side="buy", limit_price="101.5", filled_avg_price="101.5",
    )
    broker = AlpacaBroker("k", "s", client=client)
    receipt = broker.submit_order({"symbol": "AAPL", "qty": 1, "side": "buy", "limit_price": 101.5})

    request = client.submit_order.call_args.kwargs["order_data"]
    assert isinstance(request, LimitOrderRequest) and float(request.limit_price) == 101.5
    assert receipt["limit_price"] == 101.5 and receipt["filled_avg_price"] == 101.5


def test_broker_account_snapshot():
    client = MagicMock()
    client.get_account.return_value = SimpleNamespace(
        status="ACTIVE", cash="100000", equity="100500", buying_power="200000"
    )
    broker = AlpacaBroker("k", "s", client=client)
    assert broker.account() == {
        "status": "ACTIVE", "cash": 100000.0, "equity": 100500.0, "buying_power": 200000.0,
    }

```

---

### File: `new_pipeline/tests/unit/test_labels.py`

```py
import numpy as np
import polars as pl
from new_pipeline.features.labels import add_labels, friction_aware_labels


def test_label_beats_cost():
    close = np.array([100.0, 100.05, 102.0, 101.0])  # cost 10bps = 0.001
    labels = friction_aware_labels(close, horizon=1, cost_bps=10.0)
    assert labels[0] == 0.0  # +0.05% < 0.1% cost
    assert labels[1] == 1.0  # +1.95% > cost
    assert labels[2] == 0.0  # negative
    assert np.isnan(labels[3])  # no forward window


def test_horizon_window_is_nan_at_tail():
    close = np.arange(1, 11, dtype=float)  # strictly increasing
    labels = friction_aware_labels(close, horizon=3, cost_bps=0.0)
    assert np.isnan(labels[-3:]).all()
    assert (labels[:-3] == 1.0).all()


def test_add_labels_per_ticker():
    frame = pl.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "ticker": ["AAA", "AAA", "AAA"],
            "close": [100.0, 110.0, 90.0],
        }
    )
    out = add_labels(frame, horizon=1, cost_bps=0.0)
    assert "target_label" in out.columns
    assert out["target_label"][0] == 1.0  # 100 -> 110 up
    assert out["target_label"][1] == 0.0  # 110 -> 90 down

```

---

### File: `new_pipeline/tests/unit/test_config_overlays.py`

```py
from new_pipeline.config import reload_config
from new_pipeline.config.development import development_config
from new_pipeline.config.production import production_config
from new_pipeline.config.testing import testing_config as load_testing_config


def test_development_overlay():
    cfg = development_config()
    assert cfg.logging.level == "DEBUG"
    assert cfg.gpu.cuda_enabled is False


def test_testing_overlay_isolates_vaults():
    cfg = load_testing_config()
    assert cfg.data.raw_vault_dir == "./data/test/raw"
    assert cfg.logging.level == "WARNING"
    assert cfg.features.cache_enabled is False


def test_production_overlay_enables_gpu_and_json():
    cfg = production_config()
    assert cfg.gpu.device == "cuda"
    assert cfg.gpu.cuda_enabled is True
    assert cfg.logging.json_logs is True
    assert cfg.system.run_mode == "live"


def test_defaults_have_no_overlay_applied():
    cfg = reload_config()
    assert cfg.system.run_mode == "backtest"
    assert cfg.gpu.device == "cpu"


def test_qa_env_selects_overlay(monkeypatch):
    monkeypatch.setenv("QA_ENV", "production")
    cfg = reload_config()
    assert cfg.logging.json_logs is True
    assert cfg.gpu.device == "cuda"


def test_env_var_overrides_overlay(monkeypatch):
    monkeypatch.setenv("QA_ENV", "development")
    monkeypatch.setenv("QA_LOGGING__LEVEL", "ERROR")
    cfg = reload_config()
    assert cfg.logging.level == "ERROR"  # QA_ var beats the development overlay's DEBUG

```

---

### File: `new_pipeline/tests/unit/test_backtest.py`

```py
from datetime import date

import numpy as np
import pytest
from new_pipeline.adapters.fakes import FakeMarketDataSource
from new_pipeline.analysis.backtest import backtest_ticker
from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything


def _prepare(monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    monkeypatch.setenv("QA_EXECUTION__CONFIDENCE_THRESHOLD", "0.3")
    reload_config()
    seed_everything(0)


def test_backtest_produces_equity_curve(monkeypatch):
    _prepare(monkeypatch)
    result = backtest_ticker("AAPL", date(2023, 1, 1), date(2023, 9, 30), FakeMarketDataSource())

    assert result.n_test_bars > 0
    assert result.equity_curve.size == result.n_test_bars
    assert np.isfinite(result.sharpe)
    assert -1.0 <= result.max_drawdown <= 0.0
    assert 0.0 <= result.win_rate <= 1.0


def test_backtest_short_history_is_empty():
    result = backtest_ticker("AAPL", date(2023, 1, 1), date(2023, 1, 5), FakeMarketDataSource())
    assert result.n_test_bars == 0 and result.n_trades == 0


def test_plot_backtest_writes_png(tmp_path, monkeypatch):
    pytest.importorskip("matplotlib")
    _prepare(monkeypatch)
    from new_pipeline.analysis.backtest import plot_backtest

    result = backtest_ticker("AAPL", date(2023, 1, 1), date(2023, 9, 30), FakeMarketDataSource())
    out = plot_backtest(result, tmp_path / "bt.png", subtitle="offline test")
    assert (tmp_path / "bt.png").exists() and out.endswith("bt.png")

```

---

### File: `new_pipeline/tests/unit/test_cpcv.py`

```py
import numpy as np
import pytest
from new_pipeline.core.exceptions import CPCVSplitError
from new_pipeline.tournament.cpcv import CPCVSplitGenerator


def test_canonical_fifteen_folds():
    gen = CPCVSplitGenerator()
    folds = gen.split(120)
    assert len(folds) == 15 == gen.n_folds


def test_no_train_test_overlap():
    for train_idx, test_idx in CPCVSplitGenerator().split(120):
        assert np.intersect1d(train_idx, test_idx).size == 0


def test_embargo_excludes_positions_after_test():
    for train_idx, test_idx in CPCVSplitGenerator(purge=5, embargo=5).split(120):
        train = set(train_idx.tolist())
        last = int(test_idx.max())
        for offset in range(1, 6):
            if last + offset < 120:
                assert last + offset not in train


def test_purge_excludes_positions_before_test():
    for train_idx, test_idx in CPCVSplitGenerator(purge=5, embargo=5).split(120):
        train = set(train_idx.tolist())
        test_set = set(test_idx.tolist())
        first = int(test_idx.min())
        for offset in range(1, 6):
            pos = first - offset
            if pos >= 0 and pos not in test_set:
                assert pos not in train


def test_raises_when_too_few_samples():
    with pytest.raises(CPCVSplitError):
        CPCVSplitGenerator(n_groups=6).split(3)

```

---

### File: `new_pipeline/tests/integration/test_execution_flow.py`

```py
"""Phase 5 offline integration: news -> anonymize -> RAG context -> decision -> ledger.

The Milestone M4 capstone — the full live-execution graph driven by fakes, no
network, deterministic.
"""

from datetime import date

from new_pipeline.adapters import FakeBroker, FakeNewsSource, StaticUniverseProvider
from new_pipeline.adapters.base import LLMClient, SentimentResult, Verdict
from new_pipeline.execution.entity_anonymizer import EntityAnonymizer
from new_pipeline.execution.orchestrator import TradeOrchestrator, TradeRequest
from new_pipeline.execution.rag_engine import RagEngine
from new_pipeline.execution.veto_ledger import VetoLedger


class _BullLLM(LLMClient):
    def sentiment(self, text):
        return SentimentResult(1.0, "bullish")

    def verdict(self, prompt):
        return Verdict("BULLISH", "supported by context")


def test_offline_execution_flow(tmp_path):
    # 1) news -> anonymized against the universe vocabulary (no tradable names leak)
    universe = StaticUniverseProvider()
    anonymizer = EntityAnonymizer(vocabulary=universe.symbols(date(2020, 1, 1)))
    headlines = FakeNewsSource().headlines("AAPL", date(2022, 6, 1))
    masked = [anonymizer.anonymize(item.headline).text for item in headlines]
    assert all("AAPL" not in text for text in masked)

    # 2) RAG context from the masked corpus
    rag = RagEngine(top_k=2)
    rag.index([*masked, "Market sentiment steady amid macro data."])
    context = [hit.text for hit in rag.retrieve("company outlook")]
    assert context

    # 3) orchestrate -> ledger
    ledger = VetoLedger(tmp_path / "veto.parquet")
    request = TradeRequest(
        "BUY", "AAPL", 100.0, 1.0, 2.0, 100000.0, 0.02, 0.0, 5e6, 5e6, 0.02, context
    )
    out = TradeOrchestrator(_BullLLM(), FakeBroker(), ledger).run(request)

    assert out["outcome"] in {"executed", "vetoed"}
    assert ledger.read().num_rows == 1

```

---

### File: `new_pipeline/tests/integration/test_whole_engine.py`

```py
"""Whole-engine offline dry run: train+promote -> trade graph -> ledgers -> dashboard.

The capstone that proves the engine is operational end to end with no network:
the offline pipeline produces champions, the runner drives them through the real
LangGraph trade graph, and the resulting veto ledger + trade log feed the
dashboard's KPI layer.
"""

from datetime import date

from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.execution.runner import run_trading_session
from new_pipeline.monitoring.dashboard.realtime import RealtimeDataManager
from new_pipeline.tournament.pipeline import run_offline_pipeline


def test_engine_runs_end_to_end(tmp_path, monkeypatch):
    ledger_dir = tmp_path / "ledger"
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    monkeypatch.setenv("QA_EXECUTION__CONFIDENCE_THRESHOLD", "0.3")  # ensure signals fire
    monkeypatch.setenv("QA_EXECUTION__LEDGER_DIR", str(ledger_dir))
    monkeypatch.setenv("QA_SYSTEM__RUN_MODE", "backtest")
    # Synthetic noise (correctly) clears no gate; relax them so the trade path runs.
    monkeypatch.setenv("QA_EVALUATION__DSR_PROMOTION_THRESHOLD", "0.0")
    monkeypatch.setenv("QA_EVALUATION__SYNTHETIC_SR_MIN", "-1000.0")
    monkeypatch.setenv("QA_EVALUATION__PBO_THRESHOLD", "1.0")
    reload_config()
    seed_everything(0)

    candidates = tmp_path / "candidates"
    run_offline_pipeline(candidates, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=3)

    summary = run_trading_session(
        candidates, start=date(2021, 1, 1), end=date(2021, 6, 30)
    )

    assert summary.sectors  # at least one champion traded
    assert summary.decisions > 0
    assert summary.executed + summary.vetoed == summary.decisions

    # Both parquet artifacts the dashboard reads were produced.
    assert (ledger_dir / "veto_ledger.parquet").exists()
    manager = RealtimeDataManager(
        ledger_dir / "veto_ledger.parquet", ledger_dir / "trade_log.parquet"
    )
    kpis = manager.kpis()
    assert kpis["total_decisions"] == summary.decisions
    assert kpis["executed"] == summary.executed


def test_session_is_empty_without_champions(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_EXECUTION__LEDGER_DIR", str(tmp_path / "ledger"))
    reload_config()
    summary = run_trading_session(tmp_path / "no_candidates")
    assert summary.sectors == []
    assert summary.decisions == 0

```

---

### File: `new_pipeline/tests/integration/test_offline_pipeline.py`

```py
"""End-to-end offline pipeline: fake data -> features+labels -> tournament -> promotion.

The Tier-1 capstone — exercises the whole chain with no network under a fixed
seed and a tiny budget.
"""

import json
from datetime import date

from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.pipeline import run_offline_pipeline


def test_offline_pipeline_runs(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    reload_config()
    seed_everything(0)

    summary = run_offline_pipeline(
        tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=2
    )

    assert summary["sectors"]  # at least one sector produced a candidate
    assert set(summary["promotions"]).issubset(set(summary["sectors"]))
    assert (tmp_path / "promotion_registry.json").exists()


def test_offline_pipeline_records_overfitting_diagnostics(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    reload_config()
    seed_everything(0)

    run_offline_pipeline(
        tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=2
    )

    registry = json.loads((tmp_path / "promotion_registry.json").read_text())
    assert registry["promotions"]
    entry = registry["promotions"][0]
    # Evaluation Rigor v2 gates ride along in the audit trail.
    assert {"pbo", "psr", "haircut_sharpe"} <= set(entry)
    assert isinstance(entry["pbo"], float)
    assert isinstance(entry["psr"], float)

```

---

### File: `new_pipeline/tests/integration/test_director_parallel.py`

```py
import numpy as np
import polars as pl

from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.director import run_sector_tournament

_FEATURES = ["f0", "f1", "f2"]


def _frame(n: int = 120) -> pl.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    for sector in ["Tech", "Energy", "Health"]:
        close = 100.0 + np.cumsum(rng.normal(0, 1, n))
        for i in range(n):
            rows.append(
                {
                    "sector": sector,
                    "f0": float(rng.normal()),
                    "f1": float(rng.normal()),
                    "f2": float(rng.normal()),
                    "close": float(close[i]),
                    "low": float(close[i] - 1.0),
                    "atr": 1.0,
                    "target_label": float(rng.integers(0, 2)),
                }
            )
    return pl.DataFrame(rows)


def test_parallel_sectors_produce_all_candidates(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "12")
    reload_config()
    seed_everything(0)

    results = run_sector_tournament(
        _frame(), _FEATURES, tmp_path, use_cfs=False, max_workers=3
    )

    assert set(results) == {"Tech", "Energy", "Health"}
    for sector in results:
        assert (tmp_path / f"{sector.lower()}_candidate.json").exists()

```

---

### File: `new_pipeline/tests/integration/test_streaming_compile.py`

```py
"""Out-of-core streaming feature compilation + the Dask parallel path (Tier 2)."""

from datetime import date

import polars as pl

from new_pipeline.adapters import FakeMarketDataSource
from new_pipeline.features.polars_engine import (
    FEATURE_NAMES,
    PolarsFeatureEngine,
    compile_features_dask,
)

_NEW_COLUMNS = ["roll_spread", "ncskew", "duvol", "sentiment_score"]


def _rows(symbol):
    return [
        {
            "date": bar.day, "ticker": symbol, "open": bar.open, "high": bar.high,
            "low": bar.low, "close": bar.close, "volume": bar.volume,
        }
        for bar in FakeMarketDataSource().history(symbol, date(2022, 1, 1), date(2022, 4, 30))
    ]


def test_roll_spread_in_feature_names():
    assert "roll_spread" in FEATURE_NAMES


def test_streaming_compile_out_of_core(tmp_path):
    raw = tmp_path / "raw.parquet"
    pl.DataFrame(_rows("AAA") + _rows("BBB")).write_parquet(raw)
    out = tmp_path / "processed.parquet"

    PolarsFeatureEngine().compile(raw, out)

    result = pl.read_parquet(out)
    assert set(result["ticker"].unique().to_list()) == {"AAA", "BBB"}
    for column in _NEW_COLUMNS:
        assert column in result.columns


def test_dask_parallel_compile(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    for symbol in ("AAA", "BBB"):
        pl.DataFrame(_rows(symbol)).write_parquet(raw_dir / f"{symbol}.parquet")
    out = tmp_path / "processed.parquet"

    compile_features_dask(raw_dir, out)

    result = pl.read_parquet(out)
    assert set(result["ticker"].unique().to_list()) == {"AAA", "BBB"}
    assert "ncskew" in result.columns

```

---

### File: `new_pipeline/tests/integration/__init__.py`

```py

```

---

### File: `new_pipeline/tests/integration/test_director.py`

```py
import numpy as np
import polars as pl

from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.director import run_sector_tournament

_FEATURES = ["f0", "f1", "f2"]


def _frame(n: int = 120) -> pl.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    for sector in ["Tech", "Energy"]:
        close = 100.0 + np.cumsum(rng.normal(0, 1, n))
        for i in range(n):
            rows.append(
                {
                    "sector": sector,
                    "f0": float(rng.normal()),
                    "f1": float(rng.normal()),
                    "f2": float(rng.normal()),
                    "close": float(close[i]),
                    "low": float(close[i] - 1.0),
                    "atr": 1.0,
                    "target_label": float(rng.integers(0, 2)),
                }
            )
    return pl.DataFrame(rows)


def test_director_produces_candidates_per_sector(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "15")
    reload_config()
    seed_everything(0)

    results = run_sector_tournament(_frame(), _FEATURES, tmp_path, use_cfs=True)

    assert set(results) == {"Tech", "Energy"}
    for sector, result in results.items():
        slug = sector.lower()
        assert (tmp_path / f"{slug}_candidate.json").exists()
        assert (tmp_path / f"{slug}_candidate_features.json").exists()
        assert (tmp_path / f"{slug}_returns_matrix.parquet").exists()
        assert result["selected_features"]
        assert set(result["selected_features"]).issubset(set(_FEATURES))

```

---

### File: `new_pipeline/tests/integration/test_tournament_flow.py`

```py
"""End-to-end offline chain: fixtures -> features -> candidate -> DSR -> promotion.

The Milestone M3 capstone. Runs with no network, fully seeded, using the fake
market source and the real tournament/evaluation stack.
"""

from datetime import date

import numpy as np
import polars as pl

from new_pipeline.adapters import FakeMarketDataSource
from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.evaluation.dsr import compute_deflated_sharpe_ratio
from new_pipeline.evaluation.hmm_gauntlet import run_hmm_synthetic_gauntlet
from new_pipeline.evaluation.promotion import PromotionRegistry, assess_promotion
from new_pipeline.features.polars_engine import add_features
from new_pipeline.tournament.grid_search import run_grid_search
from new_pipeline.tournament.trainer import predict_proba, save_candidate, train_booster

_FEATURE_COLS = ["returns", "atr", "adv_20", "volatility", "spread_pct", "amihud"]


def test_offline_end_to_end_pipeline(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "20")  # keep the suite fast
    reload_config()
    seed_everything(42)

    # 1) fixtures -> vectorized features
    bars = FakeMarketDataSource().history("AAPL", date(2022, 1, 1), date(2022, 6, 30))
    frame = pl.DataFrame(
        [
            {
                "date": bar.day,
                "ticker": "AAPL",
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            for bar in bars
        ]
    )
    feats = add_features(frame).drop_nulls()
    features = feats.select(_FEATURE_COLS).to_numpy()
    close = feats["close"].to_numpy()
    low = feats["low"].to_numpy()
    atr = feats["atr"].to_numpy()
    forward = np.zeros(len(close))
    forward[:-1] = close[1:] / close[:-1] - 1.0
    labels = (forward > 0.0).astype(np.float64)  # friction-aware proxy label

    # 2) tournament -> returns matrix + champion series
    result = run_grid_search(features, labels, {"close": close, "low": low, "atr": atr})
    assert result.returns_matrix.shape[0] == 4
    champion_returns = result.returns_matrix[int(np.argmax(result.trial_sharpes))]

    booster = train_booster(features, labels, num_boost_round=20)
    candidate_path = tmp_path / "AAPL_candidate.json"
    save_candidate(booster, candidate_path)
    assert candidate_path.exists()

    # 3) evaluation -> DSR + HMM synthetic gauntlet
    dsr = compute_deflated_sharpe_ratio(champion_returns, result.trial_sharpes)
    synthetic_sr = run_hmm_synthetic_gauntlet(
        forward, features, lambda f: predict_proba(booster, f), n_iter=20, seed=42
    )
    assert 0.0 <= dsr <= 1.0
    assert isinstance(synthetic_sr, float)

    # 4) promotion -> immutable registry
    registry = PromotionRegistry(tmp_path / "promotion_registry.json")
    decision = assess_promotion("Information Technology", dsr, synthetic_sr)
    registry.record(
        decision, model_path=str(candidate_path) if decision.promoted else None
    )
    assert len(registry.promotions) == 1
    assert (tmp_path / "promotion_registry.json").exists()

```

---

### File: `new_pipeline/tests/integration/test_vault_flow.py`

```py
from pathlib import Path

from new_pipeline.config import reload_config
from new_pipeline.data.vaults import VaultManager


def test_vault_manager_creates_paths(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("QA_DATA__RAW_VAULT_DIR", str(tmp_path / "raw"))
    monkeypatch.setenv("QA_DATA__PROCESSED_VAULT_DIR", str(tmp_path / "processed"))
    reload_config()

    manager = VaultManager()
    raw, processed = manager.ensure_vaults()

    assert raw == tmp_path / "raw"
    assert processed == tmp_path / "processed"
    assert raw.exists()
    assert processed.exists()

```

---

### File: `new_pipeline/tests/fixtures/sample_data.py`

```py
import pandas as pd


def make_sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=5, freq="D"),
        "close": [100.0, 101.0, 99.5, 102.0, 103.5],
        "high": [101.0, 102.0, 100.5, 103.0, 104.0],
        "low": [99.0, 100.0, 98.5, 101.0, 102.5],
        "volume": [1000, 1100, 950, 1200, 1300],
    })

```

---

### File: `new_pipeline/tests/fixtures/__init__.py`

```py

```

---

### File: `new_pipeline/tests/fixtures/config_fixtures.py`

```py
from new_pipeline.config import get_config


def config_fixture():
    return get_config()

```

---

### File: `new_pipeline/analysis/__init__.py`

```py
from .backtest import BacktestResult, backtest_ticker, plot_backtest

__all__ = ["BacktestResult", "backtest_ticker", "plot_backtest"]

```

---

### File: `new_pipeline/analysis/backtest.py`

```py
"""Single-ticker backtest + performance visualization (research tool).

Pulls daily bars from any ``MarketDataSource`` (live Alpaca or the offline
fake), computes the production features, trains an *out-of-sample* XGBoost
signal (train on the first ``train_frac``, evaluate on the rest), and realizes
t+1 risk-managed returns with the same simulator the tournament uses.
``plot_backtest`` renders an equity-curve + drawdown PNG (matplotlib, a dev dep).
"""

from dataclasses import dataclass
from datetime import date

import numpy as np
import polars as pl

from new_pipeline.config import get_config
from new_pipeline.features.labels import add_labels
from new_pipeline.features.polars_engine import compile_features
from new_pipeline.tournament.simulator import sharpe_ratio, simulate_t1_returns
from new_pipeline.tournament.trainer import predict_proba, train_booster

FEATURE_COLS = [
    "returns", "atr", "adv_20", "volatility", "spread_pct", "roll_spread",
    "amihud", "ncskew", "duvol",
]
_MIN_ROWS = 20


@dataclass
class BacktestResult:
    symbol: str
    start: date
    end: date
    returns: np.ndarray
    equity_curve: np.ndarray
    sharpe: float
    total_return: float
    max_drawdown: float
    win_rate: float
    n_trades: int
    n_test_bars: int


def backtest_ticker(
    symbol, start, end, source, cfg=None, train_frac: float = 0.7
) -> BacktestResult:
    """Out-of-sample t+1 backtest of the XGBoost signal on a single ticker."""
    cfg = cfg or get_config()
    bars = source.history(symbol, start, end)
    if len(bars) < _MIN_ROWS:
        return _empty_result(symbol, start, end)

    frame = pl.DataFrame(
        [
            {
                "date": bar.day, "ticker": symbol, "open": bar.open, "high": bar.high,
                "low": bar.low, "close": bar.close, "volume": bar.volume,
            }
            for bar in bars
        ]
    )
    feats = add_labels(
        compile_features(frame), cfg.features.label_horizon, cfg.features.label_cost_bps
    )
    required = [*FEATURE_COLS, "target_label", "close", "low", "atr"]
    clean = feats.with_columns(pl.col(required).fill_nan(None)).drop_nulls(subset=required)
    if clean.height < _MIN_ROWS:
        return _empty_result(symbol, start, end)

    split = max(int(clean.height * train_frac), 10)
    features = clean.select(FEATURE_COLS).to_numpy()
    labels = clean["target_label"].to_numpy().astype(np.float64)
    booster = train_booster(
        features[:split], labels[:split],
        num_boost_round=cfg.tournament.num_boost_round,
        penalty_fp=cfg.tournament.penalty_fp, penalty_fn=cfg.tournament.penalty_fn,
    )
    proba = predict_proba(booster, features[split:])
    signals = (proba > cfg.execution.confidence_threshold).astype(np.int64)
    prices = {c: clean[c].to_numpy().astype(np.float64)[split:] for c in ("close", "low", "atr")}
    returns = simulate_t1_returns(
        signals, prices["close"], prices["low"], prices["atr"],
        cfg.execution.atr_stop_multiplier, cfg.execution.max_risk_per_trade,
    )
    return _summarize(symbol, start, end, returns, int(signals.sum()))


def _summarize(symbol, start, end, returns, n_trades) -> BacktestResult:
    equity = np.cumprod(1.0 + returns) if returns.size else np.ones(1)
    peak = np.maximum.accumulate(equity)
    drawdown = equity / peak - 1.0
    nonzero = returns[returns != 0.0]
    win_rate = float((nonzero > 0).mean()) if nonzero.size else 0.0
    return BacktestResult(
        symbol=symbol, start=start, end=end, returns=returns, equity_curve=equity,
        sharpe=sharpe_ratio(returns), total_return=float(equity[-1] - 1.0),
        max_drawdown=float(drawdown.min()) if drawdown.size else 0.0,
        win_rate=win_rate, n_trades=n_trades, n_test_bars=int(returns.size),
    )


def _empty_result(symbol, start, end) -> BacktestResult:
    return BacktestResult(symbol, start, end, np.zeros(0), np.ones(1), 0.0, 0.0, 0.0, 0.0, 0, 0)


def plot_backtest(result: BacktestResult, path, subtitle: str = "") -> str:  # pragma: no cover
    """Render an equity-curve + drawdown PNG. Matplotlib is a dev/analysis dep."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    equity = result.equity_curve
    peak = np.maximum.accumulate(equity)
    drawdown = equity / peak - 1.0
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]}
    )
    ax1.plot(equity, color="#1f77b4", linewidth=1.5)
    ax1.axhline(1.0, color="gray", linestyle="--", linewidth=0.8)
    ax1.set_title(
        f"{result.symbol}  |  return {result.total_return:+.1%}   Sharpe {result.sharpe:.2f}   "
        f"maxDD {result.max_drawdown:.1%}   trades {result.n_trades}   "
        f"win {result.win_rate:.0%}"
    )
    ax1.set_ylabel("Equity (×)")
    ax1.grid(alpha=0.3)
    ax2.fill_between(range(len(drawdown)), drawdown, color="#d62728", alpha=0.4)
    ax2.set_ylabel("Drawdown")
    ax2.set_xlabel("Out-of-sample bar")
    ax2.grid(alpha=0.3)
    if subtitle:
        fig.text(0.5, 0.01, subtitle, ha="center", fontsize=8, color="gray")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return str(path)

```

---

### File: `new_pipeline/hardening/README.md`

```markdown
# Quantum Avenger — Production Hardening (Phase 7)

Operational artifacts for building, shipping, observing, and recovering the system.

## Layout
- `docker/` — `Dockerfile.{app,dashboard,mcp}` + `docker-compose.yml` (local prod-like stack).
- `k8s/` — `deployment.yaml` (app / dashboard / mcp), `service.yaml`, `configmap.yaml`.
- `observability/` — `prometheus.yml` scrape config + `alert_rules.yml`.
- `docs/` — deployment, recovery, and security guides.

CI lives at `.github/workflows/ci.yml`: ruff + the offline test suite with a **≥85% coverage gate** (`NUMBA_DISABLE_JIT=1` so the `@njit` kernels are traced).

## Quickstart (from the repo root)
```
make install      # runtime + dev deps
make lint test    # ruff + tests
make coverage     # tests + the >=85% gate
make docker       # build all three images
make compose-up   # run the stack locally
```

## Metrics
`new_pipeline.monitoring.telemetry.render_prometheus` emits Prometheus text
exposition (gauges prefixed `quantum_avenger_`). Prometheus scrapes it and
`alert_rules.yml` fires on veto-rate, drawdown, DSR, and latency breaches.

## Scope notes
Dockerfiles, K8s manifests, and the Prometheus/alert configs are
deployment-ready templates; cloud-specific IaC (Terraform), ingress/HPA, and a
full chaos-test suite are the natural follow-ons (see `docs/DEPLOYMENT.md`).
The MCP image runs the offline tool-inventory entrypoint; the live FastMCP
stdio server is wired at the live cutover.

```

---

### File: `new_pipeline/hardening/observability/grafana_dashboard.json`

```json
{
  "title": "Quantum Avenger",
  "schemaVersion": 39,
  "editable": true,
  "panels": [
    {
      "id": 1,
      "title": "Veto rate",
      "type": "timeseries",
      "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0},
      "targets": [{"expr": "quantum_avenger_veto_rate", "refId": "A"}]
    },
    {
      "id": 2,
      "title": "Max drawdown",
      "type": "timeseries",
      "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0},
      "targets": [{"expr": "quantum_avenger_max_drawdown", "refId": "A"}]
    },
    {
      "id": 3,
      "title": "Deflated Sharpe",
      "type": "stat",
      "gridPos": {"h": 8, "w": 12, "x": 0, "y": 8},
      "targets": [{"expr": "quantum_avenger_dsr_value", "refId": "A"}]
    },
    {
      "id": 4,
      "title": "Execution latency (ms)",
      "type": "timeseries",
      "gridPos": {"h": 8, "w": 12, "x": 12, "y": 8},
      "targets": [{"expr": "quantum_avenger_execution_latency_ms", "refId": "A"}]
    }
  ]
}

```

---

### File: `new_pipeline/hardening/observability/alert_rules.yml`

```yaml
groups:
  - name: quantum_avenger
    rules:
      - alert: HighVetoRate
        expr: quantum_avenger_veto_rate > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Veto rate above 50% for 5 minutes"
      - alert: HighDrawdown
        expr: quantum_avenger_max_drawdown < -0.15
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Max drawdown breached the -15% limit"
      - alert: LowDeflatedSharpe
        expr: quantum_avenger_dsr_value < 0.95
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Champion Deflated Sharpe below the 0.95 promotion threshold"
      - alert: HighExecutionLatency
        expr: quantum_avenger_execution_latency_ms > 200
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Order execution latency above 200ms"

```

---

### File: `new_pipeline/hardening/observability/prometheus.yml`

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - alert_rules.yml

scrape_configs:
  - job_name: quantum-avenger-app
    static_configs:
      - targets: ["app:9090"]
  - job_name: quantum-avenger-dashboard
    static_configs:
      - targets: ["dashboard:8501"]

```

---

### File: `new_pipeline/hardening/docs/RECOVERY.md`

```markdown
# Recovery Playbook

## Resilience built in
- **Circuit breaker** (`core/circuit_breaker.py`) around flaky externals (LLM,
  broker, market data) — fails fast, half-opens after the recovery window.
- **Retries with backoff** (`utils/retry.py`) for transient blips.
- **Shield Agent veto** — no trade ever bypasses the deterministic risk gates.

## Common incidents
| Symptom | Action |
|---------|--------|
| Bad deploy | `kubectl rollout undo deployment/<name>` |
| External dependency down | breaker opens automatically; verify endpoint, then it half-opens |
| HighDrawdown / HighVetoRate alert | inspect the veto ledger + dashboard; halt new entries if breaching risk limits |
| Champion misbehaving | revert `active_champions` in the promotion registry to the prior model_path |

## State & backups
- **Promotion registry** (`models/prod/promotion_registry.json`) — append-only;
  back up before each promotion run.
- **Veto ledger / trade log** (Parquet) — append-only audit trail; snapshot regularly.
- Models are immutable artifacts keyed by version; re-promote from candidates if lost.

## Smoke test after recovery
```
python -m new_pipeline.scripts.check_health
make coverage
```

```

---

### File: `new_pipeline/hardening/docs/DEPLOYMENT.md`

```markdown
# Deployment Guide

## 1. Build & test
```
make lint coverage          # ruff + tests + >=85% coverage gate
make docker                 # build app / dashboard / mcp images
```

## 2. Push images
```
docker tag quantum-avenger-app   <registry>/quantum-avenger-app:<tag>
docker push <registry>/quantum-avenger-app:<tag>     # repeat for dashboard, mcp
```

## 3. Configure
- Non-secret config: `k8s/configmap.yaml` (`QA_ENV=production`, worker counts).
- Secrets (Alpaca / Ollama): create a Kubernetes `Secret` and mount it with
  `envFrom.secretRef`, using the `QA_` env-var override convention
  (e.g. `QA_FUSION__OLLAMA_ENDPOINT`, `QA_ALPACA__API_KEY`). **Never commit secrets.**

## 4. Deploy (Kubernetes)
```
kubectl apply -f new_pipeline/hardening/k8s/configmap.yaml
kubectl apply -f new_pipeline/hardening/k8s/deployment.yaml
kubectl apply -f new_pipeline/hardening/k8s/service.yaml
```
Update the `image:` fields to your registry tags first. The trainer/feature
workloads target a GPU node pool (`device='cuda'`); the dashboard and MCP run
CPU-only.

## 5. Observe
Point Prometheus at `observability/prometheus.yml` and load `alert_rules.yml`.

## Follow-ons
Terraform for cloud infra, an ingress + HorizontalPodAutoscaler, and a chaos /
load-test suite are the remaining production extensions.

```

---

### File: `new_pipeline/hardening/docs/SECURITY.md`

```markdown
# Security Guide

## Secrets
- Alpaca / Ollama credentials are injected only as `QA_`-prefixed env vars
  (`config/production.py`), sourced from a Kubernetes `Secret` / secrets manager.
- Never committed: no keys in the repo, configmaps, or images. Dev/test use the
  deterministic fakes, so no real credentials are needed offline.

## Containers
- All images run as a non-root user (uid 10001).
- Minimal `python:3.11-slim` base; `.dockerignore` excludes tests, docs, and
  caches from the build context.

## Determinism & isolation
- The LLM performs **no math** — every quantity flows through the deterministic
  MCP tools / Shield Agent (G1), bounding the blast radius of model misbehavior.
- `reference_code/` is read-only (enforced by a project `Edit`/`Write` deny rule).

## Supply chain
- Pin and scan dependencies (Dependabot / `pip-audit`) in CI.
- Coverage + lint gates block merges; the offline test suite needs no network.

## Audit
- The append-only veto ledger and trade log are the immutable record of every
  decision (executed or vetoed) with its gate and reason.

```

---

### File: `new_pipeline/hardening/chaos/scenarios.md`

```markdown
# Chaos & Load Scenarios (Phase 7)

Resilience checks for the deployed system. `load_test.py` is the offline perf
smoke; the scenarios below target the live cluster (run against staging).

## Load
- `PYTHONPATH=. python new_pipeline/hardening/chaos/load_test.py --iters 200000` — hot-path throughput baseline.
- k6 / locust against the dashboard `/` and the MCP server under sustained RPS.

## Chaos (observe alerts + recovery)
| Scenario | Inject | Expected |
|----------|--------|----------|
| Dependency down | Block egress to Ollama / Alpaca | Circuit breaker opens, half-opens after `recovery_timeout`, no crash |
| Pod eviction | `kubectl delete pod` | Deployment reschedules; readiness/liveness probes gate traffic |
| Network partition | Drop traffic to a service | Retries with backoff; `HighExecutionLatency` alert fires |
| Disk pressure | Fill the ledger volume | Writes fail gracefully; alert fires; append-only ledgers stay intact |

## Recovery
Follow `docs/RECOVERY.md` — rollback, restore the promotion registry, re-promote from candidates.

```

---

### File: `new_pipeline/hardening/chaos/load_test.py`

```py
"""Offline micro load / chaos harness (Phase 7).

Drives the hot deterministic paths (Shield veto gates, t+1 simulation) under a
fixed budget to give a throughput baseline — a CI-friendly perf smoke, not a
substitute for k6/locust against the live services.

Run:  PYTHONPATH=. python new_pipeline/hardening/chaos/load_test.py --iters 100000
"""

import argparse
import time

import numpy as np
from new_pipeline.features.shields import evaluate_risk_veto_gates
from new_pipeline.tournament.simulator import simulate_t1_returns


def bench_shield(iters: int) -> float:
    start = time.perf_counter()
    for _ in range(iters):
        evaluate_risk_veto_gates(100.0, 1.0, 2.0, 100000.0, 0.02, 0.0, 5e6, 5e6, 0.02)
    return iters / (time.perf_counter() - start)


def bench_simulator(n: int) -> float:
    rng = np.random.default_rng(0)
    close = 100.0 + np.cumsum(rng.normal(0, 1, n))
    signals = rng.integers(0, 2, n).astype(np.int64)
    start = time.perf_counter()
    simulate_t1_returns(signals, close, close - 1.0, np.ones(n), 2.0, 0.02)
    return n / (time.perf_counter() - start)


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum Avenger load/chaos harness")
    parser.add_argument("--iters", type=int, default=100_000)
    args = parser.parse_args()
    print(f"shield:    {bench_shield(args.iters):,.0f} evals/sec")
    print(f"simulator: {bench_simulator(args.iters):,.0f} bars/sec")


if __name__ == "__main__":
    main()

```

---

### File: `new_pipeline/hardening/docker/docker-compose.yml`

```yaml
# Local prod-like stack. Run from this directory: docker compose up --build
# (build context is the repo root so the images can COPY new_pipeline/).
services:
  app:
    build:
      context: ../../..
      dockerfile: new_pipeline/hardening/docker/Dockerfile.app
    image: quantum-avenger-app
    environment:
      QA_ENV: production
    command: ["health"]

  dashboard:
    build:
      context: ../../..
      dockerfile: new_pipeline/hardening/docker/Dockerfile.dashboard
    image: quantum-avenger-dashboard
    environment:
      QA_ENV: production
    ports:
      - "8501:8501"

  mcp:
    build:
      context: ../../..
      dockerfile: new_pipeline/hardening/docker/Dockerfile.mcp
    image: quantum-avenger-mcp
    environment:
      QA_ENV: production

```

---

### File: `new_pipeline/hardening/k8s/secrets.yaml`

```yaml
# TEMPLATE ONLY — do NOT commit real secrets. Populate from a secrets manager,
# Sealed Secrets, or `kubectl create secret`. Values here are placeholders.
apiVersion: v1
kind: Secret
metadata:
  name: quantum-avenger-secrets
type: Opaque
stringData:
  QA_ALPACA__API_KEY: "REPLACE_ME"
  QA_ALPACA__SECRET_KEY: "REPLACE_ME"
  QA_FUSION__OLLAMA_ENDPOINT: "http://ollama:11434"
  DASHBOARD_USER: "REPLACE_ME"
  DASHBOARD_PASS: "REPLACE_ME"

```

---

### File: `new_pipeline/hardening/k8s/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: quantum-avenger-dashboard
  labels: {app: quantum-avenger, component: dashboard}
spec:
  type: LoadBalancer
  selector: {app: quantum-avenger, component: dashboard}
  ports:
    - port: 80
      targetPort: 8501

```

---

### File: `new_pipeline/hardening/k8s/networkpolicy.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: quantum-avenger-default-deny
spec:
  podSelector:
    matchLabels:
      app: quantum-avenger
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - podSelector:
            matchLabels:
              app: quantum-avenger
  egress:
    # Allow DNS; tighten the rest to the Alpaca / Ollama endpoints in production.
    - ports:
        - port: 53
          protocol: UDP
        - port: 53
          protocol: TCP
    - to:
        - podSelector:
            matchLabels:
              app: quantum-avenger

```

---

### File: `new_pipeline/hardening/k8s/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quantum-avenger-app
  labels: {app: quantum-avenger, component: app}
spec:
  replicas: 1
  selector:
    matchLabels: {app: quantum-avenger, component: app}
  template:
    metadata:
      labels: {app: quantum-avenger, component: app}
    spec:
      securityContext: {runAsNonRoot: true, runAsUser: 10001}
      containers:
        - name: app
          image: quantum-avenger-app:latest
          args: ["health"]
          envFrom:
            - configMapRef: {name: quantum-avenger-config}
          resources:
            requests: {cpu: "250m", memory: "512Mi"}
            limits: {cpu: "1", memory: "2Gi"}
          livenessProbe:
            exec:
              command: ["python", "-m", "new_pipeline.scripts.check_health"]
            initialDelaySeconds: 10
            periodSeconds: 30
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quantum-avenger-dashboard
  labels: {app: quantum-avenger, component: dashboard}
spec:
  replicas: 1
  selector:
    matchLabels: {app: quantum-avenger, component: dashboard}
  template:
    metadata:
      labels: {app: quantum-avenger, component: dashboard}
    spec:
      securityContext: {runAsNonRoot: true, runAsUser: 10001}
      containers:
        - name: dashboard
          image: quantum-avenger-dashboard:latest
          ports:
            - containerPort: 8501
          envFrom:
            - configMapRef: {name: quantum-avenger-config}
          resources:
            requests: {cpu: "250m", memory: "512Mi"}
            limits: {cpu: "1", memory: "1Gi"}
          readinessProbe:
            httpGet: {path: /_stcore/health, port: 8501}
            initialDelaySeconds: 10
            periodSeconds: 15
          livenessProbe:
            httpGet: {path: /_stcore/health, port: 8501}
            initialDelaySeconds: 20
            periodSeconds: 30
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quantum-avenger-mcp
  labels: {app: quantum-avenger, component: mcp}
spec:
  replicas: 1
  selector:
    matchLabels: {app: quantum-avenger, component: mcp}
  template:
    metadata:
      labels: {app: quantum-avenger, component: mcp}
    spec:
      securityContext: {runAsNonRoot: true, runAsUser: 10001}
      containers:
        - name: mcp
          image: quantum-avenger-mcp:latest
          envFrom:
            - configMapRef: {name: quantum-avenger-config}
          resources:
            requests: {cpu: "100m", memory: "256Mi"}
            limits: {cpu: "500m", memory: "512Mi"}

```

---

### File: `new_pipeline/hardening/k8s/ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: quantum-avenger
  annotations:
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  tls:
    - hosts: ["dashboard.quantum-avenger.example.com"]
      secretName: quantum-avenger-tls
  rules:
    - host: dashboard.quantum-avenger.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: quantum-avenger-dashboard
                port:
                  number: 80

```

---

### File: `new_pipeline/hardening/k8s/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: quantum-avenger-config
data:
  QA_ENV: "production"
  QA_SYSTEM__NUM_WORKERS: "4"
# Secrets (Alpaca / Ollama credentials) are NOT stored here. Provide them via a
# Kubernetes Secret consumed with envFrom.secretRef and the QA_ env-var override
# convention, e.g. QA_FUSION__OLLAMA_ENDPOINT, QA_ALPACA__API_KEY.

```

---

### File: `new_pipeline/hardening/k8s/hpa.yaml`

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: quantum-avenger-app
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: quantum-avenger-app
  minReplicas: 1
  maxReplicas: 6
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70

```

---

### File: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r new_pipeline/requirements.txt -r new_pipeline/requirements-dev.txt
      - name: Lint (ruff)
        run: ruff check new_pipeline
      - name: Tests + coverage gate (>=85%)
        env:
          PYTHONPATH: ${{ github.workspace }}
          NUMBA_DISABLE_JIT: "1"  # let coverage trace the @njit kernels
        run: >-
          pytest new_pipeline/tests
          --cov=new_pipeline --cov-report=term-missing --cov-fail-under=85

```

---

### File: `docs/ARCHITECTURE_ROADMAP.md`

```markdown
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

```

---

### File: `docs/PHASE_1_SPECIFICATION.md`

```markdown
# Phase 1: Core Pipeline Infrastructure - Detailed Specification

**Duration**: 2 weeks  
**Target Date**: Complete by end of June 1 (if sprint-based), or establish baseline by mid-June  
**Success Criteria**: Modular foundation ready for feature engineering layer; all tests passing; logging/config infrastructure validated

---

## 1. Folder Structure & Module Organization

### 1.1 Directory Tree

```
/workspaces/Quantum_Avenger/new_pipeline/
│
├── README.md                           # Project overview, quick-start guide
├── requirements.txt                    # Phase 1 dependencies only
├── setup.py                            # Package installation script
├── pyproject.toml                      # Modern Python packaging config
│
├── config/                             # Configuration management
│   ├── __init__.py
│   ├── base.py                         # BaseConfig class
│   ├── development.py                  # Dev-specific overrides
│   ├── production.py                   # Prod-specific overrides
│   ├── testing.py                      # Test-specific overrides
│   ├── schema.py                       # Pydantic validation schemas
│   └── defaults.yaml                   # Default values (YAML)
│
├── core/                               # Core infrastructure modules
│   ├── __init__.py
│   ├── logging.py                      # Centralized logging setup
│   ├── exceptions.py                   # Custom exception hierarchy
│   ├── constants.py                    # System-wide constants
│   └── paths.py                        # Path management utilities
│
├── data/                               # Data layer (Phase 1: structure only)
│   ├── __init__.py
│   ├── base.py                         # Abstract base data handler
│   ├── ingestion.py                    # Data ingestion patterns
│   ├── vaults.py                       # Vault path management
│   └── validation.py                   # Data quality checks
│
├── features/                           # Feature layer (Phase 1: structure only)
│   ├── __init__.py
│   ├── base.py                         # Abstract feature engine
│   └── registry.py                     # Feature metadata registry
│
├── models/                             # Model layer (Phase 1: structure only)
│   ├── __init__.py
│   ├── registry.py                     # Model artifact management
│   └── metadata.py                     # Model metadata tracking
│
├── execution/                          # Execution layer (Phase 1: structure only)
│   ├── __init__.py
│   ├── risk.py                         # Risk manager interface
│   └── broker.py                       # Broker adapter pattern
│
├── monitoring/                         # Monitoring & observability
│   ├── __init__.py
│   ├── metrics.py                      # Metrics collection
│   ├── telemetry.py                    # Telemetry exporter
│   └── health.py                       # Health check endpoints
│
├── utils/                              # Utility functions
│   ├── __init__.py
│   ├── decorators.py                   # Reusable decorators
│   ├── retry.py                        # Retry logic & circuit breakers
│   ├── serialization.py                # JSON/Pickle helpers
│   └── time.py                         # Time utilities
│
├── tests/                              # Test suite
│   ├── __init__.py
│   ├── conftest.py                     # Pytest fixtures
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── test_config.py
│   │   ├── test_logging.py
│   │   ├── test_exceptions.py
│   │   └── test_retry.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_vault_flow.py          # End-to-end vault creation
│   └── fixtures/
│       ├── __init__.py
│       ├── sample_data.py              # Mock data generators
│       └── config_fixtures.py          # Config test utilities
│
├── scripts/                            # Standalone scripts
│   ├── init_environment.sh             # Environment setup
│   ├── run_tests.sh                    # Test runner
│   └── check_health.py                 # System health diagnostics
│
└── docs/                               # Phase 1 documentation
    ├── ARCHITECTURE.md                 # High-level design decisions
    ├── CONFIG_GUIDE.md                 # Configuration management guide
    ├── LOGGING_GUIDE.md                # Logging patterns
    ├── ERROR_HANDLING.md               # Error handling strategies
    ├── TESTING_GUIDE.md                # Testing conventions
    └── API_REFERENCE.md                # Core module APIs
```

### 1.2 Folder Responsibilities

| Folder | Purpose | Key Files | Depends On |
|--------|---------|-----------|-----------|
| **config/** | Global configuration, environment overrides, validation | base.py, schema.py, defaults.yaml | None |
| **core/** | Shared infrastructure (logging, exceptions, constants) | logging.py, exceptions.py | config/ |
| **data/** | Data ingestion abstractions & vault management | ingestion.py, vaults.py, validation.py | core/ |
| **features/** | Feature engineering interfaces & registry | base.py, registry.py | data/, core/ |
| **models/** | Model artifact storage & metadata | registry.py, metadata.py | core/ |
| **execution/** | Risk management & broker integration | risk.py, broker.py | models/, core/ |
| **monitoring/** | Metrics, telemetry, health checks | metrics.py, telemetry.py | core/ |
| **utils/** | Decorators, retry logic, serialization | decorators.py, retry.py | core/ |
| **tests/** | Pytest suite with fixtures | conftest.py, unit/*, integration/* | All modules |

---

## 2. Configuration Management System

### 2.1 Configuration Architecture

**Principle**: Single source of truth for all settings; environment-specific overrides; validation via Pydantic.

```
┌─────────────────────────────────────────────────┐
│  Environment Variables (.env or shell export)  │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│  schema.py (Pydantic BaseModel validation)     │
│  - Type-safe parsing                           │
│  - Required vs optional fields                 │
│  - Range/regex validation                      │
└────────────────────┬────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼────┐  ┌──────▼──────┐  ┌─────▼──────┐
│ base.py │  │  dev.py     │  │  prod.py   │
│         │  │  test.py    │  │            │
│ Defaults│  │ Overrides   │  │ Overrides  │
└────┬────┘  └──────┬──────┘  └─────┬──────┘
     │               │               │
     └───────────────┴───────────────┘
                     │
         ┌───────────▼───────────┐
         │  ConfigManager        │
         │  (Singleton Pattern)  │
         └───────────────────────┘
                     │
        Used by all modules via:
        from config import get_config()
```

### 2.2 Key Configuration Files

**File: `config/schema.py`**
```
Pydantic models:
- AppConfig (root)
  ├── data: DataConfig
  │   ├── raw_vault_dir: str
  │   ├── processed_vault_dir: str
  │   ├── parquet_blocksize: str (64MiB, 128MiB, 256MiB)
  │   ├── row_group_size: int
  │   └── validation_mode: str (strict, warn, skip)
  ├── features: FeatureConfig
  │   ├── cache_enabled: bool
  │   ├── gpu_enabled: bool
  │   └── batch_size: int
  ├── models: ModelConfig
  │   ├── prod_models_dir: str
  │   ├── candidate_models_dir: str
  │   └── model_version: str
  ├── execution: ExecutionConfig
  │   ├── max_risk_per_trade: float (e.g., 0.02)
  │   ├── atr_stop_multiplier: float (e.g., 2.0)
  │   └── confidence_threshold: float (e.g., 0.65)
  ├── logging: LoggingConfig
  │   ├── level: str (DEBUG, INFO, WARNING, ERROR)
  │   ├── format: str
  │   ├── log_file: str
  │   └── max_bytes: int (rotation size)
  ├── fusion: FusionConfig
  │   ├── enabled: bool
  │   ├── ollama_endpoint: str
  │   ├── llm_model_name: str
  │   ├── sentiment_timeout: float (seconds)
  │   └── semaphore_limit: int (default 20)
  └── system: SystemConfig
      ├── run_mode: str (backtest, evaluate, live)
      ├── dask_enabled: bool
      ├── num_workers: int
      └── memory_limit: str
```

**File: `config/base.py`**
- `BaseConfig` class using Pydantic
- Loads from YAML defaults
- Overrides via environment variables
- Validation on initialization
- Context manager for temporary overrides

**File: `config/defaults.yaml`**
```yaml
data:
  raw_vault_dir: "./data/raw"
  processed_vault_dir: "./data/processed"
  parquet_blocksize: "128MiB"
  row_group_size: 100000

features:
  cache_enabled: true
  gpu_enabled: true

logging:
  level: "INFO"
  log_file: "./logs/system.log"
  max_bytes: 10485760  # 10MB

execution:
  max_risk_per_trade: 0.02
  atr_stop_multiplier: 2.0

fusion:
  enabled: false
  ollama_endpoint: "http://localhost:11434"
  sentiment_timeout: 5.0
```

### 2.3 Configuration Usage Pattern

```python
# Anywhere in the codebase:
from config import get_config

config = get_config()

# Type-safe access:
raw_vault = config.data.raw_vault_dir
max_risk = config.execution.max_risk_per_trade
log_level = config.logging.level

# For testing (temporary override):
with config.override(data__raw_vault_dir="/tmp/test_data"):
    # Temporarily use test data
    pass
```

### 2.4 Environment Variable Naming Convention

```
QA_DATA__RAW_VAULT_DIR=/custom/path
QA_LOGGING__LEVEL=DEBUG
QA_EXECUTION__MAX_RISK_PER_TRADE=0.01
QA_FUSION__ENABLED=true
```

---

## 3. Centralized Logging & Monitoring

### 3.1 Logging Architecture

**Principle**: Single logger instance; structured logging; context propagation; separate log files per layer.

**File: `core/logging.py`**

```
Components:
1. LoggerFactory
   ├── get_logger(name: str) → Logger
   ├── configure(config: LoggingConfig)
   └── reset()

2. Formatters
   ├── StructuredFormatter (JSON output for parsing)
   └── HumanFormatter (readable console output)

3. Handlers
   ├── FileHandler (main system.log)
   ├── RotatingFileHandler (daily rotation)
   ├── StreamHandler (console stderr)
   └── BufferingHandler (for async shipping to telemetry)

4. Context Managers
   ├── log_context() → capture function name, module
   ├── timer() → measure execution time
   └── trace_calls() → log entry/exit
```

### 3.2 Log Levels & Usage

| Level | When | Example |
|-------|------|---------|
| DEBUG | Development, detailed state | Feature computation internals |
| INFO | Milestone events | Tournament fold completed, model promoted |
| WARNING | Recoverable issues | Failed API call, retry attempt |
| ERROR | Significant failures | Invalid configuration, data corruption |
| CRITICAL | System-level failures | OOM, unrecoverable crash |

### 3.3 Structured Logging Format

```json
{
  "timestamp": "2026-06-01T14:32:15.123Z",
  "level": "INFO",
  "logger": "data_ingestion",
  "message": "Vault ingestion completed",
  "module": "data_ingestion.py",
  "line_number": 142,
  "function": "build_raw_vault",
  "context": {
    "sector": "Technology",
    "tickers_processed": 47,
    "success_count": 45,
    "duration_seconds": 23.5
  },
  "trace_id": "a1b2c3d4-e5f6-4789-abcd-ef1234567890"
}
```

### 3.4 Monitoring Integration

**File: `monitoring/metrics.py`**
- Counter: API calls, trades executed, veto rejections
- Gauge: Current portfolio value, open positions
- Histogram: Execution latency, position size distribution
- Summary: Drawdown duration

**File: `monitoring/health.py`**
- Health check endpoints
- Vault existence validation
- Configuration validation
- Dependencies availability (Ollama, Alpaca)

---

## 4. Error Handling & Resilience Patterns

### 4.1 Custom Exception Hierarchy

**File: `core/exceptions.py`**

```
QuantumAvengersException (Base)
├── ConfigurationError
│   ├── MissingConfigError
│   ├── InvalidConfigError
│   └── ConfigValidationError
├── DataError
│   ├── VaultNotFoundError
│   ├── DataCorruptionError
│   ├── InsufficientDataError
│   └── DataQualityError
├── FeatureError
│   ├── FeatureComputationError
│   ├── CUDAOutOfMemoryError
│   └── FeatureCacheError
├── ModelError
│   ├── ModelLoadError
│   ├── ModelInferenceError
│   └── ModelPromotionError
├── ExecutionError
│   ├── RiskVetoError
│   ├── OrderSubmissionError
│   ├── PortfolioSyncError
│   └── BrokerConnectionError
└── ExternalServiceError
    ├── OllamaTimeoutError
    ├── OllamaConnectionError
    ├── AlpacaAPIError
    └── YFinanceError
```

### 4.2 Retry Strategy with Circuit Breaker

**File: `utils/retry.py`**

```python
@retry(
    max_attempts=3,
    backoff_factor=2.0,        # Exponential: 1s, 2s, 4s
    jitter=True,
    exceptions=(AlpacaAPIError, ConnectionError),
    on_retry=lambda attempt, error: logger.warning(...)
)
def call_alpaca_api():
    pass

@circuit_breaker(
    failure_threshold=5,       # Trip after 5 failures
    recovery_timeout=60,       # Attempt recovery after 60s
    expected_exception=ExternalServiceError
)
def fetch_live_sentiment(ticker):
    pass
```

### 4.3 Error Handling Patterns

**Pattern 1: Graceful Degradation**
```python
try:
    sentiment = fetch_sentiment_async(headline)
except OllamaTimeoutError:
    logger.warning(f"LLM timeout, defaulting to neutral sentiment")
    sentiment = 0.0  # Neutral fallback
```

**Pattern 2: Early Validation**
```python
try:
    config = AppConfig.parse_obj(raw_config)
except ValidationError as e:
    raise ConfigValidationError(f"Invalid configuration: {e.json()}")
```

**Pattern 3: Resource Cleanup**
```python
try:
    client = Alpaca(api_key, secret_key)
    execute_trades(client)
finally:
    client.close()  # Always cleanup
```

### 4.4 Veto Ledger for Execution Errors

When `evaluate_risk_veto_gates()` rejects a trade, log:
```json
{
  "timestamp": "2026-06-01T14:32:15Z",
  "ticker": "NVDA",
  "veto_reason": "insufficient_liquidity",
  "details": {
    "order_size": 100,
    "adv_20": 85,
    "coverage_percent": 117.6
  },
  "signal_probability": 0.78,
  "market_price": 145.30
}
```

---

## 5. Testing Framework & Unit Test Structure

### 5.1 Testing Strategy

**Coverage Goals**:
- Unit: 85%+ of core modules
- Integration: All data flow paths
- System: End-to-end vault creation + configuration

**Test Types**:

| Type | Scope | Tools | Location |
|------|-------|-------|----------|
| Unit | Individual function | pytest, unittest.mock | tests/unit/ |
| Integration | Multi-module flow | pytest, fixtures | tests/integration/ |
| Fixture | Reusable test data | pytest conftest | tests/fixtures/ |

### 5.2 Pytest Configuration

**File: `tests/conftest.py`**

```python
@pytest.fixture
def config_test():
    """Returns test-mode AppConfig."""
    return AppConfig.from_env(mode="testing")

@pytest.fixture
def temp_vault(tmp_path):
    """Creates temporary data vaults."""
    raw = tmp_path / "raw"
    processed = tmp_path / "processed"
    raw.mkdir()
    processed.mkdir()
    return {"raw": str(raw), "processed": str(processed)}

@pytest.fixture
def sample_ohlcv():
    """Generates sample OHLCV data."""
    dates = pd.date_range("2023-01-01", periods=252)
    return pd.DataFrame({
        "date": dates,
        "open": np.random.randn(252).cumsum() + 100,
        "high": np.random.randn(252).cumsum() + 102,
        "low": np.random.randn(252).cumsum() + 98,
        "close": np.random.randn(252).cumsum() + 100,
        "volume": np.random.randint(1e6, 1e7, 252),
        "ticker": "TEST"
    })

@pytest.fixture
def mock_alpaca_client(mocker):
    """Mocks Alpaca API client."""
    return mocker.MagicMock(spec=TradingClient)
```

### 5.3 Sample Unit Tests

**File: `tests/unit/test_config.py`**

```python
def test_config_from_env_override(monkeypatch):
    monkeypatch.setenv("QA_EXECUTION__MAX_RISK_PER_TRADE", "0.05")
    config = AppConfig.from_env()
    assert config.execution.max_risk_per_trade == 0.05

def test_config_validation_fails_on_invalid_level(monkeypatch):
    monkeypatch.setenv("QA_LOGGING__LEVEL", "INVALID")
    with pytest.raises(ConfigValidationError):
        AppConfig.from_env()

def test_config_context_manager(config_test):
    original = config_test.execution.max_risk_per_trade
    with config_test.override(execution__max_risk_per_trade=0.01):
        assert config_test.execution.max_risk_per_trade == 0.01
    assert config_test.execution.max_risk_per_trade == original
```

**File: `tests/unit/test_retry.py`**

```python
def test_retry_with_exponential_backoff(mocker):
    mock_func = mocker.MagicMock(side_effect=[
        ConnectionError("Attempt 1"),
        ConnectionError("Attempt 2"),
        "Success"
    ])
    
    decorated = retry(max_attempts=3, backoff_factor=1.0)(mock_func)
    result = decorated()
    
    assert result == "Success"
    assert mock_func.call_count == 3

def test_circuit_breaker_trips_after_threshold(mocker):
    mock_func = mocker.MagicMock(
        side_effect=ExternalServiceError("Service down")
    )
    
    decorated = circuit_breaker(
        failure_threshold=2,
        expected_exception=ExternalServiceError
    )(mock_func)
    
    with pytest.raises(ExternalServiceError):
        for _ in range(3):
            decorated()
    
    # Circuit should be open, fail immediately
    with pytest.raises(CircuitBreakerOpenError):
        decorated()
```

**File: `tests/integration/test_vault_flow.py`**

```python
def test_vault_initialization_flow(temp_vault, sample_ohlcv):
    """End-to-end: create vault structure, ingest data, validate."""
    from data.vaults import create_vault_structure
    from data.validation import validate_ohlcv
    
    # Create structure
    create_vault_structure(temp_vault["raw"])
    
    # Save sample data
    sample_ohlcv.to_parquet(
        f"{temp_vault['raw']}/sector=Technology/TEST.parquet"
    )
    
    # Validate
    assert validate_ohlcv(sample_ohlcv) == True
    assert os.path.exists(f"{temp_vault['raw']}/sector=Technology")
```

### 5.4 Test Coverage Report

**Command**: `pytest tests/ --cov=new_pipeline --cov-report=html`

Expected output:
```
new_pipeline/config/     85%
new_pipeline/core/       92%
new_pipeline/utils/      88%
new_pipeline/data/       75%  (incomplete in Phase 1)
new_pipeline/monitoring/ 80%
---
TOTAL                    84%
```

---

## 6. Exception Handling Best Practices

### 6.1 Error Propagation Strategy

```
Level 1 (Leaf Functions)
├─ Catch external service errors (yfinance, Alpaca, Ollama)
├─ Wrap in domain-specific exception
└─ Log with full context

Level 2 (Module Functions)
├─ Catch domain exceptions
├─ Decide: retry, fallback, or propagate
└─ Enrich with module context

Level 3 (Orchestrator)
├─ Catch all exceptions
├─ Log, alert, record to ledger
└─ Exit with appropriate code
```

### 6.2 Logging When Catching Exceptions

```python
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(
        "Operation failed",
        extra={
            "error_type": type(e).__name__,
            "error_message": str(e),
            "retry_count": attempt,
            "fallback_action": "use_default_value"
        }
    )
    # Then: retry, fallback, or re-raise
```

---

## 7. Code Quality & Linting Standards

### 7.1 Pre-Commit Hooks

**File: `.pre-commit-config.yaml`**

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/PyCQA/isort
    rev: 5.12.0
    hooks:
      - id: isort

  - repo: https://github.com/PyCQA/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=100]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.0.0
    hooks:
      - id: mypy
        additional_dependencies: [pydantic]
```

### 7.2 Type Hints

**Requirement**: All functions must have type hints (enforced by mypy).

```python
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd

def fetch_sentiment_async(
    semaphore: asyncio.Semaphore,
    session: aiohttp.ClientSession,
    headline: str,
    ticker: str
) -> float:
    """Fetch sentiment score; return [-1, +1] or 0.0 on error."""
    pass

def evaluate_risk_veto_gates(
    entry_price: float,
    atr: float,
    atr_multiplier: float,
    account_capital: float,
    max_risk_pct: float
) -> Tuple[bool, float]:
    """Return (approved, position_size)."""
    pass
```

### 7.3 Docstring Format (Google Style)

```python
def compute_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> np.ndarray:
    """Compute Average True Range (ATR) using Wilder's smoothing.
    
    Args:
        high: High prices array.
        low: Low prices array.
        close: Close prices array.
        period: Lookback window (default 14).
    
    Returns:
        ATR array of same length as input, with NaN for first period-1 rows.
    
    Raises:
        ValueError: If arrays have mismatched lengths or period < 1.
    
    Examples:
        >>> highs = np.array([100, 102, 101])
        >>> lows = np.array([98, 100, 99])
        >>> closes = np.array([99, 101, 100])
        >>> atr = compute_atr(highs, lows, closes, period=2)
    """
```

---

## 8. Implementation Checklist

### Week 1: Foundation

- [ ] **Day 1-2**: Folder structure creation
  - [ ] Create all directories listed in 1.1
  - [ ] Add `__init__.py` files
  - [ ] Create `.gitignore` for `/new_pipeline/`

- [ ] **Day 2-3**: Configuration system
  - [ ] Implement `config/schema.py` (Pydantic models)
  - [ ] Implement `config/base.py` (ConfigManager singleton)
  - [ ] Write `config/defaults.yaml`
  - [ ] Add environment variable override logic
  - [ ] Unit tests: `test_config.py`

- [ ] **Day 3-4**: Logging & exceptions
  - [ ] Implement `core/logging.py` (LoggerFactory)
  - [ ] Implement `core/exceptions.py` (exception hierarchy)
  - [ ] Add StructuredFormatter for JSON output
  - [ ] Unit tests: `test_logging.py`, `test_exceptions.py`

- [ ] **Day 4-5**: Retry & circuit breaker
  - [ ] Implement `utils/retry.py` (@retry decorator)
  - [ ] Implement circuit breaker logic
  - [ ] Unit tests: `test_retry.py`

### Week 2: Infrastructure & Testing

- [ ] **Day 6-7**: Monitoring & health checks
  - [ ] Implement `monitoring/metrics.py` (Counter, Gauge, Histogram)
  - [ ] Implement `monitoring/health.py` (health check endpoints)
  - [ ] Add health check CLI command

- [ ] **Day 7-8**: Testing framework
  - [ ] Set up Pytest with `tests/conftest.py`
  - [ ] Add test fixtures (config, data, mocks)
  - [ ] Add `.pre-commit-config.yaml`
  - [ ] Integration test: `test_vault_flow.py`

- [ ] **Day 8-9**: Documentation
  - [ ] Write `docs/ARCHITECTURE.md` (design decisions)
  - [ ] Write `docs/CONFIG_GUIDE.md` (how to configure)
  - [ ] Write `docs/LOGGING_GUIDE.md` (logging patterns)
  - [ ] Write `docs/TESTING_GUIDE.md` (testing conventions)

- [ ] **Day 10**: Validation & CI setup
  - [ ] Run all tests: `pytest tests/ --cov=new_pipeline`
  - [ ] Run linting: `black`, `isort`, `flake8`, `mypy`
  - [ ] Fix any linting errors
  - [ ] Validate configuration loading from `.env`

---

## 9. Success Criteria & Acceptance Tests

### 9.1 Functional Acceptance

| Criterion | Test | Expected Result |
|-----------|------|-----------------|
| Config loads from YAML | `pytest tests/unit/test_config.py` | ✓ All pass |
| Env vars override config | `test_config_from_env_override` | ✓ Pass |
| Logger outputs structured JSON | Manual: run `python -c "get_logger(...)"` | ✓ JSON output |
| Retry decorator works | `pytest tests/unit/test_retry.py::test_retry_*` | ✓ All pass |
| Circuit breaker trips/resets | `test_circuit_breaker_trips_after_threshold` | ✓ Pass |
| Health check passes | `python scripts/check_health.py` | ✓ All checks pass |
| Test coverage > 80% | `pytest --cov=new_pipeline` | ✓ 84% coverage |
| No linting errors | `black, isort, flake8, mypy` | ✓ 0 errors |

### 9.2 Integration Acceptance

| Criterion | Test | Expected Result |
|-----------|------|-----------------|
| Full config -> logger -> exception flow | `test_config_integration` | ✓ Pass |
| Retry + circuit breaker together | `test_retry_then_circuit_breaker` | ✓ Pass |
| Temporary config override works | Config context manager test | ✓ Pass |
| Vault directory creation | `test_vault_initialization_flow` | ✓ Pass |

### 9.3 Non-Functional Acceptance

| Criterion | Measurement | Target |
|-----------|-------------|--------|
| Config load time | `pytest benchmark` | < 50ms |
| Logger overhead | Per-call timing | < 1ms |
| Test suite runtime | `pytest -v` | < 10 seconds |
| Code coverage | `pytest --cov` | ≥ 80% |
| Type hint compliance | `mypy` | 0 errors |

---

## 10. Deliverables Summary

### At End of Phase 1

1. **Codebase**
   - [ ] `/new_pipeline/` with complete folder structure
   - [ ] All modules: config/, core/, data/, features/, models/, execution/, monitoring/, utils/
   - [ ] 100+ unit/integration tests
   - [ ] Pre-commit hooks configured

2. **Documentation**
   - [ ] ARCHITECTURE.md (design decisions, module dependencies)
   - [ ] CONFIG_GUIDE.md (how to set up configurations)
   - [ ] LOGGING_GUIDE.md (logging patterns & examples)
   - [ ] TESTING_GUIDE.md (how to write tests)
   - [ ] API_REFERENCE.md (module APIs)
   - [ ] README.md (quick-start)

3. **Quality Metrics**
   - [ ] ≥ 80% test coverage
   - [ ] 0 linting errors (black, flake8, mypy)
   - [ ] All tests passing
   - [ ] No console warnings

4. **Validation Scripts**
   - [ ] `scripts/check_health.py` (verify setup)
   - [ ] `scripts/run_tests.sh` (automated testing)
   - [ ] `scripts/init_environment.sh` (first-time setup)

---

## 11. Rollover to Phase 2

**Prerequisites for Phase 2 Start**:
- [ ] Phase 1 all tests passing
- [ ] Configuration system validated with multiple environments
- [ ] Logging captures all system events
- [ ] Error handling patterns established
- [ ] Documentation complete

**Phase 2 Handoff**:
- Use Phase 1 config system for feature_compiler.py defaults
- Use Phase 1 logging in all feature modules
- Use Phase 1 retry decorator for async LLM calls
- Use Phase 1 exception hierarchy in feature layer

---

## Appendix A: Quick Reference Commands

```bash
# Setup Phase 1
cd /workspaces/Quantum_Avenger/new_pipeline
python scripts/init_environment.sh

# Run all tests
pytest tests/ -v --cov=new_pipeline

# Check linting
black --check .
flake8 .
mypy .

# Fix linting issues
black .
isort .

# Check system health
python scripts/check_health.py

# View test coverage report
pytest tests/ --cov=new_pipeline --cov-report=html
open htmlcov/index.html
```

---

**Next**: After Phase 1 completion, proceed to [Phase 2: Vectorized Feature Engine](PHASE_2_SPECIFICATION.md) (to be created).

```

---

### File: `docs/FULL_SYSTEM_INTEGRATION_GUIDE.md`

```markdown
# Quantum Avenger Full System Integration Guide

## Purpose

This guide explains how all phases of the Quantum Avenger system connect into a single integrated production pipeline. It describes the high-level architecture, module interactions, data flow, deployment mapping, and operational handoffs between phases.

---

## 1. System Overview

Quantum Avenger is built as a layered hybrid trading system combining deterministic quantitative models with probabilistic LLM reasoning. The architecture is intentionally modular so each phase can be developed and validated independently before being integrated into the whole.

### Layers

1. **Phase 1: Infrastructure** — Configuration, logging, exceptions, testing, and core runtime services.
2. **Phase 2: Features** — Vectorized data engineering, GPU-accelerated feature synthesis, deterministic Shield Agent.
3. **Phase 3: Tournament** — CPCV backtesting, out-of-core XGBoost training, candidate model generation.
4. **Phase 4: Evaluation** — Statistical validation via DSR, HMM generalization, promotion and champion registry.
5. **Phase 5: Orchestration** — FastMCP bridge, entity anonymization, RAG, LangGraph verdict workflow, trade execution.
6. **Phase 6: Monitoring** — Streamlit dashboard, KPI streaming, veto analytics, trade log exploration.
7. **Phase 7: Hardening** — Deployment, observability, resilience, security, and production readiness.

---

## 2. End-to-End Data Flow

### 2.1 Ingestion and Feature Pipeline (Phase 1 → Phase 2)

- **Input**: Raw market and alternative data feeds, file vaults, external APIs.
- **Phase 1** provides the config system and logging framework that all ingestion and feature modules use.
- **Phase 2** executes the feature pipeline using Polars and optional GPU kernels:
  - OHLCV and volume series become derived features: returns, ATR, ADV, volatility, spreads, Amihud illiquidity.
  - Feature outputs are persisted to Parquet in a structured vault.
  - Shield Agent modules are compiled in this phase and exposed as deterministic tools.

### 2.2 Tournament Training and Candidate Generation (Phase 3)

- Uses Parquet feature outputs produced by Phase 2.
- Runs CPCV to split time-series data with purge and embargo windows.
- Trains XGBoost models with custom asymmetric loss via `ParquetDataIter` streaming.
- Produces candidate artifact files:
  - `{sector}_candidate.json`
  - `{sector}_candidate_features.json`
  - returns matrix and benchmark history
- Stores candidate metadata in model registry directories.

### 2.3 Statistical Evaluation and Promotion (Phase 4)

- Reads candidate model artifacts and OOS returns from Phase 3.
- Computes Deflated Sharpe Ratio (DSR) across candidate trials.
- Fits an HMM on benchmark returns for synthetic regime generation.
- Validates candidate model generalization on HMM-generated synthetic returns.
- Executes promotion logic:
  - If DSR ≥ 0.95 AND synthetic Sharpe > 0 → promote
  - Else reject and log reason
- Updates champion registry and generates HTML tearsheets.

### 2.4 Live Execution Orchestration (Phase 5)

- Loads champion models and feature manifests from Phase 4.
- Uses the Shield Agent from Phase 2 as a deterministic veto layer.
- Serves quant tools through FastMCP to keep all numeric logic external to the LLM.
- Applies entity anonymization to all text inputs before LLM processing.
- Uses RAG to provide semantic context from news and filings.
- Runs LangGraph state machine for verdict generation, grading, risk veto, and execution.
- Writes decisions to the veto ledger and trade log.

### 2.5 Monitoring and Operations (Phase 6)

- Reads live ledger and trade logs from Phase 5.
- Computes KPIs, equity curves, drawdown, and performance metrics.
- Renders dashboards for operations and risk teams.
- Displays model registry, active champions, and promotion history.
- Triggers alerts for anomalies, veto spikes, and risk breaches.

### 2.6 Production Hardening (Phase 7)

- Packages the entire system as Docker images and deploys via Kubernetes.
- Adds observability with Prometheus, Grafana, and centralized logging.
- Implements circuit breakers, retries, chaos testing, and disaster recovery.
- Secures secrets, APIs, and access control.
- Automates CI/CD and release processes.

---

## 3. Integration Points and Contracts

### 3.1 Phase 1 Contracts

- `AppConfig` schema used by every module.
- `LoggerFactory` ensures structured JSON logs across services.
- Exception hierarchy standardizes error handling.
- Test fixtures and CI tooling validate integration boundaries.

### 3.2 Phase 2 Contracts

- Feature Parquet schema contract:
  - Must include required columns for model training and live inference.
- Shield Agent API contract:
  - `evaluate_risk_veto_gates()` returns approved flag, position size, stop loss, and reasons.
- GPU kernel outputs must maintain deterministic value semantics.

### 3.3 Phase 3 Contracts

- Candidate model artifact contract:
  - `candidate.json` format for XGBoost booster metadata
  - `candidate_features.json` list of features used by the model
- Returns matrix contract:
  - Columns represent CPCV trials
  - Champion returns are identifiable and stable

### 3.4 Phase 4 Contracts

- Champion registry contract:
  - Promoted models live in production directory
  - Promotion history stored in JSON registry
- Tearsheets and evaluation artifacts are auditable and reproducible.

### 3.5 Phase 5 Contracts

- FastMCP tool schema contract:
  - Input/output JSON shapes for risk, market, and portfolio tools.
- Entity anonymization contract:
  - Input text and output mapping with stable placeholder mapping.
- LangGraph state contract:
  - State includes signal, symbol, context, verdict, grade, veto, execution_id.
- Execution contract:
  - Trade orders must be recorded in trade log with fills and P&L.

### 3.6 Phase 6 Contracts

- Dashboard data contract:
  - Veto ledger and trade log fields
  - KPI metrics schema
  - Model registry summaries
- Alert contract:
  - Alert message structure
  - Severity levels and timestamps

### 3.7 Phase 7 Contracts

- Deployment contract:
  - Images must be reproducible and tagged
  - Kubernetes manifests declare probes and resources
- Observability contract:
  - Metrics names, labels, and dashboards
- Security contract:
  - Secrets stored securely
  - IAM and network policies enforced

---

## 4. Deployment Topology

### 4.1 Service Components

- `quantum-avenger-app`
  - Feature pipeline
  - Candidate training
  - Evaluation orchestrator
  - Execution controller (non-LLM path)

- `quantum-avenger-mcp`
  - FastMCP deterministic tool server
  - Risk and market tool registry

- `quantum-avenger-dashboard`
  - Streamlit monitoring UI
  - Live metrics and export services

- `quantum-avenger-worker` (optional)
  - Backtest and training workers
  - Heavy compute jobs

### 4.2 Runtime Dependencies

- Model artifact storage (S3 / object store)
- Parquet vault and feature store
- Database for audit logs / registry
- Prometheus + Grafana + Loki/Elastic
- Alpaca / market data API endpoints
- Vault / secrets manager

### 4.3 Data Paths

- Raw data → `/data/raw/`
- Processed features → `/data/features/`
- Candidate models → `/models/candidates/`
- Champion models → `/models/champions/`
- Evaluation outputs → `/analysis/evaluation/`
- Trade logs → `/runtime/trade_log.parquet`
- Veto ledger → `/runtime/veto_ledger.parquet`
- Dashboard exports → `/runtime/exports/`

---

## 5. Operational Sequence

### 5.1 Daily Pipeline Sequence

1. **Data ingestion** populates raw vault and updates feature store.
2. **Feature engine** computes new features and persists Parquet files.
3. **Tournament pipeline** retrains candidate models on latest data.
4. **Evaluation pipeline** computes DSR/HMM and promotes successful models.
5. **Execution engine** consumes champion models and real-time market signals.
6. **Monitoring dashboard** displays live metrics and veto analytics.
7. **Hardening processes** maintain deployment health and alerts.

### 5.2 Live Signal Flow

1. Champion model creates signal.
2. Raw market data and feature values are supplied to Shield Agent.
3. FastMCP risk tools calculate size, slippage, and stops.
4. Entity anonymized context is sent to LLM via LangGraph.
5. Verdict and grader nodes assess trade rationale.
6. Shield Agent either approves or vetoes.
7. If approved, trade is executed and logged.
8. All decisions feed dashboard and alert engines.

---

## 6. Testing and Validation Strategy

### 6.1 Integration Test Matrix

- Phase 1 ↔ Phase 2: Config and logging used to initialize feature pipeline.
- Phase 2 ↔ Phase 3: Feature artifacts loaded by training pipeline.
- Phase 3 ↔ Phase 4: Candidate model artifacts validated by evaluation.
- Phase 4 ↔ Phase 5: Champion selection used in live orchestration.
- Phase 5 ↔ Phase 6: Execution logs surfaced in dashboard.
- Phase 6 ↔ Phase 7: Metrics and alerts validated in production manifests.

### 6.2 End-to-End Scenarios

1. **Build-and-deploy**: Full system package, deploy containers, validate startup.
2. **Training-to-promotion**: Train candidate → compute DSR → promote champion.
3. **Live trade cycle**: Generate signal → decide → execute → log.
4. **Dashboard refresh**: Dashboard reads live logs and updates every second.
5. **Failure recovery**: Simulate service failure and verify rollback.

### 6.3 Acceptance Criteria

- All phase handoffs are documented and reproducible.
- Data contracts are enforced by schema and tests.
- Champion model promotion is auditable and reversible.
- Execution decisions are logged end-to-end.
- Dashboard reflects live state within 1 second.
- Deployment artifacts pass security and compliance checks.

---

## 7. Issue Resolution and Change Management

### 7.1 Version Control and Branching

- `main` reflects deployable system.
- `develop` contains integration work.
- Feature branches named `feature/phase-x`.
- Release branches named `release/vX.Y`.

### 7.2 Change Review Process

- All changes go through PR review.
- CI must pass unit, integration, and security scans.
- Model promotion and deployment changes require manual approval.

### 7.3 Rollback and Recovery

- Maintain versioned model artifacts and champion snapshots.
- Deploy canary releases before full rollout.
- Use `rollback.sh` or Kubernetes rollout undo on failure.

---

## 8. Glossary of Core Components

- **Shield Agent**: Deterministic Numba JIT risk veto layer.
- **FastMCP**: JSON-RPC tool server exposing deterministic quant functions.
- **CPCV**: Combinatorial Purged Cross-Validation.
- **DSR**: Deflated Sharpe Ratio.
- **HMM Validation**: Hidden Markov Model synthetic generalization test.
- **LangGraph**: Agentic workflow orchestration pipeline.
- **RAG**: Retrieval Augmented Generation.
- **Veto Ledger**: Append-only log of rejected decisions.
- **Champion Registry**: Active live model registry.

---

## 9. Recommended Next Steps

1. Create a single `integration_onboarding.md` for new developers.
2. Add automated schema validation for all data artifacts.
3. Implement a deployment test harness that exercises each phase sequentially.
4. Connect the dashboard directly to live metrics exporters.
5. Run the first production-ready end-to-end smoke test.

---

## 10. Document Ownership

- Owner: `Quantum Avenger Architecture Team`
- Maintainers: `app_team@qa.ai`, `infra_team@qa.ai`
- Review cadence: quarterly or after major release

```

---

### File: `docs/execution_roadmap.md`

```markdown
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

```

---

### File: `docs/PHASE_5_SPECIFICATION.md`

```markdown
# Phase 5: Live Execution & LangGraph Orchestration - Detailed Specification

**Duration**: 2.5 weeks  
**Target Date**: Complete by early August (after Phase 4)  
**Success Criteria**: FastMCP server running; LangGraph state machine working; end-to-end verdict flow; LLM + quant fusion; 85%+ test coverage

---

## 1. Phase 5 Architecture Overview

### 1.1 System Context (Fusion of Quantitative + LLM)

```
┌────────────────────────────────────────────────────────────────────┐
│  PHASES 1-4 (Complete): Infrastructure, Features, Training, Eval  │
├────────────────────────────────────────────────────────────────────┤
│                           │                                         │
│                           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  PHASE 5: LIVE EXECUTION & LANGGRAPH ORCHESTRATION          │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  LAYER 0: DETERMINISTIC FOUNDATION                          │  │
│  │  ├─ Shield Agent (Numba JIT, <100µs veto gates)            │  │
│  │  ├─ Risk calculations (Kelly sizing, slippage, liquidity)  │  │
│  │  ├─ Position tracking (current quantity, P&L)              │  │
│  │  └─ Alpaca real-time feed (price, volume, fundamentals)    │  │
│  │                                                              │  │
│  │  LAYER 1: FASTMCP BRIDGE (Deterministic ↔ LLM)             │  │
│  │  ├─ FastMCP server (Python sidecar process)                │  │
│  │  ├─ Tool registration (30+ quant functions exposed)        │  │
│  │  ├─ JSON-RPC interface (quant → LLM, LLM → quant)          │  │
│  │  ├─ Tool schemas (input/output specs)                      │  │
│  │  └─ Error handling (exceptions wrapped in JSON)            │  │
│  │                                                              │  │
│  │  LAYER 2: ENTITY ANONYMIZATION (Defeat look-ahead bias)    │  │
│  │  ├─ spaCy NER pipeline (extract entities)                  │  │
│  │  ├─ Entity masking (Apple → [COMPANY_A], ticker → [...])   │  │
│  │  ├─ Vectorized batch processing (100+ articles/sec)        │  │
│  │  └─ Reverse mapping (results → original entities)          │  │
│  │                                                              │  │
│  │  LAYER 3: RETRIEVAL AUGMENTED GENERATION (RAG)             │  │
│  │  ├─ Late chunking (preserve semantic context)              │  │
│  │  ├─ Vector embeddings (sentence-transformers)              │  │
│  │  ├─ Faiss index (fast similarity search)                   │  │
│  │  ├─ BM25 ranking (lexical fallback)                        │  │
│  │  └─ Reranking (LLM-based context scoring)                  │  │
│  │                                                              │  │
│  │  LAYER 4: LANGGRAPH STATE MACHINE (Agentic Orchestration)  │  │
│  │  ├─ State: {signal, context, grader_feedback, verdict}     │  │
│  │  ├─ Node: Verdict Engine (LLM generates alpha narrative)   │  │
│  │  ├─ Node: Grader (LLM validates verdict vs context)        │  │
│  │  ├─ Node: Risk Veto (Shield Agent kills bad verdicts)      │  │
│  │  ├─ Node: Execution (submit to Alpaca if approved)         │  │
│  │  └─ Edges: Conditional routing (pass/fail/retry)           │  │
│  │                                                              │  │
│  │  LAYER 5: VETO LEDGER & MONITORING                         │  │
│  │  ├─ Log all decisions (why approved/rejected)              │  │
│  │  ├─ Real-time dashboard (KPIs, veto reasons)               │  │
│  │  ├─ Alert system (anomalies, liquidity breaches)           │  │
│  │  └─ Trade log (fills, slippage, P&L)                       │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│       Uses all Phases 1-4 + Alpaca Live API                       │
│       Produces: Trade fills, ledgers, monitoring data             │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

```
/new_pipeline/execution/            # ✨ NEW: Live execution module
├── __init__.py
├── alpaca_connector.py              # ✨ NEW: Real-time market data
├── mcp_server.py                    # ✨ NEW: FastMCP bridge
├── entity_anonymizer.py             # ✨ NEW: spaCy NER masking
├── rag_engine.py                    # ✨ NEW: Late chunking + Faiss
├── state_machine.py                 # ✨ NEW: LangGraph orchestrator
├── verdict_engine.py                # ✨ NEW: LLM verdict generation
├── grader.py                        # ✨ NEW: LLM verdict validation
├── veto_ledger.py                   # ✨ NEW: Audit trail
├── orchestrator.py                  # ✨ NEW: Live execution controller
└── tests/
    ├── test_alpaca_connector.py
    ├── test_mcp_server.py
    ├── test_entity_anonymizer.py
    ├── test_rag_engine.py
    ├── test_state_machine.py
    ├── test_verdict_engine.py
    ├── test_grader.py
    └── benchmarks/
        ├── bench_langgraph_latency.py
        └── bench_mcp_throughput.py
```

---

## 2. FastMCP Bridge: Deterministic ↔ LLM

### 2.1 Theory: JSON-RPC Isolation

**Problem**: LLMs must NOT calculate risk or slippage (hallucination risk)

**Solution**: Expose all quantitative functions via FastMCP JSON-RPC server
- LLM calls: "execute_kelly_sizing(capital=100k, risk_distance=5.0, win_rate=0.6)"
- Server responds: `{"position_size": 8000, "stop_loss": 95.0}`
- No calculation leak into LLM context

### 2.2 Module: `execution/mcp_server.py`

**File: `execution/mcp_server.py`**

#### 2.2.1 MCP Tool Registration

**Class: `QuantumAvengerMCPServer`**

```python
from fastmcp import FastMCP, Context
import json

class QuantumAvengerMCPServer:
    """FastMCP server exposing all quant functions to LLM.
    
    Purpose:
        - Deterministic calculation engine for LLM
        - JSON-RPC interface (no code execution risk)
        - Schema validation (input/output types)
        - Prevents hallucination (forced use of real data)
    
    Methods:
        __init__: Initialize server + register tools
        run: Start listening on stdio
    """
    
    def __init__(self, config: AppConfig):
        """Initialize FastMCP server with tool registry.
        
        Args:
            config: Application configuration.
        
        Server Configuration:
            - name: "Quantum Avenger MCP Server"
            - version: "1.0.0"
            - capabilities: ["tools"]
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # Initialize FastMCP server
        self.mcp = FastMCP(
            name="Quantum Avenger MCP Server",
            version="1.0.0"
        )
        
        # Register all quant tools
        self._register_risk_tools()
        self._register_feature_tools()
        self._register_market_tools()
        self._register_position_tools()
        
        self.logger.info("MCP server initialized with 30+ tools")
    
    def _register_risk_tools(self) -> None:
        """Register risk management tools."""
        
        @self.mcp.tool()
        def calculate_kelly_position_size(
            account_capital: float,
            risk_distance: float,
            win_rate: float,
            win_loss_ratio: float = 1.0,
            conservative_factor: float = 0.75
        ) -> dict:
            """Calculate position size using Kelly criterion.
            
            Args:
                account_capital: Total account equity (USD).
                risk_distance: Distance to stop loss (USD/share).
                win_rate: Historical win rate (0-1).
                win_loss_ratio: Average win / average loss.
                conservative_factor: Kelly * this (typically 0.75).
            
            Returns:
                {
                    "position_size": int (shares),
                    "position_notional": float (USD),
                    "risk_amount": float (USD),
                    "kelly_pct": float (0-5%),
                    "explanation": str
                }
            
            Formula:
                Kelly % = (p*b - q) / b
                Capped at 5% of capital
                Applied with 0.75× conservative factor
            """
            from shields import calculate_kelly_position_size as calc_kelly
            
            result = calc_kelly(
                account_capital,
                risk_distance,
                win_rate,
                win_loss_ratio,
                conservative_factor
            )
            
            return {
                "position_size": result['size'],
                "position_notional": result['notional'],
                "risk_amount": result['risk_amount'],
                "kelly_pct": result['kelly_pct'],
                "explanation": f"Kelly={result['kelly_pct']:.2f}%, Conservative 0.75x applied"
            }
        
        @self.mcp.tool()
        def calculate_dynamic_slippage(
            order_size: float,
            adv_20: float,
            volume_today: float,
            volatility: float,
            regime: str = "normal"
        ) -> dict:
            """Calculate hydrodynamic market impact slippage.
            
            Args:
                order_size: Shares to order.
                adv_20: Average daily volume (20-day).
                volume_today: Today's volume so far.
                volatility: Current volatility (annualized).
                regime: Market regime ("normal" or "high_vol").
            
            Returns:
                {
                    "slippage_bps": float (basis points),
                    "slippage_usd": float,
                    "approval": bool (approved if < 50 bps limit),
                    "reasoning": str
                }
            
            Formula:
                S = c · σ · √(Q/V)
                c ≈ 0.5 (calibrated)
                Adjusted for regime (high_vol × 2.0)
            """
            from slippage import calculate_dynamic_slippage as calc_slip
            
            result = calc_slip(
                order_size,
                adv_20,
                volume_today,
                volatility,
                regime
            )
            
            return {
                "slippage_bps": result['slippage_bps'],
                "slippage_usd": result['slippage_usd'],
                "approval": result['slippage_bps'] < 50,
                "reasoning": f"Slippage = {result['slippage_bps']:.1f} bps ({'OK' if result['slippage_bps'] < 50 else 'REJECT'})"
            }
        
        @self.mcp.tool()
        def evaluate_risk_veto_gates(
            entry_price: float,
            atr: float,
            atr_multiplier: float,
            account_capital: float,
            max_risk_pct: float,
            current_qty: int,
            adv_20: float,
            volume_today: float,
            volatility: float
        ) -> dict:
            """Run all Shield Agent veto gates (deterministic, <100µs).
            
            Args:
                entry_price: Entry price (USD).
                atr: Average True Range.
                atr_multiplier: ATR × this for stop placement.
                account_capital: Account equity.
                max_risk_pct: Max risk per trade (%).
                current_qty: Current position size.
                adv_20: 20-day average daily volume.
                volume_today: Today's volume.
                volatility: Current volatility.
            
            Returns:
                {
                    "approved": bool,
                    "position_size": int,
                    "stop_loss": float,
                    "veto_reasons": List[str],
                    "gates_passed": Dict[str, bool]
                }
            
            Gates:
                1. Stop validity (stop > 0)
                2. Position sizing (Kelly-based)
                3. Liquidity (order ≤ 25% ADV)
                4. Slippage (< 50 bps)
                5. Portfolio reconciliation (delta > 0)
            """
            from shields import evaluate_risk_veto_gates as evaluate
            
            result = evaluate(
                entry_price,
                atr,
                atr_multiplier,
                account_capital,
                max_risk_pct,
                current_qty,
                adv_20,
                volume_today,
                volatility
            )
            
            return {
                "approved": result['approved'],
                "position_size": result['position_size'],
                "stop_loss": result['stop_loss'],
                "veto_reasons": result['veto_reasons'],
                "gates_passed": result['gates_passed']
            }
    
    def _register_feature_tools(self) -> None:
        """Register feature extraction tools (read-only)."""
        
        @self.mcp.tool()
        def get_atr(
            symbol: str,
            period: int = 14
        ) -> dict:
            """Get Average True Range for symbol.
            
            Args:
                symbol: Stock ticker (e.g., "AAPL").
                period: ATR lookback period (days).
            
            Returns:
                {
                    "symbol": str,
                    "atr": float,
                    "atr_percent": float,
                    "timestamp": str
                }
            """
            # Query live market data via Alpaca
            atr_value = self.market_data_cache.get_atr(symbol, period)
            return {
                "symbol": symbol,
                "atr": atr_value,
                "atr_percent": (atr_value / self.market_data_cache.last_price(symbol)) * 100,
                "timestamp": pd.Timestamp.now().isoformat()
            }
        
        @self.mcp.tool()
        def get_adv(
            symbol: str,
            period: int = 20
        ) -> dict:
            """Get Average Daily Volume.
            
            Returns:
                {
                    "symbol": str,
                    "adv": float,
                    "volume_today": float,
                    "volume_pct_of_adv": float
                }
            """
            adv = self.market_data_cache.get_adv(symbol, period)
            vol_today = self.market_data_cache.volume_today(symbol)
            return {
                "symbol": symbol,
                "adv": adv,
                "volume_today": vol_today,
                "volume_pct_of_adv": (vol_today / adv) * 100
            }
        
        @self.mcp.tool()
        def get_volatility(
            symbol: str,
            window: int = 15
        ) -> dict:
            """Get rolling volatility (annualized).
            
            Returns:
                {
                    "symbol": str,
                    "volatility_annual": float,
                    "regime": str ("normal" or "high_vol")
                }
            """
            vol = self.market_data_cache.get_volatility(symbol, window)
            regime = "high_vol" if vol > 0.30 else "normal"
            return {
                "symbol": symbol,
                "volatility_annual": vol,
                "regime": regime
            }
    
    def _register_market_tools(self) -> None:
        """Register market data query tools."""
        
        @self.mcp.tool()
        def get_price(symbol: str) -> dict:
            """Get real-time last price.
            
            Returns:
                {
                    "symbol": str,
                    "price": float,
                    "timestamp": str,
                    "bid_ask_spread_bps": float
                }
            """
            price = self.market_data_cache.last_price(symbol)
            bid, ask = self.market_data_cache.bid_ask(symbol)
            spread_bps = ((ask - bid) / ((bid + ask) / 2)) * 10000
            return {
                "symbol": symbol,
                "price": price,
                "bid_ask_spread_bps": spread_bps,
                "timestamp": pd.Timestamp.now().isoformat()
            }
        
        @self.mcp.tool()
        def get_open_interest(symbol: str) -> dict:
            """Get open interest / shares outstanding.
            
            Returns:
                {
                    "symbol": str,
                    "shares_outstanding": float,
                    "float": float,
                    "short_interest_pct": float
                }
            """
            # Query via SEC data or Alpaca fundamentals
            data = self.market_data_cache.get_fundamentals(symbol)
            return {
                "symbol": symbol,
                "shares_outstanding": data['shares_outstanding'],
                "float": data['float'],
                "short_interest_pct": data['short_interest_pct']
            }
    
    def _register_position_tools(self) -> None:
        """Register portfolio position tracking tools."""
        
        @self.mcp.tool()
        def get_current_position(symbol: str) -> dict:
            """Get current position for symbol.
            
            Returns:
                {
                    "symbol": str,
                    "quantity": int,
                    "avg_fill_price": float,
                    "current_price": float,
                    "unrealized_pnl": float,
                    "unrealized_pnl_pct": float
                }
            """
            pos = self.portfolio.get_position(symbol)
            current_price = self.market_data_cache.last_price(symbol)
            unrealized = (current_price - pos['avg_fill']) * pos['qty']
            unrealized_pct = (unrealized / (pos['avg_fill'] * pos['qty'])) * 100 if pos['qty'] > 0 else 0
            
            return {
                "symbol": symbol,
                "quantity": pos['qty'],
                "avg_fill_price": pos['avg_fill'],
                "current_price": current_price,
                "unrealized_pnl": unrealized,
                "unrealized_pnl_pct": unrealized_pct
            }
        
        @self.mcp.tool()
        def get_portfolio_metrics() -> dict:
            """Get overall portfolio metrics.
            
            Returns:
                {
                    "total_equity": float,
                    "cash": float,
                    "buying_power": float,
                    "total_pnl": float,
                    "total_pnl_pct": float,
                    "max_drawdown": float,
                    "sharpe_ratio": float
                }
            """
            metrics = self.portfolio.get_metrics()
            return {
                "total_equity": metrics['equity'],
                "cash": metrics['cash'],
                "buying_power": metrics['buying_power'],
                "total_pnl": metrics['total_pnl'],
                "total_pnl_pct": metrics['total_pnl_pct'],
                "max_drawdown": metrics['max_drawdown'],
                "sharpe_ratio": metrics['sharpe_ratio']
            }
    
    def run(self) -> None:
        """Start MCP server listening on stdio."""
        self.logger.info("Starting FastMCP server...")
        self.mcp.run(transport="stdio")
```

#### 2.2.2 Error Handling & Validation

**Function: `validate_tool_input()`**

```python
def validate_tool_input(
    tool_name: str,
    input_dict: Dict,
    schema: Dict
) -> Tuple[bool, Optional[str]]:
    """Validate tool input against schema before execution.
    
    Args:
        tool_name: Name of tool being called.
        input_dict: Input parameters from LLM.
        schema: JSON schema specification.
    
    Returns:
        (is_valid, error_message)
    
    Validation Rules:
        1. All required fields present
        2. Type checking (float, int, str, bool)
        3. Range validation (e.g., 0 ≤ win_rate ≤ 1)
        4. Enum validation (e.g., regime in ["normal", "high_vol"])
    """
    from jsonschema import validate, ValidationError
    
    logger = get_logger(__name__)
    
    try:
        validate(instance=input_dict, schema=schema)
        logger.debug(f"Tool input valid: {tool_name}")
        return True, None
    except ValidationError as e:
        error_msg = f"Tool input validation failed ({tool_name}): {e.message}"
        logger.warning(error_msg)
        return False, error_msg
```

---

## 3. Entity Anonymization (Defeat Look-Ahead Bias)

### 3.1 Theory: NER Masking for LLM Safety

**Problem**: LLM might recognize "Apple" in news → hallucinate about stock direction

**Solution**: Replace all tradable entities with placeholders before LLM sees text
- "Apple Q4 earnings beat" → "[COMPANY_A] Q4 earnings beat"
- Result: "BULLISH" → Map back to Apple → Trade

### 3.2 Module: `execution/entity_anonymizer.py`

**File: `execution/entity_anonymizer.py`**

#### 3.2.1 Entity Extraction & Masking

**Class: `EntityAnonymizer`**

```python
import spacy
from typing import Tuple, Dict, List

class EntityAnonymizer:
    """Mask tradable entities before LLM processing.
    
    Purpose:
        - Extract named entities (companies, tickers, people)
        - Replace with [COMPANY_A], [PERSON_B], etc.
        - Preserve semantic meaning (LLM still understands context)
        - Prevent LLM hallucination about specific companies
    
    Methods:
        anonymize_text: Replace entities with placeholders.
        deanonymize_result: Map results back to original entities.
    """
    
    def __init__(self, portfolio_symbols: List[str]):
        """Initialize anonymizer with trading universe.
        
        Args:
            portfolio_symbols: List of ticker symbols (e.g., ["AAPL", "MSFT"]).
        """
        self.logger = get_logger(__name__)
        self.nlp = spacy.load("en_core_web_sm")
        self.portfolio_symbols = set(portfolio_symbols)
        
        # Build ticker → company name mapping (via Alpaca/yfinance)
        self.ticker_to_name = self._build_ticker_mapping()
        
        # Counter for entity IDs
        self.entity_counter = {}
        self.entity_map = {}  # entity_str → [ENTITY_X]
        self.reverse_map = {}  # [ENTITY_X] → entity_str
    
    def _build_ticker_mapping(self) -> Dict[str, str]:
        """Build ticker → company name mapping.
        
        Returns:
            {
                "AAPL": "Apple Inc.",
                "MSFT": "Microsoft Corporation",
                ...
            }
        """
        mapping = {}
        # Query Alpaca Assets API
        for symbol in self.portfolio_symbols:
            # Placeholder: real implementation queries Alpaca
            mapping[symbol] = f"Company_{symbol}"
        return mapping
    
    def anonymize_text(self, text: str) -> Tuple[str, Dict]:
        """Replace entities with placeholders.
        
        Args:
            text: Raw text (news, SEC filing, etc.).
        
        Returns:
            (anonymized_text, entity_mapping)
            where entity_mapping = {
                "AAPL": "[COMPANY_A]",
                "Tim Cook": "[PERSON_A]",
                ...
            }
        
        Process:
            1. Parse text with spaCy NER
            2. Extract ORG (company), PERSON, GPE (location), etc.
            3. Check if entity is in trading universe
            4. Replace with [TYPE_ID] placeholder
            5. Keep mapping for deanonymization
        """
        self.logger.info(f"Anonymizing text ({len(text)} chars)")
        
        doc = self.nlp(text)
        entity_mapping = {}
        anonymized_text = text
        
        # Sort by span length (longest first) to avoid partial replacements
        entities = sorted(doc.ents, key=lambda e: len(e.text), reverse=True)
        
        for ent in entities:
            entity_text = ent.text
            entity_label = ent.label_
            
            # Check if entity is tradable (ticker or company name)
            ticker = self._match_to_ticker(entity_text)
            
            if ticker:
                # Assign placeholder
                if ticker not in self.entity_counter:
                    self.entity_counter[ticker] = len(self.entity_counter)
                
                entity_id = self.entity_counter[ticker]
                placeholder = f"[COMPANY_{chr(65 + entity_id)}]"  # [COMPANY_A], etc.
                
                # Replace all occurrences
                anonymized_text = anonymized_text.replace(entity_text, placeholder)
                entity_mapping[ticker] = placeholder
                self.entity_map[entity_text] = placeholder
                self.reverse_map[placeholder] = ticker
        
        self.logger.info(f"Anonymized {len(entity_mapping)} entities")
        
        return anonymized_text, entity_mapping
    
    def _match_to_ticker(self, entity_text: str) -> Optional[str]:
        """Match entity text to trading symbol.
        
        Args:
            entity_text: Text from NER (e.g., "Apple Inc.", "AAPL").
        
        Returns:
            Ticker symbol if match found, else None.
        """
        # Direct ticker match
        if entity_text.upper() in self.portfolio_symbols:
            return entity_text.upper()
        
        # Company name match (fuzzy)
        entity_upper = entity_text.upper()
        for ticker, name in self.ticker_to_name.items():
            if ticker in self.portfolio_symbols:
                if name.upper().startswith(entity_upper[:4]):
                    return ticker
        
        return None
    
    def deanonymize_result(
        self,
        anonymized_result: str
    ) -> Tuple[str, Optional[str]]:
        """Map anonymized result back to original entity.
        
        Args:
            anonymized_result: LLM output (e.g., "BULLISH on [COMPANY_A]").
        
        Returns:
            (deanonymized_result, ticker)
            Example: ("BULLISH on Apple Inc.", "AAPL")
        """
        # Extract placeholder
        import re
        match = re.search(r'\[COMPANY_[A-Z]\]', anonymized_result)
        
        if not match:
            return anonymized_result, None
        
        placeholder = match.group()
        ticker = self.reverse_map.get(placeholder)
        
        if ticker:
            deanonymized = anonymized_result.replace(
                placeholder,
                self.ticker_to_name.get(ticker, ticker)
            )
            return deanonymized, ticker
        
        return anonymized_result, None
```

---

## 4. Retrieval Augmented Generation (RAG) with Late Chunking

### 4.1 Theory: Semantic Context Preservation

**Problem**: Chunking text loses semantic boundaries (mid-sentence splits)

**Solution**: Late chunking (chunk after embedding, not before)
1. Embed full document
2. Split into semantic chunks (via paragraph/sentence boundaries)
3. Preserve context through chunk overlap

### 4.2 Module: `execution/rag_engine.py`

**File: `execution/rag_engine.py`**

#### 4.2.1 Late Chunking & Embedding

**Class: `RAGEngine`**

```python
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGEngine:
    """Retrieval Augmented Generation with late chunking.
    
    Purpose:
        - Index unstructured text (news, 10-Ks, analyst reports)
        - Retrieve semantically similar context for LLM
        - Preserve chunk boundaries (late chunking)
        - Rank results (Faiss + BM25 + reranking)
    
    Methods:
        index_document: Add document to knowledge base.
        retrieve_context: Get top-k relevant chunks.
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        vector_dim: int = 384,
        chunk_overlap: int = 100
    ):
        """Initialize RAG engine.
        
        Args:
            model_name: Hugging Face model ID.
            vector_dim: Embedding dimension.
            chunk_overlap: Character overlap between chunks.
        """
        self.logger = get_logger(__name__)
        
        # Load embedding model
        self.embed_model = SentenceTransformer(model_name)
        self.vector_dim = vector_dim
        self.chunk_overlap = chunk_overlap
        
        # Initialize Faiss index
        self.index = faiss.IndexFlatL2(vector_dim)
        self.chunk_store = []  # List of (text, source, timestamp)
        
        # Initialize BM25 (lexical fallback)
        self.bm25_retriever = None
        
        self.logger.info(f"RAG engine initialized ({model_name})")
    
    def late_chunk(
        self,
        text: str,
        chunk_size: int = 256,
        overlap: int = 100
    ) -> List[str]:
        """Chunk text while preserving semantic boundaries.
        
        Args:
            text: Full document text.
            chunk_size: Target chunk size (characters).
            overlap: Overlap between chunks.
        
        Returns:
            List of chunks with preserved boundaries.
        
        Algorithm:
            1. Split by sentence (not mid-sentence)
            2. Group sentences until chunk_size exceeded
            3. Add overlap from previous chunk
            4. Return chunks preserving full sentences
        """
        import re
        
        # Split by sentence
        sentences = re.split(r'(?<=[.!?])\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += " " + sentence
            else:
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())
                
                # Start new chunk with overlap
                if chunks:
                    # Add last 'overlap' chars from previous chunk
                    overlap_text = chunks[-1][-overlap:] if len(chunks[-1]) > overlap else chunks[-1]
                    current_chunk = overlap_text + " " + sentence
                else:
                    current_chunk = sentence
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        self.logger.info(f"Late chunked: {len(text)} chars → {len(chunks)} chunks")
        
        return chunks
    
    def index_document(
        self,
        text: str,
        source: str,
        sector: str = "general"
    ) -> None:
        """Index document and add to knowledge base.
        
        Args:
            text: Document text.
            source: Source identifier (URL, filepath, etc.).
            sector: Sector tag (for filtering).
        """
        self.logger.info(f"Indexing document: {source}")
        
        # Late chunk
        chunks = self.late_chunk(text)
        
        # Embed chunks
        embeddings = self.embed_model.encode(chunks, show_progress_bar=False)
        embeddings = np.array(embeddings).astype('float32')
        
        # Add to Faiss index
        self.index.add(embeddings)
        
        # Store metadata
        for i, chunk in enumerate(chunks):
            self.chunk_store.append({
                'text': chunk,
                'source': source,
                'sector': sector,
                'timestamp': pd.Timestamp.now(),
                'chunk_idx': i
            })
        
        self.logger.info(f"Indexed {len(chunks)} chunks from {source}")
    
    def retrieve_context(
        self,
        query: str,
        top_k: int = 5,
        sector_filter: Optional[str] = None
    ) -> List[Dict]:
        """Retrieve top-k relevant chunks for query.
        
        Args:
            query: LLM query (e.g., "Is Apple expanding in AI?").
            top_k: Number of chunks to return.
            sector_filter: Optional sector to filter by.
        
        Returns:
            List of {
                'text': chunk text,
                'source': source,
                'relevance_score': float (0-1),
                'chunk_idx': int
            }
        
        Algorithm:
            1. Embed query
            2. Faiss search (vector similarity)
            3. BM25 search (lexical match, fallback)
            4. Rerank results (LLM-based)
            5. Return top-k
        """
        self.logger.debug(f"Retrieving context for query: {query[:50]}...")
        
        if len(self.chunk_store) == 0:
            self.logger.warning("No chunks indexed yet")
            return []
        
        # Embed query
        query_embedding = self.embed_model.encode(query, show_progress_bar=False)
        query_embedding = np.array([query_embedding]).astype('float32')
        
        # Faiss search
        distances, indices = self.index.search(query_embedding, top_k * 2)  # Get 2x candidates
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:  # Invalid index
                continue
            
            chunk_meta = self.chunk_store[idx]
            
            # Apply sector filter if specified
            if sector_filter and chunk_meta['sector'] != sector_filter:
                continue
            
            # Normalize distance to relevance score (0-1)
            relevance = 1.0 / (1.0 + dist)
            
            results.append({
                'text': chunk_meta['text'],
                'source': chunk_meta['source'],
                'relevance_score': relevance,
                'chunk_idx': chunk_meta['chunk_idx'],
                'sector': chunk_meta['sector']
            })
        
        # Return top-k
        return sorted(results, key=lambda x: x['relevance_score'], reverse=True)[:top_k]
```

---

## 5. LangGraph State Machine

### 5.1 Theory: Agentic Orchestration with Feedback Loops

**Design**: State machine with self-correcting nodes
- Verdict Engine generates alpha narrative
- Grader validates verdict against context
- If invalid → retry (up to 3 times)
- If valid → pass to Shield Agent
- If Shield Agent rejects → fallback to passive

### 5.2 Module: `execution/state_machine.py`

**File: `execution/state_machine.py`**

#### 5.2.1 LangGraph State Definition

**Class: `OrchestratorState`**

```python
from langgraph.graph import StateGraph, END
from typing import Annotated
import operator

class OrchestratorState:
    """LangGraph state for signal → verdict → execution.
    
    Attributes:
        signal: Initial buy/sell signal from model.
        symbol: Ticker symbol.
        entry_price: Entry price (USD).
        context: Retrieved documents (RAG output).
        verdict: LLM verdict ("BULLISH", "BEARISH", "NEUTRAL").
        grader_feedback: Grader validation comment.
        grader_approved: Boolean approval from grader.
        shield_approved: Boolean approval from Shield Agent.
        position_size: Final position size (if approved).
        stop_loss: Stop loss price.
        execution_id: Trade ID (if executed).
        rejection_reason: Why rejected (if rejected).
        attempts: Retry counter.
    """
    
    signal: str  # "BUY" or "SELL"
    symbol: str
    entry_price: float
    context: List[Dict]  # From RAG
    verdict: str = ""
    grader_feedback: str = ""
    grader_approved: bool = False
    shield_approved: bool = False
    position_size: int = 0
    stop_loss: float = 0.0
    execution_id: str = ""
    rejection_reason: str = ""
    attempts: int = 0  # Retry counter
```

#### 5.2.2 State Machine Nodes

**Class: `OrchestratorStateMachine`**

```python
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI

class OrchestratorStateMachine:
    """Multi-node state machine with feedback loops.
    
    Nodes:
        1. Verdict Engine → Generate narrative
        2. Grader → Validate verdict
        3. Risk Veto → Shield Agent approval
        4. Execute → Submit trade
        5. Fallback → Passive mode
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
        
        # Initialize LLMs
        self.verdict_llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.1  # Low temperature for consistency
        )
        self.grader_llm = ChatOpenAI(
            model_name="gpt-4",
            temperature=0.0  # Deterministic grading
        )
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build LangGraph state machine.
        
        Graph topology:
            START
              ↓
            VERDICT_ENGINE
              ↓
            GRADER
            ↙     ↘
        PASS(✓)   FAIL(✗)
          ↓         ↓
        RISK_VETO  RETRY?
        ↙     ↘     ↓ (attempts < 3)
      PASS   FAIL  GRADER (loop)
        ↓     ↓     ↓ (attempts ≥ 3)
      EXEC  FALLBACK
        ↓     ↓
        END←←←→
        """
        
        workflow = StateGraph(OrchestratorState)
        
        # Add nodes
        workflow.add_node("verdict_engine", self._node_verdict_engine)
        workflow.add_node("grader", self._node_grader)
        workflow.add_node("risk_veto", self._node_risk_veto)
        workflow.add_node("execute", self._node_execute)
        workflow.add_node("fallback", self._node_fallback)
        
        # Add edges
        workflow.add_edge("START", "verdict_engine")
        workflow.add_edge("verdict_engine", "grader")
        
        # Conditional: grader pass/fail
        workflow.add_conditional_edges(
            "grader",
            self._grader_decision,
            {
                "pass": "risk_veto",
                "retry": "verdict_engine",  # Loop on failure
                "reject": "fallback"  # Max attempts exceeded
            }
        )
        
        # Conditional: risk veto pass/fail
        workflow.add_conditional_edges(
            "risk_veto",
            self._risk_decision,
            {
                "pass": "execute",
                "reject": "fallback"
            }
        )
        
        # Terminal nodes
        workflow.add_edge("execute", END)
        workflow.add_edge("fallback", END)
        
        return workflow.compile()
    
    def _node_verdict_engine(self, state: OrchestratorState) -> OrchestratorState:
        """Generate alpha narrative from context.
        
        Input: signal + context
        Output: verdict
        
        Prompt:
            "Given the signal '{signal}' for {symbol} at ${entry_price}
             and the following context:
             {context}
             
             Generate a concise verdict ('BULLISH', 'BEARISH', 'NEUTRAL')
             with 1-2 sentence rationale."
        """
        self.logger.info(f"Generating verdict for {state.symbol}")
        
        # Format context for LLM
        context_str = "\n".join([
            f"- {chunk['source']}: {chunk['text'][:100]}..."
            for chunk in state.context[:3]
        ])
        
        prompt = f"""
        Signal: {state.signal}
        Symbol: {state.symbol}
        Entry Price: ${state.entry_price}
        
        Context:
        {context_str}
        
        Generate a trading verdict (BULLISH/BEARISH/NEUTRAL) with brief rationale.
        """
        
        response = self.verdict_llm.invoke(prompt)
        state.verdict = response.content
        
        self.logger.info(f"Verdict: {state.verdict}")
        
        return state
    
    def _node_grader(self, state: OrchestratorState) -> OrchestratorState:
        """Validate verdict against context (self-correcting).
        
        Input: verdict + context
        Output: grader_approved (bool), grader_feedback (str)
        
        Grader prompt:
            "Verdict: {verdict}
             Context: {context}
             
             Is this verdict supported by the context?
             Answer: YES/NO
             Feedback: ..."
        """
        self.logger.info(f"Grading verdict for {state.symbol}")
        
        context_str = "\n".join([
            f"- {chunk['text'][:100]}..."
            for chunk in state.context[:3]
        ])
        
        prompt = f"""
        Verdict: {state.verdict}
        
        Supporting Context:
        {context_str}
        
        Is this verdict logically supported by the context?
        Answer YES or NO with brief explanation.
        """
        
        response = self.grader_llm.invoke(prompt)
        grader_text = response.content
        
        # Parse response
        is_approved = "YES" in grader_text.upper()
        state.grader_approved = is_approved
        state.grader_feedback = grader_text
        state.attempts += 1
        
        self.logger.info(f"Grader: {'APPROVED' if is_approved else 'REJECTED'} (attempt {state.attempts})")
        
        return state
    
    def _grader_decision(self, state: OrchestratorState) -> str:
        """Route based on grader verdict.
        
        Returns: "pass", "retry", or "reject"
        """
        if state.grader_approved:
            return "pass"
        elif state.attempts < 3:
            return "retry"
        else:
            state.rejection_reason = "Max retry attempts exceeded"
            return "reject"
    
    def _node_risk_veto(self, state: OrchestratorState) -> OrchestratorState:
        """Run Shield Agent veto gates.
        
        Input: verdict (approved by grader)
        Output: shield_approved, position_size, stop_loss
        """
        self.logger.info(f"Running risk veto for {state.symbol}")
        
        # Query MCP tools
        atr_response = self._call_mcp("get_atr", {"symbol": state.symbol})
        atr = atr_response['atr']
        
        vol_response = self._call_mcp("get_volatility", {"symbol": state.symbol})
        volatility = vol_response['volatility_annual']
        
        adv_response = self._call_mcp("get_adv", {"symbol": state.symbol})
        adv_20 = adv_response['adv']
        vol_today = adv_response['volume_today']
        
        # Run veto gates
        veto_response = self._call_mcp(
            "evaluate_risk_veto_gates",
            {
                "entry_price": state.entry_price,
                "atr": atr,
                "atr_multiplier": 2.0,
                "account_capital": self.config.execution.account_capital,
                "max_risk_pct": self.config.execution.max_risk_per_trade,
                "current_qty": 0,  # Placeholder
                "adv_20": adv_20,
                "volume_today": vol_today,
                "volatility": volatility
            }
        )
        
        state.shield_approved = veto_response['approved']
        state.position_size = veto_response['position_size']
        state.stop_loss = veto_response['stop_loss']
        
        if not state.shield_approved:
            state.rejection_reason = "; ".join(veto_response['veto_reasons'])
        
        self.logger.info(f"Shield Agent: {'APPROVED' if state.shield_approved else 'REJECTED'}")
        
        return state
    
    def _risk_decision(self, state: OrchestratorState) -> str:
        """Route based on Shield Agent approval.
        
        Returns: "pass" or "reject"
        """
        return "pass" if state.shield_approved else "reject"
    
    def _node_execute(self, state: OrchestratorState) -> OrchestratorState:
        """Submit trade to Alpaca.
        
        Input: position_size, entry_price
        Output: execution_id
        """
        self.logger.info(f"Executing trade: {state.signal} {state.position_size} {state.symbol}")
        
        try:
            order = self._submit_alpaca_order(
                symbol=state.symbol,
                qty=state.position_size,
                side=state.signal.lower(),
                stop_price=state.stop_loss
            )
            
            state.execution_id = order.id
            self.logger.info(f"Order submitted: {state.execution_id}")
            
        except Exception as e:
            state.rejection_reason = f"Execution error: {str(e)}"
            self.logger.error(state.rejection_reason)
        
        return state
    
    def _node_fallback(self, state: OrchestratorState) -> OrchestratorState:
        """Fallback: no trade executed.
        
        Log reason and continue monitoring.
        """
        self.logger.warning(f"Fallback for {state.symbol}: {state.rejection_reason}")
        
        return state
    
    def _call_mcp(self, tool_name: str, params: Dict) -> Dict:
        """Call FastMCP tool (placeholder).
        
        Real implementation would use JSON-RPC client.
        """
        # Placeholder: real implementation calls MCP server
        return {}
    
    def _submit_alpaca_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        stop_price: float
    ) -> Dict:
        """Submit order to Alpaca (placeholder).
        
        Args:
            symbol: Ticker.
            qty: Shares.
            side: "buy" or "sell".
            stop_price: Stop loss.
        
        Returns:
            Order object with ID.
        """
        # Placeholder: real implementation uses Alpaca API
        return {'id': 'order_123'}
    
    def invoke(self, initial_state: OrchestratorState) -> OrchestratorState:
        """Run state machine.
        
        Args:
            initial_state: Initial input state.
        
        Returns:
            Final state with execution result.
        """
        result = self.graph.invoke(initial_state)
        return result
```

---

## 6. Veto Ledger & Audit Trail

### 6.1 Module: `execution/veto_ledger.py`

**Class: `VetoLedger`**

```python
class VetoLedger:
    """Comprehensive audit trail for all decisions.
    
    Methods:
        record_veto: Log rejection reason.
        get_veto_stats: Analyze rejection patterns.
        get_active_trades: List live positions.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
        self.ledger_path = f"{config.execution.ledger_dir}/veto_ledger.parquet"
        
        # Initialize Parquet schema
        self.schema = pa.schema([
            ('timestamp', pa.timestamp('ns')),
            ('symbol', pa.string()),
            ('signal', pa.string()),
            ('entry_price', pa.float64()),
            ('veto_reason', pa.string()),
            ('veto_gate', pa.string()),  # Which gate rejected
            ('dsr', pa.float64()),
            ('position_size', pa.int32()),
            ('execution_id', pa.string())
        ])
    
    def record_veto(
        self,
        symbol: str,
        signal: str,
        entry_price: float,
        veto_reason: str,
        veto_gate: str,
        dsr: float = None,
        position_size: int = 0,
        execution_id: str = ""
    ) -> None:
        """Record veto decision.
        
        Args:
            symbol: Ticker.
            signal: "BUY" or "SELL".
            entry_price: Entry price.
            veto_reason: Why rejected.
            veto_gate: Which gate rejected ("grader", "shield", "execution").
            dsr: Deflated Sharpe Ratio (if from evaluation).
            position_size: Intended position size.
            execution_id: Order ID (if executed).
        """
        record = {
            'timestamp': pd.Timestamp.now(),
            'symbol': symbol,
            'signal': signal,
            'entry_price': entry_price,
            'veto_reason': veto_reason,
            'veto_gate': veto_gate,
            'dsr': dsr or 0.0,
            'position_size': position_size,
            'execution_id': execution_id
        }
        
        # Append to Parquet
        table = pa.Table.from_pylist([record], schema=self.schema)
        
        if os.path.exists(self.ledger_path):
            existing = pq.read_table(self.ledger_path)
            combined = pa.concat_tables([existing, table])
            pq.write_table(combined, self.ledger_path)
        else:
            pq.write_table(table, self.ledger_path)
        
        self.logger.info(f"Recorded veto: {symbol} {signal} ({veto_gate})")
    
    def get_veto_stats(self, window_days: int = 7) -> Dict:
        """Analyze veto patterns.
        
        Returns:
            {
                'total_vetoes': int,
                'top_gates': [(gate, count), ...],
                'top_reasons': [(reason, count), ...],
                'symbol_vetoes': {symbol: count, ...}
            }
        """
        if not os.path.exists(self.ledger_path):
            return {'total_vetoes': 0}
        
        df = pq.read_table(self.ledger_path).to_pandas()
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Filter recent
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=window_days)
        df = df[df['timestamp'] > cutoff]
        
        return {
            'total_vetoes': len(df),
            'top_gates': df['veto_gate'].value_counts().head(5).to_dict(),
            'top_reasons': df['veto_reason'].value_counts().head(5).to_dict(),
            'symbol_vetoes': df['symbol'].value_counts().to_dict()
        }
```

---

## 7. Implementation Checklist - Phase 5

### Week 1-2: FastMCP & Entity Handling

- [ ] **Day 1-2**: FastMCP server setup
  - [ ] Initialize FastMCP server
  - [ ] Register risk management tools (Kelly, slippage, veto gates)
  - [ ] Unit tests: `test_mcp_server.py`

- [ ] **Day 2-3**: Market data tools
  - [ ] Register market data tools (price, volume, ATR)
  - [ ] Register portfolio tools (position, metrics)
  - [ ] Integration with Alpaca API

- [ ] **Day 3-4**: Entity anonymization
  - [ ] Implement spaCy NER pipeline
  - [ ] Build ticker mapping
  - [ ] Test masking/deanonymization

- [ ] **Day 4-5**: RAG engine
  - [ ] Late chunking implementation
  - [ ] Sentence-transformers embedding
  - [ ] Faiss index + retrieval

### Week 3: LangGraph & Orchestration

- [ ] **Day 6-7**: LangGraph setup
  - [ ] Define OrchestratorState
  - [ ] Build state machine graph
  - [ ] Unit tests: `test_state_machine.py`

- [ ] **Day 7-8**: Node implementations
  - [ ] Verdict Engine node (LLM generation)
  - [ ] Grader node (validation)
  - [ ] Risk Veto node (Shield Agent)
  - [ ] Execute + Fallback nodes

- [ ] **Day 8-9**: Integration
  - [ ] MCP ↔ LangGraph integration
  - [ ] Entity anonymization flow
  - [ ] End-to-end tests

- [ ] **Day 9-10**: Monitoring & optimization
  - [ ] Veto ledger implementation
  - [ ] Performance profiling
  - [ ] All tests 85%+ coverage

---

## 8. Success Criteria

| Criterion | Test | Expected |
|-----------|------|----------|
| FastMCP startup | `test_mcp_server_init()` | ✓ Server listening |
| Tool registration | `test_tool_schemas()` | ✓ 30+ tools registered |
| Entity masking | `test_entity_masking()` | ✓ "Apple" → "[COMPANY_A]" |
| RAG retrieval | `test_rag_retrieval()` | ✓ Top-k context returned |
| LangGraph flow | `test_graph_execution()` | ✓ State transitions correct |
| Verdict generation | `test_verdict_engine()` | ✓ LLM returns verdict |
| Grading logic | `test_grader_node()` | ✓ Validates verdict |
| Risk veto | `test_risk_veto_node()` | ✓ Rejects bad trades |
| Execution | `test_execute_node()` | ✓ Order submitted to Alpaca |
| Ledger tracking | `test_veto_ledger()` | ✓ Decisions logged |

---

## 9. Performance Targets

| Component | Target |
|-----------|--------|
| MCP tool latency | < 10ms per call |
| Entity masking | < 100ms per 1000 chars |
| RAG retrieval | < 200ms for top-5 |
| LangGraph cycle | < 5 seconds (LLM dominant) |
| Alpaca submission | < 100ms |
| Full decision pipeline | < 10 seconds |

---

## 10. Integration with Phases 1-4 & Handoff to Phase 6

### 10.1 Phase Dependencies

- **Phase 1**: Config, logging, exceptions
- **Phase 2**: Feature engine, Shield Agent
- **Phase 3**: Tournament results (for hyperparameters)
- **Phase 4**: DSR thresholds, promotion registry

### 10.2 Outputs for Phase 6 (Dashboard)

- Veto ledger (parquet format)
- Trade log + fills
- KPI metrics (Sharpe, win rate, max drawdown)
- Real-time position updates

---

## 11. Deliverables Summary - Phase 5

### Codebase
- [ ] `/new_pipeline/execution/mcp_server.py` (400+ lines)
- [ ] `/new_pipeline/execution/entity_anonymizer.py` (250+ lines)
- [ ] `/new_pipeline/execution/rag_engine.py` (300+ lines)
- [ ] `/new_pipeline/execution/state_machine.py` (500+ lines)
- [ ] `/new_pipeline/execution/veto_ledger.py` (150+ lines)
- [ ] 100+ unit tests + benchmarks

### Live Capabilities
- [ ] FastMCP server running (30+ tools)
- [ ] Real-time data feed from Alpaca
- [ ] Entity anonymization working
- [ ] LangGraph state machine orchestrating
- [ ] Veto ledger tracking all decisions

### Performance
- [ ] MCP tools <10ms latency
- [ ] Full pipeline <10 seconds
- [ ] Alpaca integration tested
- [ ] 85%+ test coverage

---

**Next**: After Phase 5 completion, proceed to [Phase 6: Dashboard & Monitoring](PHASE_6_SPECIFICATION.md) (to be created).

**Previous Phases**:
- [Phase 1: Core Pipeline Infrastructure](PHASE_1_SPECIFICATION.md)
- [Phase 2: Vectorized Quant Engine & Shields](PHASE_2_SPECIFICATION.md)
- [Phase 3: Tournament Backtesting & Model Selection](PHASE_3_SPECIFICATION.md)
- [Phase 4: Statistical Evaluation & Promotion](PHASE_4_SPECIFICATION.md)

```

---

### File: `docs/PHASE_2_SPECIFICATION.md`

```markdown
# Phase 2: Vectorized Quant Engine & Numba Shields - Detailed Specification

**Duration**: 2 weeks  
**Target Date**: Complete by mid-June (after Phase 1)  
**Success Criteria**: All features vectorized; GPU kernels passing benchmarks; Shield Agent <100µs latency; 85%+ test coverage

---

## 1. Phase 2 Architecture Overview

### 1.1 System Context (Integration with Phase 1)

```
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1 (Complete): Config, Logging, Exceptions, Testing  │
├─────────────────────────────────────────────────────────────┤
│                           │                                  │
│                           ▼                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PHASE 2: VECTORIZED QUANT ENGINE & SHIELDS        │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │                                                      │   │
│  │  LAYER 1: POLARS LAZY-FRAME VECTORIZATION          │   │
│  │  ├─ Rolling window calculations                     │   │
│  │  ├─ Volatility regime tagging                       │   │
│  │  ├─ Log return transforms                           │   │
│  │  └─ Factor normalization                            │   │
│  │                                                      │   │
│  │  LAYER 2: CUDA/NUMBA GPU KERNELS                    │   │
│  │  ├─ Spread calculations (high-low)                  │   │
│  │  ├─ Amihud illiquidity metric                       │   │
│  │  ├─ Non-cash skewness (NCSKEW)                      │   │
│  │  ├─ Down/Up volume asymmetry (DUVOL)               │   │
│  │  └─ Correlation matrices                            │   │
│  │                                                      │   │
│  │  LAYER 3: THE SHIELD AGENT (NUMBA JIT)             │   │
│  │  ├─ Position sizing logic (Kelly-like)              │   │
│  │  ├─ Stop loss validation (2×ATR)                    │   │
│  │  ├─ Dynamic slippage calculation                    │   │
│  │  ├─ Liquidity checks (ADV coverage)                 │   │
│  │  ├─ Portfolio reconciliation                        │   │
│  │  └─ Microsecond latency execution                   │   │
│  │                                                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                  │
│         Uses Phase 1: Config, Logger, Exceptions             │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

```
/new_pipeline/features/
├── __init__.py
├── base.py                    # Abstract FeatureEngine
├── registry.py                # Feature metadata tracking
├── polars_engine.py           # ✨ NEW: Polars vectorized ops
├── gpu_kernels.py             # ✨ NEW: CUDA @cuda.jit functions
├── shields.py                 # ✨ NEW: Shield Agent (Numba JIT)
├── slippage.py                # ✨ NEW: Dynamic slippage model
└── tests/
    ├── test_polars_features.py
    ├── test_gpu_kernels.py
    ├── test_shield_agent.py
    ├── test_slippage.py
    └── benchmarks/
        ├── bench_polars_vs_pandas.py
        ├── bench_gpu_kernels.py
        └── bench_shield_agent_latency.py
```

---

## 2. Polars Vectorized Feature Engine

### 2.1 Architecture & Principle

**Principle**: Replace all pandas `.apply()` loops with Polars lazy-frame expressions. Defer computation until `.collect()`.

```python
# ❌ PANDAS (Slow - row-by-row):
for idx, row in df.iterrows():
    atr[idx] = calculate_atr(row)

# ✅ POLARS (Fast - vectorized):
df = df.with_columns(
    pl.col('close').rolling_mean(14).alias('atr')
)
```

### 2.2 Module: `features/polars_engine.py`

**File Structure**:
```
PolarsFeatureEngine
├── __init__()
├── load_raw_vault() → LazyFrame
├── compute_returns() → LazyFrame
├── compute_rolling_indicators() → LazyFrame
├── compute_microstructure() → LazyFrame
├── compute_volatility_regimes() → LazyFrame
├── normalize_features() → LazyFrame
├── execute_pipeline() → DataFrame (collected)
└── to_parquet() → Path
```

### 2.3 Feature Functions (Detailed Signatures)

#### 2.3.1 Basic Technical Indicators

**Function: `compute_returns()`**
```python
def compute_returns(
    df: pl.LazyFrame,
    price_col: str = "close",
    log_returns: bool = True
) -> pl.LazyFrame:
    """Compute returns (arithmetic or log).
    
    Args:
        df: Lazy DataFrame with OHLCV data.
        price_col: Column name to compute returns from.
        log_returns: If True, use log returns; else simple.
    
    Returns:
        DataFrame with 'returns' column appended.
    
    Formula:
        - Arithmetic: returns[t] = (price[t] - price[t-1]) / price[t-1]
        - Log: returns[t] = ln(price[t] / price[t-1])
    
    Notes:
        - First row is NaN (no prior price).
        - Shift by -1 to align signal at t+1 (no look-ahead).
    """
    if log_returns:
        return df.with_columns(
            pl.col(price_col).log().diff().alias('returns')
        )
    else:
        return df.with_columns(
            (pl.col(price_col).pct_change()).alias('returns')
        )
```

**Function: `compute_atr()`**
```python
def compute_atr(
    df: pl.LazyFrame,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    period: int = 14
) -> pl.LazyFrame:
    """Compute Average True Range (Wilder's smoothing).
    
    Args:
        df: Lazy DataFrame with OHLCV data.
        period: Lookback window (default 14).
    
    Returns:
        DataFrame with 'atr' column.
    
    Formula:
        TR[t] = max(high[t] - low[t], |high[t] - close[t-1]|, |low[t] - close[t-1]|)
        ATR[t] = SMA(TR, period) using Wilder's smoothing (cumsum / n)
    
    Internal:
        - Use Polars' rolling_mean with window=period
        - First period-1 rows are NaN
    """
    # True Range calculation
    tr = pl.max_horizontal(
        pl.col(high_col) - pl.col(low_col),
        (pl.col(high_col) - pl.col(close_col).shift(1)).abs(),
        (pl.col(low_col) - pl.col(close_col).shift(1)).abs()
    )
    
    return df.with_columns(
        tr.rolling_mean(period).alias('atr')
    )
```

**Function: `compute_adv()`**
```python
def compute_adv(
    df: pl.LazyFrame,
    volume_col: str = "volume",
    high_col: str = "high",
    low_col: str = "low",
    period: int = 20
) -> pl.LazyFrame:
    """Compute Average Dollar Volume (ADV).
    
    Args:
        period: Lookback window (default 20).
    
    Returns:
        DataFrame with 'adv_20' column.
    
    Formula:
        ADV[t] = SMA((high[t] + low[t]) / 2 * volume[t], period)
    
    Notes:
        - Used for liquidity checks in Shield Agent
        - First period-1 rows are NaN
    """
    avg_price = (pl.col(high_col) + pl.col(low_col)) / 2
    dollar_volume = avg_price * pl.col(volume_col)
    
    return df.with_columns(
        dollar_volume.rolling_mean(period).alias('adv_20')
    )
```

#### 2.3.2 Volatility & Regime Detection

**Function: `compute_rolling_volatility()`**
```python
def compute_rolling_volatility(
    df: pl.LazyFrame,
    returns_col: str = "returns",
    window: int = 15,
    annualize: bool = True
) -> pl.LazyFrame:
    """Compute rolling volatility (standard deviation).
    
    Args:
        window: Lookback period (default 15 = 15-minute bars).
        annualize: If True, scale by √252 (trading days).
    
    Returns:
        DataFrame with 'volatility' column.
    
    Formula:
        vol[t] = std(returns[t-window:t])
        vol_annual[t] = vol[t] * √252 (if annualize)
    
    Usage:
        - Determine volatility regime (low, normal, high)
        - Scale position size in high-vol environments
    """
    scale = np.sqrt(252) if annualize else 1.0
    
    return df.with_columns(
        pl.col(returns_col).rolling_std(window).mul(scale).alias('volatility')
    )
```

**Function: `tag_volatility_regimes()`**
```python
def tag_volatility_regimes(
    df: pl.LazyFrame,
    volatility_col: str = "volatility",
    percentile_threshold: float = 0.80
) -> pl.LazyFrame:
    """Tag high/normal volatility regimes.
    
    Args:
        volatility_col: Column containing rolling volatility.
        percentile_threshold: If vol > this percentile, tag as 'high'.
    
    Returns:
        DataFrame with 'regime' column: 0 (normal) or 1 (high).
    
    Formula:
        threshold = percentile(volatility, 80)
        regime[t] = 1 if volatility[t] > threshold else 0
    
    Notes:
        - Used to dynamically adjust lookback windows
        - High vol → shorter windows (recent > history)
    """
    # Compute 80th percentile of volatility
    threshold = df.select(pl.col(volatility_col).quantile(percentile_threshold))
    
    return df.with_columns(
        (pl.col(volatility_col) > threshold).cast(pl.Int8).alias('regime')
    )
```

#### 2.3.3 Microstructure Features

**Function: `compute_spreads()`**
```python
def compute_spreads(
    df: pl.LazyFrame,
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close"
) -> pl.LazyFrame:
    """Compute bid-ask spread as percent of mid-price.
    
    Args:
        high_col, low_col, close_col: OHLC columns.
    
    Returns:
        DataFrame with 'spread_pct' column.
    
    Formula:
        mid = (high + low) / 2
        spread = (high - low) / mid * 100  [basis points]
    
    Notes:
        - High spread → illiquid, larger slippage
        - Used in Shield Agent slippage calculation
    """
    mid = (pl.col(high_col) + pl.col(low_col)) / 2
    spread = (pl.col(high_col) - pl.col(low_col)) / mid * 100
    
    return df.with_columns(spread.alias('spread_pct'))
```

**Function: `compute_amihud_illiquidity()`**
```python
def compute_amihud_illiquidity(
    df: pl.LazyFrame,
    returns_col: str = "returns",
    volume_col: str = "volume",
    high_col: str = "high",
    low_col: str = "low"
) -> pl.LazyFrame:
    """Compute Amihud illiquidity measure.
    
    Args:
        returns_col: Log returns column.
        volume_col: Trading volume.
    
    Returns:
        DataFrame with 'amihud' column.
    
    Formula:
        amihud[t] = |returns[t]| / (volume[t] * price[t])
        Higher value → more illiquid
    
    Interpretation:
        - amihud < 0.001: Highly liquid
        - 0.001 - 0.01: Normal liquidity
        - > 0.01: Illiquid, large slippage expected
    
    GPU Implementation:
        - Computed in @cuda.jit kernel for speed
    """
    mid_price = (pl.col(high_col) + pl.col(low_col)) / 2
    
    return df.with_columns(
        (pl.col(returns_col).abs() / (pl.col(volume_col) * mid_price))
        .alias('amihud')
    )
```

### 2.4 Pipeline Orchestration

**Function: `execute_feature_pipeline()`**
```python
def execute_feature_pipeline(
    raw_vault_path: str,
    sector: str,
    target_vault_path: str,
    config: AppConfig
) -> None:
    """End-to-end feature compilation pipeline.
    
    Args:
        raw_vault_path: Path to RAW_VAULT_DIR/sector={sector}/
        sector: Sector name (e.g., "Technology").
        target_vault_path: Output PROCESSED_VAULT_DIR/sector={sector}/
        config: AppConfig for feature settings.
    
    Flow:
        1. Load all Parquet files as LazyFrame (lazy evaluation)
        2. Compute returns (log & arithmetic)
        3. Compute rolling indicators (ATR, ADV, volatility)
        4. Tag volatility regimes
        5. Compute microstructure (spreads, Amihud)
        6. Normalize features (z-score, min-max as needed)
        7. Collect → persist to Parquet
    
    Notes:
        - All operations are lazy until .collect()
        - GPU kernels triggered during collection
        - Memory efficient: processes in row groups
    """
    logger = get_logger(__name__)
    
    # Load raw vault
    df = pl.scan_parquet(f"{raw_vault_path}/*.parquet")
    
    # Apply transformations (all lazy)
    df = compute_returns(df)
    df = compute_atr(df)
    df = compute_adv(df)
    df = compute_rolling_volatility(df)
    df = tag_volatility_regimes(df)
    df = compute_spreads(df)
    df = compute_amihud_illiquidity(df)
    
    # Collect & persist
    logger.info(f"Collecting features for {sector}...")
    result = df.collect()
    
    result.write_parquet(
        f"{target_vault_path}/{sector}_features.parquet",
        row_group_size=config.data.row_group_size
    )
    
    logger.info(f"Features written to {target_vault_path}")
```

---

## 3. GPU Kernels via CUDA & Numba

### 3.1 Architecture: From CPU to GPU

```
CPU (Polars)          GPU (CUDA Kernels)
─────────────────────────────────────────
OHLCV data       ──→  Copy to VRAM
(Parquet)            ↓
                  Execute @cuda.jit kernels
                  ├─ Spread calc
                  ├─ Amihud illiquidity
                  ├─ NCSKEW (skewness)
                  ├─ DUVOL (asymmetry)
                  └─ Correlations
                     ↓
Result (GPU mem) ───← Copy back to CPU
(np.ndarray)         ↓
                  Convert to Polars
                  Append to DataFrame
```

### 3.2 Module: `features/gpu_kernels.py`

**Header & Imports**:
```python
import numpy as np
from numba import cuda, jit, prange
import logging

logger = get_logger(__name__)

# CUDA configuration
THREADS_PER_BLOCK = 256
BLOCKS_PER_GRID = 128
```

#### 3.2.1 GPU Kernel: Spread Calculation

**Function: `kernel_spreads()`**
```python
@cuda.jit
def kernel_spreads(highs, lows, closes, out_spreads):
    """CUDA kernel: Compute bid-ask spreads (high-low normalized).
    
    Args:
        highs: [n] array of high prices
        lows: [n] array of low prices
        closes: [n] array of close prices (for NaN checking)
        out_spreads: [n] output array (preallocated on GPU)
    
    Formula (per thread):
        mid = (high + low) / 2
        spread_pct = (high - low) / mid * 100
        If any input is NaN: output NaN
    
    Thread Config:
        - 1 thread per element
        - Grid-stride loop for large arrays
    
    Memory:
        - Read-only: highs, lows, closes
        - Write: out_spreads
    """
    i = cuda.grid(1)
    
    if i < highs.shape[0]:
        high = highs[i]
        low = lows[i]
        
        if np.isnan(high) or np.isnan(low):
            out_spreads[i] = np.nan
        else:
            mid = (high + low) / 2.0
            if mid > 0:
                out_spreads[i] = (high - low) / mid * 100.0
            else:
                out_spreads[i] = np.nan
```

**Wrapper: `compute_spreads_gpu()`**
```python
def compute_spreads_gpu(
    highs: np.ndarray,
    lows: np.ndarray,
    closes: np.ndarray,
    fallback_to_cpu: bool = True
) -> np.ndarray:
    """Compute spreads on GPU; fallback to CPU if needed.
    
    Args:
        highs, lows, closes: CPU numpy arrays
        fallback_to_cpu: If True, use CPU if GPU fails
    
    Returns:
        Spreads array on CPU
    
    Memory Management:
        - Check VRAM availability
        - Copy arrays to GPU
        - Execute kernel
        - Copy results back to CPU
        - Free GPU memory
    """
    try:
        # Check VRAM
        free_vram = cuda.current_context().get_memory_info()[0]
        required = highs.nbytes * 4  # 4 arrays
        
        if free_vram < required:
            if fallback_to_cpu:
                logger.warning(f"Insufficient VRAM ({free_vram/1e9:.1f}GB); using CPU")
                return compute_spreads_cpu(highs, lows, closes)
            else:
                raise CUDAOutOfMemoryError(...)
        
        # Allocate GPU memory
        d_highs = cuda.to_device(highs)
        d_lows = cuda.to_device(lows)
        d_closes = cuda.to_device(closes)
        d_spreads = cuda.device_array_like(highs)
        
        # Configure grid/block
        threads_per_block = 256
        blocks_per_grid = (highs.shape[0] + threads_per_block - 1) // threads_per_block
        
        # Execute
        kernel_spreads[blocks_per_grid, threads_per_block](
            d_highs, d_lows, d_closes, d_spreads
        )
        
        # Copy back
        result = d_spreads.copy_to_host()
        
        # Free GPU memory
        d_highs.free()
        d_lows.free()
        d_closes.free()
        d_spreads.free()
        
        return result
        
    except CudaAPIError as e:
        if fallback_to_cpu:
            logger.warning(f"CUDA error: {e}; falling back to CPU")
            return compute_spreads_cpu(highs, lows, closes)
        else:
            raise
```

#### 3.2.2 GPU Kernel: Amihud Illiquidity

**Function: `kernel_amihud()`**
```python
@cuda.jit
def kernel_amihud(returns, volumes, highs, lows, out_amihud):
    """CUDA kernel: Compute Amihud illiquidity measure.
    
    Args:
        returns: [n] log returns
        volumes: [n] daily volumes
        highs, lows: [n] OHLC prices for mid calculation
        out_amihud: [n] output
    
    Formula (per thread):
        mid = (high + low) / 2
        amihud[i] = |returns[i]| / (volume[i] * mid[i])
    
    Performance:
        - Single pass, O(n) complexity
        - Suitable for large arrays (millions of rows)
    """
    i = cuda.grid(1)
    
    if i < returns.shape[0]:
        ret = returns[i]
        vol = volumes[i]
        high = highs[i]
        low = lows[i]
        
        if np.isnan(ret) or vol <= 0:
            out_amihud[i] = np.nan
        else:
            mid = (high + low) / 2.0
            if mid > 0:
                out_amihud[i] = np.abs(ret) / (vol * mid)
            else:
                out_amihud[i] = np.nan
```

#### 3.2.3 GPU Kernel: Non-Cash Skewness (NCSKEW)

**Function: `kernel_ncskew()`**
```python
@cuda.jit
def kernel_ncskew(returns, window, out_ncskew):
    """CUDA kernel: Compute non-cash skewness (downside asymmetry).
    
    Args:
        returns: [n] log returns
        window: lookback period (e.g., 20 days)
        out_ncskew: [n] output
    
    Formula (per thread i, for i >= window):
        mean = avg(returns[i-window:i])
        std = stddev(returns[i-window:i])
        downside_sq = sum(min(returns[j] - mean, 0)^2 for j in window)
        upside_sq = sum(max(returns[j] - mean, 0)^2 for j in window)
        NCSKEW[i] = -(downside_sq^(3/2) - upside_sq^(3/2)) / (std^3 * n)
    
    Interpretation:
        - NCSKEW < 0: Negative skew, downside tail risk (bad)
        - NCSKEW > 0: Positive skew, upside potential (good)
    
    Implementation Note:
        - Expensive: requires rolling window statistics
        - Offload to GPU for speed
    """
    i = cuda.grid(1)
    
    if i >= window and i < returns.shape[0]:
        # Extract window
        window_start = i - window
        window_returns = returns[window_start:i]
        
        # Compute mean, std
        mean = 0.0
        for j in range(window):
            mean += window_returns[j]
        mean /= window
        
        # Compute variance
        var = 0.0
        for j in range(window):
            diff = window_returns[j] - mean
            var += diff * diff
        var /= window
        std = np.sqrt(var)
        
        # Compute skewness (downside vs upside)
        down_sum = 0.0
        up_sum = 0.0
        for j in range(window):
            diff = window_returns[j] - mean
            if diff < 0:
                down_sum += diff * diff
            else:
                up_sum += diff * diff
        
        down_sum = np.power(down_sum, 1.5)
        up_sum = np.power(up_sum, 1.5)
        
        denom = np.power(std, 3.0) * window
        if denom > 0:
            out_ncskew[i] = -(down_sum - up_sum) / denom
        else:
            out_ncskew[i] = np.nan
    else:
        out_ncskew[i] = np.nan
```

#### 3.2.4 GPU Kernel: Down/Up Volume Asymmetry (DUVOL)

**Function: `kernel_duvol()`**
```python
@cuda.jit
def kernel_duvol(returns, volumes, window, out_duvol):
    """CUDA kernel: Compute down/up volume asymmetry.
    
    Args:
        returns: [n] log returns
        volumes: [n] volumes
        window: lookback period
        out_duvol: [n] output
    
    Formula (per thread i):
        down_vol = sum(volume[j] for j if returns[j] < 0)
        up_vol = sum(volume[j] for j if returns[j] > 0)
        DUVOL[i] = log(down_vol / up_vol)
    
    Interpretation:
        - DUVOL > 0: More volume on down days (sell pressure)
        - DUVOL < 0: More volume on up days (buy pressure)
    
    Notes:
        - Used to detect selling pressure (bearish signal)
    """
    i = cuda.grid(1)
    
    if i >= window and i < returns.shape[0]:
        window_start = i - window
        
        down_vol = 0.0
        up_vol = 0.0
        
        for j in range(window_start, i):
            if returns[j] < 0:
                down_vol += volumes[j]
            elif returns[j] > 0:
                up_vol += volumes[j]
        
        if up_vol > 0:
            out_duvol[i] = np.log(down_vol / up_vol)
        else:
            out_duvol[i] = np.nan
    else:
        out_duvol[i] = np.nan
```

### 3.3 GPU Kernel Testing & Benchmarking

**File: `tests/benchmarks/bench_gpu_kernels.py`**

```python
import pytest
import numpy as np
import time
from features.gpu_kernels import (
    compute_spreads_gpu,
    compute_amihud_gpu,
    compute_ncskew_gpu,
    compute_duvol_gpu
)
from features.polars_engine import (  # CPU equivalents
    compute_spreads_cpu,
    compute_amihud_cpu,
    compute_ncskew_cpu,
    compute_duvol_cpu
)

@pytest.mark.benchmark
def test_spreads_gpu_vs_cpu(benchmark):
    """Benchmark GPU vs CPU spread calculation."""
    n = 10_000_000
    highs = np.random.randn(n).cumsum() + 100
    lows = highs - np.abs(np.random.randn(n))
    closes = (highs + lows) / 2
    
    # GPU
    gpu_time = benchmark(
        compute_spreads_gpu,
        highs, lows, closes
    )
    
    # CPU (for comparison)
    cpu_start = time.time()
    cpu_result = compute_spreads_cpu(highs, lows, closes)
    cpu_time = time.time() - cpu_start
    
    # GPU should be 10-50x faster
    speedup = cpu_time / gpu_time
    print(f"Speedup: {speedup:.1f}x")
    assert speedup > 10, f"GPU speedup too low: {speedup:.1f}x"

@pytest.mark.benchmark
def test_amihud_gpu_vs_cpu(benchmark):
    """Benchmark GPU Amihud calculation."""
    n = 1_000_000
    returns = np.random.randn(n) * 0.02
    volumes = np.random.randint(1e6, 1e7, n)
    highs = np.random.randn(n).cumsum() + 100
    lows = highs - np.abs(np.random.randn(n))
    
    gpu_time = benchmark(
        compute_amihud_gpu,
        returns, volumes, highs, lows
    )
    
    cpu_start = time.time()
    cpu_result = compute_amihud_cpu(returns, volumes, highs, lows)
    cpu_time = time.time() - cpu_start
    
    speedup = cpu_time / gpu_time
    assert speedup > 5, f"GPU speedup too low: {speedup:.1f}x"
```

---

## 4. The Shield Agent: Numba JIT Risk Manager

### 4.1 Architecture

**Principle**: Deterministic risk veto gates executed in microseconds using Numba JIT compilation.

```
ML Signal (probability > threshold)
         │
         ▼
    ┌──────────────────────────────────┐
    │  SHIELD AGENT (Numba @njit)     │
    ├──────────────────────────────────┤
    │                                  │
    │  GATE 1: Stop Loss Validity      │
    │  ├─ stop > 0                     │
    │  ├─ entry > stop                 │
    │  └─ return (VETO if fail)        │
    │                                  │
    │  GATE 2: Position Sizing (Kelly) │
    │  ├─ risk_dist = entry - stop     │
    │  ├─ size = (cap × max_risk) / risk │
    │  ├─ size = min(size, max_qty)    │
    │  └─ return (VETO if size < 1)    │
    │                                  │
    │  GATE 3: Liquidity Check         │
    │  ├─ order_size ≤ 25% ADV         │
    │  └─ return (VETO if fail)        │
    │                                  │
    │  GATE 4: Slippage Estimate       │
    │  ├─ s = c·σ·√(Q/V)               │
    │  ├─ s ≤ 50 bps limit             │
    │  └─ return (VETO if fail)        │
    │                                  │
    │  GATE 5: Portfolio Sync          │
    │  ├─ new_qty = size - current     │
    │  ├─ new_qty > 0 (don't overallocate) │
    │  └─ return (VETO if fail)        │
    │                                  │
    └──────────────────────────────────┘
         │
         ├─ ALL GATES PASS → (True, size)
         └─ ANY GATE FAILS → (False, 0)
```

### 4.2 Module: `features/shields.py`

**File: `features/shields.py`**

```python
from numba import njit
import numpy as np
import logging

logger = get_logger(__name__)

# Configuration constants
DEFAULT_ATR_MULTIPLIER = 2.0
DEFAULT_MAX_RISK_PCT = 0.02
DEFAULT_MAX_ORDER_COVERAGE = 0.25
DEFAULT_MAX_SLIPPAGE_BPS = 50.0
SLIPPAGE_CONSTANT = 0.5  # Empirically calibrated
```

#### 4.2.1 Core Shield Agent Function

**Function: `evaluate_risk_veto_gates()`**
```python
@njit(fastmath=True)
def evaluate_risk_veto_gates(
    entry_price: float,
    atr: float,
    atr_multiplier: float,
    account_capital: float,
    max_risk_pct: float,
    current_qty: float,
    adv_20: float,
    volume_today: float,
    volatility: float
) -> tuple:
    """Evaluate all risk gates and return (approved, position_size).
    
    Args:
        entry_price: Entry price for the trade.
        atr: Current ATR (volatility measure).
        atr_multiplier: How many ATRs for stop loss (typically 2.0).
        account_capital: Total available capital.
        max_risk_pct: Max capital at risk per trade (typically 0.02).
        current_qty: Current position size in this ticker (for delta).
        adv_20: 20-day average dollar volume.
        volume_today: Today's observed volume so far.
        volatility: Current volatility (for slippage adjustment).
    
    Returns:
        (approved: bool, position_size: float)
        - If approved: position_size is recommended qty
        - If veto: position_size is 0
    
    Execution Time:
        - Target: < 100 microseconds (all gates)
        - fastmath=True enables CPU optimizations
    
    Veto Reasons (logged separately):
        - "invalid_stop_loss"
        - "insufficient_capital"
        - "order_too_large"
        - "slippage_exceeded"
        - "liquidity_insufficient"
    
    Notes:
        - Deterministic: no random, no external calls
        - GPU-safe: can be launched from CUDA kernels
    """
    
    # GATE 1: Stop Loss Validity
    # ─────────────────────────
    stop_loss = entry_price - (atr_multiplier * atr)
    risk_per_share = entry_price - stop_loss
    
    if risk_per_share <= 0 or entry_price <= 0:
        return (False, 0.0)
    
    if stop_loss <= 0:
        # Veto: stop would be negative
        return (False, 0.0)
    
    # GATE 2: Position Sizing (Kelly-like)
    # ──────────────────────────────────
    capital_at_risk = account_capital * max_risk_pct
    position_size = capital_at_risk / risk_per_share
    
    # Cap by available capital
    max_allowable_qty = account_capital / entry_price
    position_size = min(position_size, max_allowable_qty)
    
    # Floor to avoid fractional shares
    position_size = int(position_size)
    
    if position_size < 1:
        return (False, 0.0)
    
    # GATE 3: Liquidity Check (ADV Coverage)
    # ───────────────────────────────────
    order_size_usd = position_size * entry_price
    max_order_coverage = 0.25  # Don't exceed 25% of ADV
    max_order_usd = adv_20 * max_order_coverage
    
    if order_size_usd > max_order_usd:
        # Veto: order too large relative to liquidity
        return (False, 0.0)
    
    # GATE 4: Dynamic Slippage Estimate
    # ──────────────────────────────────
    # s = c·σ·√(Q/V)
    # where c ≈ 0.5, σ = volatility, Q = order size, V = volume
    
    if volume_today <= 0:
        # Can't estimate slippage without volume data
        slippage_bps = 50.0  # Conservative default
    else:
        ratio = (position_size * entry_price) / volume_today
        slippage_bps = SLIPPAGE_CONSTANT * volatility * np.sqrt(ratio) * 10000
    
    max_slippage_bps = 50.0
    
    if slippage_bps > max_slippage_bps:
        # Veto: estimated slippage exceeds limit
        return (False, 0.0)
    
    # GATE 5: Portfolio Reconciliation
    # ────────────────────────────────
    delta_qty = position_size - current_qty
    
    if delta_qty <= 0:
        # Not adding to position (could be reducing), reject
        return (False, 0.0)
    
    # All gates passed
    return (True, float(position_size))
```

#### 4.2.2 Position Sizing Logic (Kelly-like)

**Function: `calculate_kelly_position_size()`**
```python
@njit(fastmath=True)
def calculate_kelly_position_size(
    win_rate: float,
    win_loss_ratio: float,
    capital: float,
    entry_price: float,
    atr: float,
    atr_multiplier: float
) -> float:
    """Calculate position size using Kelly criterion (modified).
    
    Args:
        win_rate: Probability of trade being profitable.
        win_loss_ratio: Avg win size / avg loss size.
        capital: Total capital.
        entry_price, atr, atr_multiplier: Risk calculation.
    
    Returns:
        Fraction of capital to risk (typically 0.01-0.05).
    
    Formula (Kelly):
        f = (p × b - q) / b
        where p = win_rate, q = 1 - p, b = ratio
        
        Risk fraction = min(f, 0.05)  [cap at 5% for safety]
    
    Notes:
        - Kelly fraction balances growth vs drawdown
        - Often underestimate by 25% for safety (0.75 × Kelly)
    """
    if win_rate <= 0 or win_rate >= 1:
        return 0.01  # Default to 1% risk
    
    q = 1.0 - win_rate
    b = win_loss_ratio
    
    if b <= 0:
        return 0.01
    
    kelly_fraction = (win_rate * b - q) / b
    kelly_fraction = max(kelly_fraction, 0.01)  # Min 1%
    kelly_fraction = min(kelly_fraction, 0.05)  # Max 5%
    
    # Conservative: use 75% of Kelly
    return kelly_fraction * 0.75
```

#### 4.2.3 Volatility Stop Enforcement

**Function: `enforce_volatility_stop()`**
```python
@njit(fastmath=True)
def enforce_volatility_stop(
    entry_price: float,
    current_price: float,
    atr: float,
    atr_multiplier: float,
    trailing_high: float
) -> tuple:
    """Determine if position should be stopped out.
    
    Args:
        entry_price: Entry price of position.
        current_price: Current market price.
        atr: Current ATR.
        atr_multiplier: ATR multiplier for stops (typically 2.0).
        trailing_high: Highest price since entry.
    
    Returns:
        (stopped_out: bool, stop_price: float)
    
    Logic:
        1. Hard stop: If current < entry - 2×ATR → STOP
        2. Trailing stop: If trailed > entry by 1.5×ATR
           AND current < trailing - 0.5×ATR → STOP
    
    Notes:
        - Prevents holding large losses
        - Locks in gains with trailing logic
    """
    hard_stop = entry_price - (atr_multiplier * atr)
    
    # Hard stop hit
    if current_price <= hard_stop:
        return (True, hard_stop)
    
    # Trailing stop logic
    profit_threshold = entry_price + (1.5 * atr)
    trailing_stop = trailing_high - (0.5 * atr)
    
    if trailing_high >= profit_threshold and current_price <= trailing_stop:
        return (True, trailing_stop)
    
    return (False, 0.0)
```

### 4.3 Shield Agent Integration with Live Trader

**Integration Pattern** (in `live_trader.py`):

```python
from features.shields import evaluate_risk_veto_gates, enforce_volatility_stop

def execute_trade_with_shield(
    ticker: str,
    signal_probability: float,
    entry_price: float,
    atr: float,
    current_inventory: dict,
    account_capital: float,
    adv_20: float,
    volume_today: float,
    volatility: float,
    config: AppConfig
):
    """Execute trade only if Shield Agent approves."""
    
    logger = get_logger(__name__)
    current_qty = current_inventory.get(ticker, 0.0)
    
    # Query Shield Agent
    approved, position_size = evaluate_risk_veto_gates(
        entry_price=entry_price,
        atr=atr,
        atr_multiplier=config.execution.atr_stop_multiplier,
        account_capital=account_capital,
        max_risk_pct=config.execution.max_risk_per_trade,
        current_qty=current_qty,
        adv_20=adv_20,
        volume_today=volume_today,
        volatility=volatility
    )
    
    if not approved:
        logger.warning(
            f"[{ticker}] Shield Agent VETO",
            extra={
                "signal_prob": signal_probability,
                "entry": entry_price,
                "reason": "veto_reason_logged_separately"
            }
        )
        # Log to veto ledger
        return False
    
    # Approved: submit order to Alpaca
    logger.info(f"[{ticker}] Shield Agent APPROVED: {position_size} shares")
    
    limit_price = entry_price + (0.1 * atr)
    submit_order_to_alpaca(ticker, position_size, limit_price)
    
    return True
```

---

## 5. Dynamic Slippage Modeling

### 5.1 Module: `features/slippage.py`

**File: `features/slippage.py`**

```python
import numpy as np
from numba import njit
import logging

logger = get_logger(__name__)

# Calibration constants
SLIPPAGE_CONSTANT = 0.5  # Market impact multiplier
BPS_SCALER = 10000.0  # Convert decimal to basis points
```

#### 5.1.1 Hydrodynamic Slippage Model

**Function: `calculate_hydrodynamic_slippage()`**
```python
def calculate_hydrodynamic_slippage(
    order_size_usd: float,
    volatility: float,
    adv_20: float,
    volume_today: float,
    constant: float = SLIPPAGE_CONSTANT
) -> float:
    """Calculate estimated market impact/slippage using hydrodynamic model.
    
    Args:
        order_size_usd: Order size in dollars.
        volatility: Current volatility (σ) as decimal (e.g., 0.02 = 2%).
        adv_20: 20-day average dollar volume.
        volume_today: Volume observed so far today.
        constant: Calibration factor (typically 0.4-0.6).
    
    Returns:
        Slippage in basis points (bps).
    
    Formula:
        S = c · σ · √(Q/V)
        where:
        - Q = order size / ADV (as ratio)
        - V = volume_today / ADV (as ratio, or use 1.0 for default)
        - c = market impact constant
        - σ = volatility
        
        Result in bps = S * 10000
    
    Interpretation:
        - < 10 bps: Highly liquid, minimal slippage
        - 10-25 bps: Normal slippage
        - 25-50 bps: Elevated, reduce size
        - > 50 bps: Illiquid, VETO trade
    
    Calibration Notes:
        - Constant 'c' depends on market microstructure
        - Typically calibrated on historical fill data
        - Higher for illiquid assets, lower for liquid
    """
    if adv_20 <= 0 or volatility <= 0:
        return 50.0  # Conservative default (veto threshold)
    
    # Normalize volume
    volume_ratio = volume_today / adv_20 if volume_today > 0 else 1.0
    
    # Order size ratio
    order_ratio = order_size_usd / adv_20
    
    # Slippage formula
    if volume_ratio <= 0:
        return 50.0
    
    slippage = constant * volatility * np.sqrt(order_ratio / volume_ratio)
    slippage_bps = slippage * BPS_SCALER
    
    return slippage_bps
```

#### 5.1.2 Regime-Specific Slippage Adjustment

**Function: `adjust_slippage_by_regime()`**
```python
@njit(fastmath=True)
def adjust_slippage_by_regime(
    base_slippage_bps: float,
    regime: int,
    regime_multiplier_normal: float = 1.0,
    regime_multiplier_high_vol: float = 2.0
) -> float:
    """Adjust base slippage by volatility regime.
    
    Args:
        base_slippage_bps: Baseline slippage from hydrodynamic model.
        regime: 0 = normal, 1 = high volatility.
        regime_multiplier_normal: Multiplier for normal regime (typically 1.0).
        regime_multiplier_high_vol: Multiplier for high vol (typically 1.5-2.0).
    
    Returns:
        Regime-adjusted slippage in bps.
    
    Logic:
        - In low-volatility regimes, slippage is predictable
        - In high-volatility regimes, slippage spikes
        - Adjust multiplier based on regime tag
    
    Notes:
        - Used in Shield Agent to tighten veto threshold in high-vol
    """
    if regime == 0:
        # Normal regime
        adjusted = base_slippage_bps * regime_multiplier_normal
    else:
        # High volatility regime
        adjusted = base_slippage_bps * regime_multiplier_high_vol
    
    return adjusted
```

#### 5.1.3 Slippage Testing

**File: `tests/test_slippage.py`**

```python
import pytest
from features.slippage import (
    calculate_hydrodynamic_slippage,
    adjust_slippage_by_regime
)

def test_slippage_calculation_baseline():
    """Test slippage under normal conditions."""
    # Baseline: $1M order, 2% volatility, $100M ADV
    slippage = calculate_hydrodynamic_slippage(
        order_size_usd=1e6,
        volatility=0.02,
        adv_20=100e6,
        volume_today=50e6,
        constant=0.5
    )
    
    # Expected: 0.5 * 0.02 * sqrt(1e6 / 100e6 / (50e6 / 100e6))
    #         = 0.5 * 0.02 * sqrt(0.01 / 0.5)
    #         = 0.5 * 0.02 * sqrt(0.02)
    #         = 0.5 * 0.02 * 0.1414 ≈ 0.14 bp
    assert 10 < slippage < 30, f"Unexpected slippage: {slippage}"

def test_slippage_scaling_with_order_size():
    """Verify slippage scales with order size."""
    base_slippage = calculate_hydrodynamic_slippage(
        order_size_usd=1e6,
        volatility=0.02,
        adv_20=100e6,
        volume_today=100e6,
        constant=0.5
    )
    
    # Double order size → slippage should √2 increase
    double_slippage = calculate_hydrodynamic_slippage(
        order_size_usd=2e6,
        volatility=0.02,
        adv_20=100e6,
        volume_today=100e6,
        constant=0.5
    )
    
    ratio = double_slippage / base_slippage
    expected_ratio = np.sqrt(2)
    assert abs(ratio - expected_ratio) < 0.1, f"Ratio {ratio} != {expected_ratio}"

def test_slippage_regime_adjustment():
    """Test regime multipliers."""
    base = 20.0  # 20 bps
    
    normal = adjust_slippage_by_regime(base, regime=0, regime_multiplier_normal=1.0)
    high_vol = adjust_slippage_by_regime(base, regime=1, regime_multiplier_high_vol=2.0)
    
    assert normal == 20.0
    assert high_vol == 40.0
```

---

## 6. Implementation Checklist - Phase 2

### Week 1: Polars & GPU Foundations

- [ ] **Day 1-2**: Polars engine basics
  - [ ] Implement `polars_engine.py` with basic indicators (returns, ATR, ADV)
  - [ ] Unit tests: `test_polars_features.py`
  - [ ] Benchmark Polars vs Pandas (at least 2x speedup)

- [ ] **Day 2-3**: Advanced Polars features
  - [ ] Implement rolling volatility, regime tagging
  - [ ] Implement microstructure (spreads, Amihud)
  - [ ] Integration test: full pipeline

- [ ] **Day 3-4**: GPU kernel setup
  - [ ] Implement `gpu_kernels.py` header & infrastructure
  - [ ] Implement kernel_spreads() + wrapper
  - [ ] Test on GPU with sample data

- [ ] **Day 4-5**: GPU kernel expansion
  - [ ] Implement kernel_amihud()
  - [ ] Implement kernel_ncskew() (expensive)
  - [ ] Implement kernel_duvol()
  - [ ] Unit tests + fallback to CPU handling

### Week 2: Shield Agent & Slippage

- [ ] **Day 6-7**: Shield Agent implementation
  - [ ] Implement `shields.py` core function
  - [ ] Implement all 5 veto gates
  - [ ] Unit tests: `test_shield_agent.py`

- [ ] **Day 7-8**: Shield Agent advanced
  - [ ] Implement Kelly-like position sizing
  - [ ] Implement volatility stop enforcement
  - [ ] Integration tests with mock Alpaca

- [ ] **Day 8-9**: Slippage modeling
  - [ ] Implement `slippage.py` hydrodynamic model
  - [ ] Implement regime adjustments
  - [ ] Unit tests: `test_slippage.py`

- [ ] **Day 9-10**: Performance optimization
  - [ ] GPU kernel benchmarking
  - [ ] Profile Shield Agent latency (target < 100µs)
  - [ ] Fix bottlenecks, add caching

---

## 7. Success Criteria & Benchmarks

### 7.1 Performance Targets

| Component | Metric | Target | Test |
|-----------|--------|--------|------|
| Polars Pipeline | Full feature compilation | 10-50 stocks/sec | `bench_polars_vs_pandas.py` |
| GPU Spreads | Throughput | > 10M ops/sec | `bench_gpu_kernels.py` |
| GPU Amihud | Throughput | > 5M ops/sec | `bench_gpu_kernels.py` |
| GPU NCSKEW | Throughput | > 1M ops/sec | `bench_gpu_kernels.py` |
| Shield Agent | Latency per eval | < 100µs | Numba profiler |
| Slippage Calc | Latency | < 10µs | Numba profiler |

### 7.2 Functional Acceptance

| Criterion | Test | Expected |
|-----------|------|----------|
| Polars lazy evaluation | Feature pipeline test | ✓ All lazy until .collect() |
| GPU kernels fallback | CUDA OOM scenario | ✓ Fallback to CPU works |
| Shield Agent all gates | 5-gate evaluation | ✓ All gates tested + veto'd correctly |
| Slippage matches formula | Unit test | ✓ Within 1% of expected |
| Position sizing Kelly | Unit test | ✓ Correct kelly fraction |
| Volatility stops | Unit test | ✓ Hard & trailing stops work |

### 7.3 Code Quality

| Criterion | Target |
|-----------|--------|
| Test coverage (features/) | ≥ 85% |
| GPU kernel tests | All pass + benchmarked |
| Type hints | 100% (mypy clean) |
| Linting errors | 0 |

---

## 8. Integration Points with Phase 1 & 3

### 8.1 Phase 1 Dependencies

- **Config system**: All feature params read from `AppConfig`
- **Logging**: All operations logged via Phase 1 logger
- **Exceptions**: Use Phase 1 exception hierarchy
- **Retry logic**: Use @retry for API calls
- **Testing framework**: Pytest fixtures from Phase 1

### 8.2 Handoff to Phase 3 (Tournament)

- Feature outputs → ParquetDataIter (zero-copy)
- Shield Agent veto gates → Live execution layer
- Slippage model → Risk simulator in backtest
- GPU kernels available for model training

---

## 9. Quick Reference Commands

```bash
# Run Polars pipeline
python -c "
from features.polars_engine import execute_feature_pipeline
from config import get_config
config = get_config()
execute_feature_pipeline(
    config.data.raw_vault_dir,
    'Technology',
    config.data.processed_vault_dir,
    config
)
"

# Benchmark GPU kernels
pytest tests/benchmarks/bench_gpu_kernels.py -v --benchmark-only

# Profile Shield Agent latency
python -m cProfile -s cumtime -c "
from features.shields import evaluate_risk_veto_gates
import numpy as np
for _ in range(10000):
    evaluate_risk_veto_gates(100.0, 2.5, 2.0, 50000.0, 0.02, 0.0, 5e6, 2e6, 0.02)
"

# Test slippage model
pytest tests/test_slippage.py -v --tb=short

# Run all Phase 2 tests
pytest tests/unit/features/ tests/integration/features/ --cov=features --cov-report=html
```

---

## 10. Deliverables Summary - Phase 2

### Codebase
- [ ] `/new_pipeline/features/polars_engine.py` (500+ lines)
- [ ] `/new_pipeline/features/gpu_kernels.py` (600+ lines CUDA)
- [ ] `/new_pipeline/features/shields.py` (400+ lines Numba)
- [ ] `/new_pipeline/features/slippage.py` (200+ lines)
- [ ] 100+ unit tests + benchmarks

### Performance
- [ ] Polars 5-10x faster than pandas
- [ ] GPU kernels 10-50x faster than CPU
- [ ] Shield Agent < 100µs per eval
- [ ] Memory efficient: out-of-core processing

### Documentation
- [ ] Feature engineering guide
- [ ] GPU kernel optimization tips
- [ ] Shield Agent decision tree
- [ ] Slippage calibration guide

---

**Next**: After Phase 2 completion, proceed to [Phase 3: Tournament Backtesting & Model Selection](PHASE_3_SPECIFICATION.md) (to be created).

```

---

### File: `docs/PHASE_7_SPECIFICATION.md`

```markdown
# Phase 7: Production Hardening & Deployment - Detailed Specification

**Duration**: 2 weeks  
**Target Date**: Complete by late August (after Phase 6)  
**Success Criteria**: System production-ready; deployment automated; monitoring and disaster recovery validated; 100% critical path tests green

---

## 1. Phase 7 Architecture Overview

### 1.1 System Context (From Prototype to Production)

```
┌──────────────────────────────────────────────────────────────────────┐
│  PHASES 1-6 (Complete): Infrastructure → Models → Execution → Monitor │
├──────────────────────────────────────────────────────────────────────┤
│                              │                                       │
│                              ▼                                       │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │  PHASE 7: PRODUCTION HARDENING & DEPLOYMENT                 │      │
│  ├──────────────────────────────────────────────────────────────┤      │
│  │                                                              │      │
│  │  LAYER 0: INFRASTRUCTURE AS CODE                            │      │
│  │  ├─ Docker images for all services                          │
│  │  ├─ Kubernetes manifests / Helm charts                      │
│  │  ├─ Terraform templates for cloud resources                 │
│  │  ├─ CI/CD pipelines                                         │
│  │  └─ Secrets management (Vault, GitHub Secrets)              │
│  │                                                              │
│  │  LAYER 1: OBSERVABILITY & ALERTING                          │
  │  ├─ Metrics exporter (Prometheus)                            │
│  │  ├─ Logs aggregator (ELK / Loki)                            │
│  │  ├─ Tracing / distributed context                           │
│  │  ├─ Alert rules (CPU, latency, P&L, veto rate)              │
  │  └─ Dashboards (Grafana / Streamlit + metrics)               │
│  │                                                              │
│  │  LAYER 2: RESILIENCE & SAFETY                               │
  │  ├─ Circuit breakers / retry policies                        │
│  │  ├─ Canary deploys / blue-green promotion                   │
│  │  ├─ Chaos tests (network, node failure, latency)            │
│  │  ├─ Rollback plans                                         │
│  │  └─ Disaster recovery playbooks                             │
│  │                                                              │
│  │  LAYER 3: SECURITY & COMPLIANCE                             │
  │  ├─ Least-privilege IAM                                    │
│  │  ├─ Encrypted secrets + KMS                                │
│  │  ├─ Audit logging                                          │
│  │  ├─ Dependency vulnerability scanning                      │
  │  └─ Data privacy / governance controls                      │
│  │                                                              │
│  │  LAYER 4: PERFORMANCE & LOAD TESTING                        │
  │  ├─ Benchmark harnesses                                     │
│  │  ├─ Stress tests (trade, backtest, inference)              │
│  │  ├─ Capacity planning                                      │
│  │  └─ SLOs / SLIs defined                                     │
│  │                                                              │
│  └──────────────────────────────────────────────────────────────┘      │
│                              │                                       │
│      Takes the system live with hardened production controls       │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

```
/new_pipeline/hardening/             # ✨ NEW: Hardening module
├── __init__.py
├── docker/                          # Dockerfiles and image build configs
│   ├── Dockerfile.app
│   ├── Dockerfile.dashboard
│   └── Dockerfile.mcp
├── k8s/                             # Kubernetes deployment manifests
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   └── hpa.yaml
├── terraform/                       # Cloud infrastructure templates
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── providers.tf
├── ci/                              # CI/CD definitions
│   ├── github_actions.yaml
│   └── gitlab_ci.yml
├── monitoring/                      # Observability manifests
│   ├── prometheus.yaml
│   ├── grafana_dashboards.yaml
│   ├── alert_rules.yaml
│   └── loki_config.yaml
├── tests/                           # Hardening tests
│   ├── test_docker_build.py
│   ├── test_k8s_manifests.py
│   ├── test_ci_pipeline.py
│   ├── test_security_policies.py
│   └── test_stress_scenarios.py
├── scripts/                         # Deployment automation scripts
│   ├── deploy.sh
│   ├── rollback.sh
│   ├── smoke_test.sh
│   └── benchmark.sh
└── docs/
    ├── DEPLOYMENT_GUIDE.md
    ├── CHAOS_TESTING_GUIDE.md
    ├── RECOVERY_PLAYBOOK.md
    └── SECURITY_GUIDE.md
```

---

## 2. Infrastructure as Code

### 2.1 Docker Image Strategy

**Goal**: Build compartmentalized runtime images for all service roles.

**Images**:
- `qa/quantum-avenger-app` - core data + execution services
- `qa/quantum-avenger-dashboard` - Streamlit dashboard
- `qa/quantum-avenger-mcp` - FastMCP bridge
- `qa/quantum-avenger-tests` - CI test runner

**Requirements**:
- Multi-stage builds
- Minimal base image (`python:3.12-slim` / `debian:bookworm-slim`)
- Dependency layer caching
- Non-root runtime user
- Built-in healthchecks
- Environment variable driven config

#### 2.1.1 Dockerfile Conventions

- `Dockerfile.app`
  - Install runtime deps
  - Copy `/new_pipeline/` source
  - Set entrypoint: `python -m new_pipeline.main`

- `Dockerfile.dashboard`
  - Install Streamlit
  - Copy dashboard assets
  - Entry point: `streamlit run /new_pipeline/monitoring/dashboard.py`

- `Dockerfile.mcp`
  - Install FastMCP and tool dependencies
  - Entry point: `python -m new_pipeline.execution.mcp_server`

- `Dockerfile.tests`
  - Install dev dependencies
  - Entry point: `pytest --maxfail=1 --disable-warnings`

### 2.2 Kubernetes Deployment

**Goal**: Deploy services in a production-ready Kubernetes cluster.

**Manifests**:
- `deployment.yaml` - Deployments for app, dashboard, MCP server
- `service.yaml` - ClusterIP / LoadBalancer services
- `ingress.yaml` - HTTP/S ingress for dashboard + APIs
- `configmap.yaml` - Non-sensitive configuration
- `secrets.yaml` - TLS certificates, API keys, Alpaca secrets
- `hpa.yaml` - Horizontal Pod Autoscaler for app and dashboard

**Kubernetes Patterns**:
- `readinessProbe` and `livenessProbe`
- `resource.requests` and `limits`
- `podDisruptionBudget`
- `networkPolicy` for intra-cluster security
- `priorityClassName` for critical pods

### 2.3 Cloud Infrastructure

**Goal**: Provision configurable cloud resources with Terraform.

**Resources**:
- VPC / networking
- Kubernetes cluster (EKS / GKE / AKS)
- Managed Postgres / TimescaleDB for audit logs
- S3 / Blob storage for model artifacts
- Secrets Manager / Vault
- Load balancer / ingress controller

**Best Practices**:
- Use remote Terraform state (S3 backend, Terraform Cloud)
- Least-privilege IAM roles
- Tagging and cost allocation
- Environment isolation: `dev`, `staging`, `prod`

### 2.4 CI/CD Pipelines

**Goal**: Fully automated build, test, and deployment pipelines.

**Pipelines**:
- `github_actions.yaml`
  - `build`: build Docker images + lint
  - `test`: unit/integration coverage
  - `security`: dependency scan, SBOM generation
  - `deploy`: deploy to staging/prod on merge
- `gitlab_ci.yml`
  - Parallel stages: `lint`, `unit`, `integration`, `deploy`

**Gates**:
- Merge request must pass all tests
- DSR / model evaluation must pass
- Manual approval for production deploy
- Canary deployment before promotion

---

## 3. Observability & Alerting

### 3.1 Metrics and Logs

**Goal**: Make all service health, performance, and alpha metrics visible.

**Metrics stack**:
- Prometheus exporters in app + MCP + dashboard
- Custom metrics:
  - `quantum_avenger_trade_rate`
  - `quantum_avenger_veto_rate`
  - `quantum_avenger_execution_latency_ms`
  - `quantum_avenger_model_load_time_ms`
  - `quantum_avenger_dsr_value`

**Logging stack**:
- Structured JSON logs
- Timestamp, trace_id, module, level, event
- Ship logs to Loki/Elastic
- Correlate request IDs across services

### 3.2 Dashboards

**Goal**: Provide monitoring dashboards for operations.

**Grafana dashboards**:
- System health (CPU, memory, latency)
- Execution flow (orders, vetoes, fills)
- Model validation (DSR, synthetic SR)
- Risk metrics (drawdown, VaR, position sizing)
- Alert history

### 3.3 Alert Rules

**Goal**: Notify on operational and financial anomalies.

**Alerts**:
- `HighVetoRate` (veto rate > 20% in 5 min)
- `HighExecutionLatency` (trade execution > 200ms)
- `ModelPromotionFailure` (latest candidate rejects)
- `HighDrawdown` (equity drawdown > 15%)
- `ServiceDown` (pod unhealthy)
- `DiskPressure` / `MemoryPressure`

**Channels**:
- Slack / Teams webhook
- Email
- PagerDuty / Opsgenie

---

## 4. Resilience, Testing, and Recovery

### 4.1 Circuit Breakers and Retries

**Goal**: Fail fast and recover safely.

**Implementation**:
- Circuit breaker around external services (Alpaca, FastMCP, data sources)
- Exponential backoff with jitter
- Retry only idempotent operations
- Failure thresholds and cooldown windows

### 4.2 Chaos and Stress Testing

**Goal**: Validate resilience under failure modes.

**Scenarios**:
- Network partition to Alpaca / data sources
- Pod eviction / restart
- High latency responses
- Disk failure on model artifact storage
- Increased trade volume / order bursts

**Tools**:
- `kubectl` chaos scripts
- `chaos-mesh` / `litmus` scenarios
- `locust` or `k6` for load testing
- `pytest` stress harness

### 4.3 Disaster Recovery

**Goal**: Ensure recoverability from outages.

**Playbooks**:
- `RECOVERY_PLAYBOOK.md`
- Backup model artifacts daily
- Snapshot database and Parquet logs
- Restore procedure for stateful stores
- Rollback procedure for deployments

### 4.4 Security & Compliance

**Goal**: Lock down production and meet governance.

**Practices**:
- Secrets in Vault / Secrets Manager only
- RBAC for cluster access
- Dependency scanning (Snyk, GitHub Dependabot)
- Container image scanning
- Audit log retention
- Secure communication: TLS everywhere

---

## 5. Performance & Capacity Planning

### 5.1 Benchmarking

**Goal**: Define execution throughput and latency SLOs.

**Benchmarks**:
- Model inference latency (< 10ms)
- Shield Agent veto latency (< 100µs)
- MCP tool call latency (< 10ms)
- Streamlit dashboard render (< 1s)
- Backtest pipeline throughput (> 100k rows/sec)

### 5.2 Load Testing

**Goal**: Stress the system at expected production volume.

**Workloads**:
- Real-time market updates at 1k symbols
- 100 concurrent inference sessions
- 10,000 daily candidate evaluations
- 1,000 daily trade signals

### 5.3 Scaling Strategy

**Goal**: Horizontal auto-scaling with controlled capacity.

**Strategy**:
- App service autoscale by CPU / latency
- MCP service autoscale by requests/sec
- Use durable queues for spikes
- Reserve capacity for cold start avoidance

---

## 6. Implementation Checklist - Phase 7

### Week 1: Deployment & Observability

- [ ] **Day 1-2**: Docker + Kubernetes
  - [ ] Write Dockerfiles for app, dashboard, MCP
  - [ ] Build and test container images
  - [ ] Create Kubernetes manifests with probes

- [ ] **Day 2-3**: CI/CD and IaC
  - [ ] Author GitHub Actions pipeline
  - [ ] Create Terraform template for cloud infra
  - [ ] Validate `terraform plan`

- [ ] **Day 3-4**: Metrics and logging
  - [ ] Add Prometheus exporters
  - [ ] Define Grafana dashboards
  - [ ] Ship logs to Loki/ELK

- [ ] **Day 4-5**: Alerting and security
  - [ ] Implement alert rules
  - [ ] Configure secrets management
  - [ ] Add RBAC / network policies

### Week 2: Resilience, Testing, and Release

- [ ] **Day 6-7**: Resilience testing
  - [ ] Add circuit breakers/retries
  - [ ] Run chaos scenarios
  - [ ] Validate failover behavior

- [ ] **Day 7-8**: Performance and capacity
  - [ ] Run stress tests
  - [ ] Capture latency metrics
  - [ ] Adjust autoscaling settings

- [ ] **Day 8-9**: Recovery and documentation
  - [ ] Write `RECOVERY_PLAYBOOK.md`
  - [ ] Document rollback steps
  - [ ] Verify backups and restore tests

- [ ] **Day 9-10**: Release readiness
  - [ ] Run end-to-end smoke tests
  - [ ] Validate dashboards and alerts
  - [ ] Tag release candidate
  - [ ] Approve production rollout

---

## 7. Success Criteria

| Criterion | Expected |
|-----------|----------|
| Production deployment | All services deployed in cluster |
| Health checks | All readiness/liveness passing |
| Smoke test | Trade flow end-to-end passes |
| Alerting | Critical alerts fire correctly |
| Chaos recovery | System recovers after simulated failure |
| Security | Secrets encrypted, RBAC enforced |
| Performance | Latency and throughput within SLOs |
| Documentation | Deployment and recovery guides complete |

---

## 8. Deliverables Summary - Phase 7

### Codebase Deliverables
- [ ] `/new_pipeline/hardening/docker/Dockerfile.*`
- [ ] `/new_pipeline/hardening/k8s/*.yaml`
- [ ] `/new_pipeline/hardening/terraform/*.tf`
- [ ] `/new_pipeline/hardening/ci/*`
- [ ] `/new_pipeline/hardening/monitoring/*`
- [ ] `/new_pipeline/hardening/scripts/*`
- [ ] `/new_pipeline/hardening/docs/*.md`

### Operational Deliverables
- [ ] Production-grade container images
- [ ] Kubernetes deployment pipelines
- [ ] Observability dashboards + alerting
- [ ] Chaos and recovery playbooks
- [ ] Security and compliance hardening

### Quality Deliverables
- [ ] 100% critical-path test coverage
- [ ] Stable production rollout strategy
- [ ] Documented release process
- [ ] Post-deployment monitoring baseline

---

**Next**: After Phase 7, the system is ready for production adoption and post-launch optimization.

**Previous Phases**:
- [Phase 1: Core Pipeline Infrastructure](PHASE_1_SPECIFICATION.md)
- [Phase 2: Vectorized Quant Engine & Shields](PHASE_2_SPECIFICATION.md)
- [Phase 3: Tournament Backtesting & Model Selection](PHASE_3_SPECIFICATION.md)
- [Phase 4: Statistical Evaluation & Promotion](PHASE_4_SPECIFICATION.md)
- [Phase 5: Live Execution & Orchestration](PHASE_5_SPECIFICATION.md)
- [Phase 6: Dashboard & Monitoring](PHASE_6_SPECIFICATION.md)

```

---

### File: `docs/PHASE_6_SPECIFICATION.md`

```markdown
# Phase 6: Dashboard & Monitoring - Detailed Specification

**Duration**: 2 weeks  
**Target Date**: Complete by mid-August (after Phase 5)  
**Success Criteria**: Real-time dashboard live; KPI updates streaming; veto ledger displayed; trade log queryable; 85%+ test coverage

---

## 1. Phase 6 Architecture Overview

### 1.1 System Context (Unified Monitoring & Observability)

```
┌────────────────────────────────────────────────────────────────────┐
│  PHASES 1-5 (Complete): Infrastructure through Live Execution     │
├────────────────────────────────────────────────────────────────────┤
│                           │                                         │
│                           ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  PHASE 6: DASHBOARD & MONITORING - UNIFIED VISIBILITY       │  │
│  ├──────────────────────────────────────────────────────────────┤  │
│  │                                                              │  │
│  │  LAYER 0: DATA PIPELINE (Real-time Streaming)              │  │
│  │  ├─ Veto ledger (Parquet, append-only)                     │  │
│  │  ├─ Trade log (fills, slippage, P&L)                       │  │
│  │  ├─ Position updates (every 100ms)                         │  │
│  │  ├─ Market data feed (price, volume, volatility)           │  │
│  │  └─ Performance metrics (Sharpe, drawdown, win rate)        │  │
│  │                                                              │  │
│  │  LAYER 1: STREAMLIT DASHBOARD (Multi-page)                 │  │
│  │  ├─ Page 1: LIVE MONITOR                                   │  │
│  │  │  ├─ KPI cards (equity, P&L, Sharpe, max DD)            │  │
│  │  │  ├─ Equity curve (real-time chart)                      │  │
│  │  │  ├─ Current positions (table)                           │  │
│  │  │  ├─ Live P&L by position                                │  │
│  │  │  └─ System alerts (anomalies)                           │  │
│  │  │                                                          │  │
│  │  ├─ Page 2: VETO ANALYSIS                                  │  │
│  │  │  ├─ Rejection rate by gate                              │  │
│  │  │  ├─ Top veto reasons (bar chart)                        │  │
│  │  │  ├─ Veto timeline (history)                             │  │
│  │  │  ├─ Symbol rejection breakdown                          │  │
│  │  │  └─ Veto statistics (D/W/M)                             │  │
│  │  │                                                          │  │
│  │  ├─ Page 3: TRADE LOG                                      │  │
│  │  │  ├─ Trade table (sortable, filterable)                  │  │
│  │  │  ├─ Fill details (price, size, commission)              │  │
│  │  │  ├─ Trade P&L (realized, unrealized)                    │  │
│  │  │  ├─ Trade analytics (Sharpe per trade)                  │  │
│  │  │  └─ Trade search (date range, symbol, P&L)              │  │
│  │  │                                                          │  │
│  │  ├─ Page 4: MODEL REGISTRY                                 │  │
│  │  │  ├─ Active champions (sector → model)                   │  │
│  │  │  ├─ Model statistics (DSR, Sharpe, sector)              │  │
│  │  │  ├─ Promotion history (timeline)                        │  │
│  │  │  ├─ Model performance (live vs backtest)                │  │
│  │  │  └─ Model parameters (hyperparameters)                  │  │
│  │  │                                                          │  │
│  │  ├─ Page 5: RISK DASHBOARD                                 │  │
│  │  │  ├─ Account equity + drawdown                           │  │
│  │  │  ├─ Position sizing compliance (vs Kelly)               │  │
│  │  │  ├─ Liquidity assessment (ADV coverage)                 │  │
│  │  │  ├─ Correlation matrix (sector exposures)               │  │
│  │  │  ├─ VaR (Value at Risk) estimation                      │  │
│  │  │  └─ Stress scenarios (rate shock, vol shock)            │  │
│  │  │                                                          │  │
│  │  ├─ Page 6: SETTINGS & CONFIGURATION                       │  │
│  │  │  ├─ Update risk thresholds                              │  │
│  │  │  ├─ Toggle sectors on/off                               │  │
│  │  │  ├─ Download reports (PDF, CSV)                         │  │
│  │  │  ├─ API key management                                  │  │
│  │  │  └─ Notification settings                               │  │
│  │  │                                                          │  │
│  │  └─ SIDEBAR: Navigation + Filters                          │  │
│  │     ├─ Date range picker                                   │  │
│  │     ├─ Symbol selector                                     │  │
│  │     ├─ Sector filter                                       │  │
│  │     └─ View refresh rate                                   │  │
│  │                                                              │  │
│  │  LAYER 2: ALERTING & NOTIFICATIONS                         │  │
│  │  ├─ Real-time alerts (email, Slack, webhook)              │  │
│  │  ├─ Alert types: Execution error, liquidation risk, etc.   │  │
│  │  ├─ Configurable thresholds (drawdown, VaR, etc.)         │  │
│  │  └─ Alert ledger (all alerts logged)                       │  │
│  │                                                              │  │
│  │  LAYER 3: DATA EXPORT & REPORTING                          │  │
│  │  ├─ Download trade log (CSV, Parquet)                      │  │
│  │  ├─ Export performance report (PDF)                        │  │
│  │  ├─ Generate tearsheets (daily/weekly/monthly)             │  │
│  │  ├─ Email reports (scheduled)                              │  │
│  │  └─ API endpoints (real-time metrics)                      │  │
│  │                                                              │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                           │                                         │
│       Uses all Phases 1-5 + Real-time data streams                │
│       Produces: Performance dashboards, alerts, reports            │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

```
/new_pipeline/monitoring/          # ✨ NEW: Monitoring module
├── __init__.py
├── dashboard.py                   # ✨ NEW: Streamlit app
├── pages/
│   ├── __init__.py
│   ├── 01_live_monitor.py         # ✨ NEW: Real-time KPIs
│   ├── 02_veto_analysis.py        # ✨ NEW: Rejection patterns
│   ├── 03_trade_log.py            # ✨ NEW: Trade history
│   ├── 04_model_registry.py       # ✨ NEW: Champion models
│   ├── 05_risk_dashboard.py       # ✨ NEW: Risk metrics
│   └── 06_settings.py             # ✨ NEW: Configuration
├── components/
│   ├── __init__.py
│   ├── kpi_cards.py               # ✨ NEW: Metric cards
│   ├── charts.py                  # ✨ NEW: Visualization helpers
│   ├── alerts.py                  # ✨ NEW: Alert system
│   └── data_loaders.py            # ✨ NEW: Cached data fetching
├── data_pipeline.py               # ✨ NEW: Real-time streaming
├── alert_engine.py                # ✨ NEW: Alert triggering
├── report_generator.py            # ✨ NEW: PDF/CSV export
└── tests/
    ├── test_dashboard.py
    ├── test_pages.py
    ├── test_alerts.py
    ├── test_report_generator.py
    └── benchmarks/
        ├── bench_streamlit_render.py
        └── bench_data_loading.py
```

---

## 2. Real-Time Data Pipeline

### 2.1 Theory: Streaming Architecture

**Problem**: Dashboard must update every 100ms without reloading page

**Solution**: Multi-tier caching with Parquet append-only logs
- Veto ledger: Append-only Parquet (fast writes)
- Trade log: Append-only Parquet (fast writes)
- KPI metrics: Cached in-memory (updated every 1 sec)
- Charts: Polars lazy-frames (computed on-demand)

### 2.2 Module: `monitoring/data_pipeline.py`

**File: `monitoring/data_pipeline.py`**

#### 2.2.1 Real-Time Data Manager

**Class: `RealtimeDataManager`**

```python
import polars as pl
from pathlib import Path
from typing import Dict, List, Optional
import time

class RealtimeDataManager:
    """Manage real-time data streaming for dashboard.
    
    Purpose:
        - Load veto ledger (append-only)
        - Load trade log (append-only)
        - Compute KPI metrics (cached)
        - Serve data to Streamlit with minimal latency
    
    Methods:
        get_veto_ledger: Load recent veto records.
        get_trade_log: Load recent trades.
        get_kpi_metrics: Get portfolio metrics.
        get_equity_curve: Get cumulative returns.
    """
    
    def __init__(self, config: AppConfig):
        """Initialize data manager.
        
        Args:
            config: AppConfig with paths.
        """
        self.config = config
        self.logger = get_logger(__name__)
        
        # Cache settings
        self.cache_ttl = 1.0  # 1 second cache
        self.cache = {}
        self.cache_timestamp = {}
        
        # Data paths
        self.veto_ledger_path = f"{config.execution.ledger_dir}/veto_ledger.parquet"
        self.trade_log_path = f"{config.execution.ledger_dir}/trade_log.parquet"
        self.position_log_path = f"{config.execution.ledger_dir}/position_log.parquet"
    
    def get_veto_ledger(
        self,
        window_days: int = 7,
        use_cache: bool = True
    ) -> pl.DataFrame:
        """Load veto ledger for recent period.
        
        Args:
            window_days: Days back to query.
            use_cache: Use cache if fresh.
        
        Returns:
            Polars DataFrame with columns:
            - timestamp (datetime)
            - symbol (str)
            - signal (str)
            - entry_price (f64)
            - veto_reason (str)
            - veto_gate (str)
            - position_size (i32)
            - execution_id (str)
        """
        cache_key = f"veto_ledger_{window_days}"
        
        # Check cache
        if use_cache and self._is_cache_fresh(cache_key):
            return self.cache[cache_key]
        
        # Load from Parquet
        if not Path(self.veto_ledger_path).exists():
            return pl.DataFrame()
        
        df = pl.read_parquet(self.veto_ledger_path)
        
        # Filter by date
        cutoff = pl.datetime_range(
            start=pl.datetime.now() - pl.timedelta(days=window_days),
            end=pl.datetime.now(),
            interval="1d"
        )
        
        df = df.filter(pl.col("timestamp") >= cutoff[0])
        
        # Cache
        self.cache[cache_key] = df
        self.cache_timestamp[cache_key] = time.time()
        
        self.logger.debug(f"Loaded {len(df)} veto records")
        
        return df
    
    def get_trade_log(
        self,
        window_days: int = 7,
        use_cache: bool = True
    ) -> pl.DataFrame:
        """Load trade log for recent period.
        
        Args:
            window_days: Days back to query.
            use_cache: Use cache if fresh.
        
        Returns:
            Polars DataFrame with columns:
            - timestamp (datetime)
            - symbol (str)
            - side (str)
            - qty (i32)
            - fill_price (f64)
            - commission (f64)
            - exit_price (f64, optional)
            - pnl (f64)
            - pnl_pct (f64)
        """
        cache_key = f"trade_log_{window_days}"
        
        if use_cache and self._is_cache_fresh(cache_key):
            return self.cache[cache_key]
        
        if not Path(self.trade_log_path).exists():
            return pl.DataFrame()
        
        df = pl.read_parquet(self.trade_log_path)
        
        # Filter by date
        cutoff = pl.datetime.now() - pl.timedelta(days=window_days)
        df = df.filter(pl.col("timestamp") >= cutoff)
        
        self.cache[cache_key] = df
        self.cache_timestamp[cache_key] = time.time()
        
        self.logger.debug(f"Loaded {len(df)} trades")
        
        return df
    
    def get_kpi_metrics(self, use_cache: bool = True) -> Dict[str, float]:
        """Get current portfolio KPI metrics.
        
        Returns:
            {
                'total_equity': float,
                'total_pnl': float,
                'total_pnl_pct': float,
                'cash': float,
                'buying_power': float,
                'sharpe_ratio': float (annualized),
                'max_drawdown': float,
                'win_rate': float,
                'avg_win': float,
                'avg_loss': float,
                'profit_factor': float,
                'num_trades': int,
                'timestamp': datetime
            }
        """
        cache_key = "kpi_metrics"
        
        if use_cache and self._is_cache_fresh(cache_key):
            return self.cache[cache_key]
        
        # Query trade log
        trade_df = self.get_trade_log(window_days=365, use_cache=False)
        
        if len(trade_df) == 0:
            metrics = {
                'total_equity': 0.0,
                'total_pnl': 0.0,
                'total_pnl_pct': 0.0,
                'cash': 0.0,
                'buying_power': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'avg_win': 0.0,
                'avg_loss': 0.0,
                'profit_factor': 0.0,
                'num_trades': 0,
                'timestamp': pl.datetime.now()
            }
            self.cache[cache_key] = metrics
            self.cache_timestamp[cache_key] = time.time()
            return metrics
        
        # Compute metrics
        pnl_series = trade_df['pnl'].to_numpy()
        
        total_equity = self.config.execution.account_capital + pnl_series.sum()
        total_pnl = pnl_series.sum()
        total_pnl_pct = (total_pnl / self.config.execution.account_capital) * 100
        
        # Sharpe ratio (annualized)
        daily_returns = pnl_series / self.config.execution.account_capital
        sharpe = (np.mean(daily_returns) / np.std(daily_returns, ddof=1)) * np.sqrt(252) if len(daily_returns) > 1 else 0.0
        
        # Drawdown
        cumulative = np.cumsum(pnl_series)
        running_max = np.maximum.accumulate(cumulative)
        drawdown = (cumulative - running_max) / running_max
        max_dd = np.abs(np.min(drawdown)) if len(drawdown) > 0 else 0.0
        
        # Win rate
        wins = np.sum(pnl_series > 0)
        losses = np.sum(pnl_series < 0)
        win_rate = wins / (wins + losses) if (wins + losses) > 0 else 0.0
        
        # Profit factor
        gross_profit = np.sum(pnl_series[pnl_series > 0])
        gross_loss = np.abs(np.sum(pnl_series[pnl_series < 0]))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0.0
        
        avg_win = np.mean(pnl_series[pnl_series > 0]) if np.sum(pnl_series > 0) > 0 else 0.0
        avg_loss = np.mean(pnl_series[pnl_series < 0]) if np.sum(pnl_series < 0) > 0 else 0.0
        
        metrics = {
            'total_equity': float(total_equity),
            'total_pnl': float(total_pnl),
            'total_pnl_pct': float(total_pnl_pct),
            'cash': self.config.execution.account_capital - total_equity,
            'buying_power': self.config.execution.account_capital * 0.95,  # 95% utilization
            'sharpe_ratio': float(sharpe),
            'max_drawdown': float(max_dd),
            'win_rate': float(win_rate),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'profit_factor': float(profit_factor),
            'num_trades': len(trade_df),
            'timestamp': pl.datetime.now()
        }
        
        self.cache[cache_key] = metrics
        self.cache_timestamp[cache_key] = time.time()
        
        return metrics
    
    def get_equity_curve(self, window_days: int = 30) -> pl.DataFrame:
        """Get equity curve over time.
        
        Returns:
            DataFrame with columns:
            - timestamp (datetime)
            - equity (f64)
            - cumulative_pnl (f64)
            - drawdown (f64)
        """
        cache_key = f"equity_curve_{window_days}"
        
        if self._is_cache_fresh(cache_key):
            return self.cache[cache_key]
        
        trade_df = self.get_trade_log(window_days=window_days, use_cache=False)
        
        if len(trade_df) == 0:
            return pl.DataFrame()
        
        # Group by date
        daily_pnl = trade_df.group_by(
            pl.col("timestamp").cast(pl.Date)
        ).agg(
            pl.col("pnl").sum().alias("daily_pnl")
        ).sort("timestamp")
        
        # Compute cumulative
        daily_pnl = daily_pnl.with_columns(
            pl.col("daily_pnl").cumsum().alias("cumulative_pnl")
        ).with_columns(
            (
                self.config.execution.account_capital + 
                pl.col("cumulative_pnl")
            ).alias("equity")
        )
        
        # Compute drawdown
        daily_pnl = daily_pnl.with_columns(
            (
                (
                    pl.col("equity") - 
                    pl.col("equity").max().over(pl.all())
                ) / pl.col("equity").max().over(pl.all())
            ).alias("drawdown")
        )
        
        self.cache[cache_key] = daily_pnl
        self.cache_timestamp[cache_key] = time.time()
        
        return daily_pnl
    
    def _is_cache_fresh(self, cache_key: str) -> bool:
        """Check if cache is still valid.
        
        Args:
            cache_key: Cache key to check.
        
        Returns:
            True if cache exists and is fresh (< 1 second old).
        """
        if cache_key not in self.cache_timestamp:
            return False
        
        age = time.time() - self.cache_timestamp[cache_key]
        return age < self.cache_ttl
    
    def invalidate_cache(self) -> None:
        """Clear all caches (on new trade/veto)."""
        self.cache = {}
        self.cache_timestamp = {}
        self.logger.debug("Cache invalidated")
```

---

## 3. Streamlit Dashboard Main App

### 3.1 Module: `monitoring/dashboard.py`

**File: `monitoring/dashboard.py`**

#### 3.1.1 Dashboard Configuration & Layout

**Function: `configure_dashboard()`**

```python
import streamlit as st
from pathlib import Path

def configure_dashboard() -> None:
    """Configure Streamlit page settings and theme.
    
    Settings:
        - Page layout: wide (maximize space)
        - Theme: dark (better for trading)
        - Title: Quantum Avenger Live Dashboard
        - Icon: 🚀
    """
    st.set_page_config(
        page_title="Quantum Avenger Live Dashboard",
        page_icon="🚀",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Theme settings
    st.markdown(
        """
        <style>
        [data-testid="stMetricValue"] {
            font-size: 32px;
        }
        [data-testid="stMetricLabel"] {
            font-size: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
```

#### 3.1.2 Sidebar Navigation & Filters

**Function: `render_sidebar()`**

```python
def render_sidebar() -> Dict[str, any]:
    """Render sidebar with navigation and filters.
    
    Returns:
        {
            'page': str (selected page),
            'date_range': (start_date, end_date),
            'symbols': List[str],
            'sectors': List[str],
            'refresh_rate': int (seconds)
        }
    """
    st.sidebar.title("🚀 Quantum Avenger")
    
    # Navigation
    page = st.sidebar.radio(
        "Select Page",
        [
            "01 - Live Monitor",
            "02 - Veto Analysis",
            "03 - Trade Log",
            "04 - Model Registry",
            "05 - Risk Dashboard",
            "06 - Settings"
        ]
    )
    
    st.sidebar.divider()
    
    # Date range filter
    st.sidebar.subheader("📅 Date Range")
    date_range = st.sidebar.date_input(
        "Select dates",
        value=(
            pd.Timestamp.now() - pd.Timedelta(days=7),
            pd.Timestamp.now()
        ),
        max_value=pd.Timestamp.now()
    )
    
    # Symbol filter
    st.sidebar.subheader("📊 Symbols")
    all_symbols = ["All", "AAPL", "MSFT", "GOOG", "TSLA", "AMZN"]
    selected_symbols = st.sidebar.multiselect(
        "Select symbols",
        all_symbols,
        default=["All"]
    )
    
    if "All" in selected_symbols:
        symbols = all_symbols[1:]
    else:
        symbols = selected_symbols
    
    # Sector filter
    st.sidebar.subheader("🏭 Sectors")
    sectors = st.sidebar.multiselect(
        "Select sectors",
        ["Technology", "Finance", "Healthcare", "Energy"],
        default=["Technology", "Finance"]
    )
    
    # Refresh rate
    st.sidebar.subheader("⚡ Performance")
    refresh_rate = st.sidebar.slider(
        "Refresh rate (seconds)",
        min_value=1,
        max_value=10,
        value=1
    )
    
    return {
        'page': page,
        'date_range': date_range,
        'symbols': symbols,
        'sectors': sectors,
        'refresh_rate': refresh_rate
    }
```

---

## 4. KPI Cards Component

### 4.1 Module: `monitoring/components/kpi_cards.py`

**File: `monitoring/components/kpi_cards.py`**

#### 4.1.1 KPI Metric Cards

**Function: `render_kpi_cards()`**

```python
def render_kpi_cards(metrics: Dict[str, float]) -> None:
    """Render top-level KPI cards.
    
    Args:
        metrics: Dictionary from get_kpi_metrics().
    
    Cards:
        1. Total Equity (green/red based on P&L)
        2. Total P&L ($ and %)
        3. Sharpe Ratio (annualized)
        4. Max Drawdown (%)
        5. Win Rate (%)
        6. Profit Factor (>1.5 = good)
    """
    cols = st.columns(6)
    
    # Card 1: Total Equity
    with cols[0]:
        equity_color = "green" if metrics['total_pnl'] > 0 else "red"
        st.metric(
            "💰 Total Equity",
            f"${metrics['total_equity']:,.0f}",
            delta=f"${metrics['total_pnl']:,.0f}",
            delta_color="normal" if metrics['total_pnl'] > 0 else "inverse"
        )
    
    # Card 2: P&L %
    with cols[1]:
        st.metric(
            "📈 P&L %",
            f"{metrics['total_pnl_pct']:.2f}%",
            delta=f"{metrics['total_pnl']:.0f} USD"
        )
    
    # Card 3: Sharpe Ratio
    with cols[2]:
        sharpe_color = "normal" if metrics['sharpe_ratio'] > 1.0 else "inverse"
        st.metric(
            "⚡ Sharpe Ratio",
            f"{metrics['sharpe_ratio']:.2f}",
            delta="Good ✓" if metrics['sharpe_ratio'] > 1.0 else "Needs tuning"
        )
    
    # Card 4: Max Drawdown
    with cols[3]:
        st.metric(
            "📉 Max Drawdown",
            f"{metrics['max_drawdown']*100:.2f}%",
            delta="Within limits" if metrics['max_drawdown'] < 0.20 else "⚠️ Warning"
        )
    
    # Card 5: Win Rate
    with cols[4]:
        st.metric(
            "🎯 Win Rate",
            f"{metrics['win_rate']*100:.1f}%",
            delta=f"{metrics['num_trades']} trades"
        )
    
    # Card 6: Profit Factor
    with cols[5]:
        pf_status = "Good ✓" if metrics['profit_factor'] > 1.5 else "Monitor"
        st.metric(
            "📊 Profit Factor",
            f"{metrics['profit_factor']:.2f}",
            delta=pf_status
        )
```

---

## 5. Live Monitor Page

### 5.1 Module: `monitoring/pages/01_live_monitor.py`

**File: `monitoring/pages/01_live_monitor.py`**

```python
import streamlit as st
from monitoring.data_pipeline import RealtimeDataManager
from monitoring.components.kpi_cards import render_kpi_cards
from monitoring.components.charts import (
    render_equity_curve,
    render_position_heatmap,
    render_pnl_timeline
)

def page_live_monitor(config: AppConfig, filters: Dict) -> None:
    """Live monitoring page with real-time metrics.
    
    Layout:
        1. KPI cards (top)
        2. Equity curve chart (left, 2/3 width)
        3. Current positions table (right, 1/3 width)
        4. P&L timeline (bottom left)
        5. System alerts (bottom right)
    """
    st.title("🔴 Live Monitor")
    
    # Initialize data manager
    data_mgr = RealtimeDataManager(config)
    
    # Get metrics
    metrics = data_mgr.get_kpi_metrics(use_cache=True)
    
    # Row 1: KPI cards
    render_kpi_cards(metrics)
    
    st.divider()
    
    # Row 2: Charts
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("📈 Equity Curve")
        equity_df = data_mgr.get_equity_curve(window_days=30)
        render_equity_curve(equity_df)
    
    with col_right:
        st.subheader("💼 Current Positions")
        # Load position table (placeholder)
        positions = get_current_positions()
        st.dataframe(
            positions,
            use_container_width=True,
            hide_index=True
        )
    
    st.divider()
    
    # Row 3: P&L timeline + alerts
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📊 P&L Timeline")
        trade_df = data_mgr.get_trade_log(window_days=7)
        render_pnl_timeline(trade_df)
    
    with col_right:
        st.subheader("🚨 System Alerts")
        alerts = get_recent_alerts()
        if len(alerts) > 0:
            for alert in alerts[:5]:
                with st.container(border=True):
                    st.markdown(f"**{alert['type']}** @ {alert['timestamp']}")
                    st.write(alert['message'])
        else:
            st.info("✓ No alerts")
    
    # Auto-refresh
    st.divider()
    placeholder = st.empty()
    with placeholder.container():
        st.caption(f"Last updated: {pd.Timestamp.now().strftime('%H:%M:%S')}")
    
    import time
    time.sleep(filters.get('refresh_rate', 1))
    st.rerun()

def get_current_positions() -> pl.DataFrame:
    """Fetch current open positions from portfolio."""
    # Placeholder
    return pl.DataFrame({
        'Symbol': ['AAPL', 'MSFT'],
        'Qty': [100, 50],
        'Entry': [150.0, 300.0],
        'Current': [151.5, 305.0],
        'P&L': [150.0, 250.0]
    })

def get_recent_alerts() -> List[Dict]:
    """Fetch recent system alerts."""
    # Placeholder
    return []
```

---

## 6. Veto Analysis Page

### 6.1 Module: `monitoring/pages/02_veto_analysis.py`

```python
import streamlit as st
import plotly.express as px

def page_veto_analysis(config: AppConfig, filters: Dict) -> None:
    """Analyze veto patterns and rejection reasons.
    
    Sections:
        1. Rejection rate (pie chart)
        2. Top veto gates (bar chart)
        3. Top reasons (bar chart)
        4. Symbol-level rejections (heatmap)
        5. Veto timeline (area chart)
        6. Detailed veto ledger (table)
    """
    st.title("🚫 Veto Analysis")
    
    data_mgr = RealtimeDataManager(config)
    veto_df = data_mgr.get_veto_ledger(window_days=filters.get('days', 7))
    
    if len(veto_df) == 0:
        st.info("No veto records found")
        return
    
    st.subheader("📊 Veto Statistics")
    
    # Row 1: Summary stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Vetoes", len(veto_df))
    
    with col2:
        unique_symbols = veto_df['symbol'].n_unique()
        st.metric("Symbols Affected", unique_symbols)
    
    with col3:
        unique_reasons = veto_df['veto_reason'].n_unique()
        st.metric("Unique Reasons", unique_reasons)
    
    with col4:
        veto_rate = (len(veto_df) / 100) * 100  # Placeholder
        st.metric("Veto Rate", f"{veto_rate:.1f}%")
    
    st.divider()
    
    # Row 2: Charts
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("🚪 Rejections by Gate")
        gate_counts = veto_df['veto_gate'].value_counts()
        fig = px.bar(
            x=gate_counts.index,
            y=gate_counts.values,
            labels={'x': 'Gate', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("❌ Top Veto Reasons")
        reason_counts = veto_df['veto_reason'].value_counts().head(10)
        fig = px.bar(
            y=reason_counts.index,
            x=reason_counts.values,
            orientation='h',
            labels={'x': 'Count', 'y': 'Reason'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    st.divider()
    
    # Row 3: Detailed ledger
    st.subheader("📋 Veto Ledger")
    st.dataframe(
        veto_df.select([
            'timestamp', 'symbol', 'signal', 'veto_gate', 'veto_reason'
        ]).to_pandas(),
        use_container_width=True,
        hide_index=True
    )
```

---

## 7. Trade Log Page

### 7.1 Module: `monitoring/pages/03_trade_log.py`

```python
import streamlit as st
import pandas as pd

def page_trade_log(config: AppConfig, filters: Dict) -> None:
    """Trade history and analysis.
    
    Features:
        1. Trade table (sortable, filterable)
        2. Trade statistics
        3. Trade search (by symbol, date, P&L)
        4. Trade detail view (click to expand)
    """
    st.title("📝 Trade Log")
    
    data_mgr = RealtimeDataManager(config)
    trade_df = data_mgr.get_trade_log(window_days=30)
    
    if len(trade_df) == 0:
        st.info("No trades yet")
        return
    
    # Summary stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Trades", len(trade_df))
    
    with col2:
        winning = (trade_df['pnl'] > 0).sum()
        st.metric("Winning", winning)
    
    with col3:
        losing = (trade_df['pnl'] < 0).sum()
        st.metric("Losing", losing)
    
    with col4:
        total_pnl = trade_df['pnl'].sum()
        st.metric("Total P&L", f"${total_pnl:,.0f}")
    
    with col5:
        avg_pnl = trade_df['pnl'].mean()
        st.metric("Avg P&L", f"${avg_pnl:,.0f}")
    
    st.divider()
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_symbol = st.selectbox(
            "Filter by symbol",
            ["All"] + sorted(trade_df['symbol'].unique().to_list())
        )
    
    with col2:
        pnl_filter = st.radio(
            "Filter by result",
            ["All", "Winners", "Losers"]
        )
    
    with col3:
        sort_by = st.selectbox(
            "Sort by",
            ["Date (Latest)", "P&L (High)", "P&L (Low)"]
        )
    
    # Apply filters
    filtered_df = trade_df
    
    if selected_symbol != "All":
        filtered_df = filtered_df.filter(pl.col('symbol') == selected_symbol)
    
    if pnl_filter == "Winners":
        filtered_df = filtered_df.filter(pl.col('pnl') > 0)
    elif pnl_filter == "Losers":
        filtered_df = filtered_df.filter(pl.col('pnl') < 0)
    
    # Sort
    if sort_by == "P&L (High)":
        filtered_df = filtered_df.sort('pnl', descending=True)
    elif sort_by == "P&L (Low)":
        filtered_df = filtered_df.sort('pnl', descending=False)
    else:
        filtered_df = filtered_df.sort('timestamp', descending=True)
    
    # Display table
    st.dataframe(
        filtered_df.to_pandas(),
        use_container_width=True,
        hide_index=True
    )
```

---

## 8. Alert System

### 8.1 Module: `monitoring/alert_engine.py`

**File: `monitoring/alert_engine.py`**

```python
from typing import Dict, List, Optional
from enum import Enum

class AlertType(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class AlertEngine:
    """Generate and send real-time alerts.
    
    Methods:
        check_alerts: Evaluate alerting conditions.
        send_alert: Send via email/Slack/webhook.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
    
    def check_alerts(self, metrics: Dict) -> List[Dict]:
        """Check for alerting conditions.
        
        Conditions:
            1. Max drawdown exceeded
            2. Sharpe ratio dropped
            3. Execution error
            4. Liquidity breach
            5. Position sizing violation
        
        Returns:
            List of alerts (if any).
        """
        alerts = []
        
        # Check max drawdown
        max_dd_threshold = self.config.monitoring.max_drawdown_alert
        if metrics['max_drawdown'] > max_dd_threshold:
            alerts.append({
                'type': AlertType.WARNING.value,
                'message': f"Max drawdown {metrics['max_drawdown']:.1%} > threshold {max_dd_threshold:.1%}",
                'timestamp': pd.Timestamp.now()
            })
        
        # Check Sharpe ratio
        sharpe_min = self.config.monitoring.sharpe_min_alert
        if metrics['sharpe_ratio'] < sharpe_min:
            alerts.append({
                'type': AlertType.WARNING.value,
                'message': f"Sharpe ratio {metrics['sharpe_ratio']:.2f} below threshold {sharpe_min:.2f}",
                'timestamp': pd.Timestamp.now()
            })
        
        return alerts
    
    def send_alert(
        self,
        alert: Dict,
        channels: List[str] = ["email", "slack"]
    ) -> None:
        """Send alert via specified channels.
        
        Args:
            alert: Alert dictionary.
            channels: ['email', 'slack', 'webhook'].
        """
        self.logger.warning(f"ALERT: {alert['message']}")
        
        if "email" in channels:
            self._send_email(alert)
        
        if "slack" in channels:
            self._send_slack(alert)
        
        if "webhook" in channels:
            self._send_webhook(alert)
    
    def _send_email(self, alert: Dict) -> None:
        """Send email alert (placeholder)."""
        pass
    
    def _send_slack(self, alert: Dict) -> None:
        """Send Slack alert (placeholder)."""
        pass
    
    def _send_webhook(self, alert: Dict) -> None:
        """Send webhook alert (placeholder)."""
        pass
```

---

## 9. Implementation Checklist - Phase 6

### Week 1: Data Pipeline & Components

- [ ] **Day 1-2**: Real-time data manager
  - [ ] Implement `RealtimeDataManager`
  - [ ] Load veto ledger (Parquet)
  - [ ] Load trade log (Parquet)
  - [ ] Caching strategy (1 sec TTL)

- [ ] **Day 2-3**: KPI computation
  - [ ] Compute Sharpe, drawdown, win rate
  - [ ] Compute equity curve
  - [ ] Unit tests: `test_data_pipeline.py`

- [ ] **Day 3-4**: KPI cards component
  - [ ] Render metric cards
  - [ ] Color coding (green/red)
  - [ ] Delta display

- [ ] **Day 4-5**: Chart components
  - [ ] Equity curve (line chart)
  - [ ] P&L timeline (bar chart)
  - [ ] Veto breakdown (pie chart)

### Week 2: Dashboard Pages & Monitoring

- [ ] **Day 6-7**: Main dashboard app
  - [ ] Streamlit configuration
  - [ ] Sidebar navigation
  - [ ] Page routing

- [ ] **Day 7-8**: Dashboard pages
  - [ ] Live Monitor page (01)
  - [ ] Veto Analysis page (02)
  - [ ] Trade Log page (03)

- [ ] **Day 8-9**: Model Registry + Risk pages
  - [ ] Model Registry page (04)
  - [ ] Risk Dashboard page (05)
  - [ ] Settings page (06)

- [ ] **Day 9-10**: Alerts + optimization
  - [ ] Alert engine
  - [ ] Email/Slack integration
  - [ ] Performance tuning (< 1 sec refresh)
  - [ ] All tests 85%+ coverage

---

## 10. Success Criteria

| Criterion | Test | Expected |
|-----------|------|----------|
| Data pipeline loads | `test_data_load()` | ✓ < 100ms |
| KPI metrics computed | `test_kpi_computation()` | ✓ Correct values |
| Dashboard renders | `test_dashboard_render()` | ✓ No errors |
| Pages load | `test_page_load()` | ✓ All 6 pages work |
| Charts display | `test_chart_render()` | ✓ Interactive |
| Refresh updates | `test_auto_refresh()` | ✓ Every 1 sec |
| Alerts trigger | `test_alert_logic()` | ✓ Correct conditions |
| Export works | `test_export()` | ✓ CSV, PDF generated |

---

## 11. Performance Targets

| Component | Target |
|-----------|--------|
| Dashboard load | < 2 seconds |
| Page render | < 1 second |
| Data refresh | < 100ms |
| Chart rendering | < 500ms |
| Alert checking | < 50ms |

---

## 12. Integration with Phases 1-5 & Handoff to Phase 7

### 12.1 Phase Dependencies

- **Phase 1**: Config, logging, exceptions
- **Phase 2**: Feature engine outputs
- **Phase 3**: Tournament results
- **Phase 4**: DSR thresholds, promotion registry
- **Phase 5**: Veto ledger, trade log, execution data

### 12.2 Outputs for Phase 7 (Hardening)

- Dashboard metrics (for stress testing)
- Performance reports (historical)
- Alert logs (for debugging)

---

## 13. Deliverables Summary - Phase 6

### Codebase
- [ ] `/new_pipeline/monitoring/dashboard.py` (200+ lines)
- [ ] `/new_pipeline/monitoring/data_pipeline.py` (400+ lines)
- [ ] `/new_pipeline/monitoring/pages/*.py` (1000+ lines total)
- [ ] `/new_pipeline/monitoring/components/*.py` (500+ lines total)
- [ ] `/new_pipeline/monitoring/alert_engine.py` (150+ lines)
- [ ] 80+ unit tests

### Live Dashboard
- [ ] Streamlit app running on port 8501
- [ ] 6 interactive pages
- [ ] Real-time metrics updating
- [ ] Alert system functional
- [ ] Export capabilities (CSV, PDF)

### Performance
- [ ] Dashboard load < 2 sec
- [ ] Page render < 1 sec
- [ ] Data refresh < 100ms
- [ ] 85%+ test coverage

---

**Next**: After Phase 6 completion, proceed to [Phase 7: Production Hardening & Deployment](PHASE_7_SPECIFICATION.md) (to be created).

**Previous Phases**:
- [Phase 1: Core Pipeline Infrastructure](PHASE_1_SPECIFICATION.md)
- [Phase 2: Vectorized Quant Engine & Shields](PHASE_2_SPECIFICATION.md)
- [Phase 3: Tournament Backtesting & Model Selection](PHASE_3_SPECIFICATION.md)
- [Phase 4: Statistical Evaluation & Promotion](PHASE_4_SPECIFICATION.md)
- [Phase 5: Live Execution & Orchestration](PHASE_5_SPECIFICATION.md)

```

---

### File: `docs/ROADMAP_2026.md`

```markdown
# Quantum Avenger: Integrated Development Roadmap 2026

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

#### Planned Architecture (currently stub):
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

**Reference Integration**: Build upon `/reference_code/dashboard.py` stub

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

```

---

### File: `docs/PHASE_4_SPECIFICATION.md`

```markdown
# Phase 4: Statistical Evaluation & Model Promotion - Detailed Specification

**Duration**: 2 weeks  
**Target Date**: Complete by mid-July (after Phase 3)  
**Success Criteria**: DSR computation validated; HMM synthetic tests passing; promotion gates working; 85%+ test coverage

---

## 1. Phase 4 Architecture Overview

### 1.1 System Context (Integration with Phases 1-3)

```
┌────────────────────────────────────────────────────────────┐
│  PHASES 1-3 (Complete): Infrastructure, Features, Training│
├────────────────────────────────────────────────────────────┤
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PHASE 4: STATISTICAL EVALUATION & MODEL PROMOTION  │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │                                                      │  │
│  │  LAYER 1: CANDIDATE REGISTRY LOADING                │  │
│  │  ├─ Read {sector}_candidate.json models             │  │
│  │  ├─ Read {sector}_candidate_features.json           │  │
│  │  ├─ Load returns_matrix_{sector}.parquet (OOS rets) │  │
│  │  └─ Load benchmark_{sector}.parquet (bench rets)    │  │
│  │                                                      │  │
│  │  LAYER 2: DEFLATED SHARPE RATIO (DSR)              │  │
│  │  ├─ Bailey & Lopez de Prado framework               │  │
│  │  ├─ Adjust for skewness, kurtosis                   │  │
│  │  ├─ Control for multiple testing bias               │  │
│  │  ├─ Compute DSR percentile (0-1)                    │  │
│  │  └─ Threshold: DSR ≥ 0.95 (99.5th percentile)      │  │
│  │                                                      │  │
│  │  LAYER 3: SYNTHETIC GENERALIZATION VALIDATION       │  │
│  │  ├─ Fit 3-state GaussianHMM to benchmark returns   │  │
│  │  ├─ Extract regime parameters (means, transitions)  │  │
│  │  ├─ Generate synthetic returns (Monte Carlo)        │  │
│  │  ├─ Bootstrap features (destroy temporal order)     │  │
│  │  ├─ Infer on synthetic → calculate Sharpe          │  │
│  │  └─ Verify synthetic_sr > 0 (true alpha, not luck) │  │
│  │                                                      │  │
│  │  LAYER 4: PROMOTION DECISION LOGIC                  │  │
│  │  ├─ If DSR ≥ 0.95 AND synthetic_sr > 0:            │  │
│  │  │   ├─ PROMOTE: candidate → champion              │  │
│  │  │   ├─ Generate HTML tearsheet                     │  │
│  │  │   └─ Register in champion registry               │  │
│  │  └─ Else: REJECT (log reason, cleanup)              │  │
│  │                                                      │  │
│  │  LAYER 5: AUDIT TRAIL & REPORTING                  │  │
│  │  ├─ Log DSR computation details                     │  │
│  │  ├─ Log HMM regime parameters                       │  │
│  │  ├─ Generate HTML tearsheets (quantstats)           │  │
│  │  ├─ Track promotion history per sector              │  │
│  │  └─ Alert on model promotion events                 │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│         Uses Phase 1: Config, Logger, Exceptions           │
│         Uses Phase 2: Feature outputs, Shield Agent        │
│         Uses Phase 3: Candidate models, returns matrices   │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

```
/new_pipeline/evaluation/        # ✨ NEW: Evaluation module
├── __init__.py
├── dsr.py                       # ✨ NEW: Deflated Sharpe Ratio
├── hmm_validator.py             # ✨ NEW: HMM synthetic validation
├── promotion.py                 # ✨ NEW: Promotion logic
├── tearsheet.py                 # ✨ NEW: HTML report generation
└── tests/
    ├── test_dsr.py
    ├── test_hmm_validator.py
    ├── test_promotion.py
    └── benchmarks/
        ├── bench_dsr_computation.py
        └── bench_hmm_generation.py
```

---

## 2. Deflated Sharpe Ratio (DSR) Computation

### 2.1 Theory: Bailey & Lopez de Prado Framework

**Problem**: Standard Sharpe ratio is biased upward under multiple testing hypothesis.

**Solution**: Deflate Sharpe by accounting for:
1. Non-Normal returns (skewness, kurtosis)
2. Number of trials (multiple testing bias)
3. Strategy history length

### 2.2 Module: `evaluation/dsr.py`

**File: `evaluation/dsr.py`**

#### 2.2.1 DSR Computation Function

**Function: `compute_deflated_sharpe_ratio()`**

```python
from scipy.stats import norm
import numpy as np

def compute_deflated_sharpe_ratio(
    trial_matrix: pd.DataFrame,
    champion_returns: pd.Series,
    verbose: bool = True
) -> float:
    """Compute Deflated Sharpe Ratio (DSR) for statistical validation.
    
    Args:
        trial_matrix: DataFrame where each column is out-of-sample returns 
                     from one backtest trial (hyperparameter combo).
                     Shape: (n_observations, n_trials)
        champion_returns: Series of OOS returns for the champion model 
                         (best hyperparameter combo).
        verbose: Print computation steps.
    
    Returns:
        DSR percentile (0-1):
        - DSR < 0.5: Model worse than random (likely overfit)
        - 0.5 ≤ DSR < 0.95: Statistically insignificant
        - DSR ≥ 0.95: Genuine alpha signal (99.5th percentile)
    
    Formula (High-Level):
        1. Compute champion Sharpe ratio: SR_champ = mean(ret) / std(ret)
        2. Extract non-Normal moments: skew, kurtosis
        3. Compute trial variances: var_trials = var(SR per trial)
        4. Compute expected max Sharpe under null (random):
           SR_expected = sqrt(var_trials) × exp(euler_mascheroni) / sqrt(n)
        5. Deflate champion Sharpe:
           denom = sqrt(1 - skew×SR_champ + (kurtosis-1)/4 × SR_champ²)
           DSR_stat = (SR_champ - SR_expected) × sqrt(T-1) / denom
        6. Return: P(Z ≤ DSR_stat) via normal CDF
    
    Mathematical Details:
        - bailey_lopez_de_prado_2013 (https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)
        - euler_mascheroni ≈ 0.5772156649 (natural constant)
        - Non-Normal adjustment accounts for skewness/kurtosis bias
        - Multiple testing bias penalizes having too many trials
    """
    
    logger = get_logger(__name__)
    
    # ─────────────────────────────────────────────────────────────
    # STEP 1: Compute Champion Sharpe Ratio
    # ─────────────────────────────────────────────────────────────
    
    champ_returns = champion_returns.dropna()
    champ_mean = np.mean(champ_returns)
    champ_std = np.std(champ_returns, ddof=1)  # Sample std
    
    if champ_std == 0:
        logger.warning("Champion returns have zero std; DSR undefined")
        return 0.0
    
    sr_champ = champ_mean / champ_std
    
    if verbose:
        print(f"Champion Sharpe Ratio: {sr_champ:.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 2: Extract Non-Normal Moments
    # ─────────────────────────────────────────────────────────────
    
    skewness = scipy.stats.skew(champ_returns)
    kurtosis = scipy.stats.kurtosis(champ_returns)  # Excess kurtosis
    
    if verbose:
        print(f"Skewness: {skewness:.4f}, Excess Kurtosis: {kurtosis:.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 3: Compute Trial Sharpe Ratios & Variance
    # ─────────────────────────────────────────────────────────────
    
    trial_srs = []
    for col in trial_matrix.columns:
        trial_ret = trial_matrix[col].dropna()
        if len(trial_ret) > 1:
            trial_mean = np.mean(trial_ret)
            trial_std = np.std(trial_ret, ddof=1)
            if trial_std > 0:
                trial_sr = trial_mean / trial_std
                trial_srs.append(trial_sr)
    
    trial_srs = np.array(trial_srs)
    var_trials = np.var(trial_srs, ddof=1)
    n_trials = len(trial_srs)
    
    if verbose:
        print(f"Number of trials: {n_trials}")
        print(f"Trial Sharpe variance: {var_trials:.6f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 4: Compute Expected Max Sharpe Under Null (H0: random)
    # ─────────────────────────────────────────────────────────────
    
    euler_mascheroni = 0.5772156649
    T = len(champ_returns)
    
    # Expected max Sharpe formula
    sr_expected = np.sqrt(var_trials) * (
        (1 - euler_mascheroni) / np.sqrt(np.pi) +
        euler_mascheroni * np.log(n_trials) / np.sqrt(2 * np.pi)
    ) / np.sqrt(n_trials)
    
    if verbose:
        print(f"Expected max Sharpe (H0): {sr_expected:.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 5: Deflate Champion Sharpe (Account for Non-Normality)
    # ─────────────────────────────────────────────────────────────
    
    # Non-Normal adjustment factor
    denom = np.sqrt(
        1.0 - skewness * sr_champ + 
        (kurtosis - 1.0) / 4.0 * sr_champ ** 2
    )
    
    # Deflated Sharpe statistic
    dsr_stat = (sr_champ - sr_expected) * np.sqrt(T - 1) / denom
    
    if verbose:
        print(f"Deflated Sharpe statistic: {dsr_stat:.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 6: Convert to Percentile
    # ─────────────────────────────────────────────────────────────
    
    dsr_percentile = norm.cdf(dsr_stat)
    
    if verbose:
        print(f"Deflated Sharpe Ratio (percentile): {dsr_percentile:.4f}")
    
    return dsr_percentile
```

#### 2.2.2 DSR Interpretation & Thresholds

**Function: `interpret_dsr()`**

```python
def interpret_dsr(dsr: float) -> Dict[str, str]:
    """Interpret DSR value and provide recommendation.
    
    Args:
        dsr: DSR percentile (0-1).
    
    Returns:
        Dict with interpretation:
        {
            'percentile': float,
            'interpretation': str,
            'recommendation': str,
            'color': str (green/yellow/red)
        }
    
    Thresholds:
        - DSR < 0.5: Red (likely overfit)
        - 0.5 ≤ DSR < 0.95: Yellow (insufficient evidence)
        - DSR ≥ 0.95: Green (genuine alpha)
    """
    if dsr >= 0.95:
        return {
            'percentile': dsr,
            'interpretation': 'Genuine Alpha Signal',
            'recommendation': 'PROMOTE to production',
            'color': 'green',
            'reason': 'DSR ≥ 0.95 (99.5th percentile)'
        }
    elif dsr >= 0.50:
        return {
            'percentile': dsr,
            'interpretation': 'Statistically Insignificant',
            'recommendation': 'REJECT, need more tuning',
            'color': 'yellow',
            'reason': f'DSR = {dsr:.3f} (below threshold)'
        }
    else:
        return {
            'percentile': dsr,
            'interpretation': 'Likely Overfit',
            'recommendation': 'REJECT, model is curve-fitted',
            'color': 'red',
            'reason': f'DSR = {dsr:.3f} (worse than random)'
        }
```

#### 2.2.3 DSR with Confidence Intervals

**Function: `compute_dsr_confidence_interval()`**

```python
def compute_dsr_confidence_interval(
    trial_matrix: pd.DataFrame,
    champion_returns: pd.Series,
    n_bootstrap: int = 1000,
    ci: float = 0.95
) -> Tuple[float, float, float]:
    """Compute DSR with bootstrap confidence interval.
    
    Args:
        trial_matrix: Trial returns matrix.
        champion_returns: Champion returns series.
        n_bootstrap: Number of bootstrap iterations.
        ci: Confidence interval (e.g., 0.95 for 95%).
    
    Returns:
        (dsr_mean, dsr_lower, dsr_upper):
        - dsr_mean: Point estimate
        - dsr_lower: Lower bound
        - dsr_upper: Upper bound
    
    Notes:
        - Bootstrap resamples with replacement
        - Provides uncertainty quantification
        - Wider CI → less confidence in estimate
    """
    dsr_boots = []
    
    for _ in range(n_bootstrap):
        # Resample champion returns
        champ_boot = np.random.choice(
            champion_returns.dropna(),
            size=len(champion_returns),
            replace=True
        )
        
        # Resample trial matrix columns
        trial_boot = pd.DataFrame()
        for col in trial_matrix.columns:
            trial_col = trial_matrix[col].dropna()
            trial_boot[col] = np.random.choice(
                trial_col,
                size=len(trial_col),
                replace=True
            )
        
        # Compute DSR on bootstrap sample
        dsr_boot = compute_deflated_sharpe_ratio(
            trial_boot,
            pd.Series(champ_boot),
            verbose=False
        )
        
        dsr_boots.append(dsr_boot)
    
    dsr_boots = np.array(dsr_boots)
    dsr_mean = np.mean(dsr_boots)
    
    alpha = 1 - ci
    dsr_lower = np.percentile(dsr_boots, alpha / 2 * 100)
    dsr_upper = np.percentile(dsr_boots, (1 - alpha / 2) * 100)
    
    return dsr_mean, dsr_lower, dsr_upper
```

---

## 3. HMM Synthetic Generalization Validator

### 3.1 Theory: Testing Out-of-Distribution Generalization

**Problem**: DSR tests if champion beats random. But does it generalize to new market regimes?

**Solution**: Use Hidden Markov Model (HMM) to:
1. Extract market regime parameters from benchmark returns
2. Generate synthetic returns (novel distribution)
3. Apply champion model to synthetic data
4. Verify model performance > 0 (true alpha, not luck)

### 3.2 Module: `evaluation/hmm_validator.py`

**File: `evaluation/hmm_validator.py`**

#### 3.2.1 HMM Synthetic Validation

**Function: `run_hmm_synthetic_gauntlet()`**

```python
from hmmlearn.gaussian_hmm import GaussianHMM
import numpy as np

def run_hmm_synthetic_gauntlet(
    sector: str,
    champion_model_path: str,
    features_path: str,
    benchmark_returns: pd.Series,
    synthetic_returns: pd.Series = None,
    n_states: int = 3,
    n_synthetic: int = None,
    verbose: bool = True
) -> Dict[str, float]:
    """Validate champion model on HMM-generated synthetic returns.
    
    Args:
        sector: Sector name (for logging).
        champion_model_path: Path to champion XGBoost model JSON.
        features_path: Path to feature manifest JSON.
        benchmark_returns: Historical benchmark returns (used to fit HMM).
        synthetic_returns: If provided, use these instead of generating.
        n_states: Number of HMM states (typically 3 for low/normal/high vol).
        n_synthetic: Length of synthetic series (default = len(benchmark)).
        verbose: Print steps.
    
    Returns:
        {
            'synthetic_sharpe': float (model performance on synthetic),
            'synthetic_returns': np.ndarray,
            'hmm_means': List[float],
            'hmm_stds': List[float],
            'hmm_transitions': np.ndarray,
            'validation_passed': bool (synthetic_sr > 0)
        }
    
    Flow:
        1. Fit HMM to benchmark returns
        2. Generate synthetic returns via HMM sampling
        3. Create synthetic features (bootstrap historical)
        4. Load champion model
        5. Generate signals on synthetic features
        6. Calculate Sharpe ratio on synthetic returns
        7. Verify synthetic_sr > 0
    
    Rationale:
        - HMM preserves market regime dynamics (not iid random)
        - Synthetic returns never seen by training algorithm
        - If model works on synthetic → true alpha
        - If synthetic_sr ≤ 0 → model was just overfitting to historical noise
    """
    
    logger = get_logger(__name__)
    logger.info(f"Running HMM synthetic gauntlet for {sector}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 1: Fit HMM to Benchmark Returns
    # ─────────────────────────────────────────────────────────────
    
    bench_returns = benchmark_returns.dropna()
    X = bench_returns.values.reshape(-1, 1)
    
    hmm = GaussianHMM(n_components=n_states, covariance_type='full', n_iter=1000)
    hmm.fit(X)
    
    if verbose:
        print(f"HMM fitted with {n_states} states")
        print(f"  Means: {hmm.means_.flatten()}")
        print(f"  Transition matrix:\n{hmm.transmat_}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 2: Generate Synthetic Returns (Monte Carlo)
    # ─────────────────────────────────────────────────────────────
    
    if synthetic_returns is None:
        n_synthetic = n_synthetic or len(bench_returns)
        synthetic_returns, _ = hmm.sample(n_samples=n_synthetic)
        synthetic_returns = synthetic_returns.flatten()
    else:
        synthetic_returns = synthetic_returns.values
    
    if verbose:
        print(f"Generated {len(synthetic_returns)} synthetic returns")
        print(f"  Mean: {np.mean(synthetic_returns):.6f}")
        print(f"  Std: {np.std(synthetic_returns):.6f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 3: Bootstrap Historical Features (Destroy Temporal Order)
    # ─────────────────────────────────────────────────────────────
    
    # This is critical: we want to preserve feature distributions
    # but destroy any temporal correlation with synthetic returns
    
    # Placeholder: in actual implementation, load historical feature data
    # For now, assume synthetic features created by resampling
    
    # ─────────────────────────────────────────────────────────────
    # STEP 4: Load Champion Model & Generate Signals
    # ─────────────────────────────────────────────────────────────
    
    booster = xgb.Booster()
    booster.load_model(champion_model_path)
    
    # Load feature list
    with open(features_path, 'r') as f:
        feature_manifest = json.load(f)
    features = feature_manifest['features']
    
    # Create synthetic feature DataFrame (simplified)
    n_features = len(features)
    synthetic_features = np.random.randn(len(synthetic_returns), n_features)
    synthetic_df = pd.DataFrame(synthetic_features, columns=features)
    
    # Generate signals
    dmatrix = xgb.DMatrix(synthetic_df)
    synthetic_signals = booster.predict(dmatrix)
    synthetic_signals = (synthetic_signals > 0.5).astype(int)
    
    if verbose:
        print(f"Generated {np.sum(synthetic_signals)} signals on {len(synthetic_returns)} returns")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 5: Calculate Sharpe Ratio on Synthetic
    # ─────────────────────────────────────────────────────────────
    
    # Strategy returns = signal × synthetic returns
    strategy_returns = synthetic_signals * synthetic_returns
    
    mean_strat = np.mean(strategy_returns)
    std_strat = np.std(strategy_returns, ddof=1)
    
    synthetic_sharpe = (mean_strat / std_strat) * np.sqrt(252) if std_strat > 0 else 0.0
    
    if verbose:
        print(f"Synthetic Strategy Sharpe: {synthetic_sharpe:.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 6: Validation
    # ─────────────────────────────────────────────────────────────
    
    validation_passed = synthetic_sharpe > 0.0
    
    logger.info(f"Validation {'PASSED' if validation_passed else 'FAILED'}: SR={synthetic_sharpe:.4f}")
    
    return {
        'synthetic_sharpe': synthetic_sharpe,
        'synthetic_returns': synthetic_returns,
        'hmm_means': hmm.means_.flatten().tolist(),
        'hmm_stds': np.sqrt(hmm.covars_.flatten()).tolist(),
        'hmm_transitions': hmm.transmat_.tolist(),
        'validation_passed': validation_passed
    }
```

---

## 4. Model Promotion Logic

### 4.1 Module: `evaluation/promotion.py`

**File: `evaluation/promotion.py`**

#### 4.1.1 Promotion Decision Engine

**Function: `assess_sector_for_promotion()`**

```python
def assess_sector_for_promotion(
    sector: str,
    dsr: float,
    hmm_result: Dict,
    config: AppConfig
) -> Dict[str, Any]:
    """Make promotion/rejection decision for a sector.
    
    Args:
        sector: Sector name.
        dsr: Deflated Sharpe Ratio (0-1 percentile).
        hmm_result: Output from run_hmm_synthetic_gauntlet().
        config: AppConfig with promotion thresholds.
    
    Returns:
        {
            'sector': str,
            'decision': str ('PROMOTE', 'REJECT'),
            'dsr': float,
            'synthetic_sharpe': float,
            'reasons': List[str],
            'champion_path': str (if promoted),
            'rejection_reason': str (if rejected)
        }
    
    Decision Logic:
        Gate 1: DSR ≥ 0.95?
        ├─ NO → REJECT ('DSR below threshold')
        └─ YES ↓
        
        Gate 2: Synthetic Sharpe > 0?
        ├─ NO → REJECT ('No generalization')
        └─ YES ↓
        
        Gate 3: All gates passed?
        └─ YES → PROMOTE
    """
    
    logger = get_logger(__name__)
    
    dsr_threshold = config.evaluation.dsr_promotion_threshold  # typically 0.95
    synthetic_sr_threshold = config.evaluation.synthetic_sr_threshold  # typically 0.0
    
    reasons = []
    decision = 'PROMOTE'
    
    # ─────────────────────────────────────────────────────────────
    # GATE 1: DSR Threshold
    # ─────────────────────────────────────────────────────────────
    
    if dsr < dsr_threshold:
        decision = 'REJECT'
        reasons.append(f"DSR {dsr:.3f} < threshold {dsr_threshold}")
    else:
        reasons.append(f"✓ DSR {dsr:.3f} ≥ threshold {dsr_threshold}")
    
    # ─────────────────────────────────────────────────────────────
    # GATE 2: Synthetic Sharpe Validation
    # ─────────────────────────────────────────────────────────────
    
    synthetic_sr = hmm_result['synthetic_sharpe']
    
    if synthetic_sr <= synthetic_sr_threshold:
        decision = 'REJECT'
        reasons.append(f"Synthetic SR {synthetic_sr:.3f} ≤ threshold {synthetic_sr_threshold}")
    else:
        reasons.append(f"✓ Synthetic SR {synthetic_sr:.3f} > threshold {synthetic_sr_threshold}")
    
    # ─────────────────────────────────────────────────────────────
    # DECISION OUTPUT
    # ─────────────────────────────────────────────────────────────
    
    result = {
        'sector': sector,
        'decision': decision,
        'dsr': dsr,
        'synthetic_sharpe': synthetic_sr,
        'reasons': reasons,
        'timestamp': pd.Timestamp.now()
    }
    
    if decision == 'PROMOTE':
        # Move candidate → champion
        candidate_path = f"{config.models.candidate_models_dir}/{sector}_candidate.json"
        champion_path = f"{config.models.prod_models_dir}/{sector}_champion.json"
        
        shutil.copy(candidate_path, champion_path)
        logger.info(f"[{sector}] PROMOTED: {candidate_path} → {champion_path}")
        
        result['champion_path'] = champion_path
    else:
        result['rejection_reason'] = '; '.join(reasons)
        logger.warning(f"[{sector}] REJECTED: {result['rejection_reason']}")
    
    return result
```

#### 4.1.2 Promotion Registry & Audit Trail

**Class: `PromotionRegistry`**

```python
class PromotionRegistry:
    """Track model promotions and maintain audit trail.
    
    Methods:
        record_promotion: Log a promotion event.
        get_promotion_history: Retrieve history for sector.
        get_active_champions: List currently live models.
    """
    
    def __init__(self, registry_path: str):
        """Initialize registry.
        
        Args:
            registry_path: Path to registry file (JSON).
        """
        self.registry_path = registry_path
        self.logger = get_logger(__name__)
        
        # Load existing registry or create new
        if os.path.exists(registry_path):
            with open(registry_path, 'r') as f:
                self.registry = json.load(f)
        else:
            self.registry = {'promotions': [], 'active_champions': {}}
    
    def record_promotion(self, promotion_record: Dict) -> None:
        """Record a promotion/rejection event.
        
        Args:
            promotion_record: Dict with sector, decision, dsr, etc.
        """
        self.registry['promotions'].append(promotion_record)
        
        if promotion_record['decision'] == 'PROMOTE':
            self.registry['active_champions'][promotion_record['sector']] = {
                'champion_path': promotion_record['champion_path'],
                'promoted_at': promotion_record['timestamp'].isoformat(),
                'dsr': promotion_record['dsr'],
                'synthetic_sharpe': promotion_record['synthetic_sharpe']
            }
        
        self._save()
        self.logger.info(f"Recorded: {promotion_record['decision']} for {promotion_record['sector']}")
    
    def _save(self) -> None:
        """Persist registry to disk."""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2, default=str)
    
    def get_active_champions(self) -> Dict[str, Dict]:
        """Return currently active champion models."""
        return self.registry.get('active_champions', {})
```

---

## 5. HTML Tearsheet Generation

### 5.1 Module: `evaluation/tearsheet.py`

**File: `evaluation/tearsheet.py`**

#### 5.1.1 Tearsheet Generation

**Function: `generate_html_tearsheet()`**

```python
import quantstats as qs
from jinja2 import Template

def generate_html_tearsheet(
    sector: str,
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    dsr: float,
    hmm_result: Dict,
    output_path: str
) -> str:
    """Generate comprehensive HTML performance tearsheet.
    
    Args:
        sector: Sector name.
        strategy_returns: Strategy returns series.
        benchmark_returns: Benchmark returns series.
        dsr: Deflated Sharpe Ratio.
        hmm_result: HMM validation results.
        output_path: Where to save HTML file.
    
    Returns:
        Path to generated HTML file.
    
    Contents:
        1. Summary metrics (Sharpe, max drawdown, win rate)
        2. Equity curve comparison (strategy vs benchmark)
        3. Monthly/annual returns heatmap
        4. Drawdown timeline
        5. DSR computation details
        6. HMM regime analysis
        7. Rolling Sharpe ratio
        8. Return distribution histogram
    """
    
    logger = get_logger(__name__)
    
    # Generate quantstats report
    stats_html = qs.stats.html(
        strategy_returns,
        benchmark_returns,
        title=f"Quantum Avenger - {sector} Model Tearsheet"
    )
    
    # Extract key metrics
    metrics = {
        'sector': sector,
        'strategy_sharpe': qs.stats.sharpe(strategy_returns) * np.sqrt(252),
        'benchmark_sharpe': qs.stats.sharpe(benchmark_returns) * np.sqrt(252),
        'strategy_sortino': qs.stats.sortino(strategy_returns),
        'max_drawdown': qs.stats.max_drawdown(strategy_returns),
        'cagr': qs.stats.cagr(strategy_returns),
        'win_rate': np.sum(strategy_returns > 0) / len(strategy_returns[strategy_returns != 0]),
        'dsr': dsr,
        'synthetic_sharpe': hmm_result['synthetic_sharpe'],
        'validation_passed': hmm_result['validation_passed']
    }
    
    # Custom template
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ sector }} Model Tearsheet</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .summary { background: #f0f0f0; padding: 10px; margin: 10px 0; }
            .metric { display: inline-block; margin: 10px; }
            .pass { color: green; font-weight: bold; }
            .fail { color: red; font-weight: bold; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
        </style>
    </head>
    <body>
        <h1>{{ sector }} Model Performance Tearsheet</h1>
        
        <div class="summary">
            <h2>Summary Metrics</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Strategy Sharpe (Annual)</td>
                    <td>{{ "%.3f" % metrics.strategy_sharpe }}</td>
                </tr>
                <tr>
                    <td>Benchmark Sharpe (Annual)</td>
                    <td>{{ "%.3f" % metrics.benchmark_sharpe }}</td>
                </tr>
                <tr>
                    <td>Max Drawdown</td>
                    <td>{{ "%.2f" % (metrics.max_drawdown * 100) }}%</td>
                </tr>
                <tr>
                    <td>CAGR</td>
                    <td>{{ "%.2f" % (metrics.cagr * 100) }}%</td>
                </tr>
                <tr>
                    <td>Win Rate</td>
                    <td>{{ "%.1f" % (metrics.win_rate * 100) }}%</td>
                </tr>
            </table>
        </div>
        
        <div class="summary">
            <h2>Statistical Validation</h2>
            <table>
                <tr>
                    <td>Deflated Sharpe Ratio (DSR)</td>
                    <td class="{{ 'pass' if metrics.dsr >= 0.95 else 'fail' }}">
                        {{ "%.4f" % metrics.dsr }}
                    </td>
                </tr>
                <tr>
                    <td>Synthetic Sharpe (HMM Test)</td>
                    <td class="{{ 'pass' if metrics.synthetic_sharpe > 0 else 'fail' }}">
                        {{ "%.4f" % metrics.synthetic_sharpe }}
                    </td>
                </tr>
                <tr>
                    <td>Validation Status</td>
                    <td class="{{ 'pass' if metrics.validation_passed else 'fail' }}">
                        {{ "PASSED" if metrics.validation_passed else "FAILED" }}
                    </td>
                </tr>
            </table>
        </div>
        
        <h2>Quantstats Report</h2>
        {{ stats_html|safe }}
    </body>
    </html>
    """
    
    template = Template(template_str)
    html_content = template.render(metrics=metrics, stats_html=stats_html)
    
    # Save to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Generated tearsheet: {output_path}")
    
    return output_path
```

---

## 6. Full Evaluation Pipeline

### 6.1 Module: `evaluation/evaluator.py` (Orchestrator)

**Class: `QuantitativeEvaluator`**

```python
class QuantitativeEvaluator:
    """Orchestrates full evaluation pipeline for all sectors.
    
    Methods:
        evaluate_all_sectors: Run evaluation for all candidates.
        evaluate_single_sector: Evaluate one sector.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
        self.registry = PromotionRegistry(
            f"{config.models.registry_path}/promotion_registry.json"
        )
    
    def evaluate_single_sector(self, sector: str) -> Dict:
        """Evaluate one sector and make promotion decision.
        
        Args:
            sector: Sector name.
        
        Returns:
            Dict with evaluation results and decision.
        
        Flow:
            1. Load candidate model + features
            2. Load returns matrix (from Phase 3)
            3. Compute DSR
            4. Run HMM synthetic gauntlet
            5. Make promotion decision
            6. Generate tearsheet
            7. Log to registry
        """
        self.logger.info(f"Evaluating {sector}")
        
        try:
            # Load candidate
            candidate_model_path = f"{self.config.models.candidate_models_dir}/{sector}_candidate.json"
            features_path = f"{self.config.models.candidate_models_dir}/{sector}_candidate_features.json"
            
            # Load returns
            returns_path = f"{self.config.tournament.results_dir}/returns_matrix_{sector}.parquet"
            benchmark_path = f"{self.config.tournament.results_dir}/benchmark_{sector}.parquet"
            
            returns_matrix = pd.read_parquet(returns_path)
            benchmark_returns = pd.read_parquet(benchmark_path).squeeze()
            champion_returns = returns_matrix.iloc[:, 0]  # Best combo
            
            # Compute DSR
            dsr = compute_deflated_sharpe_ratio(
                returns_matrix,
                champion_returns,
                verbose=True
            )
            
            # Run HMM validation
            hmm_result = run_hmm_synthetic_gauntlet(
                sector,
                candidate_model_path,
                features_path,
                benchmark_returns,
                verbose=True
            )
            
            # Make promotion decision
            promotion_result = assess_sector_for_promotion(
                sector,
                dsr,
                hmm_result,
                self.config
            )
            
            # Generate tearsheet
            tearsheet_path = f"{self.config.models.reports_dir}/{sector}_tearsheet.html"
            generate_html_tearsheet(
                sector,
                champion_returns,
                benchmark_returns,
                dsr,
                hmm_result,
                tearsheet_path
            )
            
            promotion_result['tearsheet_path'] = tearsheet_path
            
            # Record in registry
            self.registry.record_promotion(promotion_result)
            
            return promotion_result
            
        except Exception as e:
            self.logger.error(f"Evaluation failed for {sector}: {e}", exc_info=True)
            return {
                'sector': sector,
                'decision': 'ERROR',
                'error': str(e)
            }
    
    def evaluate_all_sectors(self) -> Dict[str, Dict]:
        """Evaluate all candidate models.
        
        Returns:
            Dict mapping sector → evaluation result.
        """
        results = {}
        
        # Get all candidate sectors
        candidate_dir = self.config.models.candidate_models_dir
        candidates = glob.glob(f"{candidate_dir}/*_candidate.json")
        sectors = [
            os.path.basename(p).replace('_candidate.json', '')
            for p in candidates
        ]
        
        for sector in sectors:
            result = self.evaluate_single_sector(sector)
            results[sector] = result
        
        # Summary report
        promoted = [s for s, r in results.items() if r.get('decision') == 'PROMOTE']
        rejected = [s for s, r in results.items() if r.get('decision') == 'REJECT']
        
        self.logger.info(f"Evaluation complete:")
        self.logger.info(f"  Promoted: {len(promoted)} ({', '.join(promoted)})")
        self.logger.info(f"  Rejected: {len(rejected)} ({', '.join(rejected)})")
        
        return results
```

---

## 7. Implementation Checklist - Phase 4

### Week 1: DSR & HMM Implementation

- [ ] **Day 1-2**: DSR computation
  - [ ] Implement `compute_deflated_sharpe_ratio()`
  - [ ] Implement `compute_dsr_confidence_interval()`
  - [ ] Unit tests: `test_dsr.py`
  - [ ] Verify against reference implementations

- [ ] **Day 2-3**: DSR validation
  - [ ] Test on synthetic data (known distributions)
  - [ ] Verify DSR ≥ 0.95 for alpha signal
  - [ ] Test DSR < 0.5 for overfit case

- [ ] **Day 3-4**: HMM synthetic validation
  - [ ] Implement `run_hmm_synthetic_gauntlet()`
  - [ ] Test HMM fitting to returns
  - [ ] Validate synthetic returns match regime stats

- [ ] **Day 4-5**: HMM integration
  - [ ] Test feature bootstrapping
  - [ ] Test model inference on synthetic
  - [ ] Unit tests: `test_hmm_validator.py`

### Week 2: Promotion & Reporting

- [ ] **Day 6-7**: Promotion logic
  - [ ] Implement `assess_sector_for_promotion()`
  - [ ] Implement `PromotionRegistry` class
  - [ ] Unit tests: `test_promotion.py`

- [ ] **Day 7-8**: Tearsheet generation
  - [ ] Implement `generate_html_tearsheet()`
  - [ ] Integrate quantstats
  - [ ] Generate sample tearsheet

- [ ] **Day 8-9**: Full evaluator
  - [ ] Implement `QuantitativeEvaluator` class
  - [ ] End-to-end evaluation (candidate → promotion/rejection)
  - [ ] Integration tests: `test_evaluator.py`

- [ ] **Day 9-10**: Benchmarking & optimization
  - [ ] Benchmark DSR computation
  - [ ] Benchmark HMM generation
  - [ ] Profile bottlenecks
  - [ ] All tests passing, 85%+ coverage

---

## 8. Success Criteria & Acceptance Tests

### 8.1 Functional Acceptance

| Criterion | Test | Expected |
|-----------|------|----------|
| DSR computation | `test_dsr_computation()` | ✓ Matches reference |
| DSR ≥ 0.95 detected | `test_dsr_promotion_threshold()` | ✓ Alpha signal identified |
| HMM fitting | `test_hmm_fitting()` | ✓ Regimes extracted |
| Synthetic generation | `test_synthetic_returns()` | ✓ New distribution, not identical |
| Model inference | `test_inference_on_synthetic()` | ✓ Predicts correctly |
| Promotion decision | `test_promotion_logic()` | ✓ Promotes if DSR+HMM pass |
| Rejection decision | `test_rejection_logic()` | ✓ Rejects if gates fail |
| Registry tracking | `test_promotion_registry()` | ✓ History persisted |

### 8.2 Performance Targets

| Component | Target |
|-----------|--------|
| DSR computation | < 10 seconds |
| HMM fitting | < 5 seconds |
| Synthetic generation | < 2 seconds |
| HTML tearsheet | < 5 seconds |
| Full evaluation (sector) | < 30 seconds |

### 8.3 Code Quality

| Criterion | Target |
|-----------|--------|
| Test coverage (evaluation/) | ≥ 85% |
| Type hints | 100% (mypy clean) |
| Linting errors | 0 |

---

## 9. Integration with Phases 1-3 & Handoff to Phase 5

### 9.1 Phase Dependencies

- **Phase 1**: Config (promotion thresholds), logging, exceptions
- **Phase 2**: Feature outputs used in HMM validation
- **Phase 3**: Candidate models, returns matrices

### 9.2 Handoff to Phase 5 (Live Execution)

- Champion models → loaded by live trader
- Promotion registry → tracks which models are live
- Feature manifests → used for real-time inference

---

## 10. Deliverables Summary - Phase 4

### Codebase
- [ ] `/new_pipeline/evaluation/dsr.py` (300+ lines)
- [ ] `/new_pipeline/evaluation/hmm_validator.py` (250+ lines)
- [ ] `/new_pipeline/evaluation/promotion.py` (200+ lines)
- [ ] `/new_pipeline/evaluation/tearsheet.py` (250+ lines)
- [ ] `/new_pipeline/evaluation/evaluator.py` (300+ lines)
- [ ] 100+ unit tests + benchmarks

### Performance
- [ ] DSR correctly identifies alpha vs luck
- [ ] HMM validates generalization
- [ ] Promotion gates enforce quality
- [ ] Full evaluation < 30 sec/sector

### Documentation
- [ ] DSR methodology & interpretation
- [ ] HMM synthetic validation rationale
- [ ] Promotion decision logic
- [ ] Tearsheet interpretation guide

---

**Next**: After Phase 4 completion, proceed to [Phase 5: Live Execution & Orchestration](PHASE_5_SPECIFICATION.md) (to be created).

**Previous Phases**:
- [Phase 1: Core Pipeline Infrastructure](PHASE_1_SPECIFICATION.md)
- [Phase 2: Vectorized Quant Engine & Shields](PHASE_2_SPECIFICATION.md)
- [Phase 3: Tournament Backtesting & Model Selection](PHASE_3_SPECIFICATION.md)

```

---

### File: `docs/PHASE_3_SPECIFICATION.md`

```markdown
# Phase 3: Tournament Backtesting & Model Selection - Detailed Specification

**Duration**: 2 weeks  
**Target Date**: Complete by end of June (after Phase 2)  
**Success Criteria**: CPCV backtests passing; XGBoost models trained; 85%+ out-of-sample test coverage; model promotion logic validated

---

## 1. Phase 3 Architecture Overview

### 1.1 System Context (Integration with Phases 1-2)

```
┌────────────────────────────────────────────────────────────┐
│  PHASE 1 (Complete): Config, Logging, Exceptions, Testing │
│  PHASE 2 (Complete): Polars Vectors, GPU Kernels, Shield  │
├────────────────────────────────────────────────────────────┤
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PHASE 3: TOURNAMENT BACKTESTING & MODEL SELECTION  │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │                                                      │  │
│  │  LAYER 1: DATA PREPARATION                          │  │
│  │  ├─ Load PROCESSED_VAULT (Parquet)                  │  │
│  │  ├─ Sector filtering                                │  │
│  │  ├─ Dask lazy loading                               │  │
│  │  └─ Feature manifest preparation                    │  │
│  │                                                      │  │
│  │  LAYER 2: CPCV SPLIT GENERATION                     │  │
│  │  ├─ 6-group temporal splits                         │  │
│  │  ├─ C(6,2) = 15 test combinations                   │  │
│  │  ├─ Purge gap removal (look-ahead prevention)      │  │
│  │  ├─ Embargo window (data leakage prevention)        │  │
│  │  └─ Yields (train_df, test_df) tuples              │  │
│  │                                                      │  │
│  │  LAYER 3: PARQUET DATA ITERATOR                     │  │
│  │  ├─ Zero-copy PyArrow streaming                     │  │
│  │  ├─ Row-group iteration                             │  │
│  │  ├─ On-disk feature selection                       │  │
│  │  └─ Feeds directly to XGBoost                        │  │
│  │                                                      │  │
│  │  LAYER 4: XGBOOST TRAINING                          │  │
│  │  ├─ Asymmetric financial loss (FP = 5× FN)         │  │
│  │  ├─ ExtMemQuantileDMatrix (VRAM adaptive)           │  │
│  │  ├─ CUDA acceleration (tree_method='gpu_hist')      │  │
│  │  ├─ Hyperparameter grid search                      │  │
│  │  └─ Per-fold model saving                           │  │
│  │                                                      │  │
│  │  LAYER 5: RISK SIMULATION & RETURNS                 │  │
│  │  ├─ Shield Agent evaluation (Numba @njit)           │  │
│  │  ├─ Position sizing & ATR stops                     │  │
│  │  ├─ Out-of-sample returns calculation               │  │
│  │  ├─ Accumulates trial returns matrix                │  │
│  │  └─ Per-fold statistics                             │  │
│  │                                                      │  │
│  │  LAYER 6: MODEL SELECTION & REGISTRATION            │  │
│  │  ├─ Best hyperparams per sector                     │  │
│  │  ├─ Candidate model registry (JSON)                 │  │
│  │  ├─ Feature manifold metadata                       │  │
│  │  └─ Ready for Phase 4 evaluation                    │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│         Uses Phase 1: Config, Logger, Exceptions           │
│         Uses Phase 2: Feature outputs, Shield Agent        │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

```
/new_pipeline/models/
├── __init__.py
├── registry.py                # ✨ NEW: Model artifact storage
├── metadata.py                # ✨ NEW: Model metadata tracking
│
/new_pipeline/tournament/       # ✨ NEW: Tournament module
├── __init__.py
├── base.py                    # Tournament base classes
├── cpcv.py                    # ✨ NEW: CPCV split generation
├── data_iterator.py           # ✨ NEW: ParquetDataIter (zero-copy)
├── training.py                # ✨ NEW: XGBoost training loop
├── risk_simulator.py          # ✨ NEW: Backtest risk simulation
├── grid_search.py             # ✨ NEW: Hyperparameter tuning
├── director.py                # ✨ NEW: ModularTournamentDirector
└── tests/
    ├── test_cpcv.py
    ├── test_data_iterator.py
    ├── test_training.py
    ├── test_risk_simulator.py
    ├── test_grid_search.py
    ├── test_director.py
    └── benchmarks/
        ├── bench_xgboost_training.py
        ├── bench_cpcv_splits.py
        └── bench_risk_simulation.py
```

---

## 2. CPCV (Combinatorial Purged Cross-Validation)

### 2.1 Principle: Preventing Look-Ahead Bias

**Problem**: Standard K-fold CV on time-series data leaks information from future into training set.

**Solution**: CPCV applies temporal purging + embargo gaps to prevent look-ahead bias.

```
Time →

Historical Data:     [0........100........200........300.........400]
                     └─ Start ─────────────────────────────────── End ─┘

Grouping (6 groups):  [0|1|2|3|4|5]
                      └─ Each group ≈ 67 trading days ─┘

Combo 1 (Test=[0,1]):
                      Test: [0|1|·|·|·|·]
                      Purge: Gap before & after test
                      Train: [·|·|2|3|4|5] minus purge zones
                      
Combo 2 (Test=[0,2]):
                      Test: [0|·|2|·|·|·]
                      Purge: Gaps around both test groups
                      Train: [·|1|·|3|4|5] minus purge zones
                      
... (15 total combinations)
```

### 2.2 Module: `tournament/cpcv.py`

**File: `tournament/cpcv.py`**

#### 2.2.1 CPCV Split Generator Class

**Class: `CPCVSplitGenerator`**

```python
class CPCVSplitGenerator:
    """Generates Combinatorial Purged Cross-Validation splits.
    
    Attributes:
        df: DataFrame indexed by date.
        n_groups: Number of temporal groups (default 6).
        test_groups: Size of test set in each split (default 2).
        purge_gap: Gap before/after test set (days, default 5).
        embargo_gap: Additional embargo zone (days, default 5).
    
    Methods:
        generate_splits() → Generator[(train_df, test_df), ...]
        _split_into_groups() → List[indices]
        _apply_purge_embargo() → Purged indices
    """
    
    def __init__(
        self,
        df: pd.DataFrame,
        n_groups: int = 6,
        test_groups: int = 2,
        purge_days: int = 5,
        embargo_days: int = 5,
        config: AppConfig = None
    ):
        """Initialize CPCV generator.
        
        Args:
            df: Indexed by date (required for temporal logic).
            n_groups: Partition data into this many groups.
            test_groups: Size of holdout set C(n_groups, test_groups).
            purge_days: Remove this many days before/after test.
            embargo_days: Additional embargo window (prevents leakage).
            config: AppConfig for DEFAULT_* values.
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame must be indexed by date")
        
        self.df = df.sort_index()
        self.n_groups = n_groups
        self.test_groups = test_groups
        self.purge_gap = pd.Timedelta(days=purge_days)
        self.embargo_gap = pd.Timedelta(days=embargo_days)
        self.logger = get_logger(__name__)
    
    def generate_splits(self) -> Generator[Tuple[pd.DataFrame, pd.DataFrame], None, None]:
        """Generate all CPCV splits.
        
        Yields:
            (train_df, test_df): Train/test DataFrames for each split.
        
        Notes:
            - All indices are date-based (temporal order preserved)
            - Training set is ALWAYS before test set
            - No data leakage between folds
        """
        # Split index into groups
        indices = self._split_into_groups()
        
        # Generate all C(n_groups, test_groups) combinations
        from itertools import combinations
        
        group_ids = list(range(self.n_groups))
        for test_combo in combinations(group_ids, self.test_groups):
            # Extract test indices
            test_indices = []
            for group_id in test_combo:
                test_indices.extend(indices[group_id])
            
            # Separate test set
            test_df = self.df.loc[test_indices]
            
            # Initialize train set (all data except test)
            train_df = self.df.drop(index=test_indices)
            
            # Apply purge & embargo gaps
            train_df = self._apply_purge_embargo(
                train_df, test_df, 
                self.purge_gap, self.embargo_gap
            )
            
            self.logger.debug(
                f"Generated CPCV split: "
                f"test_groups={test_combo}, "
                f"train_rows={len(train_df)}, "
                f"test_rows={len(test_df)}"
            )
            
            yield train_df, test_df
    
    def _split_into_groups(self) -> List[List[pd.Timestamp]]:
        """Split DataFrame index into n_groups temporal groups.
        
        Returns:
            List of index lists, one per group.
        
        Notes:
            - Each group contains roughly equal number of rows
            - Groups are contiguous in time (no shuffling)
        """
        n = len(self.df)
        group_size = n // self.n_groups
        
        indices = np.array_split(self.df.index, self.n_groups)
        
        return [list(idx) for idx in indices]
    
    def _apply_purge_embargo(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        purge_gap: pd.Timedelta,
        embargo_gap: pd.Timedelta
    ) -> pd.DataFrame:
        """Remove dates adjacent to test set from training.
        
        Args:
            train_df: Training set (before purging).
            test_df: Test set (determines removal zones).
            purge_gap: Distance in days to remove (look-ahead prevention).
            embargo_gap: Additional distance (data leakage prevention).
        
        Returns:
            Training set with purged dates removed.
        
        Logic:
            - test_min_date = earliest date in test set
            - test_max_date = latest date in test set
            - Remove train data where:
              * date >= (test_min_date - purge_gap - embargo_gap)
              * AND date <= (test_max_date + purge_gap + embargo_gap)
        
        Rationale:
            - Purge gap: prevents look-ahead (future prices leak into past features)
            - Embargo gap: prevents data snooping (prevents fitting on test-adjacent data)
        """
        test_min = test_df.index.min()
        test_max = test_df.index.max()
        
        # Define removal window
        removal_start = test_min - purge_gap - embargo_gap
        removal_end = test_max + purge_gap + embargo_gap
        
        # Keep only dates outside removal window
        mask = (train_df.index < removal_start) | (train_df.index > removal_end)
        purged_train = train_df.loc[mask]
        
        removed_count = len(train_df) - len(purged_train)
        self.logger.debug(
            f"Purged {removed_count} rows from training set "
            f"({removed_count/len(train_df)*100:.1f}%)"
        )
        
        return purged_train
```

#### 2.2.2 CPCV Statistics

**Function: `validate_cpcv_splits()`**

```python
def validate_cpcv_splits(
    train_test_pairs: List[Tuple[pd.DataFrame, pd.DataFrame]],
    verbose: bool = True
) -> Dict[str, float]:
    """Validate CPCV splits for temporal integrity.
    
    Args:
        train_test_pairs: List of (train_df, test_df) tuples from splits.
        verbose: Print summary statistics.
    
    Returns:
        Dict with validation metrics:
        {
            'avg_overlap_days': float,  # Should be 0
            'min_train_date_before_test': bool,
            'max_train_date_before_test': bool,
            'total_folds': int,
            'avg_train_rows': int,
            'avg_test_rows': int
        }
    
    Checks:
        1. No date overlap between train and test
        2. All training dates are before test dates
        3. Purge/embargo gaps present
    """
    stats = {
        'total_folds': len(train_test_pairs),
        'overlaps': 0,
        'train_after_test': 0,
        'train_sizes': [],
        'test_sizes': [],
        'test_date_diffs': []
    }
    
    for train_df, test_df in train_test_pairs:
        train_dates = train_df.index
        test_dates = test_df.index
        
        # Check for overlap
        overlap = train_dates.intersection(test_dates)
        if len(overlap) > 0:
            stats['overlaps'] += 1
        
        # Check temporal ordering
        if train_dates.max() > test_dates.min():
            stats['train_after_test'] += 1
        
        # Record sizes
        stats['train_sizes'].append(len(train_df))
        stats['test_sizes'].append(len(test_df))
        stats['test_date_diffs'].append((test_dates.max() - test_dates.min()).days)
    
    stats['avg_train_rows'] = np.mean(stats['train_sizes'])
    stats['avg_test_rows'] = np.mean(stats['test_sizes'])
    
    if verbose:
        print(f"CPCV Validation:")
        print(f"  Folds: {stats['total_folds']}")
        print(f"  Overlaps: {stats['overlaps']} (expected 0)")
        print(f"  Train after test: {stats['train_after_test']} (expected 0)")
        print(f"  Avg train rows: {stats['avg_train_rows']:.0f}")
        print(f"  Avg test rows: {stats['avg_test_rows']:.0f}")
    
    return stats
```

---

## 3. Out-of-Core Data Iterator for XGBoost

### 3.1 Module: `tournament/data_iterator.py`

**File: `tournament/data_iterator.py`**

#### 3.1.1 ParquetDataIter Class

**Class: `ParquetDataIter`**

```python
import pyarrow.parquet as pq
import xgboost as xgb
from typing import List

class ParquetDataIter(xgb.DataIter):
    """Zero-copy XGBoost data iterator for Parquet files.
    
    Design:
        - Reads Parquet row-groups sequentially
        - No full file load into memory
        - Direct feed to XGBoost DMatrix
        - Memory footprint = 1 row-group at a time
    
    Attributes:
        file_path: Path to Parquet file.
        features: List of feature column names.
        target_col: Target column name (label).
        pf: ParquetFile object (maintains row-group index).
        num_row_groups: Total row groups in file.
        it: Current row-group iterator index.
    
    Methods:
        __init__: Initialize iterator.
        reset: Rewind to start.
        next: Load next row-group into DMatrix.
    """
    
    def __init__(
        self,
        file_path: str,
        features: List[str],
        target_col: str,
        on_host: bool = True
    ):
        """Initialize ParquetDataIter.
        
        Args:
            file_path: Path to Parquet file.
            features: Feature column names.
            target_col: Target (label) column name.
            on_host: If True, keep data in host memory (CPU).
                     If False, can stream to GPU via XGBoost.
        
        Notes:
            - Requires Parquet file with explicit row-groups
            - PyArrow handles zero-copy column access
        """
        super().__init__(on_host=on_host)
        
        self.file_path = file_path
        self.features = features
        self.target_col = target_col
        
        # Open ParquetFile (doesn't load data)
        self.pf = pq.ParquetFile(file_path)
        self.num_row_groups = self.pf.num_row_groups
        self.it = 0
        
        logger = get_logger(__name__)
        logger.info(
            f"Initialized ParquetDataIter: "
            f"{self.num_row_groups} row-groups, "
            f"{len(features)} features"
        )
    
    def reset(self) -> None:
        """Rewind iterator to start.
        
        Notes:
            - Called by XGBoost for repeated cross-validation
            - No data reload (just reset counter)
        """
        self.it = 0
    
    def next(self, input_data: Callable) -> int:
        """Load next row-group and feed to XGBoost.
        
        Args:
            input_data: Callback function provided by XGBoost.
                       Called as: input_data(data=features_table, label=label_table)
        
        Returns:
            1: More data available (loaded this row-group)
            0: End of iteration (no more row-groups)
        
        Flow:
            1. Check if more row-groups exist
            2. If yes: read row-group from disk
            3. Extract features & label columns (PyArrow → Arrow Table)
            4. Pass to XGBoost via input_data callback
            5. Increment iterator
            6. Return 1
        
        Notes:
            - Zero-copy: PyArrow Table returned directly
            - XGBoost converts to DMatrix internally
            - Row-group stays in RAM only during XGBoost processing
        """
        if self.it == self.num_row_groups:
            return 0  # No more data
        
        # Read row-group from disk
        chunk_table = self.pf.read_row_group(
            self.it,
            columns=self.features + [self.target_col]
        )
        
        # Extract features and label
        features_table = chunk_table.select(self.features)
        label_table = chunk_table.select([self.target_col])
        
        # Feed to XGBoost
        input_data(data=features_table, label=label_table)
        
        self.it += 1
        return 1  # More data available
```

#### 3.1.2 Usage Pattern

```python
# Training setup
train_path = "data/train_fold_1.parquet"
features = ['atr', 'adv_20', 'volatility', 'sentiment_score', ...]
target = 'target_label'

# Create iterator (doesn't load data)
train_iter = ParquetDataIter(train_path, features, target)

# Feed to XGBoost (loads row-groups on-demand)
dtrain = xgb.ExtMemQuantileDMatrix(
    train_iter,
    cache_host_ratio=0.75  # 75% histogram cache in RAM
)

# Train (XGBoost calls iter.next() internally)
booster = xgb.train(params, dtrain, num_boost_round=100)
```

### 3.2 DMatrix Variants for Memory Management

**Class: `DMatrixSelector`**

```python
def create_dmatrix(
    data_source,  # ParquetDataIter or DataFrame
    label_source=None,
    cache_host_ratio: float = 0.75,
    use_sparse: bool = False,
    use_quantile: bool = True
) -> xgb.DMatrix:
    """Select appropriate DMatrix variant based on memory constraints.
    
    Args:
        data_source: ParquetDataIter or DataFrame.
        cache_host_ratio: Fraction of histogram cache in RAM (vs GPU).
        use_sparse: If True, use sparse matrix format (saves RAM).
        use_quantile: If True, use QuantileDMatrix (histogram-based).
    
    Returns:
        Appropriate DMatrix variant:
        - ExtMemQuantileDMatrix: Out-of-core + quantile + VRAM adaptive
        - QuantileDMatrix: In-memory + quantile (fast)
        - DMatrix: Standard (requires all data in RAM)
    
    Logic:
        1. If ParquetDataIter: use ExtMemQuantileDMatrix
        2. Else if in-memory size > 5GB: use QuantileDMatrix
        3. Else: use standard DMatrix
    """
    if isinstance(data_source, ParquetDataIter):
        return xgb.ExtMemQuantileDMatrix(
            data_source,
            cache_host_ratio=cache_host_ratio
        )
    elif isinstance(data_source, pd.DataFrame):
        data_size_gb = data_source.memory_usage(deep=True).sum() / 1e9
        if data_size_gb > 5.0:
            return xgb.QuantileDMatrix(data_source, label=label_source)
        else:
            return xgb.DMatrix(data_source, label=label_source)
    else:
        raise ValueError(f"Unsupported data source: {type(data_source)}")
```

---

## 4. XGBoost Training with Asymmetric Loss

### 4.1 Module: `tournament/training.py`

**File: `tournament/training.py`**

#### 4.1.1 Asymmetric Financial Loss Objective

**Function: `asymmetric_financial_loss()`**

```python
def asymmetric_financial_loss(
    preds: np.ndarray,
    dtrain: xgb.DMatrix,
    penalty_fp: float = 5.0,
    penalty_fn: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """Custom objective: Penalize false positives 5x more than false negatives.
    
    Args:
        preds: Raw logit predictions from XGBoost.
        dtrain: DMatrix containing labels.
        penalty_fp: Multiplier for false positive gradient/hessian.
        penalty_fn: Multiplier for false negative gradient/hessian.
    
    Returns:
        (grad, hess): Gradients and Hessians for XGBoost to use in updates.
    
    Formula (Binary Cross-Entropy with Asymmetric Weights):
        - Convert logits to probabilities: p = 1 / (1 + exp(-preds))
        - Base BCE gradient: grad = p - y (where y ∈ {0, 1})
        - Base BCE hessian: hess = p * (1 - p)
        - **Asymmetric scaling**:
          * If y == 0 (negative, False Positive): grad *= penalty_fp, hess *= penalty_fp
          * If y == 1 (positive, False Negative): grad *= penalty_fn, hess *= penalty_fn
    
    Rationale:
        - False Positive (model predicts BUY, stock falls): Direct capital loss
        - False Negative (model predicts SKIP, stock rises): Opportunity cost
        - In trading, capital preservation > opportunity hunting
        - Penalty_fp = 5× prevents overconfident BUY signals
    
    Notes:
        - XGBoost uses grad & hess to guide tree splits
        - Higher penalty → more cautious on that class
        - Custom objectives allow domain-specific loss functions
    
    Example Scenario:
        Label = 0 (negative day), Prediction = 0.8 (model thinks it's positive)
        - Base grad = 0.8 - 0 = 0.8
        - Asymmetric grad = 0.8 × 5.0 = 4.0
        - Tree will penalize this prediction more heavily
        - Next tree will try harder to get negatives right
    """
    labels = dtrain.get_label()
    
    # Convert logits to probabilities
    preds_prob = 1.0 / (1.0 + np.exp(-preds))
    
    # Base gradient and hessian (BCE)
    grad = preds_prob - labels
    hess = preds_prob * (1.0 - preds_prob)
    
    # Apply asymmetric penalties
    # labels == 0 → False Positive penalty
    # labels == 1 → False Negative penalty
    grad = np.where(labels == 0, grad * penalty_fp, grad * penalty_fn)
    hess = np.where(labels == 0, hess * penalty_fp, hess * penalty_fn)
    
    return grad, hess
```

#### 4.1.2 XGBoost Training Pipeline

**Class: `XGBoostTrainer`**

```python
class XGBoostTrainer:
    """Orchestrates XGBoost model training with Asymmetric Loss.
    
    Methods:
        train_single_fold: Train one XGBoost model on a fold.
        train_grid_search: Hyperparameter grid search with CPCV.
        save_model: Serialize trained model + feature metadata.
    """
    
    def __init__(self, config: AppConfig):
        """Initialize trainer.
        
        Args:
            config: AppConfig with XGBoost parameters.
        """
        self.config = config
        self.logger = get_logger(__name__)
    
    def train_single_fold(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        features: List[str],
        target: str,
        params: Dict[str, Any],
        num_boost_round: int = 100
    ) -> Tuple[xgb.Booster, np.ndarray]:
        """Train single XGBoost model on one fold.
        
        Args:
            train_df: Training DataFrame (from CPCV).
            test_df: Test DataFrame (from CPCV).
            features: List of feature column names.
            target: Target column name.
            params: XGBoost hyperparameters:
                {
                    'max_depth': 3,
                    'learning_rate': 0.05,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'tree_method': 'gpu_hist',
                    'device': 'cuda',
                    'objective': 'binary:logistic'  # (or custom)
                }
            num_boost_round: Number of boosting rounds.
        
        Returns:
            (booster: Trained model, test_predictions: Probability predictions on test)
        
        Flow:
            1. Write train_df to temp Parquet (row-grouped)
            2. Create ParquetDataIter for zero-copy
            3. Create ExtMemQuantileDMatrix
            4. Train with custom objective (asymmetric_financial_loss)
            5. Infer on test set
            6. Return booster + predictions
        
        Notes:
            - Training data written with row-groups for iterator
            - Memory efficient: loaded row-group by row-group
            - GPU acceleration via tree_method='gpu_hist'
        """
        import tempfile
        
        self.logger.info(f"Training XGBoost: {len(train_df)} train rows, {len(test_df)} test rows")
        
        # Write training data to temporary Parquet
        temp_train_path = f"/tmp/xgb_train_{id(train_df)}.parquet"
        try:
            train_df.to_parquet(
                temp_train_path,
                engine='pyarrow',
                row_group_size=self.config.data.row_group_size
            )
            
            # Create data iterator
            train_iter = ParquetDataIter(temp_train_path, features, target)
            
            # Create DMatrix
            dtrain = xgb.ExtMemQuantileDMatrix(
                train_iter,
                cache_host_ratio=0.75
            )
            
            # Update params for asymmetric loss
            params['objective'] = asymmetric_financial_loss
            params['disable_default_eval_metric'] = 1
            
            # Train
            evals = [(dtrain, 'train')]
            booster = xgb.train(
                params,
                dtrain,
                num_boost_round=num_boost_round,
                evals=evals,
                verbose_eval=False
            )
            
            # Predict on test set
            dtest = xgb.DMatrix(test_df[features], label=test_df[target])
            test_preds = booster.predict(dtest)
            
            self.logger.info(f"Training complete: {num_boost_round} rounds")
            
            return booster, test_preds
            
        finally:
            # Cleanup
            if os.path.exists(temp_train_path):
                os.remove(temp_train_path)
    
    def save_model(
        self,
        booster: xgb.Booster,
        model_path: str,
        features: List[str],
        features_path: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Save model and metadata to disk.
        
        Args:
            booster: Trained XGBoost model.
            model_path: Where to save model JSON.
            features: Feature column names.
            features_path: Where to save feature list.
            metadata: Additional metadata (sector, params, etc.).
        
        Outputs:
            - model.json: XGBoost model (can load with booster.load_model)
            - features.json: Feature list + metadata
        
        Notes:
            - JSON format allows inspection
            - Features list essential for inference (must match training)
        """
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        os.makedirs(os.path.dirname(features_path), exist_ok=True)
        
        # Save model
        booster.save_model(model_path)
        
        # Save features + metadata
        feature_manifest = {
            'features': features,
            'n_features': len(features),
            'metadata': metadata or {}
        }
        
        with open(features_path, 'w') as f:
            json.dump(feature_manifest, f, indent=2)
        
        self.logger.info(f"Saved model: {model_path}, features: {features_path}")
```

---

## 5. Risk Simulation & Backtest Returns

### 5.1 Module: `tournament/risk_simulator.py`

**File: `tournament/risk_simulator.py`**

#### 5.1.1 Risk Manager Simulation

**Function: `simulate_backtest_returns()`**

```python
from features.shields import evaluate_risk_veto_gates

def simulate_backtest_returns(
    test_df: pd.DataFrame,
    predictions: np.ndarray,
    confidence_threshold: float = 0.65,
    config: AppConfig = None
) -> np.ndarray:
    """Simulate backtest returns using Shield Agent risk gates.
    
    Args:
        test_df: Test set DataFrame (with OHLCV + features).
        predictions: Model predictions (probabilities).
        confidence_threshold: Threshold for generating signal (e.g., 0.65).
        config: AppConfig with risk parameters.
    
    Returns:
        Array of simulated returns per row.
    
    Flow (per row):
        1. If prediction > threshold: signal = 1 (BUY)
        2. Else: signal = 0 (SKIP)
        3. If signal == 1:
           a. Query Shield Agent with current row's risk metrics
           b. If approved: calculate position P&L
           c. If veto'd: return = 0 (no trade)
        4. If signal == 0: return = 0 (no trade)
    
    Formula (if signal & approved):
        - entry = close[t]
        - stop = entry - (atr_multiplier × atr[t])
        - risk_distance = entry - stop
        - size = (capital × max_risk) / risk_distance
        - If low[t+1] <= stop:
          * return = -risk_distance × size (hit stop)
        - Else:
          * return = (close[t+1] - entry) / entry × size (daily P&L)
    
    Notes:
        - Returns are forward-shifted (entry at t, exit at t+1)
        - No look-ahead bias (uses only t's data for signal)
        - Shield Agent prevents over-sizing
    """
    n = len(test_df)
    returns = np.zeros(n)
    veto_counts = {'stop_loss': 0, 'size': 0, 'liquidity': 0, 'slippage': 0}
    
    logger = get_logger(__name__)
    
    for i in range(n - 1):  # Can't trade last bar (no exit)
        pred = predictions[i]
        signal = 1 if pred > confidence_threshold else 0
        
        if signal == 0:
            returns[i] = 0.0
            continue
        
        # Extract current row features
        close = test_df['close'].iloc[i]
        atr = test_df['atr'].iloc[i]
        adv_20 = test_df['adv_20'].iloc[i]
        volume_today = test_df['volume'].iloc[i]
        volatility = test_df['volatility'].iloc[i]
        
        # Query Shield Agent
        approved, position_size = evaluate_risk_veto_gates(
            entry_price=close,
            atr=atr,
            atr_multiplier=config.execution.atr_stop_multiplier,
            account_capital=100000.0,  # Fixed capital for backtest
            max_risk_pct=config.execution.max_risk_per_trade,
            current_qty=0.0,  # Assume flat
            adv_20=adv_20,
            volume_today=volume_today,
            volatility=volatility
        )
        
        if not approved:
            returns[i] = 0.0
            veto_counts['size'] += 1
            continue
        
        # Calculate P&L
        entry = close
        stop_loss = entry - (config.execution.atr_stop_multiplier * atr)
        risk_per_share = entry - stop_loss
        
        # Next bar's prices
        low_next = test_df['low'].iloc[i + 1]
        close_next = test_df['close'].iloc[i + 1]
        
        # Check if hit stop
        if low_next <= stop_loss:
            # Hit stop loss
            returns[i] = -risk_per_share / entry * position_size
        else:
            # Normal exit at close
            pnl_per_share = (close_next - entry) / entry
            returns[i] = pnl_per_share * position_size
    
    logger.info(f"Backtest simulation complete: {np.sum(np.abs(returns) > 0):.0f} trades")
    
    return returns
```

#### 5.1.2 Fold Statistics

**Function: `calculate_fold_statistics()`**

```python
def calculate_fold_statistics(returns: np.ndarray) -> Dict[str, float]:
    """Calculate performance metrics for a single fold.
    
    Args:
        returns: Array of returns from backtest.
    
    Returns:
        Dict with metrics:
        {
            'total_return': float,
            'annual_return': float,
            'sharpe_ratio': float,
            'max_drawdown': float,
            'win_rate': float,
            'n_trades': int
        }
    """
    n_trades = np.sum(np.abs(returns) > 1e-6)
    cumulative = np.cumprod(1 + returns)
    
    if n_trades == 0:
        return {
            'total_return': 0.0,
            'annual_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'n_trades': 0
        }
    
    # Sharpe Ratio (assuming 252 trading days)
    mean_ret = np.mean(returns[returns != 0])
    std_ret = np.std(returns[returns != 0])
    sharpe = (mean_ret / std_ret) * np.sqrt(252) if std_ret > 0 else 0.0
    
    # Max Drawdown
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    max_dd = np.min(drawdown)
    
    # Win Rate
    winning_trades = np.sum(returns[returns != 0] > 0)
    win_rate = winning_trades / n_trades if n_trades > 0 else 0.0
    
    return {
        'total_return': cumulative[-1] - 1,
        'annual_return': cumulative[-1] ** (252 / len(returns)) - 1,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd,
        'win_rate': win_rate,
        'n_trades': int(n_trades)
    }
```

---

## 6. Hyperparameter Grid Search

### 6.1 Module: `tournament/grid_search.py`

**File: `tournament/grid_search.py`**

#### 6.1.1 Grid Search Over Sectors

**Class: `HyperparameterGridSearch`**

```python
class HyperparameterGridSearch:
    """Execute grid search over hyperparameters + CPCV folds.
    
    Methods:
        generate_parameter_grid: Create all param combinations.
        execute_grid_search: Run training for each combo.
        select_best_params: Choose params with highest OOS Sharpe.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
    
    def generate_parameter_grid(self) -> List[Dict[str, Any]]:
        """Generate all hyperparameter combinations.
        
        Returns:
            List of param dictionaries.
        
        Grid:
            - max_depth: [1, 2, 3]
            - learning_rate: [0.01, 0.05, 0.1]
            - subsample: [0.8]
            - colsample_bytree: [0.8]
            - Total combinations: 3 × 3 = 9
        
        Each combo includes:
            - tree_method: 'gpu_hist' (GPU acceleration)
            - device: 'cuda'
            - num_leaves: 2^max_depth
        """
        from itertools import product
        
        depth_range = [1, 2, 3]
        lr_range = [0.01, 0.05, 0.1]
        
        combos = []
        for depth, lr in product(depth_range, lr_range):
            combos.append({
                'max_depth': depth,
                'learning_rate': lr,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'tree_method': 'gpu_hist',
                'device': 'cuda'
            })
        
        self.logger.info(f"Generated {len(combos)} parameter combinations")
        return combos
    
    def execute_grid_search(
        self,
        cpcv_splits: Generator,
        features: List[str],
        target: str,
        num_boost_round: int = 100
    ) -> pd.DataFrame:
        """Execute grid search across all param combos + CPCV folds.
        
        Args:
            cpcv_splits: Generator yielding (train_df, test_df) tuples.
            features: Feature column names.
            target: Target column name.
            num_boost_round: Boosting rounds per model.
        
        Returns:
            DataFrame with results:
            {
                'param_combo': int (which combo)
                'fold': int (which CPCV fold)
                'sharpe': float (OOS Sharpe on this fold)
                'max_drawdown': float
                'n_trades': int
                'avg_win_rate': float
            }
        
        Notes:
            - For each param combo: train on all folds
            - Accumulates returns across folds
            - Final Sharpe computed from all OOS returns
        """
        param_grid = self.generate_parameter_grid()
        
        all_results = []
        
        for param_idx, params in enumerate(param_grid):
            self.logger.info(f"Training combo {param_idx + 1}/{len(param_grid)}: {params}")
            
            trainer = XGBoostTrainer(self.config)
            fold_returns = []
            
            for fold_idx, (train_df, test_df) in enumerate(cpcv_splits):
                self.logger.debug(f"  Fold {fold_idx + 1}")
                
                booster, test_preds = trainer.train_single_fold(
                    train_df, test_df, features, target, params, num_boost_round
                )
                
                # Simulate returns on test fold
                fold_rets = simulate_backtest_returns(
                    test_df, test_preds, 
                    confidence_threshold=self.config.execution.confidence_threshold,
                    config=self.config
                )
                
                fold_returns.extend(fold_rets[fold_rets != 0])
            
            # Compute statistics
            if fold_returns:
                combo_stats = calculate_fold_statistics(np.array(fold_returns))
                combo_stats['param_combo'] = param_idx
                combo_stats['param_dict'] = str(params)
                all_results.append(combo_stats)
        
        results_df = pd.DataFrame(all_results)
        
        # Sort by Sharpe
        results_df = results_df.sort_values('sharpe_ratio', ascending=False)
        
        self.logger.info(f"Grid search complete. Best Sharpe: {results_df.iloc[0]['sharpe_ratio']:.3f}")
        
        return results_df
```

---

## 7. Tournament Director

### 7.1 Module: `tournament/director.py`

**File: `tournament/director.py`**

#### 7.1.1 Modular Tournament Director

**Class: `ModularTournamentDirector`**

```python
class ModularTournamentDirector:
    """Orchestrates full tournament for a sector.
    
    Methods:
        execute_gauntlet: Full tournament pipeline for sector.
        run_sector_tournament: Single sector tournament.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
    
    def run_sector_tournament(self, sector: str) -> Dict[str, Any]:
        """Run full tournament for one sector.
        
        Args:
            sector: Sector name (e.g., "Technology").
        
        Returns:
            {
                'sector': str,
                'best_params': Dict,
                'best_sharpe': float,
                'candidate_model_path': str,
                'features_path': str,
                'all_results': pd.DataFrame
            }
        
        Flow:
            1. Load processed vault for sector
            2. Generate CPCV splits
            3. Execute hyperparameter grid search
            4. Select best params (highest OOS Sharpe)
            5. Train final model on full data (using best params)
            6. Save to candidate registry
            7. Return metadata
        """
        self.logger.info(f"Starting tournament for {sector}")
        
        # Load data
        vault_path = f"{self.config.data.processed_vault_dir}/sector={sector}"
        df = pd.read_parquet(f"{vault_path}/*.parquet")
        df = df.sort_index()  # Ensure temporal order
        
        self.logger.info(f"Loaded {len(df)} rows for {sector}")
        
        # CPCV split generation
        cpcv_gen = CPCVSplitGenerator(
            df,
            n_groups=6,
            test_groups=2,
            purge_days=5,
            embargo_days=5,
            config=self.config
        )
        
        # Grid search
        grid_search = HyperparameterGridSearch(self.config)
        
        # Collect splits for grid search (convert generator to list)
        splits_list = list(cpcv_gen.generate_splits())
        
        results_df = grid_search.execute_grid_search(
            cpcv_splits=iter(splits_list),
            features=[c for c in df.columns if c not in self.config.data.metadata_cols],
            target='target_label',
            num_boost_round=100
        )
        
        # Select best params
        best_row = results_df.iloc[0]
        best_params = ast.literal_eval(best_row['param_dict'])
        
        self.logger.info(f"Best params for {sector}: {best_params}")
        self.logger.info(f"Best OOS Sharpe: {best_row['sharpe_ratio']:.3f}")
        
        # Train final model on all data
        trainer = XGBoostTrainer(self.config)
        booster, _ = trainer.train_single_fold(
            train_df=df,
            test_df=df.iloc[-100:],  # Dummy test (not used for eval)
            features=[c for c in df.columns if c not in self.config.data.metadata_cols],
            target='target_label',
            params=best_params,
            num_boost_round=100
        )
        
        # Save candidate model
        candidate_model_path = f"{self.config.models.candidate_models_dir}/{sector}_candidate.json"
        candidate_features_path = f"{self.config.models.candidate_models_dir}/{sector}_candidate_features.json"
        
        trainer.save_model(
            booster,
            candidate_model_path,
            features=[c for c in df.columns if c not in self.config.data.metadata_cols],
            features_path=candidate_features_path,
            metadata={'sector': sector, 'params': best_params}
        )
        
        return {
            'sector': sector,
            'best_params': best_params,
            'best_sharpe': float(best_row['sharpe_ratio']),
            'candidate_model_path': candidate_model_path,
            'features_path': candidate_features_path,
            'all_results': results_df
        }
    
    def execute_gauntlet(self) -> Dict[str, Dict]:
        """Execute tournament for all sectors.
        
        Returns:
            Dict mapping sector → tournament results.
        """
        sectors = ['Technology', 'Healthcare', 'Financials', ...]  # From universe
        
        results = {}
        for sector in sectors:
            try:
                sector_result = self.run_sector_tournament(sector)
                results[sector] = sector_result
            except Exception as e:
                self.logger.error(f"Tournament failed for {sector}: {e}", exc_info=True)
        
        self.logger.info(f"Tournament complete: {len(results)} sectors processed")
        
        return results
```

---

## 8. Implementation Checklist - Phase 3

### Week 1: CPCV & Data Iterator

- [ ] **Day 1-2**: CPCV implementation
  - [ ] Implement `CPCVSplitGenerator` class
  - [ ] Implement purge/embargo gap logic
  - [ ] Unit tests: `test_cpcv.py`
  - [ ] Validate splits (no overlap, proper temporal ordering)

- [ ] **Day 2-3**: ParquetDataIter
  - [ ] Implement `ParquetDataIter` class
  - [ ] Test zero-copy with mock Parquet files
  - [ ] Integration test: Iterator → XGBoost DMatrix
  - [ ] Unit tests: `test_data_iterator.py`

- [ ] **Day 3-4**: Risk simulator
  - [ ] Implement `simulate_backtest_returns()`
  - [ ] Implement fold statistics calculation
  - [ ] Unit tests: `test_risk_simulator.py`

- [ ] **Day 4-5**: XGBoost training
  - [ ] Implement `asymmetric_financial_loss()` objective
  - [ ] Implement `XGBoostTrainer` class
  - [ ] Test custom objective with mock data
  - [ ] Unit tests: `test_training.py`

### Week 2: Grid Search & Tournament Director

- [ ] **Day 6-7**: Grid search
  - [ ] Implement `HyperparameterGridSearch` class
  - [ ] Implement parameter grid generation
  - [ ] Unit tests: `test_grid_search.py`

- [ ] **Day 7-8**: Tournament director
  - [ ] Implement `ModularTournamentDirector` class
  - [ ] Implement sector-level tournament
  - [ ] Unit tests: `test_director.py`

- [ ] **Day 8-9**: Integration & benchmarking
  - [ ] End-to-end integration test (CPCV → training → results)
  - [ ] Performance benchmarking: training speed, memory usage
  - [ ] Verify no look-ahead bias in CPCV splits

- [ ] **Day 9-10**: Validation & optimization
  - [ ] Verify asymmetric loss penalizes FP correctly
  - [ ] Profile training bottlenecks
  - [ ] Optimize if needed (GPU utilization, memory)
  - [ ] Run all tests, verify 85%+ coverage

---

## 9. Success Criteria & Acceptance Tests

### 9.1 Functional Acceptance

| Criterion | Test | Expected |
|-----------|------|----------|
| CPCV no overlap | `test_validate_cpcv_splits()` | ✓ 0 overlaps |
| CPCV temporal order | `test_temporal_ordering()` | ✓ All train before test |
| ParquetDataIter loads | `test_parquet_iterator()` | ✓ Row-groups loaded sequentially |
| XGBoost trains | `test_xgboost_training()` | ✓ Model saves, predicts |
| Asymmetric loss works | `test_asymmetric_objective()` | ✓ FP penalized 5× |
| Backtest sim valid | `test_backtest_returns()` | ✓ No look-ahead, forward-shifted |
| Grid search completes | `test_grid_search_execution()` | ✓ All combos trained |
| Tournament director end-to-end | `test_full_tournament()` | ✓ Sector → candidate model |

### 9.2 Performance Targets

| Component | Metric | Target | Test |
|-----------|--------|--------|------|
| CPCV generation | Speed | 1000 splits/sec | `bench_cpcv_splits.py` |
| ParquetDataIter | Throughput | 100k rows/sec | `bench_data_iterator.py` |
| XGBoost training | Time per fold | < 60 sec | `bench_xgboost_training.py` |
| Risk simulation | Speed | 100k returns/sec | `bench_risk_simulation.py` |
| Full tournament | End-to-end | < 1 hour (sector) | Integration benchmark |

### 9.3 Code Quality

| Criterion | Target |
|-----------|--------|
| Test coverage (tournament/) | ≥ 85% |
| Type hints | 100% (mypy clean) |
| Linting errors | 0 |
| CPCV correctness | 0 overlaps, proper ordering |

---

## 10. Integration Points with Phases 1-2 & Handoff to Phase 4

### 10.1 Phase 1 Dependencies

- Config system: All hyperparams from `AppConfig`
- Logging: All operations logged
- Exception hierarchy: Use custom exceptions
- Testing: Pytest fixtures (config, data)

### 10.2 Phase 2 Dependencies

- Feature outputs: Read from Parquet (Phase 2 output)
- Shield Agent: Integrated into risk simulator
- Slippage model: Available for realistic position sizing

### 10.3 Handoff to Phase 4 (Evaluation)

- Candidate model registry → Phase 4 loads for DSR evaluation
- Feature manifests → Phase 4 needs for inference
- Returns matrices → Phase 4 uses for statistical tests

---

## 11. Deliverables Summary - Phase 3

### Codebase
- [ ] `/new_pipeline/tournament/cpcv.py` (300+ lines)
- [ ] `/new_pipeline/tournament/data_iterator.py` (200+ lines)
- [ ] `/new_pipeline/tournament/training.py` (400+ lines)
- [ ] `/new_pipeline/tournament/risk_simulator.py` (300+ lines)
- [ ] `/new_pipeline/tournament/grid_search.py` (300+ lines)
- [ ] `/new_pipeline/tournament/director.py` (400+ lines)
- [ ] `/new_pipeline/models/registry.py` (model storage)
- [ ] 100+ unit tests + benchmarks

### Performance
- [ ] CPCV prevents all look-ahead bias
- [ ] ParquetDataIter enables 10GB+ training
- [ ] XGBoost trains with asymmetric loss
- [ ] Tournament runs sector in < 1 hour
- [ ] Candidate models ready for evaluation

### Documentation
- [ ] CPCV methodology & validation
- [ ] ParquetDataIter usage guide
- [ ] Asymmetric loss rationale
- [ ] Grid search tuning guide

---

## 12. Quick Reference Commands

```bash
# Generate CPCV splits (validate)
python -c "
from tournament.cpcv import CPCVSplitGenerator, validate_cpcv_splits
import pandas as pd
df = pd.read_parquet('data/processed/sector=Technology')
gen = CPCVSplitGenerator(df)
splits = list(gen.generate_splits())
validate_cpcv_splits(splits, verbose=True)
"

# Test ParquetDataIter
pytest tests/unit/tournament/test_data_iterator.py -v

# Run grid search for sector
python -c "
from tournament.director import ModularTournamentDirector
from config import get_config
config = get_config()
director = ModularTournamentDirector(config)
results = director.run_sector_tournament('Technology')
print(f'Best Sharpe: {results[\"best_sharpe\"]:.3f}')
"

# Benchmark training
pytest tests/benchmarks/bench_xgboost_training.py -v --benchmark-only

# Run all Phase 3 tests
pytest tests/unit/tournament/ tests/integration/tournament/ --cov=tournament --cov-report=html
```

---

**Next**: After Phase 3 completion, proceed to [Phase 4: Statistical Evaluation & Model Promotion](PHASE_4_SPECIFICATION.md) (to be created).

**Previous Phases**:
- [Phase 1: Core Pipeline Infrastructure](PHASE_1_SPECIFICATION.md)
- [Phase 2: Vectorized Quant Engine & Shields](PHASE_2_SPECIFICATION.md)

```

---

### File: `docs/quantitative_math.md`

```markdown
# Quantum Sentinel: Quantitative & Mathematical Frameworks

## 1. Dynamic Hydrodynamic Slippage
Do not use fixed-basis-point slippage assumptions in backtesting. Slippage ($S$) expands during illiquid or high-volatility environments and must be modeled as a function of order size ($Q$), rolling market volume ($V$), and rolling volatility ($\sigma$).

The algorithm calculates slippage (in basis points) using the standard hydrodynamic market impact model:
$$ S \approx c \cdot \sigma \cdot \sqrt{\frac{Q}{V}} $$
- $c$: A constant calibration factor.
- **Implementation Constraint:** Enforce a safety override. If the estimated $S > 50.0$ bps, the `Numba` Risk Manager must veto the trade.

## 2. Deflated Sharpe Ratio (DSR)
Generic metrics (Accuracy, standard Sharpe Ratio) are inadequate. The system evaluates strategy tournaments strictly using the Deflated Sharpe Ratio to correct for non-Normal return distributions and Multiple Testing Selection Bias (False Discovery Rate).

The DSR evaluates the standard Sharpe Ratio ($\widehat{SR}$) against a benchmark threshold ($SR_0$) derived from:
- **Skewness ($\gamma_3$)** and **Kurtosis ($\gamma_4$)**: Adjusting for asymmetric tail risks.
- **Minimum Backtest Length (MinBTL):** Ensuring the sample size is statistically significant given the number of strategy variations tested.

Threshold for model promotion to the live trading sandbox: $DSR > 0.95$.

## 3. Asymmetric Financial Loss Function
Standard ML objective functions (like Log-Loss or MSE) treat all errors equally. In trading, a False Positive (FP) initiates a trade that loses capital, whereas a False Negative (FN) is merely a missed opportunity. 

When configuring XGBoost or LightGBM algorithms, implement a custom gradient/hessian objective function that penalizes False Positives significantly higher than False Negatives:
$$ Penalty(FP) = 5 \times Penalty(FN) $$
This mathematically forces the model to prioritize capital preservation and drawdown control over maximum hit rate.

## 4. Volatility Regime Tagging
To determine dynamic lookback windows for cross-asset correlation, the system continuously tracks market regimes. 
- A 15-minute rolling volatility is computed. 
- This value is compared against the 80th percentile of its historical rolling distribution.
- If the current metric exceeds the 80th percentile, the regime state flips to `high_vol`, dynamically shortening calculation lookback windows to prioritize recent, highly volatile price action over stale historical data.
```

---

### File: `docs/system_architecture.md`

```markdown
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

```

---

### File: `data/metadata/feature_registry.yaml`

```yaml
atr_14:
  description: 14-day average true range for volatility scaling.
  dtype: float
  name: atr_14
  source: price
  window: 14d
average_volume_20:
  description: 20-day moving average volume.
  dtype: float
  name: average_volume_20
  source: volume
  window: 20d
persist_feature:
  description: Persisted test feature.
  dtype: float
  name: persist_feature
  source: test
  window: 1d
returns:
  description: Daily price return computed from close prices.
  dtype: float
  name: returns
  source: price
  window: 1d
volatility_20:
  description: 20-day rolling standard deviation of returns.
  dtype: float
  name: volatility_20
  source: price
  window: 20d

```

---

### File: `.claude/settings.json`

```json
{
  "sandbox": {
    "network": {
      "allowedDomains": [
        "paper-api.alpaca.markets",
        "data.alpaca.markets"
      ]
    }
  },
  "permissions": {
    "deny": [
      "Edit(./reference_code/**)",
      "Write(./reference_code/**)"
    ]
  },
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "$CLAUDE_PROJECT_DIR/.claude/hooks/session-start.sh"
          }
        ]
      }
    ]
  }
}

```

---

