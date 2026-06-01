import pandas as pd

from new_pipeline.config import reload_config
from new_pipeline.data.ingestion import DataIngestion


def test_stage_and_load_dataframe(monkeypatch, tmp_path):
    monkeypatch.setenv("QA_DATA__RAW_VAULT_DIR", str(tmp_path / "raw"))
    reload_config()

    ingestion = DataIngestion()
    df = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02"],
            "open": [100.0, 101.0],
            "high": [101.0, 102.0],
            "low": [99.0, 100.0],
            "close": [100.5, 101.5],
            "volume": [1000, 1100],
        }
    )

    target = ingestion.stage_dataframe(df, "sample.csv")
    loaded = ingestion.load_raw_dataframe("sample.csv")

    assert target.exists()
    assert list(loaded.columns) == ["date", "open", "high", "low", "close", "volume"]
    assert len(loaded) == 2
