"""Whole-engine trading runner: champions -> walk-forward replay -> trade graph.

The composition root that drives the engine end to end. For each promoted
champion it pulls the sector's bars from the market-data adapter, computes
features, walks the bars forward, and at every signal builds a ``TradeRequest``
and runs the LangGraph ``TradeOrchestrator`` (Verdict -> Grader -> Shield veto ->
Execute/Fallback). Decisions land in the veto ledger; executed trades realize a
t+1 return via the backtest simulator and land in the trade log — the two
parquet files the dashboard reads.

Offline this runs over the deterministic fakes with no network. The *same* loop
runs live the moment ``build_adapters`` returns live clients for a live
``run_mode`` — only the adapters change, not the orchestration.
"""

import json
import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import polars as pl

from new_pipeline.adapters.factory import build_adapters
from new_pipeline.config import get_config
from new_pipeline.evaluation.promotion import PromotionRegistry
from new_pipeline.execution.orchestrator import TradeOrchestrator, TradeRequest
from new_pipeline.execution.trade_log import TradeLog, TradeRecord
from new_pipeline.execution.veto_ledger import VetoLedger
from new_pipeline.features.polars_engine import compile_features
from new_pipeline.tournament.simulator import simulate_t1_returns
from new_pipeline.tournament.trainer import load_booster, predict_proba

_PRICE_COLS = ("close", "low", "atr", "adv_20", "volatility", "volume")
_logger = logging.getLogger(__name__)


@dataclass
class SessionSummary:
    sectors: list[str]
    decisions: int
    executed: int
    vetoed: int
    realized_pnl: float


def run_trading_session(
    candidates_dir,
    start: date = date(2021, 1, 1),
    end: date = date(2021, 12, 31),
    adapters=None,
    cfg=None,
    registry_path=None,
) -> SessionSummary:
    """Drive promoted champions through the live trade graph over a bar replay."""
    cfg = cfg or get_config()
    adapters = adapters or build_adapters(cfg)
    candidates = Path(candidates_dir)
    registry = PromotionRegistry(registry_path or candidates / "promotion_registry.json")
    champions = registry.active_champions()
    if not champions:
        _logger.info("no active champions; nothing to trade")
        return SessionSummary([], 0, 0, 0, 0.0)

    ledger_dir = Path(cfg.execution.ledger_dir)
    ledger = VetoLedger(ledger_dir / "veto_ledger.parquet")
    trade_log = TradeLog(ledger_dir / "trade_log.parquet")
    orchestrator = TradeOrchestrator(
        adapters.llm,
        adapters.broker,
        ledger,
        max_retries=cfg.execution.max_retries,
        tif=cfg.execution.tif,
    )
    dsr_by_sector = _champion_dsr(registry)
    sector_of = adapters.universe.sectors()

    counters = {"decisions": 0, "executed": 0, "vetoed": 0, "pnl": 0.0}
    for sector, model_path in champions.items():
        booster = load_booster(model_path)
        selected = _selected_features(model_path)
        symbols = [ticker for ticker, sec in sector_of.items() if sec == sector]
        for symbol in symbols:
            _replay_symbol(
                symbol, dsr_by_sector.get(sector, 0.0), booster, selected,
                adapters, orchestrator, trade_log, start, end, cfg, counters,
            )

    return SessionSummary(
        sectors=list(champions),
        decisions=counters["decisions"],
        executed=counters["executed"],
        vetoed=counters["vetoed"],
        realized_pnl=round(counters["pnl"], 6),
    )


def _replay_symbol(
    symbol, dsr, booster, selected, adapters, orchestrator, trade_log, start, end, cfg, counters
):
    bars = adapters.market_data.history(symbol, start, end)
    if len(bars) < 2:
        return
    frame = pl.DataFrame(
        [
            {
                "date": bar.day, "ticker": symbol, "open": bar.open, "high": bar.high,
                "low": bar.low, "close": bar.close, "volume": bar.volume,
            }
            for bar in bars
        ]
    )
    features = compile_features(frame)
    required = [*selected, *_PRICE_COLS]
    clean = features.with_columns(pl.col(required).fill_nan(None)).drop_nulls(subset=required)
    if clean.height < 2:
        return

    matrix = clean.select(selected).to_numpy()
    proba = predict_proba(booster, matrix)
    signals = proba > cfg.execution.confidence_threshold
    prices = {col: clean[col].to_numpy().astype(np.float64) for col in _PRICE_COLS}
    dates = clean["date"].to_list()

    for i in range(clean.height - 1):
        if not signals[i]:
            continue
        counters["decisions"] += 1
        request = _build_request(symbol, dsr, prices, i, cfg, adapters, dates[i])
        state = orchestrator.run(request)
        if state.get("outcome") == "executed":
            counters["executed"] += 1
            pnl = _realized_return(prices, i, cfg)
            counters["pnl"] += pnl
            _record_fill(trade_log, request, state, prices["close"][i], pnl)
        else:
            counters["vetoed"] += 1


def _build_request(symbol, dsr, prices, i, cfg, adapters, day) -> TradeRequest:
    context = [item.headline for item in adapters.news.headlines(symbol, day)]
    current_qty = adapters.broker.get_positions().get(symbol, 0.0)
    return TradeRequest(
        signal="BUY",
        symbol=symbol,
        entry_price=float(prices["close"][i]),
        atr=float(prices["atr"][i]),
        atr_multiplier=cfg.execution.atr_stop_multiplier,
        account_capital=cfg.execution.account_capital,
        max_risk_pct=cfg.execution.max_risk_per_trade,
        current_qty=current_qty,
        adv_20=float(prices["adv_20"][i]),
        volume_today=float(prices["volume"][i]),
        volatility=float(prices["volatility"][i]),
        context=context,
        dsr=dsr,
    )


def _realized_return(prices, i, cfg) -> float:
    """t+1 realized return of the entry, reusing the backtest simulator's math."""
    window = simulate_t1_returns(
        np.array([1, 0], dtype=np.int64),
        prices["close"][i : i + 2],
        prices["low"][i : i + 2],
        prices["atr"][i : i + 2],
        cfg.execution.atr_stop_multiplier,
        cfg.execution.max_risk_per_trade,
    )
    return float(window[0])


def _record_fill(trade_log, request, state, fill_price, pnl) -> None:
    limit_price = round(request.entry_price + 0.1 * request.atr, 2)
    trade_log.append(
        TradeRecord(
            symbol=request.symbol,
            side="buy",
            qty=int(state.get("position_size", 0)),
            limit_price=limit_price,
            status="filled",
            order_id=str(state.get("execution_id", "")),
            fill_price=float(fill_price),
            pnl=pnl,
        )
    )


def _selected_features(model_path) -> list[str]:
    features_path = str(model_path).replace("_candidate.json", "_candidate_features.json")
    return json.loads(Path(features_path).read_text(encoding="utf-8"))["features"]


def _champion_dsr(registry: PromotionRegistry) -> dict[str, float]:
    """Most recent promoted DSR per sector, for the ledger's audit column."""
    dsr: dict[str, float] = {}
    for entry in registry.promotions:
        if entry.get("promoted"):
            dsr[entry["sector"]] = entry.get("dsr", 0.0)
    return dsr
