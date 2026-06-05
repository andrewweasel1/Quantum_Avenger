"""Asyncio-batched LLM sentiment (restores the legacy Semaphore(20) pattern).

Scores many texts concurrently through a (sync) ``LLMClient``, bounding in-flight
calls with an ``asyncio.Semaphore``. Sync client calls run in the default
executor so a slow/network-bound LLM never blocks the event loop. Order is
preserved; offline + deterministic with ``FakeLLMClient``.
"""

import asyncio

from new_pipeline.adapters.base import LLMClient, SentimentResult


async def _score_one(client, text, semaphore, loop):
    async with semaphore:
        return await loop.run_in_executor(None, client.sentiment, text)


async def batch_sentiment_async(
    client: LLMClient, texts, concurrency: int = 20
) -> list[SentimentResult]:
    semaphore = asyncio.Semaphore(concurrency)
    loop = asyncio.get_running_loop()
    return list(
        await asyncio.gather(*[_score_one(client, text, semaphore, loop) for text in texts])
    )


def batch_sentiment(client: LLMClient, texts, concurrency: int = 20) -> list[SentimentResult]:
    """Sync entry point: score texts concurrently, preserving input order."""
    return asyncio.run(batch_sentiment_async(client, list(texts), concurrency))
