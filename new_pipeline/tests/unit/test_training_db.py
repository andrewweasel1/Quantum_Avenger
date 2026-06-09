from datetime import date

import polars as pl
from new_pipeline.adapters.fakes import FakeLLMClient, FakeMarketDataSource, FakeNewsSource
from new_pipeline.adapters.universe_static import StaticUniverseProvider
from new_pipeline.config import reload_config
from new_pipeline.data.training_db import build_training_database


def test_build_training_database_with_news(tmp_path):
    reload_config()
    out = tmp_path / "training.parquet"
    summary = build_training_database(
        out, FakeMarketDataSource(), StaticUniverseProvider(),
        start=date(2023, 1, 1), end=date(2023, 4, 30),
        news_source=FakeNewsSource(), llm=FakeLLMClient(),
    )

    assert out.exists() and summary["rows"] > 0
    df = pl.read_parquet(out)
    assert {"target_label", "sentiment_score"} <= set(df.columns)
    assert df["sentiment_score"].is_between(-1.0, 1.0).all()
    assert df["sentiment_score"].n_unique() > 1  # news enrichment varies the score


def test_build_training_database_without_news(tmp_path):
    reload_config()
    out = tmp_path / "t.parquet"
    summary = build_training_database(
        out, FakeMarketDataSource(), StaticUniverseProvider(),
        start=date(2023, 1, 1), end=date(2023, 3, 31),
    )
    assert out.exists() and summary["rows"] > 0
    # sentiment_score is part of the feature contract; without news it stays the placeholder.
    assert pl.read_parquet(out)["sentiment_score"].n_unique() == 1
