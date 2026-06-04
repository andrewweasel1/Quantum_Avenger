import pandas as pd
from new_pipeline.config import reload_config
from new_pipeline.data.ingestion import DataIngestion


def test_load_many_concurrent(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_DATA__RAW_VAULT_DIR", str(tmp_path / "raw"))
    reload_config()
    ingestion = DataIngestion()
    names = ["a.csv", "b.csv", "c.csv"]
    for name in names:
        ingestion.stage_dataframe(pd.DataFrame({"date": ["2024-01-01"], "close": [1.0]}), name)

    frames = ingestion.load_many(names)

    assert set(frames) == set(names)
    assert all(len(frame) == 1 for frame in frames.values())
