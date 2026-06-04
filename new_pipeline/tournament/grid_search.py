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


def run_grid_search(features, labels, prices, grid=None, confidence_threshold=0.5):
    """``prices`` is a dict of equal-length 'close'/'low'/'atr' arrays."""
    cfg = get_config()
    grid = grid or _DEFAULT_GRID
    splitter = CPCVSplitGenerator(
        n_groups=cfg.tournament.n_groups,
        test_groups=cfg.tournament.test_groups,
        purge=cfg.tournament.purge_days,
        embargo=cfg.tournament.embargo_days,
    )
    folds = splitter.split(len(labels))
    combos = [dict(zip(grid, values, strict=True)) for values in itertools.product(*grid.values())]

    rows: list[np.ndarray] = []
    sharpes: list[float] = []
    for combo in combos:
        oos_sum = np.zeros(len(labels), dtype=np.float64)
        oos_count = np.zeros(len(labels), dtype=np.float64)
        for train_idx, test_idx in folds:
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
            oos_sum[test_idx] += fold_returns
            oos_count[test_idx] += 1.0
        oos = np.where(oos_count > 0.0, oos_sum / np.maximum(oos_count, 1.0), 0.0)
        rows.append(oos)
        sharpes.append(sharpe_ratio(oos))

    matrix = np.vstack(rows)
    best = int(np.argmax(sharpes))
    return GridSearchResult(
        best_params=combos[best],
        best_sharpe=sharpes[best],
        returns_matrix=matrix,
        trial_sharpes=sharpes,
    )
