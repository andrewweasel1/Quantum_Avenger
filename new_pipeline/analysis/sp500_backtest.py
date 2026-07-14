"""S&P 500 portfolio backtest with optional news-sentiment + fundamentals fusion.

The single-ticker research tool (:mod:`new_pipeline.analysis.backtest`) trains
one model per symbol; this module runs the *pooled cross-sectional* variant the
dashboard exposes:

1. Universe — the S&P 500 membership fixture
   (``new_pipeline/data/universe/sp500_membership.csv``: ticker, GICS sector,
   security name, CIK).
2. Bars — daily OHLCV from Alpaca (IEX feed), fetched in multi-symbol batches
   and cached to Parquet.
3. Features — the production Polars feature set, plus (toggleable):
   * ``news`` family — GDELT sector-tone ``sentiment_score`` (z-scored daily
     average tone per GICS sector, market-level fallback);
   * ``fundamentals`` family — SEC EDGAR point-in-time ``fund_rev_yoy`` /
     ``fund_net_margin`` / ``fund_roe`` merged by backward as-of join on the
     filing date;
   * ``expanded`` families — crash-risk (ncskew, duvol) + volatility-regime
     columns on top of the core price/volume family.
4. Model — one pooled XGBoost booster (asymmetric loss), trained on all
   tickers before the chronological split date, evaluated strictly after it.
5. Simulation — the same t+1 risk-managed simulator the tournament uses, per
   ticker, aggregated equal-weight by date into a portfolio equity curve.
6. Snapshot — options, KPIs, equity curve, per-symbol table, and an
   equity/drawdown PNG under ``data/backtests/sp500_<timestamp>/``.

Everything network-facing is injectable so unit tests run offline on fakes.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path

import numpy as np
import polars as pl

from new_pipeline.adapters.fundamentals_sec import (
    FEATURE_COLUMNS as FUNDAMENTALS_FAMILY,
)
from new_pipeline.adapters.fundamentals_sec import (
    SecFundamentalsSource,
    merge_fundamentals,
)
from new_pipeline.config import get_config
from new_pipeline.core.paths import data_dir
from new_pipeline.features.labels import add_labels
from new_pipeline.features.polars_engine import compile_features
from new_pipeline.tournament.simulator import sharpe_ratio, simulate_t1_returns
from new_pipeline.tournament.trainer import predict_proba, train_booster

logger = logging.getLogger(__name__)

MEMBERSHIP_PATH = Path(__file__).resolve().parents[1] / "data" / "universe" / "sp500_membership.csv"

CORE_FAMILY = ("returns", "atr", "adv_20", "volatility", "spread_pct", "roll_spread", "amihud")
CRASH_FAMILY = ("ncskew", "duvol")
REGIME_FAMILY = ("regime",)
NEWS_FAMILY = ("sentiment_score",)

_MIN_ROWS = 40
_BATCH_SIZE = 100


@dataclass(frozen=True)
class SP500BacktestOptions:
    start: date
    end: date
    use_news_sentiment: bool = True
    expanded_families: bool = True
    use_fundamentals: bool = True
    train_frac: float = 0.7
    # The asymmetric 5x-FP objective compresses predicted probabilities to a
    # ceiling of ~p/(p+5(1-p)) ≈ 0.16 at a ~0.49 base rate, so the absolute
    # execution confidence gate (0.65) never fires on the pooled signal. The
    # backtest gates on a quantile of the *train-set* probability distribution
    # instead — fixed at fit time, so no test-set look-ahead.
    signal_quantile: float = 0.90
    max_symbols: int | None = None
    write_snapshot: bool = True

    def feature_columns(self) -> list[str]:
        columns = list(CORE_FAMILY)
        if self.expanded_families:
            columns += [*CRASH_FAMILY, *REGIME_FAMILY]
        if self.use_news_sentiment:
            columns += list(NEWS_FAMILY)
        if self.use_fundamentals:
            columns += list(FUNDAMENTALS_FAMILY)
        return columns


@dataclass
class SP500BacktestReport:
    options: SP500BacktestOptions
    feature_cols: list[str]
    n_symbols: int
    n_train_rows: int
    n_test_rows: int
    split_date: date
    test_dates: list[date]
    portfolio_returns: np.ndarray
    equity_curve: np.ndarray
    sharpe: float
    total_return: float
    max_drawdown: float
    win_rate: float
    n_trades: int
    signal_threshold: float
    per_symbol: pl.DataFrame
    degradations: list[str] = field(default_factory=list)
    snapshot_path: str | None = None

    def kpis(self) -> dict:
        return {
            "sharpe": self.sharpe,
            "total_return": self.total_return,
            "max_drawdown": self.max_drawdown,
            "win_rate": self.win_rate,
            "n_trades": self.n_trades,
            "signal_threshold": self.signal_threshold,
            "signal_quantile": self.options.signal_quantile,
            "n_symbols": self.n_symbols,
            "n_train_rows": self.n_train_rows,
            "n_test_rows": self.n_test_rows,
            "split_date": self.split_date.isoformat(),
            "test_start": self.test_dates[0].isoformat() if self.test_dates else None,
            "test_end": self.test_dates[-1].isoformat() if self.test_dates else None,
        }


@dataclass(frozen=True)
class UniverseRecord:
    ticker: str
    gics_sector: str
    security_name: str
    cik: int


def load_sp500_universe(path: Path | None = None) -> list[UniverseRecord]:
    frame = pl.read_csv(path or MEMBERSHIP_PATH)
    return [
        UniverseRecord(
            ticker=row["ticker"],
            gics_sector=row["gics_sector"],
            security_name=row["security_name"],
            cik=int(row["cik"]),
        )
        for row in frame.iter_rows(named=True)
    ]


def fetch_sp500_bars(
    symbols: list[str], start: date, end: date, cfg=None, cache_dir: Path | None = None
) -> pl.DataFrame:
    """Daily OHLCV for ``symbols`` from Alpaca (IEX), batched + Parquet-cached."""
    cfg = cfg or get_config()
    cache_dir = cache_dir or (data_dir() / "backtest_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    key = f"bars_{start:%Y%m%d}_{end:%Y%m%d}_{len(symbols)}"
    cache_path = cache_dir / f"{key}.parquet"
    if cache_path.exists():
        return pl.read_parquet(cache_path)

    from alpaca.data.enums import Adjustment, DataFeed
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockBarsRequest
    from alpaca.data.timeframe import TimeFrame

    client = StockHistoricalDataClient(cfg.alpaca.api_key, cfg.alpaca.secret_key)

    def fetch(batch: list[str]) -> dict:
        request = StockBarsRequest(
            symbol_or_symbols=batch,
            timeframe=TimeFrame.Day,
            start=datetime.combine(start, datetime.min.time()),
            end=datetime.combine(end, datetime.max.time()),
            feed=DataFeed(cfg.alpaca.data_feed),
            adjustment=Adjustment.ALL,
        )
        barset = client.get_stock_bars(request)
        return barset.data if hasattr(barset, "data") else dict(barset)

    rows: list[dict] = []
    for index in range(0, len(symbols), _BATCH_SIZE):
        batch = symbols[index : index + _BATCH_SIZE]
        try:
            data = fetch(batch)
        except Exception as exc:  # noqa: BLE001 - one bad symbol shouldn't sink the batch
            logger.warning("batch bar fetch failed (%s); retrying per symbol", exc)
            data = {}
            for symbol in batch:
                try:
                    data.update(fetch([symbol]))
                except Exception as symbol_exc:  # noqa: BLE001
                    logger.warning("skipping %s: %s", symbol, symbol_exc)
        for symbol, bars in data.items():
            for bar in bars:
                rows.append(
                    {
                        "date": bar.timestamp.date(),
                        "ticker": symbol,
                        "open": float(bar.open),
                        "high": float(bar.high),
                        "low": float(bar.low),
                        "close": float(bar.close),
                        "volume": int(bar.volume),
                    }
                )
        logger.info("fetched bars for %d/%d symbols", min(index + _BATCH_SIZE, len(symbols)), len(symbols))
    frame = pl.DataFrame(rows).sort("ticker", "date") if rows else pl.DataFrame(
        schema={
            "date": pl.Date, "ticker": pl.String, "open": pl.Float64, "high": pl.Float64,
            "low": pl.Float64, "close": pl.Float64, "volume": pl.Int64,
        }
    )
    frame.write_parquet(cache_path)
    return frame


def _merge_sentiment(feats: pl.DataFrame, tone: pl.DataFrame, sectors: dict[str, str]) -> pl.DataFrame:
    """Replace the engine's neutral sentiment_score with GDELT sector tone."""
    if tone.is_empty():
        return feats
    with_sector = feats.drop("sentiment_score").with_columns(
        pl.col("ticker").replace_strict(sectors, default="Unknown").alias("gics_sector")
    )
    merged = with_sector.join(tone, on=["date", "gics_sector"], how="left")
    return merged.with_columns(pl.col("sentiment_score").fill_null(0.0)).drop("gics_sector")


def run_sp500_backtest(
    options: SP500BacktestOptions,
    cfg=None,
    bars: pl.DataFrame | None = None,
    tone: pl.DataFrame | None = None,
    fundamentals: pl.DataFrame | None = None,
    universe: list[UniverseRecord] | None = None,
) -> SP500BacktestReport:
    """Run the pooled S&P 500 backtest. ``bars``/``tone``/``fundamentals`` are
    injectable for tests and dashboard reruns; when ``None`` they are fetched
    live (Alpaca / GDELT / SEC) with Parquet caching."""
    cfg = cfg or get_config()
    degradations: list[str] = []
    universe = universe or load_sp500_universe()
    if options.max_symbols:
        universe = universe[: options.max_symbols]
    symbols = [record.ticker for record in universe]
    sectors = {record.ticker: record.gics_sector for record in universe}

    if bars is None:
        bars = fetch_sp500_bars(symbols, options.start, options.end, cfg)
    if bars.is_empty():
        raise ValueError("no bars available for the requested universe/date range")
    missing = sorted(set(symbols) - set(bars["ticker"].unique().to_list()))
    if missing:
        degradations.append(f"no bars for {len(missing)} symbols: {', '.join(missing[:10])}…")

    feats = compile_features(bars)

    if options.use_news_sentiment:
        if tone is None:
            tone = _cached_tone(sorted(set(sectors.values())), options.start, options.end)
        if tone.is_empty():
            degradations.append("GDELT tone series empty — sentiment_score stayed neutral (0.0)")
        feats = _merge_sentiment(feats, tone, sectors)

    if options.use_fundamentals:
        if fundamentals is None:
            source = SecFundamentalsSource(
                cache_dir=data_dir() / "fundamentals_cache",
                ciks_by_ticker={record.ticker: record.cik for record in universe},
            )
            fundamentals = source.features(options.start, options.end)
        if fundamentals.is_empty():
            degradations.append("SEC fundamentals empty — fund_* features stayed neutral (0.0)")
        else:
            covered = fundamentals["ticker"].n_unique()
            if covered < len(symbols) * 0.8:
                degradations.append(f"SEC fundamentals cover only {covered}/{len(symbols)} symbols")
        feats = merge_fundamentals(feats, fundamentals)

    feats = add_labels(feats, cfg.features.label_horizon, cfg.features.label_cost_bps)
    feature_cols = options.feature_columns()
    required = [*feature_cols, "target_label", "close", "low", "atr"]
    clean = (
        feats.with_columns(pl.col(required).fill_nan(None))
        .drop_nulls(subset=required)
        .sort("ticker", "date")
    )
    if clean.is_empty():
        raise ValueError("no usable rows after feature compilation — check the date range")

    unique_dates = clean["date"].unique().sort()
    split_date = unique_dates[max(int(len(unique_dates) * options.train_frac) - 1, 0)]
    train = clean.filter(pl.col("date") <= split_date)
    test = clean.filter(pl.col("date") > split_date)
    if train.is_empty() or test.is_empty():
        raise ValueError("chronological split produced an empty train or test set")

    booster = train_booster(
        train.select(feature_cols).to_numpy(),
        train["target_label"].to_numpy().astype(np.float64),
        num_boost_round=cfg.tournament.num_boost_round,
        penalty_fp=cfg.tournament.penalty_fp,
        penalty_fn=cfg.tournament.penalty_fn,
    )
    train_proba = predict_proba(booster, train.select(feature_cols).to_numpy())
    threshold = float(np.quantile(train_proba, options.signal_quantile))

    daily: dict[date, list[float]] = {}
    per_symbol_rows: list[dict] = []
    n_trades = 0
    for (ticker,), group in test.group_by("ticker", maintain_order=True):
        if group.height < 2:
            continue
        proba = predict_proba(booster, group.select(feature_cols).to_numpy())
        signals = (proba > threshold).astype(np.int64)
        returns = simulate_t1_returns(
            signals,
            group["close"].to_numpy().astype(np.float64),
            group["low"].to_numpy().astype(np.float64),
            group["atr"].to_numpy().astype(np.float64),
            cfg.execution.atr_stop_multiplier,
            cfg.execution.max_risk_per_trade,
        )
        n_trades += int(signals.sum())
        for day, value in zip(group["date"].to_list(), returns):
            daily.setdefault(day, []).append(float(value))
        per_symbol_rows.append(
            {
                "ticker": ticker,
                "gics_sector": sectors.get(ticker, "Unknown"),
                "n_test_bars": group.height,
                "n_trades": int(signals.sum()),
                "total_return": float(np.prod(1.0 + returns) - 1.0),
                "sharpe": sharpe_ratio(returns),
            }
        )

    test_dates = sorted(daily)
    portfolio_returns = np.array([float(np.mean(daily[day])) for day in test_dates])
    equity = np.cumprod(1.0 + portfolio_returns) if portfolio_returns.size else np.ones(1)
    peak = np.maximum.accumulate(equity)
    drawdown = equity / peak - 1.0
    nonzero = portfolio_returns[portfolio_returns != 0.0]

    report = SP500BacktestReport(
        options=options,
        feature_cols=feature_cols,
        n_symbols=len(per_symbol_rows),
        n_train_rows=train.height,
        n_test_rows=test.height,
        split_date=split_date,
        test_dates=test_dates,
        portfolio_returns=portfolio_returns,
        equity_curve=equity,
        sharpe=sharpe_ratio(portfolio_returns),
        total_return=float(equity[-1] - 1.0),
        max_drawdown=float(drawdown.min()) if drawdown.size else 0.0,
        win_rate=float((nonzero > 0).mean()) if nonzero.size else 0.0,
        n_trades=n_trades,
        signal_threshold=threshold,
        per_symbol=pl.DataFrame(per_symbol_rows).sort("sharpe", descending=True)
        if per_symbol_rows
        else pl.DataFrame(),
        degradations=degradations,
    )
    if options.write_snapshot:
        report.snapshot_path = write_snapshot(report)
    return report


def _cached_tone(sectors: list[str], start: date, end: date) -> pl.DataFrame:
    """GDELT sector tone with a Parquet cache (12 rate-limited calls otherwise)."""
    from new_pipeline.adapters.news_gdelt import sector_tone_frame

    cache_dir = data_dir() / "backtest_cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"gdelt_tone_{start:%Y%m%d}_{end:%Y%m%d}.parquet"
    if cache_path.exists():
        return pl.read_parquet(cache_path)
    tone = sector_tone_frame(sectors, start, end, cache_dir=cache_dir / "gdelt_series")
    if not tone.is_empty():
        tone.write_parquet(cache_path)
    return tone


def snapshots_dir() -> Path:
    return data_dir() / "backtests"


def write_snapshot(report: SP500BacktestReport) -> str:
    """Persist the run: options, KPIs, curves, per-symbol table, equity PNG."""
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = snapshots_dir() / f"sp500_{stamp}"
    out.mkdir(parents=True, exist_ok=True)
    options = report.options
    (out / "options.json").write_text(
        json.dumps(
            {
                "universe": "S&P 500",
                "start": options.start.isoformat(),
                "end": options.end.isoformat(),
                "use_news_sentiment": options.use_news_sentiment,
                "expanded_families": options.expanded_families,
                "use_fundamentals": options.use_fundamentals,
                "train_frac": options.train_frac,
                "max_symbols": options.max_symbols,
                "feature_columns": report.feature_cols,
                "degradations": report.degradations,
            },
            indent=2,
        )
    )
    (out / "kpis.json").write_text(json.dumps(report.kpis(), indent=2))
    pl.DataFrame(
        {
            "date": report.test_dates,
            "portfolio_return": report.portfolio_returns,
            "equity": report.equity_curve,
        }
    ).write_parquet(out / "equity_curve.parquet")
    if not report.per_symbol.is_empty():
        report.per_symbol.write_csv(out / "per_symbol.csv")
    try:
        _plot_equity(report, out / "equity.png")
    except ImportError:
        logger.info("matplotlib unavailable; snapshot has no PNG")
    return str(out)


def _plot_equity(report: SP500BacktestReport, path: Path) -> None:  # pragma: no cover
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    equity = report.equity_curve
    peak = np.maximum.accumulate(equity)
    drawdown = equity / peak - 1.0
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [3, 1]}
    )
    ax1.plot(report.test_dates, equity, color="#1f77b4", linewidth=1.5)
    ax1.axhline(1.0, color="gray", linestyle="--", linewidth=0.8)
    toggles = []
    if report.options.use_news_sentiment:
        toggles.append("news")
    if report.options.expanded_families:
        toggles.append("expanded")
    if report.options.use_fundamentals:
        toggles.append("fundamentals")
    ax1.set_title(
        f"S&P 500 pooled backtest [{'+'.join(toggles) or 'core'}]  |  "
        f"return {report.total_return:+.1%}   Sharpe {report.sharpe:.2f}   "
        f"maxDD {report.max_drawdown:.1%}   trades {report.n_trades}"
    )
    ax1.set_ylabel("Equity (×)")
    ax1.grid(alpha=0.3)
    ax2.fill_between(report.test_dates, drawdown, color="#d62728", alpha=0.4)
    ax2.set_ylabel("Drawdown")
    ax2.grid(alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
