from datetime import date

import numpy as np
import pytest
from new_pipeline.adapters.fakes import FakeMarketDataSource
from new_pipeline.analysis.backtest import backtest_ticker
from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything


def _prepare(monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    monkeypatch.setenv("QA_EXECUTION__CONFIDENCE_THRESHOLD", "0.3")
    reload_config()
    seed_everything(0)


def test_backtest_produces_equity_curve(monkeypatch):
    _prepare(monkeypatch)
    result = backtest_ticker("AAPL", date(2023, 1, 1), date(2023, 9, 30), FakeMarketDataSource())

    assert result.n_test_bars > 0
    assert result.equity_curve.size == result.n_test_bars
    assert np.isfinite(result.sharpe)
    assert -1.0 <= result.max_drawdown <= 0.0
    assert 0.0 <= result.win_rate <= 1.0


def test_backtest_short_history_is_empty():
    result = backtest_ticker("AAPL", date(2023, 1, 1), date(2023, 1, 5), FakeMarketDataSource())
    assert result.n_test_bars == 0 and result.n_trades == 0


def test_plot_backtest_writes_png(tmp_path, monkeypatch):
    pytest.importorskip("matplotlib")
    _prepare(monkeypatch)
    from new_pipeline.analysis.backtest import plot_backtest

    result = backtest_ticker("AAPL", date(2023, 1, 1), date(2023, 9, 30), FakeMarketDataSource())
    out = plot_backtest(result, tmp_path / "bt.png", subtitle="offline test")
    assert (tmp_path / "bt.png").exists() and out.endswith("bt.png")
