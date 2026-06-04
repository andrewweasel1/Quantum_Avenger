"""Lightweight performance summary (+ optional quantstats HTML tearsheet)."""

import numpy as np

from new_pipeline.tournament.simulator import sharpe_ratio


def summary_metrics(returns) -> dict:
    series = np.asarray(returns, dtype=np.float64)
    if series.size == 0:
        return {"sharpe": 0.0, "max_drawdown": 0.0, "win_rate": 0.0, "profit_factor": 0.0}
    equity = np.cumprod(1.0 + series)
    running_max = np.maximum.accumulate(equity)
    drawdown = (equity - running_max) / running_max
    wins = series[series > 0.0]
    losses = series[series < 0.0]
    gross_loss = float(-losses.sum())
    traded = series[series != 0.0]
    return {
        "sharpe": sharpe_ratio(series),
        "max_drawdown": float(drawdown.min()),
        "win_rate": float(wins.size / traded.size) if traded.size else 0.0,
        "profit_factor": float(wins.sum()) / gross_loss if gross_loss > 0.0 else 0.0,
    }


def write_html_tearsheet(returns, path) -> bool:
    """Write a quantstats HTML tearsheet if quantstats is installed, else False."""
    try:
        import pandas as pd
        import quantstats as qs
    except ImportError:
        return False
    series = pd.Series(np.asarray(returns, dtype=np.float64))
    qs.reports.html(series, output=str(path))  # pragma: no cover - optional dep
    return True
