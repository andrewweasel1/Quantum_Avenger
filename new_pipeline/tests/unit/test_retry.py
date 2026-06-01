from new_pipeline.utils.retry import RetryPolicy


def test_retry_policy_defaults():
    policy = RetryPolicy()
    assert policy.max_retries == 3
    assert policy.backoff_seconds == 0.5
