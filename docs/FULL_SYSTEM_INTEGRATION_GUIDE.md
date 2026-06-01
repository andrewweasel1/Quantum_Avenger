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
