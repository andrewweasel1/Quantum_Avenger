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
