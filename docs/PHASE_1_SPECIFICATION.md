# Phase 1: Core Pipeline Infrastructure - Detailed Specification

> **Implementation status: ✅ DONE.** Config (Pydantic schema + `defaults.yaml` + real dev/test/prod overlays under `QA_` env overrides), JSON logging + `trace_id`, the 20+‑leaf exception hierarchy, the CLOSED/OPEN/HALF_OPEN circuit breaker, and deterministic `seed_everything` are all implemented and tested in `new_pipeline/{config,core}/`. *This is the original build spec, kept for reference; current state lives in `ARCHITECTURE_ROADMAP.md` + `IMPLEMENTATION_STATUS.md`.*

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
