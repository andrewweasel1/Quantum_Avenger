import pandas as pd


def make_sample_dataframe() -> pd.DataFrame:
    return pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=5, freq="D"),
        "close": [100.0, 101.0, 99.5, 102.0, 103.5],
        "high": [101.0, 102.0, 100.5, 103.0, 104.0],
        "low": [99.0, 100.0, 98.5, 101.0, 102.5],
        "volume": [1000, 1100, 950, 1200, 1300],
    })
