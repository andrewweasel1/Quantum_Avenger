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
