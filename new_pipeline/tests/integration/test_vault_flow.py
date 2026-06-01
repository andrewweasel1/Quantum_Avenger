import os
from pathlib import Path

from new_pipeline.config import reload_config
from new_pipeline.data.vaults import VaultManager


def test_vault_manager_creates_paths(monkeypatch, tmp_path: Path):
    monkeypatch.setenv("QA_DATA__RAW_VAULT_DIR", str(tmp_path / "raw"))
    monkeypatch.setenv("QA_DATA__PROCESSED_VAULT_DIR", str(tmp_path / "processed"))
    reload_config()

    manager = VaultManager()
    raw, processed = manager.ensure_vaults()

    assert raw == tmp_path / "raw"
    assert processed == tmp_path / "processed"
    assert raw.exists()
    assert processed.exists()
