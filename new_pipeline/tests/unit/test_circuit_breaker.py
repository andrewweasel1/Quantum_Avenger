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
