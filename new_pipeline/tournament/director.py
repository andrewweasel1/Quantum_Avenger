"""Per-sector tournament director — the Phase 3 end-to-end orchestration.

For each sector in the processed feature frame it (optionally) prunes features
with Clustered Feature Selection, runs the CPCV grid search, trains an
early-stopped candidate, and writes the candidate booster + feature manifest +
returns matrix under the candidates directory. Sectors are independent, so they
run in parallel on a thread pool (XGBoost releases the GIL during training) when
``max_workers > 1``. Restores the legacy ``execute_gauntlet`` loop.
"""

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

import numpy as np
import polars as pl

from new_pipeline.config import get_config
from new_pipeline.core.exceptions import CPCVSplitError
from new_pipeline.core.seeding import active_seed
from new_pipeline.tournament.causal_selection import select_causal_features
from new_pipeline.tournament.cpcv import CPCVSplitGenerator, absolute_t1
from new_pipeline.tournament.feature_selection import select_orthogonal_features
from new_pipeline.tournament.grid_search import run_grid_search
from new_pipeline.tournament.meta_labeling import (
    MIN_FIRED_TEST,
    primary_signal,
    run_meta_labeling,
)
from new_pipeline.tournament.sample_weights import uniqueness_sample_weights
from new_pipeline.tournament.simulator import sharpe_ratio, simulate_t1_returns_blockwise
from new_pipeline.tournament.trainer import predict_proba, save_candidate, train_booster

_PRICE_COLUMNS = ("close", "low", "atr")
_MIN_ROWS = 40
_META_MIN_TRAIN = 30  # need a workable 80/20 split before meta-labeling


def _slug(sector: str) -> str:
    return sector.lower().replace(" ", "_").replace("/", "_")


def _sharpe_score_fn(labels, prices, cfg, block_ids=None):
    """A score_fn(feature_matrix) -> Sharpe used for CFS permutation importance."""
    rounds = min(40, cfg.tournament.num_boost_round)
    ids = np.zeros(len(labels)) if block_ids is None else block_ids

    def score(matrix):
        booster = train_booster(
            matrix,
            labels,
            num_boost_round=rounds,
            penalty_fp=cfg.tournament.penalty_fp,
            penalty_fn=cfg.tournament.penalty_fn,
        )
        proba = predict_proba(booster, matrix)
        signals = (proba > cfg.execution.confidence_threshold).astype(np.int64)
        returns = simulate_t1_returns_blockwise(
            signals,
            prices["close"],
            prices["low"],
            prices["atr"],
            ids,
            cfg.execution.atr_stop_multiplier,
            cfg.execution.max_risk_per_trade,
        )
        return sharpe_ratio(returns)

    return score


def _mda_fit_fn(cfg):
    """fit_fn(train_X, train_y) -> predict(test_X) for purged-CPCV MDA importance."""
    rounds = min(40, cfg.tournament.num_boost_round)
    threshold = cfg.execution.confidence_threshold

    def fit(train_x, train_y):
        booster = train_booster(
            train_x,
            train_y,
            num_boost_round=rounds,
            penalty_fp=cfg.tournament.penalty_fp,
            penalty_fn=cfg.tournament.penalty_fn,
        )
        return lambda test_x: (predict_proba(booster, test_x) > threshold).astype(np.int64)

    return fit


def _meta_fit_fn(cfg):
    """fit(X, y, sample_weight) -> predict(X) -> P(win): the secondary meta model."""
    rounds = min(40, cfg.tournament.num_boost_round)

    def fit(features, outcomes, weight=None):
        booster = train_booster(
            features,
            outcomes,
            num_boost_round=rounds,
            penalty_fp=cfg.tournament.penalty_fp,
            penalty_fn=cfg.tournament.penalty_fn,
            sample_weight=weight,
        )
        return lambda test_x: predict_proba(booster, test_x)

    return fit


def _meta_labeling(matrix, labels, t1_offset, block_ids, cfg):
    """Train a primary on the train split, a meta model on its fired bars, and return
    the OOS primary-vs-meta verdict (+ fired counts), or None when the split is too thin."""
    n = len(labels)
    split = int(n * 0.8)
    if split < _META_MIN_TRAIN or n - split < MIN_FIRED_TEST:
        return None
    rounds = min(40, cfg.tournament.num_boost_round)
    threshold = cfg.execution.confidence_threshold
    train_x, test_x = matrix[:split], matrix[split:]
    train_y, test_y = labels[:split], labels[split:]
    primary = train_booster(
        train_x, train_y, num_boost_round=rounds,
        penalty_fp=cfg.tournament.penalty_fp, penalty_fn=cfg.tournament.penalty_fn,
    )
    train_sig = primary_signal(predict_proba(primary, train_x), threshold)
    test_sig = primary_signal(predict_proba(primary, test_x), threshold)
    weights = None
    if t1_offset is not None and cfg.tournament.sample_weighting == "uniqueness":
        weights = uniqueness_sample_weights(absolute_t1(t1_offset, n, block_ids))[:split]
    result = run_meta_labeling(
        train_x, train_y, test_x, test_y, train_sig, test_sig,
        _meta_fit_fn(cfg), cfg.tournament.meta_threshold, cfg.tournament.meta_criterion, weights,
    )
    if result is None:
        return None
    verdict, _ = result
    return {
        **asdict(verdict),
        "n_fired_train": int((train_sig == 1).sum()),
        "n_fired_test": int((test_sig == 1).sum()),
    }


def _select_causal(clean, feature_cols, matrix, labels, prices, t1_offset, cfg, block_ids=None):
    """Granger + purged-CPCV-MDA selection, falling back to the correlational
    selector if the CPCV split is infeasible (too few rows)."""
    splitter = CPCVSplitGenerator(
        n_groups=cfg.tournament.n_groups,
        test_groups=cfg.tournament.test_groups,
        purge=cfg.tournament.purge_days,
        embargo=cfg.tournament.embargo_days,
        embargo_pct=cfg.tournament.embargo_pct,
    )
    try:
        return select_causal_features(
            matrix,
            list(feature_cols),
            clean["fwd_ret"].to_numpy().astype(np.float64),
            labels,
            _mda_fit_fn(cfg),
            splitter,
            t1=absolute_t1(t1_offset, len(labels), block_ids),
            lags=cfg.tournament.causal_granger_lags,
            horizon=cfg.features.label_horizon,
            causal_alpha=cfg.tournament.causal_alpha,
            mt_method=cfg.evaluation.mt_method,
            distance_threshold=cfg.tournament.cfs_distance_threshold,
            min_importance=cfg.tournament.cfs_min_importance,
            seed=active_seed(),
        )
    except CPCVSplitError:
        return select_orthogonal_features(
            matrix,
            list(feature_cols),
            _sharpe_score_fn(labels, prices, cfg, block_ids),
            distance_threshold=cfg.tournament.cfs_distance_threshold,
            min_importance=cfg.tournament.cfs_min_importance,
            seed=active_seed(),
        )


def run_sector_tournament(frame, feature_cols, output_dir, use_cfs=True, max_workers=None):
    """Run the tournament per sector; returns a {sector: result} summary dict."""
    cfg = get_config()
    workers = max_workers if max_workers is not None else cfg.tournament.max_workers
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    required = [*feature_cols, "target_label", *_PRICE_COLUMNS]
    if cfg.tournament.feature_selection_method == "causal":
        required += [c for c in ("fwd_ret", "label_t1_offset") if c in frame.columns]

    sectors = []
    for _, group in frame.group_by("sector", maintain_order=True):
        # Polars treats NaN as distinct from null; coerce so rolling/label NaNs drop.
        clean = group.with_columns(pl.col(required).fill_nan(None)).drop_nulls(subset=required)
        if clean.height >= _MIN_ROWS:
            sectors.append(clean)

    def work(clean):
        return _process_sector(clean, feature_cols, output, cfg, use_cfs)

    if workers and workers > 1 and len(sectors) > 1:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            outcomes = list(pool.map(work, sectors))
    else:
        outcomes = [work(clean) for clean in sectors]
    return {sector: result for sector, result in outcomes}


def _process_sector(clean, feature_cols, output, cfg, use_cfs):
    sector = clean["sector"][0]
    labels = clean["target_label"].to_numpy().astype(np.float64)
    prices = {col: clean[col].to_numpy().astype(np.float64) for col in _PRICE_COLUMNS}
    t1_offset = clean["label_t1_offset"].to_numpy() if "label_t1_offset" in clean.columns else None
    # Per-ticker run ids: cap label spans / t+1 sim at ticker boundaries (no cross-ticker leak).
    block_ids = clean["ticker"].rle_id().to_numpy() if "ticker" in clean.columns else None
    matrix = clean.select(feature_cols).to_numpy()

    selected = list(feature_cols)
    if use_cfs and matrix.shape[1] > 1:
        if cfg.tournament.feature_selection_method == "causal" and "fwd_ret" in clean.columns:
            selected = _select_causal(
                clean, feature_cols, matrix, labels, prices, t1_offset, cfg, block_ids
            )
        else:
            selected = select_orthogonal_features(
                matrix,
                list(feature_cols),
                _sharpe_score_fn(labels, prices, cfg, block_ids),
                distance_threshold=cfg.tournament.cfs_distance_threshold,
                min_importance=cfg.tournament.cfs_min_importance,
                seed=active_seed(),
            )
    selected_matrix = clean.select(selected).to_numpy()

    search = run_grid_search(
        selected_matrix, labels, prices, t1_offset=t1_offset, block_ids=block_ids
    )
    booster = _train_candidate(selected_matrix, labels, cfg, t1_offset, block_ids)
    meta = (
        _meta_labeling(selected_matrix, labels, t1_offset, block_ids, cfg)
        if cfg.tournament.enable_meta_labeling
        else None
    )
    return sector, _persist(output, sector, booster, selected, search, meta)


def _train_candidate(matrix, labels, cfg, t1_offset=None, block_ids=None):
    n = len(labels)
    split = int(n * 0.8)
    use_eval = n - split >= 10
    train_n = split if use_eval else n
    weights = None
    if t1_offset is not None and cfg.tournament.sample_weighting == "uniqueness":
        weights = uniqueness_sample_weights(absolute_t1(t1_offset, n, block_ids))[:train_n]
    return train_booster(
        matrix[:split] if use_eval else matrix,
        labels[:split] if use_eval else labels,
        num_boost_round=cfg.tournament.num_boost_round,
        penalty_fp=cfg.tournament.penalty_fp,
        penalty_fn=cfg.tournament.penalty_fn,
        eval_features=matrix[split:] if use_eval else None,
        eval_labels=labels[split:] if use_eval else None,
        early_stopping_rounds=cfg.tournament.early_stopping_rounds,
        sample_weight=weights,
    )


def _persist(output: Path, sector: str, booster, selected, search, meta=None) -> dict:
    slug = _slug(sector)
    candidate_path = output / f"{slug}_candidate.json"
    features_path = output / f"{slug}_candidate_features.json"
    returns_path = output / f"{slug}_returns_matrix.parquet"

    save_candidate(booster, candidate_path)
    features_path.write_text(
        json.dumps(
            {
                "features": selected,
                "metadata": {
                    "sector": sector, "params": search.best_params, "meta_labeling": meta
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    matrix = search.returns_matrix
    pl.DataFrame(
        matrix.T, schema=[f"trial_{i}" for i in range(matrix.shape[0])]
    ).write_parquet(returns_path)
    if search.paths is not None and search.paths.size:
        paths = search.paths
        pl.DataFrame(
            paths.T, schema=[f"path_{i}" for i in range(paths.shape[0])]
        ).write_parquet(output / f"{slug}_paths.parquet")

    return {
        "selected_features": selected,
        "best_params": search.best_params,
        "best_sharpe": search.best_sharpe,
        "trial_sharpes": search.trial_sharpes,
        "candidate_path": str(candidate_path),
        "meta_labeling": meta,
    }
