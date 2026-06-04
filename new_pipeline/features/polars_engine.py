"""Vectorized feature engine built on Polars frames.

Computes the Phase 2 technical + microstructure feature set with no Python
loops (principle G2). Operates per ticker so rolling windows never bleed across
symbols. Required input columns: date, ticker, open, high, low, close, volume.

Scale (Tier 2): :meth:`PolarsFeatureEngine.compile` is out-of-core — it scans
the vault lazily and streams one ticker at a time, writing psutil-sized row
groups, so memory stays bounded. :func:`compile_features_dask` parallelizes a
pre-partitioned (one-file-per-ticker) vault via Dask.

Hygiene (G5): purge NaNs from bad *inputs* before calling this; the leading
nulls that rolling windows legitimately produce are left for the caller to drop.
"""

import math
from pathlib import Path

import polars as pl
import pyarrow.parquet as pq

from new_pipeline.core.exceptions import SchemaValidationError
from new_pipeline.data.sizing import dynamic_row_group_size
from new_pipeline.features.base import FeatureEngine
from new_pipeline.features.gpu_kernels import rolling_duvol, rolling_ncskew
from new_pipeline.features.registry import FeatureMetadata, feature_registry

ATR_PERIOD = 14
ADV_WINDOW = 20
VOL_WINDOW = 20
AMIHUD_WINDOW = 20
SPREAD_WINDOW = 20
CRASH_WINDOW = 60
TRADING_DAYS = 252
REGIME_QUANTILE = 0.8

FEATURE_NAMES = (
    "returns",
    "atr",
    "adv_20",
    "volatility",
    "spread_pct",
    "roll_spread",
    "amihud",
    "regime",
    "ncskew",
    "duvol",
    "sentiment_score",
)
_REQUIRED_COLUMNS = ("date", "ticker", "open", "high", "low", "close", "volume")


def _feature_metadata() -> dict[str, FeatureMetadata]:
    return {
        "returns": FeatureMetadata("returns", "Arithmetic daily return.", "price", "1d"),
        "atr": FeatureMetadata("atr", "Wilder ATR (RMA of true range).", "price", f"{ATR_PERIOD}d"),
        "adv_20": FeatureMetadata("adv_20", "Average dollar volume.", "volume", f"{ADV_WINDOW}d"),
        "volatility": FeatureMetadata(
            "volatility", "Annualized rolling volatility.", "price", f"{VOL_WINDOW}d"
        ),
        "spread_pct": FeatureMetadata("spread_pct", "High-low spread over mid.", "price", "1d"),
        "roll_spread": FeatureMetadata(
            "roll_spread", "Rolling mean high-low spread.", "price", f"{SPREAD_WINDOW}d"
        ),
        "amihud": FeatureMetadata("amihud", "Amihud illiquidity.", "volume", f"{AMIHUD_WINDOW}d"),
        "regime": FeatureMetadata(
            "regime", "High-volatility regime flag.", "price", f"{VOL_WINDOW}d", "int"
        ),
        "ncskew": FeatureMetadata(
            "ncskew", "Rolling NCSKEW crash-risk skewness.", "price", f"{CRASH_WINDOW}d"
        ),
        "duvol": FeatureMetadata(
            "duvol", "Rolling down-to-up volatility.", "price", f"{CRASH_WINDOW}d"
        ),
        "sentiment_score": FeatureMetadata(
            "sentiment_score", "LLM sentiment (neutral default until fusion runs).", "fusion", "1d"
        ),
    }


def add_features(frame: pl.DataFrame) -> pl.DataFrame:
    """Add the Phase 2 features to a single ticker's frame (sorted by date)."""
    prev_close = pl.col("close").shift(1)
    true_range = pl.max_horizontal(
        pl.col("high") - pl.col("low"),
        (pl.col("high") - prev_close).abs(),
        (pl.col("low") - prev_close).abs(),
    )
    mid = (pl.col("high") + pl.col("low")) / 2.0

    out = frame.sort("date").with_columns(
        pl.col("close").pct_change().alias("returns"),
        true_range.alias("_tr"),
        mid.alias("_mid"),
    )
    out = out.with_columns(
        pl.col("_tr").ewm_mean(alpha=1.0 / ATR_PERIOD, adjust=False).alias("atr"),
        (pl.col("_mid") * pl.col("volume")).rolling_mean(window_size=ADV_WINDOW).alias("adv_20"),
        (
            pl.col("returns").rolling_std(window_size=VOL_WINDOW) * math.sqrt(TRADING_DAYS)
        ).alias("volatility"),
        ((pl.col("high") - pl.col("low")) / pl.col("_mid")).alias("spread_pct"),
    )
    out = out.with_columns(
        pl.col("spread_pct").rolling_mean(window_size=SPREAD_WINDOW).alias("roll_spread"),
        (pl.col("returns").abs() / (pl.col("close") * pl.col("volume")))
        .rolling_mean(window_size=AMIHUD_WINDOW)
        .alias("amihud"),
        (pl.col("volatility") > pl.col("volatility").quantile(REGIME_QUANTILE))
        .cast(pl.Int8)
        .alias("regime"),
    )
    returns_np = out["returns"].fill_null(0.0).to_numpy()
    out = out.with_columns(
        pl.Series("ncskew", rolling_ncskew(returns_np, CRASH_WINDOW)),
        pl.Series("duvol", rolling_duvol(returns_np, CRASH_WINDOW)),
        pl.lit(0.0).alias("sentiment_score"),
    )
    return out.drop("_tr", "_mid")


def compile_features(frame: pl.DataFrame) -> pl.DataFrame:
    """Add features per ticker and recombine. Validates required columns first."""
    missing = [column for column in _REQUIRED_COLUMNS if column not in frame.columns]
    if missing:
        raise SchemaValidationError(f"Missing required columns: {missing}")
    groups = [
        add_features(group) for _, group in frame.group_by("ticker", maintain_order=True)
    ]
    return pl.concat(groups) if groups else frame


def _compile_file(path: str) -> pl.DataFrame:
    return add_features(pl.read_parquet(path))


def compile_features_dask(input_dir, output_path) -> None:
    """Parallel per-file feature compilation via Dask (each file = one ticker)."""
    import dask

    files = sorted(Path(input_dir).glob("*.parquet"))
    if not files:
        return
    frames = dask.compute(*[dask.delayed(_compile_file)(str(path)) for path in files])
    _stream_write(frames, output_path)


def _stream_write(frames, output_path) -> None:
    row_group_size = dynamic_row_group_size()
    writer = None
    try:
        for frame in frames:
            table = frame.to_arrow()
            if writer is None:
                writer = pq.ParquetWriter(str(output_path), table.schema)
            writer.write_table(table, row_group_size=row_group_size)
    finally:
        if writer is not None:
            writer.close()


class PolarsFeatureEngine(FeatureEngine):
    """FeatureEngine implementation backed by :func:`compile_features`."""

    def __init__(self) -> None:
        self._register_features()

    def compile(self, raw_path, processed_path) -> None:
        """Out-of-core: scan lazily and stream one ticker at a time to disk."""
        lazy = pl.scan_parquet(raw_path)
        tickers = lazy.select("ticker").unique().collect().to_series().to_list()
        featured = (
            add_features(lazy.filter(pl.col("ticker") == ticker).collect()) for ticker in tickers
        )
        _stream_write(featured, processed_path)

    def list_available_features(self) -> list[str]:
        return list(FEATURE_NAMES)

    def _register_features(self) -> None:
        # persist=False: keep the tracked registry YAML stable during runs/tests.
        for name, meta in _feature_metadata().items():
            if feature_registry.get(name) is None:
                feature_registry.register(name, meta, persist=False)
