"""Training-database builder: historical stock (+ optional news) -> feature vault.

Reuses the offline training-frame assembly (bars -> production features ->
friction-aware labels -> sector join) but is source-agnostic: hand it the live
``AlpacaMarketDataSource`` to materialize a real training database, or the fake
for an offline dry run. Optionally enriches each ``(ticker, date)`` row with a
news ``sentiment_score`` via a ``NewsSource`` + ``LLMClient``.
"""

from datetime import date
from pathlib import Path

import polars as pl

from new_pipeline.adapters import StaticUniverseProvider
from new_pipeline.config import get_config
from new_pipeline.tournament.pipeline import build_training_frame


def add_news_sentiment(frame: pl.DataFrame, news_source, llm) -> pl.DataFrame:
    """Add a per-(ticker, date) ``sentiment_score`` in [-1, 1] from news headlines."""
    scores = []
    for ticker, day in zip(frame["ticker"].to_list(), frame["date"].to_list(), strict=True):
        items = news_source.headlines(ticker, day)
        if items:
            values = [llm.sentiment(item.headline).score for item in items]
            scores.append(sum(values) / len(values))
        else:
            scores.append(0.0)
    return frame.with_columns(pl.Series("sentiment_score", scores))


def build_training_database(
    output_path,
    source,
    universe=None,
    start: date = date(2023, 1, 1),
    end: date = date(2023, 12, 31),
    cfg=None,
    news_source=None,
    llm=None,
    sentiment_engine=None,
    anonymizer=None,
) -> dict:
    """Materialize a labeled feature parquet for the universe over the date range.

    Sentiment enrichment has two modes: pass ``sentiment_engine`` + ``anonymizer``
    (+ ``news_source``) for the causal FinBERT-style daily-sentiment join, or the
    simpler ``llm`` + ``news_source`` per-headline averaging.
    """
    cfg = cfg or get_config()
    universe = universe or StaticUniverseProvider()
    sectors = universe.sectors()
    symbols = list(sectors)

    use_engine = (
        sentiment_engine is not None and anonymizer is not None and news_source is not None
    )
    frame = build_training_frame(
        symbols, sectors, start, end, source, cfg,
        news_source=news_source if use_engine else None,
        sentiment_engine=sentiment_engine if use_engine else None,
        anonymizer=anonymizer if use_engine else None,
    )
    if not use_engine and news_source is not None and llm is not None:
        frame = add_news_sentiment(frame, news_source, llm)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    frame.write_parquet(out)
    return {
        "rows": frame.height,
        "symbols": len(symbols),
        "columns": frame.columns,
        "path": str(out),
        "start": start.isoformat(),
        "end": end.isoformat(),
    }
