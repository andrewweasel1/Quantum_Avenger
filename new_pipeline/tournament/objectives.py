"""Custom XGBoost objective: asymmetric financial loss.

False positives (wrong buys that lose capital) are penalized ``penalty_fp``x
relative to false negatives (missed trades). Gradient/Hessian are the standard
logistic ones scaled by the per-sample penalty, and — because a custom objective
bypasses XGBoost's built-in weighting — by the ``DMatrix`` sample weights when
present (the López de Prado uniqueness weights for overlapping labels).
"""

import numpy as np


def asymmetric_financial_loss(preds, dtrain, penalty_fp=5.0, penalty_fn=1.0):
    """XGBoost objective -> (grad, hess). ``preds`` are raw margins."""
    labels = dtrain.get_label()
    proba = 1.0 / (1.0 + np.exp(-preds))
    weight = np.where(labels == 0.0, penalty_fp, penalty_fn)
    sample_weight = dtrain.get_weight()
    if sample_weight.size == labels.size:  # fold in uniqueness weights if supplied
        weight = weight * sample_weight
    grad = (proba - labels) * weight
    hess = proba * (1.0 - proba) * weight
    return grad, hess


def asymmetric_loss_factory(penalty_fp=5.0, penalty_fn=1.0):
    """Return a 2-arg XGBoost objective with the given penalties bound."""

    def _objective(preds, dtrain):
        return asymmetric_financial_loss(preds, dtrain, penalty_fp, penalty_fn)

    return _objective
