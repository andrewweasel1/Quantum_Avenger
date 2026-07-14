"""Offline tests for the pooled S&P 500 backtest (synthetic bars, no network)."""

from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest

from new_pipeline.analysis.sp500_backtest import (
    SP500BacktestOptions,
    UniverseRecord,
    _merge_sentiment,
    load_sp500_universe,
    run_sp500_backtest,
)


def test_feature_columns_families():
    base = SP500BacktestOptions(
        start=date(2026, 1, 1), end=date(2026, 2, 1),
        use_news_sentiment=False, expanded_families=False, use_fundamentals=False,
    )
    assert base.feature_columns() == [
        "returns", "atr", "adv_20", "volatility", "spread_pct", "roll_spread", "amihud"
    ]
    full = SP500BacktestOptions(start=date(2026, 1, 1), end=date(2026, 2, 1))
    columns = full.feature_columns()
    for expected in ("ncskew", "duvol", "regime", "sentiment_score",
                     "fund_rev_yoy", "fund_net_margin", "fund_roe"):
        assert expected in columns


def test_sp500_universe_fixture_loads():
    universe = load_sp500_universe()
    assert len(universe) > 490
    tickers = {record.ticker for record in universe}
    assert {"AAPL", "MSFT", "JPM", "XOM"} <= tickers
    assert all(record.cik > 0 for record in universe)


def test_merge_sentiment_overwrites_neutral_scores():
    feats = pl.DataFrame(
        {
            "ticker": ["AAA", "AAA"],
            "date": [date(2026, 1, 2), date(2026, 1, 3)],
            "sentiment_score": [0.0, 0.0],
        }
    )
    tone = pl.DataFrame(
        {
            "date": [date(2026, 1, 2)],
            "gics_sector": ["Energy"],
            "sentiment_score": [1.25],
        }
    )
    merged = _merge_sentiment(feats, tone, {"AAA": "Energy"}).sort("date")
    assert merged["sentiment_score"].to_list() == [1.25, 0.0]  # missing day stays neutral


def _synthetic_bars(tickers, start, n_days, seed=7):
    rng = np.random.default_rng(seed)
    rows = []
    for ticker in tickers:
        close = 100.0
        day = start
        added = 0
        while added < n_days:
            if day.weekday() < 5:
                close *= 1.0 + rng.normal(0.0005, 0.01)
                spread = abs(rng.normal(0, 0.5)) + 0.1
                rows.append(
                    {
                        "date": day, "ticker": ticker,
                        "open": close * 0.999, "high": close + spread,
                        "low": close - spread, "close": close,
                        "volume": int(rng.integers(1_000_000, 5_000_000)),
                    }
                )
                added += 1
            day += timedelta(days=1)
    return pl.DataFrame(rows)


def test_run_sp500_backtest_end_to_end_offline():
    universe = [
        UniverseRecord("AAA", "Energy", "Alpha Corp", 1),
        UniverseRecord("BBB", "Financials", "Beta Corp", 2),
    ]
    start = date(2024, 1, 1)
    bars = _synthetic_bars(["AAA", "BBB"], start, 200)
    tone = pl.DataFrame(
        {
            "date": bars["date"].unique().to_list() * 2,
            "gics_sector": ["Energy"] * bars["date"].n_unique()
            + ["Financials"] * bars["date"].n_unique(),
            "sentiment_score": [0.1] * (2 * bars["date"].n_unique()),
        }
    )
    fundamentals = pl.DataFrame(
        {
            "ticker": ["AAA", "BBB"],
            "filed": [date(2024, 2, 1), date(2024, 2, 15)],
            "fund_rev_yoy": [0.2, -0.1],
            "fund_net_margin": [0.15, 0.05],
            "fund_roe": [0.3, 0.1],
        }
    )
    options = SP500BacktestOptions(
        start=start, end=bars["date"].max(), write_snapshot=False, signal_quantile=0.8
    )
    report = run_sp500_backtest(
        options, bars=bars, tone=tone, fundamentals=fundamentals, universe=universe
    )
    assert report.n_symbols == 2
    assert report.n_train_rows > 0 and report.n_test_rows > 0
    assert report.split_date < report.test_dates[0]
    assert len(report.equity_curve) == len(report.test_dates)
    assert 0.0 < report.signal_threshold < 1.0
    assert set(report.per_symbol["ticker"].to_list()) == {"AAA", "BBB"}
    # every test date strictly after the chronological split
    assert all(day > report.split_date for day in report.test_dates)


def test_run_backtest_raises_on_empty_input():
    universe = [UniverseRecord("AAA", "Energy", "Alpha Corp", 1)]
    empty = pl.DataFrame(
        schema={
            "date": pl.Date, "ticker": pl.String, "open": pl.Float64, "high": pl.Float64,
            "low": pl.Float64, "close": pl.Float64, "volume": pl.Int64,
        }
    )
    options = SP500BacktestOptions(
        start=date(2026, 1, 1), end=date(2026, 2, 1),
        use_news_sentiment=False, use_fundamentals=False, write_snapshot=False,
    )
    with pytest.raises(ValueError):
        run_sp500_backtest(options, bars=empty, universe=universe)
