from new_pipeline.adapters import FakeLLMClient
from new_pipeline.execution.async_sentiment import batch_sentiment


def test_batch_preserves_order_and_matches_sync():
    client = FakeLLMClient()
    texts = ["Apple beats earnings", "Oil slumps", "Neutral note", "Rally continues"]
    results = batch_sentiment(client, texts, concurrency=2)
    assert len(results) == len(texts)
    assert results == [client.sentiment(text) for text in texts]


def test_empty_batch():
    assert batch_sentiment(FakeLLMClient(), []) == []
