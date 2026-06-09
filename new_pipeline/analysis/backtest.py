"""Single-ticker backtest + performance visualization (research tool).

Pulls daily bars from any ``MarketDataSource`` (live Alpaca or the offline
fake), computes the production features, trains an *out-of-sample* XGBoost
signal (train on the first ``train_frac``, evaluate on the rest), and realizes
t+1 risk-managed returns with the same simulator the tournament uses.
``plot_backtest`` renders an equity-curve + drawdown PNG (matplotlib, a dev dep).
"""

from dataclasses import dataclass
from datetime import date

import numpy as np
import polars as pl

from new_pipeline.config import get_config
from new_pipeline.features.labels import add_labels
from new_pipeline.features.polars_engine import compile_features
from new_pipeline.tournament.simulator import sharpe_ratio, simulate_t1_returns
from new_pipeline.tournament.trainer import predict_proba, train_booster

FEATURE_COLS = [
    "returns", "atr", "adv_20", "volatility", "spread_pct", "roll_spread",
    "amihud", "ncskew", "duvol",
]
_MIN_ROWS = 20


@dataclass
class BacktestResult:
    symbol: str
    start: date
    end: date
    returns: np.ndarray
    equity_curve: np.ndarray
    sharpe: float
    total_return: float
    max_drawdown: float
    win_rate: float
    n_trades: int
    n_test_bars: int


def backtest_ticker(
    symbol, start, end, source, cfg=None, train_frac: float = 0.7
) -> BacktestResult:
    """Out-of-sample t+1 backtest of the XGBoost signal on a single ticker."""
    cfg = cfg or get_config()
    bars = source.history(symbol, start, end)
    if len(bars) < _MIN_ROWS:
        return _empty_result(symbol, start, end)

    frame = pl.DataFrame(
        [
            {
                "date": bar.day, "ticker": symbol, "open": bar.open, "high": bar.high,
                "low": bar.low, "close": bar.close, "volume": bar.volume,
            }
            for bar in bars
        ]
    )
    feats = add_labels(
        compile_features(frame), cfg.features.label_horizon, cfg.features.label_cost_bps
    )
    required = [*FEATURE_COLS, "target_label", "close", "low", "atr"]
    clean = feats.with_columns(pl.col(required).fill_nan(None)).drop_nulls(subset=required)
    if clean.height < _MIN_ROWS:
        return _empty_result(symbol, start, end)

    split = max(int(clean.height * train_frac), 10)
    features = clean.select(FEATURE_COLS).to_numpy()
    labels = clean["target_label"].to_numpy().astype(np.float64)
    booster = train_booster(
        features[:split], labels[:split],
        num_boost_round=cfg.tournament.num_boost_round,
        penalty_fp=cfg.tournament.penalty_fp, penalty_fn=cfg.tournament.penalty_fn,
    )
    proba = predict_proba(booster, features[split:])
    signals = (proba > cfg.execution.confidence_threshold).astype(np.int64)
    prices = {c: clean[c].to_numpy().astype(np.float64)[split:] for c in ("close", "low", "atr")}
    returns = simulate_t1_returns(
        signals, prices["close"], prices["low"], prices["atr"],
        cfg.execution.atr_stop_multiplier, cfg.execution.max_risk_per_trade,
    )
    return _summarize(symbol, start, end, returns, int(signals.sum()))


def _summarize(symbol, start, end, returns, n_trades) -> BacktestResult:
    equity = np.cumprod(1.0 + returns) if returns.size else np.ones(1)
    peak = np.maximum.accumulate(equity)
    drawdown = equity / peak - 1.0
    nonzero = returns[returns != 0.0]
    win_rate = float((nonzero > 0).mean()) if nonzero.size else 0.0
    return BacktestResult(
        symbol=symbol, start=start, end=end, returns=returns, equity_curve=equity,
        sharpe=sharpe_ratio(returns), total_return=float(equity[-1] - 1.0),
        max_drawdown=float(drawdown.min()) if drawdown.size else 0.0,
        win_rate=win_rate, n_trades=n_trades, n_test_bars=int(returns.size),
    )


def _empty_result(symbol, start, end) -> BacktestResult:
    return BacktestResult(symbol, start, end, np.zeros(0), np.ones(1), 0.0, 0.0, 0.0, 0.0, 0, 0)


def plot_backtest(result: BacktestResult, path, subtitle: str = "") -> str:  # pragma: no cover
    """Render an equity-curve + drawdown PNG. Matplotlib is a dev/analysis dep."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    equity = result.equity_curve
    peak = np.maximum.accumulate(equity)
    drawdown = equity / peak - 1.0
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(10, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]}
    )
    ax1.plot(equity, color="#1f77b4", linewidth=1.5)
    ax1.axhline(1.0, color="gray", linestyle="--", linewidth=0.8)
    ax1.set_title(
        f"{result.symbol}  |  return {result.total_return:+.1%}   Sharpe {result.sharpe:.2f}   "
        f"maxDD {result.max_drawdown:.1%}   trades {result.n_trades}   "
        f"win {result.win_rate:.0%}"
    )
    ax1.set_ylabel("Equity (×)")
    ax1.grid(alpha=0.3)
    ax2.fill_between(range(len(drawdown)), drawdown, color="#d62728", alpha=0.4)
    ax2.set_ylabel("Drawdown")
    ax2.set_xlabel("Out-of-sample bar")
    ax2.grid(alpha=0.3)
    if subtitle:
        fig.text(0.5, 0.01, subtitle, ha="center", fontsize=8, color="gray")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return str(path)
