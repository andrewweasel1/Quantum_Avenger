from dataclasses import dataclass


@dataclass
class RetryPolicy:
    max_retries: int = 3
    backoff_seconds: float = 0.5
