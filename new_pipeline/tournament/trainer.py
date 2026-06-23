"""XGBoost trainer for the tournament.

Targets the GPU in production (``device='cuda'`` + ``tree_method='hist'``) with
a one-line CPU fallback via config; trains with the asymmetric financial
objective. ``predict_proba`` applies the sigmoid the custom objective implies.
Early stopping is used when an eval set is supplied (a custom error metric is
needed because the custom objective has no built-in metric).
"""

import numpy as np
import xgboost as xgb

from new_pipeline.config import get_config
from new_pipeline.core.seeding import active_seed
from new_pipeline.tournament.objectives import asymmetric_loss_factory


def default_params(
    max_depth: int = 2,
    learning_rate: float = 0.05,
    device: str = "cpu",
    tree_method: str = "hist",
) -> dict:
    return {
        "max_depth": max_depth,
        "eta": learning_rate,
        "tree_method": tree_method,
        "device": device,
        "seed": active_seed(),
    }


def _error_metric(preds, dtrain):
    labels = dtrain.get_label()
    proba = 1.0 / (1.0 + np.exp(-preds))
    return "error", float(np.mean((proba > 0.5) != (labels > 0.5)))


def train_booster(
    features,
    labels,
    params=None,
    num_boost_round=100,
    penalty_fp=5.0,
    penalty_fn=1.0,
    eval_features=None,
    eval_labels=None,
    early_stopping_rounds=None,
    sample_weight=None,
):
    cfg = get_config().tournament
    if params is None:
        params = default_params(device=cfg.device, tree_method=cfg.tree_method)
    dtrain = xgb.DMatrix(
        np.asarray(features, dtype=np.float64),
        label=np.asarray(labels, dtype=np.float64),
        weight=None if sample_weight is None else np.asarray(sample_weight, dtype=np.float64),
    )
    objective = asymmetric_loss_factory(penalty_fp, penalty_fn)

    kwargs = {}
    if eval_features is not None and eval_labels is not None and early_stopping_rounds:
        dvalid = xgb.DMatrix(
            np.asarray(eval_features, dtype=np.float64),
            label=np.asarray(eval_labels, dtype=np.float64),
        )
        kwargs = {
            "evals": [(dvalid, "valid")],
            "custom_metric": _error_metric,
            "early_stopping_rounds": early_stopping_rounds,
            "verbose_eval": False,
        }
    return xgb.train(params, dtrain, num_boost_round=num_boost_round, obj=objective, **kwargs)


def predict_proba(booster, features) -> np.ndarray:
    margins = booster.predict(xgb.DMatrix(np.asarray(features, dtype=np.float64)))
    return 1.0 / (1.0 + np.exp(-margins))


def save_candidate(booster, path) -> None:
    booster.save_model(str(path))


def load_booster(path):
    booster = xgb.Booster()
    booster.load_model(str(path))
    return booster
