"""HMM observation construction for sentiment-fused regime detection.

Two small, dependency-light helpers shared by the macro regime evaluator
(:mod:`new_pipeline.evaluation.regime_dsr`) and the micro rolling-HMM feature
(:mod:`new_pipeline.features.markov_regime`):

* :func:`build_observation_matrix` stacks ``[returns, volatility, sentiment]``
  into a Gaussian-HMM observation matrix. Sentiment is shifted forward by
  ``sentiment_lag`` bars so the regime decoded at ``t`` is conditioned only on
  information available at ``t-1`` (strictly causal -- no look-ahead, principle
  G5). Columns are z-scored because a Gaussian HMM's means/covariances are
  scale-sensitive and raw returns (~1e-2) would otherwise be dominated by the
  sentiment column (~[-1, 1]).
* :func:`order_states_by_volatility` returns state indices sorted ascending by
  total variance, so "state 0" is always the low-vol regime -- a deterministic
  relabeling that replaces the legacy ``sorted_indices[4]`` no-op bug.
"""

from __future__ import annotations

import numpy as np


def build_observation_matrix(
    returns,
    volatility,
    sentiment,
    sentiment_lag: int = 1,
    standardize: bool = True,
) -> np.ndarray:
    """Stack ``[returns, volatility, sentiment]`` into a Gaussian-HMM observation
    matrix of shape ``(n_samples, 3)``.

    ``sentiment`` is shifted forward by ``sentiment_lag`` bars (causal); the
    leading values are filled with 0.0 (neutral). Remaining NaNs are zeroed. When
    ``standardize`` is set, each column is z-scored (constant columns are guarded).
    """
    s = np.asarray(sentiment, dtype=np.float64).copy()
    if sentiment_lag > 0:
        s = np.concatenate([np.zeros(sentiment_lag), s[:-sentiment_lag]])

    obs = np.column_stack(
        [
            np.asarray(returns, dtype=np.float64),
            np.asarray(volatility, dtype=np.float64),
            s,
        ]
    )
    obs = np.nan_to_num(obs, nan=0.0)

    if standardize:
        mu = obs.mean(axis=0)
        sd = obs.std(axis=0)
        sd[sd == 0.0] = 1.0  # guard constant columns
        obs = (obs - mu) / sd
    return obs


def order_states_by_volatility(covars) -> np.ndarray:
    """Return state indices sorted ascending by total variance, so state 0 is the
    low-vol regime. Handles ``diag`` ``(n_states, n_features)`` and ``full``
    ``(n_states, n_features, n_features)`` covariance layouts.
    """
    covars = np.asarray(covars, dtype=np.float64)
    if covars.ndim == 2:  # diag
        total_var = covars.sum(axis=1)
    else:  # full
        total_var = np.array([np.trace(c) for c in covars])
    return np.argsort(total_var)
