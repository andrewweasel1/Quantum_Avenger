from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest
from new_pipeline.core.exceptions import SchemaValidationError
from new_pipeline.features.polars_engine import (
    ATR_PERIOD,
    FEATURE_NAMES,
    PolarsFeatureEngine,
    add_features,
    compile_features,
)


def _frame(ticker: str = "AAPL", n: int = 30, seed: int = 0):
    rng = np.random.default_rng(seed)
    close = 100.0 + np.cumsum(rng.normal(0.0, 1.0, n))
    high = close + rng.uniform(0.5, 1.5, n)
    low = close - rng.uniform(0.5, 1.5, n)
    volume = rng.integers(1_000_000, 2_000_000, n).astype(float)
    dates = [date(2024, 1, 1) + timedelta(days=i) for i in range(n)]
    frame = pl.DataFrame(
        {
            "date": dates,
            "ticker": [ticker] * n,
            "open": close,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume,
        }
    )
    return frame, close, high, low


def _expected_atr_last(close, high, low) -> float:
    n = len(close)
    tr = np.empty(n)
    tr[0] = high[0] - low[0]
    for i in range(1, n):
        tr[i] = max(
            high[i] - low[i], abs(high[i] - close[i - 1]), abs(low[i] - close[i - 1])
        )
    alpha = 1.0 / ATR_PERIOD
    atr = tr[0]
    for i in range(1, n):
        atr = atr * (1.0 - alpha) + tr[i] * alpha
    return atr


def test_returns_and_spread_match_numpy():
    frame, close, high, low = _frame()
    out = add_features(frame).sort("date")
    assert out["returns"].to_list()[-1] == pytest.approx(close[-1] / close[-2] - 1.0, rel=1e-9)
    mid = (high[-1] + low[-1]) / 2.0
    assert out["spread_pct"].to_list()[-1] == pytest.approx((high[-1] - low[-1]) / mid, rel=1e-9)


def test_atr_matches_wilder_rma():
    frame, close, high, low = _frame()
    out = add_features(frame).sort("date")
    assert out["atr"].to_list()[-1] == pytest.approx(_expected_atr_last(close, high, low), rel=1e-9)


def test_volatility_matches_rolling_std():
    frame, close, _, _ = _frame()
    out = add_features(frame).sort("date")
    ret = close[1:] / close[:-1] - 1.0
    expected = ret[-20:].std(ddof=1) * np.sqrt(252)
    assert out["volatility"].to_list()[-1] == pytest.approx(expected, rel=1e-9)


def test_multi_ticker_isolation():
    a, *_ = _frame("AAPL", seed=1)
    b, *_ = _frame("MSFT", seed=2)
    out = compile_features(pl.concat([a, b]))
    for ticker in ("AAPL", "MSFT"):
        first_return = out.filter(pl.col("ticker") == ticker).sort("date")["returns"].to_list()[0]
        assert first_return is None  # no bleed across tickers
    assert set(out["ticker"].unique().to_list()) == {"AAPL", "MSFT"}


def test_missing_columns_raise():
    bad = pl.DataFrame({"date": [date(2024, 1, 1)], "ticker": ["AAPL"], "close": [100.0]})
    with pytest.raises(SchemaValidationError):
        compile_features(bad)


def test_engine_registers_features():
    engine = PolarsFeatureEngine()
    assert set(FEATURE_NAMES).issubset(set(engine.list_available_features()))
