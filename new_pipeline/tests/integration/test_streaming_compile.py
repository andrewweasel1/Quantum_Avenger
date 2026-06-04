"""Out-of-core streaming feature compilation + the Dask parallel path (Tier 2)."""

from datetime import date

import polars as pl

from new_pipeline.adapters import FakeMarketDataSource
from new_pipeline.features.polars_engine import (
    FEATURE_NAMES,
    PolarsFeatureEngine,
    compile_features_dask,
)

_NEW_COLUMNS = ["roll_spread", "ncskew", "duvol", "sentiment_score"]


def _rows(symbol):
    return [
        {
            "date": bar.day, "ticker": symbol, "open": bar.open, "high": bar.high,
            "low": bar.low, "close": bar.close, "volume": bar.volume,
        }
        for bar in FakeMarketDataSource().history(symbol, date(2022, 1, 1), date(2022, 4, 30))
    ]


def test_roll_spread_in_feature_names():
    assert "roll_spread" in FEATURE_NAMES


def test_streaming_compile_out_of_core(tmp_path):
    raw = tmp_path / "raw.parquet"
    pl.DataFrame(_rows("AAA") + _rows("BBB")).write_parquet(raw)
    out = tmp_path / "processed.parquet"

    PolarsFeatureEngine().compile(raw, out)

    result = pl.read_parquet(out)
    assert set(result["ticker"].unique().to_list()) == {"AAA", "BBB"}
    for column in _NEW_COLUMNS:
        assert column in result.columns


def test_dask_parallel_compile(tmp_path):
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    for symbol in ("AAA", "BBB"):
        pl.DataFrame(_rows(symbol)).write_parquet(raw_dir / f"{symbol}.parquet")
    out = tmp_path / "processed.parquet"

    compile_features_dask(raw_dir, out)

    result = pl.read_parquet(out)
    assert set(result["ticker"].unique().to_list()) == {"AAA", "BBB"}
    assert "ncskew" in result.columns
