from pathlib import Path

from new_pipeline.config import get_config


class VaultManager:
    def __init__(self) -> None:
        self.config = get_config()

    def raw_vault_path(self) -> Path:
        path = Path(self.config.data.raw_vault_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def processed_vault_path(self) -> Path:
        path = Path(self.config.data.processed_vault_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def ensure_vaults(self) -> tuple[Path, Path]:
        return self.raw_vault_path(), self.processed_vault_path()
