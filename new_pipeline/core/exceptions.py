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
