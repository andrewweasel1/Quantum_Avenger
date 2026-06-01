import pandas as pd

from new_pipeline.config import reload_config
from new_pipeline.data.vaults import VaultManager
from new_pipeline.features.compiler import PandasFeatureCompiler


def test_feature_compiler_generates_feature_columns(monkeypatch, tmp_path):
    monkeypatch.setenv("QA_DATA__RAW_VAULT_DIR", str(tmp_path / "raw"))
    monkeypatch.setenv("QA_DATA__PROCESSED_VAULT_DIR", str(tmp_path / "processed"))
    reload_config()

    raw_path = tmp_path / "raw"
    processed_path = tmp_path / "processed"
    raw_path.mkdir(parents=True)
    processed_path.mkdir(parents=True)

    df = pd.DataFrame(
        {
            "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04", "2026-01-05"],
            "open": [100.0, 101.0, 102.0, 103.0, 104.0],
            "high": [101.0, 102.0, 103.0, 104.0, 105.0],
            "low": [99.0, 100.0, 101.0, 102.0, 103.0],
            "close": [100.5, 101.5, 102.5, 103.5, 104.5],
            "volume": [1000, 1100, 1200, 1300, 1400],
        }
    )
    source_file = raw_path / "sample.csv"
    df.to_csv(source_file, index=False)

    compiler = PandasFeatureCompiler()
    compiler.compile(raw_path, processed_path)

    output_file = processed_path / "sample.csv"
    assert output_file.exists()

    output_df = pd.read_csv(output_file, parse_dates=["date"])
    assert "returns" in output_df.columns
    assert "atr_14" in output_df.columns
    assert "volatility_20" in output_df.columns
    assert "average_volume_20" in output_df.columns
