"""Vectorized feature engine built on Polars frames.

Computes the Phase 2 technical + microstructure feature set with no Python
loops (principle G2). Operates per ticker so rolling windows never bleed across
symbols. Required input columns: date, ticker, open, high, low, close, volume.

Hygiene (G5): purge NaNs from bad *inputs* before calling this; the leading
nulls that rolling windows legitimately produce are left for the caller to drop.
"""

import math

import polars as pl

from new_pipeline.core.exceptions import SchemaValidationError
from new_pipeline.features.base import FeatureEngine
from new_pipeline.features.gpu_kernels import rolling_duvol, rolling_ncskew
from new_pipeline.features.registry import FeatureMetadata, feature_registry

ATR_PERIOD = 14
ADV_WINDOW = 20
VOL_WINDOW = 20
AMIHUD_WINDOW = 20
CRASH_WINDOW = 60
TRADING_DAYS = 252
REGIME_QUANTILE = 0.8

FEATURE_NAMES = (
    "returns",
    "atr",
    "adv_20",
    "volatility",
    "spread_pct",
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


class PolarsFeatureEngine(FeatureEngine):
    """FeatureEngine implementation backed by :func:`compile_features`."""

    def __init__(self) -> None:
        self._register_features()

    def compile(self, raw_path, processed_path) -> None:
        compile_features(pl.read_parquet(raw_path)).write_parquet(processed_path)

    def list_available_features(self) -> list[str]:
        return list(FEATURE_NAMES)

    def _register_features(self) -> None:
        # persist=False: keep the tracked registry YAML stable during runs/tests.
        for name, meta in _feature_metadata().items():
            if feature_registry.get(name) is None:
                feature_registry.register(name, meta, persist=False)
