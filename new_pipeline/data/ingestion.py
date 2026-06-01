from pathlib import Path

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
