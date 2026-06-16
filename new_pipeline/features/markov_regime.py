"""Rolling micro-regime feature: per-asset Markov transition persistence.

Adds two XGBoost features -- ``markov_prob_persist_0`` and
``markov_prob_persist_1`` -- the diagonal of a short rolling Gaussian-HMM's
transition matrix (the probability the low- / high-vol state persists). When
``use_sentiment`` is set and a sentiment column is present, the HMM observes the
fused ``[returns, volatility, sentiment]`` space from
:func:`new_pipeline.features.regime_fusion.build_observation_matrix`.

Causality (G5): the window slice ``[i-lookback : i]`` excludes bar ``i``, so each
feature row is fit on strictly prior data and cannot see its own bar's future.
The per-window EM fit is the project's one sanctioned time-series loop -- hmmlearn
has no vectorized rolling HMM (the only other sanctioned loop is batched model
inference).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from hmmlearn import hmm

from new_pipeline.features.regime_fusion import (
    build_observation_matrix,
    order_states_by_volatility,
)

MARKOV_FEATURE_NAMES = ("markov_prob_persist_0", "markov_prob_persist_1")
_SENTIMENT_COLUMNS = ("sentiment", "sentiment_score")


def _sentiment_series(df: pd.DataFrame, use_sentiment: bool, n: int) -> np.ndarray:
    if not use_sentiment:
        return np.zeros(n)
    for column in _SENTIMENT_COLUMNS:
        if column in df.columns:
            return df[column].fillna(0.0).to_numpy(dtype=np.float64)
    return np.zeros(n)


def compute_rolling_markov_features(
    df: pd.DataFrame,
    lookback: int = 60,
    use_sentiment: bool = True,
    n_components: int = 2,
) -> pd.DataFrame:
    """Append rolling Gaussian-HMM persistence probabilities to one ticker's frame.

    The frame must be sorted by date and carry a ``close`` column. Sentiment is
    fused when ``use_sentiment`` is set and a ``sentiment``/``sentiment_score``
    column exists; otherwise the observation space is ``[returns, volatility]``
    with a neutral (zero) sentiment column.
    """
    n = len(df)
    p_low = np.full(n, np.nan)
    p_high = np.full(n, np.nan)

    returns = np.log(df["close"] / df["close"].shift(1)).fillna(0.0).to_numpy()
    volatility = pd.Series(returns).rolling(10).std().fillna(0.0).to_numpy()
    sentiment = _sentiment_series(df, use_sentiment, n)

    # standardize per-window below, not globally
    obs_full = build_observation_matrix(
        returns, volatility, sentiment, sentiment_lag=0, standardize=False
    )

    for i in range(lookback, n):
        window = obs_full[i - lookback : i]  # excludes bar i -> strictly causal
        mu, sd = window.mean(0), window.std(0)
        sd[sd == 0.0] = 1.0  # per-window z-score so the HMM is conditioned, not scaled
        window = (window - mu) / sd

        model = hmm.GaussianHMM(
            n_components=n_components, covariance_type="diag", n_iter=15, tol=1e-2
        )
        try:
            model.fit(window)
            order = order_states_by_volatility(model.covars_)  # ascending variance
            lo, hi = order[0], order[-1]
            p_low[i] = model.transmat_[lo, lo]  # P(low-vol persists)
            p_high[i] = model.transmat_[hi, hi]  # P(high-vol persists)
        except Exception:  # EM failed to converge on this window -> leave NaN
            continue

    out = df.copy()
    out["markov_prob_persist_0"] = pd.Series(p_low, index=df.index).ffill()
    out["markov_prob_persist_1"] = pd.Series(p_high, index=df.index).ffill()
    return out


def add_markov_regime_features(
    frame,
    lookback: int = 60,
    use_sentiment: bool = True,
    n_components: int = 2,
):
    """Polars wrapper: apply :func:`compute_rolling_markov_features` per ticker.

    Bridges to pandas for the per-window EM loop (hmmlearn is pandas/NumPy) and
    returns a Polars frame with the two ``markov_prob_persist_*`` columns added.
    """
    import polars as pl

    pdf = frame.to_pandas()
    parts = [
        compute_rolling_markov_features(
            group.sort_values("date").reset_index(drop=True),
            lookback=lookback,
            use_sentiment=use_sentiment,
            n_components=n_components,
        )
        for _, group in pdf.groupby("ticker", sort=False)
    ]
    if not parts:
        return frame
    return pl.from_pandas(pd.concat(parts, ignore_index=True))
