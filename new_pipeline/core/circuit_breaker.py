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
