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
from new_pipeline.tournament.cpcv import CPCVSplitGenerator
from new_pipeline.tournament.simulator import sharpe_ratio, simulate_t1_returns
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


def _absolute_t1(t1_offset, n_samples: int) -> np.ndarray | None:
    """Convert per-row 'bars ahead to first touch' offsets into clamped absolute
    event-end positions. Clamping to n-1 only ever widens the purge (conservative)."""
    if t1_offset is None:
        return None
    offsets = np.nan_to_num(np.asarray(t1_offset, dtype=np.float64), nan=0.0).astype(np.int64)
    return np.minimum(np.arange(n_samples) + offsets, n_samples - 1)


def run_grid_search(features, labels, prices, grid=None, confidence_threshold=0.5, t1_offset=None):
    """``prices`` is a dict of equal-length 'close'/'low'/'atr' arrays.

    When ``t1_offset`` (per-row bars-to-first-touch from the labeller) is given,
    CPCV purges by the real label span. For each grid combo the phi combinatorial
    backtest paths are reconstructed; the combo's OOS series is their mean (which
    equals the canonical per-sample OOS average), and the champion's full path
    matrix rides along for the path-distribution Deflated-Sharpe gate.
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
    t1 = _absolute_t1(t1_offset, n)
    folds = splitter.split(n, t1=t1)
    combo_groups = splitter.combinations()
    bounds = splitter.group_bounds(n)
    combos = [dict(zip(grid, values, strict=True)) for values in itertools.product(*grid.values())]

    rows: list[np.ndarray] = []
    sharpes: list[float] = []
    champion_paths: np.ndarray | None = None
    best_sharpe = -np.inf
    for combo in combos:
        segments: dict[tuple[int, int], np.ndarray] = {}
        for combo_index, (fold, test_groups) in enumerate(zip(folds, combo_groups, strict=True)):
            train_idx, test_idx = fold
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
            )
            proba = predict_proba(booster, features[test_idx])
            signals = (proba > confidence_threshold).astype(np.int64)
            fold_returns = simulate_t1_returns(
                signals,
                prices["close"][test_idx],
                prices["low"][test_idx],
                prices["atr"][test_idx],
                cfg.execution.atr_stop_multiplier,
                cfg.execution.max_risk_per_trade,
            )
            for g in test_groups:  # split the fold's returns back to per-group segments
                gstart, gend = bounds[g]
                segments[(combo_index, g)] = fold_returns[(test_idx >= gstart) & (test_idx <= gend)]
        paths = splitter.assemble_paths(n, segments)
        oos = paths.mean(axis=0)  # == canonical per-sample OOS average across folds
        rows.append(oos)
        sharpe = sharpe_ratio(oos)
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
    )
