from pathlib import Path

import pandas as pd

from new_pipeline.features.base import FeatureEngine
from new_pipeline.features.registry import FeatureMetadata, feature_registry
from new_pipeline.config import get_config
from new_pipeline.core.exceptions import IngestionError
from new_pipeline.data.vaults import VaultManager


class PandasFeatureCompiler(FeatureEngine):
    def __init__(self) -> None:
        self.config = get_config()
        self.vaults = VaultManager()
        self._register_features()

    def compile(self, raw_path: Path, processed_path: Path) -> None:
        if not raw_path.exists():
            raise IngestionError(f"Raw path does not exist: {raw_path}")

        processed_path.mkdir(parents=True, exist_ok=True)
        raw_files = list(raw_path.glob("*.csv"))

        for raw_file in raw_files:
            df = pd.read_csv(raw_file, parse_dates=["date"])
            df = self._validate_dataframe(df)
            df = self._compute_features(df)

            output_file = processed_path / raw_file.name
            df.to_csv(output_file, index=False)

    def list_available_features(self) -> list[str]:
        return feature_registry.list_features()

    def _register_features(self) -> None:
        for name, metadata in self._feature_definitions().items():
            if feature_registry.get(name) is None:
                feature_registry.register(name, metadata)

    @staticmethod
    def _feature_definitions() -> dict[str, FeatureMetadata]:
        return {
            "returns": FeatureMetadata(
                name="returns",
                description="Daily price return computed from close prices.",
                source="price",
                window="1d",
                dtype="float",
            ),
            "atr_14": FeatureMetadata(
                name="atr_14",
                description="14-day average true range for volatility scaling.",
                source="price",
                window="14d",
                dtype="float",
            ),
            "volatility_20": FeatureMetadata(
                name="volatility_20",
                description="20-day rolling standard deviation of returns.",
                source="price",
                window="20d",
                dtype="float",
            ),
            "average_volume_20": FeatureMetadata(
                name="average_volume_20",
                description="20-day moving average volume.",
                source="volume",
                window="20d",
                dtype="float",
            ),
        }

    def _validate_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        expected = {"date", "open", "high", "low", "close", "volume"}
        missing = expected.difference(df.columns)
        if missing:
            raise IngestionError(f"Missing required columns: {sorted(missing)}")
        return df.sort_values("date").reset_index(drop=True)

    def _compute_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df["returns"] = df["close"].pct_change().fillna(0.0)

        high_low = df["high"] - df["low"]
        high_close = (df["high"] - df["close"].shift(1)).abs()
        low_close = (df["low"] - df["close"].shift(1)).abs()
        df["atr_14"] = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1).rolling(14).mean().fillna(0.0)

        df["volatility_20"] = df["returns"].rolling(window=20).std().fillna(0.0)
        df["average_volume_20"] = df["volume"].rolling(window=20).mean().fillna(0.0)

        return df
