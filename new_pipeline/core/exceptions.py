class QuantumAvengerError(Exception):
    """Base exception for Quantum Avenger."""


class ConfigurationError(QuantumAvengerError):
    """Raised when configuration validation fails."""


class DataValidationError(QuantumAvengerError):
    """Raised when data quality checks fail."""


class IngestionError(QuantumAvengerError):
    """Raised when data ingestion fails."""


class ExecutionError(QuantumAvengerError):
    """Raised for execution or risk evaluation failures."""
