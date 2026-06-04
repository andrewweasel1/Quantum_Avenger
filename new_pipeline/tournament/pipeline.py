"""Offline end-to-end pipeline orchestration (Phase 3 glue).

Assembles the full chain with no network: synthetic market data -> vectorized
features -> sector join + friction labels -> per-sector tournament -> Deflated
Sharpe + HMM promotion. The legacy multi-phase ``main`` flow, rebuilt offline.
"""

from datetime import date
from pathlib import Path

import numpy as np
import polars as pl

from new_pipeline.adapters import FakeMarketDataSource, StaticUniverseProvider
from new_pipeline.config import get_config
from new_pipeline.evaluation.dsr import compute_deflated_sharpe_ratio
from new_pipeline.evaluation.hmm_gauntlet import run_hmm_synthetic_gauntlet
from new_pipeline.evaluation.promotion import PromotionRegistry, assess_promotion
from new_pipeline.features.labels import add_labels
from new_pipeline.features.polars_engine import compile_features
from new_pipeline.tournament.director import run_sector_tournament
from new_pipeline.tournament.trainer import load_booster, predict_proba

FEATURE_COLS = [
    "returns", "atr", "adv_20", "volatility", "spread_pct", "roll_spread",
    "amihud", "ncskew", "duvol",
]


def build_training_frame(symbols, sectors, start, end, source=None, cfg=None) -> pl.DataFrame:
    """Synthetic OHLCV -> features -> sector join + target_label, one frame."""
    source = source or FakeMarketDataSource()
    cfg = cfg or get_config()
    rows = [
        {
            "date": bar.day, "ticker": symbol, "open": bar.open, "high": bar.high,
            "low": bar.low, "close": bar.close, "volume": bar.volume,
        }
        for symbol in symbols
        for bar in source.history(symbol, start, end)
    ]
    features = compile_features(pl.DataFrame(rows))
    labeled = add_labels(features, cfg.features.label_horizon, cfg.features.label_cost_bps)
    sector_df = pl.DataFrame(
        {"ticker": list(sectors), "sector": [sectors[t] for t in sectors]}
    )
    return labeled.join(sector_df, on="ticker", how="left")


def run_offline_pipeline(
    output_dir, start=date(2021, 1, 1), end=date(2022, 12, 31), max_symbols=None, source=None
) -> dict:
    cfg = get_config()
    sectors = StaticUniverseProvider().sectors()
    symbols = list(sectors)[: max_symbols] if max_symbols else list(sectors)
    frame = build_training_frame(symbols, sectors, start, end, source, cfg)
    results = run_sector_tournament(frame, FEATURE_COLS, output_dir)
    promotions = _evaluate_and_promote(frame, results, output_dir, cfg)
    return {"sectors": list(results), "promotions": promotions}


def _evaluate_and_promote(frame: pl.DataFrame, results: dict, output_dir, cfg) -> dict:
    registry = PromotionRegistry(Path(output_dir) / "promotion_registry.json")
    decisions: dict[str, bool] = {}
    for sector, result in results.items():
        trials = result["trial_sharpes"]
        if not trials:
            continue
        best = int(np.argmax(trials))
        returns_matrix = pl.read_parquet(result["candidate_path"].replace(
            "_candidate.json", "_returns_matrix.parquet"
        ))
        champion_returns = returns_matrix[:, best].to_numpy()

        dsr = compute_deflated_sharpe_ratio(champion_returns, trials)
        synthetic_sr = _synthetic_sharpe(frame, sector, result, champion_returns)
        decision = assess_promotion(
            sector, dsr, synthetic_sr,
            cfg.evaluation.dsr_promotion_threshold, cfg.evaluation.synthetic_sr_min,
        )
        model_path = result["candidate_path"] if decision.promoted else None
        registry.record(decision, model_path=model_path)
        decisions[sector] = decision.promoted
    return decisions


def _synthetic_sharpe(frame, sector, result, champion_returns) -> float:
    booster = load_booster(result["candidate_path"])
    features = (
        frame.filter(pl.col("sector") == sector)
        .with_columns(pl.col(result["selected_features"]).fill_nan(None))
        .drop_nulls(subset=result["selected_features"])
        .select(result["selected_features"])
        .to_numpy()
    )
    if features.shape[0] < 10:
        return 0.0
    return run_hmm_synthetic_gauntlet(
        champion_returns, features, lambda matrix: predict_proba(booster, matrix), n_iter=20
    )
