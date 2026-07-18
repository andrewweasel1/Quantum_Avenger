"""Per-sector hyperparameter grid search over CPCV folds.

For each parameter combo, trains across all CPCV folds, simulates t+1 returns on
each out-of-sample test fold (via the Shield-consistent simulator), and scores
by out-of-sample Sharpe. Returns the best combo plus the stacked OOS returns
matrix (one row per combo) consumed downstream by the Deflated Sharpe Ratio.
"""

import itertools
from dataclasses import dataclass, field

import numpy as np

from new_pipeline.config import get_config
from new_pipeline.tournament.accounting import collapse_to_daily
from new_pipeline.tournament.cpcv import CPCVSplitGenerator, absolute_t1
from new_pipeline.tournament.meta_labeling import MIN_FIRED_TRAIN, meta_filtered_signal
from new_pipeline.tournament.sample_weights import uniqueness_sample_weights
from new_pipeline.tournament.simulator import sharpe_ratio, simulate_t1_returns_blockwise
from new_pipeline.tournament.trainer import default_params, predict_proba, train_booster

_DEFAULT_GRID = {"max_depth": [1, 2], "learning_rate": [0.01, 0.05]}


@dataclass
class GridSearchResult:
    best_params: dict
    best_sharpe: float
    returns_matrix: np.ndarray  # shape (n_trials, n_samples)
    trial_sharpes: list[float] = field(default_factory=list)
    paths: np.ndarray | None = None  # champion CPCV backtest paths (phi, n_samples)
    path_count: int = 0
    # Genuine OOS predicted probabilities, stitched exactly like the return
    # paths: (n_trials, phi, n_samples). Row [j, p, i] is combo j's OOS proba
    # for sample i on CPCV path p; mean over axis 1 is the bagged per-sample
    # OOS proba. Consumed by the cross-sectional long-short sleeve.
    proba_paths: np.ndarray | None = None


def _fit_fold_meta(booster, features, labels, train_idx, weights, threshold, cfg):
    """Meta model for ONE CPCV fold: trained only on the fold's FIRED train rows
    (``train_idx`` is already span-purged/embargoed, so filtering test signals
    with it is leakage-safe). Returns a ``predict(X) -> P(win)`` or None when
    too few rows fire or the fired outcomes are single-class.

    The captured ``proba_segments`` stay the RAW primary beliefs either way —
    the long-short sleeve ranks beliefs; meta gating is an entry concept."""
    train_proba = predict_proba(booster, features[train_idx])
    fired = train_proba > threshold
    outcomes = labels[train_idx][fired]
    if fired.sum() < MIN_FIRED_TRAIN or np.unique(outcomes).size < 2:
        return None
    meta_booster = train_booster(
        features[train_idx][fired],
        outcomes,
        num_boost_round=min(40, cfg.tournament.num_boost_round),
        penalty_fp=cfg.tournament.penalty_fp,
        penalty_fn=cfg.tournament.penalty_fn,
        sample_weight=None if weights is None else weights[train_idx][fired],
    )
    return lambda x: predict_proba(meta_booster, x)


def run_grid_search(
    features, labels, prices, grid=None, confidence_threshold=0.5, t1_offset=None,
    block_ids=None, dates=None,
):
    """``prices`` is a dict of equal-length 'close'/'low'/'atr' arrays.

    When ``t1_offset`` (per-row bars-to-first-touch from the labeller) is given,
    CPCV purges by the real label span. For each grid combo the phi combinatorial
    backtest paths are reconstructed; the combo's OOS series is their mean (which
    equals the canonical per-sample OOS average), and the champion's full path
    matrix rides along for the path-distribution Deflated-Sharpe gate.

    When ``dates`` (per-row sample dates) is given, each combo is SCORED on its
    equal-weight calendar-daily series rather than the pooled samples. Selection
    must happen on the same axis the promotion gates evaluate — and the persisted
    champion paths belong to this argmax, so a downstream re-rank could orphan
    them. The pooled per-sample rows are still returned in ``returns_matrix``
    (they are the artifact; consumers collapse them as needed).
    """
    cfg = get_config()
    grid = grid or _DEFAULT_GRID
    splitter = CPCVSplitGenerator(
        n_groups=cfg.tournament.n_groups,
        test_groups=cfg.tournament.test_groups,
        purge=cfg.tournament.purge_days,
        embargo=cfg.tournament.embargo_days,
        embargo_pct=cfg.tournament.embargo_pct,
    )
    n = len(labels)
    t1 = absolute_t1(t1_offset, n, block_ids)
    weights = (
        uniqueness_sample_weights(t1)
        if t1 is not None and cfg.tournament.sample_weighting == "uniqueness"
        else None
    )
    folds = splitter.split(n, t1=t1)
    combo_groups = splitter.combinations()
    bounds = splitter.group_bounds(n)
    combos = [dict(zip(grid, values, strict=True)) for values in itertools.product(*grid.values())]

    rows: list[np.ndarray] = []
    sharpes: list[float] = []
    champion_paths: np.ndarray | None = None
    proba_paths_per_combo: list[np.ndarray] = []
    best_sharpe = -np.inf
    for combo in combos:
        segments: dict[tuple[int, int], np.ndarray] = {}
        proba_segments: dict[tuple[int, int], np.ndarray] = {}
        for combo_index, (fold, test_groups) in enumerate(zip(folds, combo_groups, strict=True)):
            train_idx, _ = fold
            params = default_params(
                max_depth=combo["max_depth"],
                learning_rate=combo["learning_rate"],
                device=cfg.tournament.device,
                tree_method=cfg.tournament.tree_method,
            )
            booster = train_booster(
                features[train_idx],
                labels[train_idx],
                params=params,
                num_boost_round=cfg.tournament.num_boost_round,
                penalty_fp=cfg.tournament.penalty_fp,
                penalty_fn=cfg.tournament.penalty_fn,
                sample_weight=None if weights is None else weights[train_idx],
            )
            meta_predict = (
                _fit_fold_meta(booster, features, labels, train_idx, weights,
                               confidence_threshold, cfg)
                if cfg.tournament.enable_meta_labeling
                else None
            )
            # Simulate each test group on its own contiguous block, block-wise per
            # ticker, so a trade's t+1 never crosses a group OR ticker boundary.
            for g in test_groups:
                gstart, gend = bounds[g]
                block = slice(gstart, gend + 1)
                proba = predict_proba(booster, features[block])
                proba_segments[(combo_index, g)] = proba  # OOS beliefs, kept raw
                signals = (proba > confidence_threshold).astype(np.int64)
                if meta_predict is not None:  # meta veto: act only when both agree
                    signals = meta_filtered_signal(
                        signals, meta_predict(features[block]), cfg.tournament.meta_threshold
                    )
                group_ids = np.zeros(gend - gstart + 1) if block_ids is None else block_ids[block]
                segments[(combo_index, g)] = simulate_t1_returns_blockwise(
                    signals,
                    prices["close"][block],
                    prices["low"][block],
                    prices["atr"][block],
                    group_ids,
                    cfg.execution.atr_stop_multiplier,
                    cfg.execution.max_risk_per_trade,
                )
        paths = splitter.assemble_paths(n, segments)
        proba_paths_per_combo.append(splitter.assemble_paths(n, proba_segments))
        oos = paths.mean(axis=0)  # == canonical per-sample OOS average across folds
        rows.append(oos)
        # ANNUALIZED (sharpe_ratio x sqrt(252)) — reporting/selection units.
        # Deflation statistics consume these via _per_period_trials, which
        # de-annualizes; never feed them to a DSR benchmark raw.
        sharpe = sharpe_ratio(oos if dates is None else collapse_to_daily(dates, oos)[1])
        sharpes.append(sharpe)
        if sharpe > best_sharpe:
            best_sharpe, champion_paths = sharpe, paths

    matrix = np.vstack(rows)
    best = int(np.argmax(sharpes))
    return GridSearchResult(
        best_params=combos[best],
        best_sharpe=sharpes[best],
        returns_matrix=matrix,
        trial_sharpes=sharpes,
        paths=champion_paths,
        path_count=splitter.path_count,
        proba_paths=np.stack(proba_paths_per_combo),
    )
