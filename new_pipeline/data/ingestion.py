from pathlib import Path

import pandas as pd

from new_pipeline.config import get_config
from new_pipeline.core.exceptions import IngestionError


class DataIngestion:
    def __init__(self) -> None:
        self.config = get_config()

    def ensure_raw_vault(self) -> Path:
        raw_dir = Path(self.config.data.raw_vault_dir)
        raw_dir.mkdir(parents=True, exist_ok=True)
        return raw_dir

    def stage_source_file(self, source_path: Path, destination_name: str) -> Path:
        raw_dir = self.ensure_raw_vault()
        target_path = raw_dir / destination_name
        try:
            if not source_path.exists():
                raise IngestionError(f"Source file does not exist: {source_path}")
            with source_path.open("rb") as source, target_path.open("wb") as dest:
                dest.write(source.read())
            return target_path
        except Exception as exc:
            raise IngestionError(f"Failed to stage source file: {exc}") from exc

    def stage_dataframe(self, df: pd.DataFrame, destination_name: str) -> Path:
        raw_dir = self.ensure_raw_vault()
        target_path = raw_dir / destination_name
        try:
            if target_path.suffix == ".parquet":
                try:
                    df.to_parquet(target_path, index=False)
                except ImportError as exc:
                    raise IngestionError(
                        "Parquet support requires pyarrow or fastparquet. "
                        "Install it before using .parquet output."
                    ) from exc
            else:
                df.to_csv(target_path, index=False)
            return target_path
        except Exception as exc:
            raise IngestionError(f"Failed to persist dataframe: {exc}") from exc

    def load_raw_dataframe(self, source_name: str) -> pd.DataFrame:
        raw_dir = self.ensure_raw_vault()
        source_path = raw_dir / source_name
        if not source_path.exists():
            raise IngestionError(f"Raw file missing: {source_path}")

        try:
            if source_path.suffix == ".parquet":
                return pd.read_parquet(source_path)
            return pd.read_csv(source_path, parse_dates=["date"])
        except Exception as exc:
            raise IngestionError(f"Failed to load raw dataframe: {exc}") from exc
