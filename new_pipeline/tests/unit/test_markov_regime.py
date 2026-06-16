import numpy as np
import pandas as pd
from new_pipeline.features.markov_regime import (
    MARKOV_FEATURE_NAMES,
    compute_rolling_markov_features,
)


def _price_frame(n: int = 160, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100.0 * np.exp(np.cumsum(rng.normal(0.0005, 0.01, n)))
    return pd.DataFrame(
        {
            "date": pd.date_range("2021-01-01", periods=n, freq="D"),
            "ticker": "AAA",
            "close": close,
        }
    )


def test_markov_features_added_and_bounded():
    df = compute_rolling_markov_features(_price_frame(), lookback=40, n_components=2)
    for name in MARKOV_FEATURE_NAMES:
        assert name in df.columns
    finite = df[list(MARKOV_FEATURE_NAMES)].to_numpy()
    finite = finite[~np.isnan(finite)]
    assert finite.size > 0
    assert (finite >= 0.0).all() and (finite <= 1.0).all()


def test_markov_is_causal_with_leading_nans():
    lookback = 40
    df = compute_rolling_markov_features(_price_frame(), lookback=lookback, n_components=2)
    # the window [i-lookback:i] excludes bar i, so nothing is computed before lookback
    assert df["markov_prob_persist_0"].iloc[:lookback].isna().all()


def test_sentiment_toggle_runs_both_paths():
    frame = _price_frame()
    frame["sentiment"] = np.linspace(-1.0, 1.0, len(frame))
    fused = compute_rolling_markov_features(frame, lookback=40, use_sentiment=True, n_components=2)
    plain = compute_rolling_markov_features(frame, lookback=40, use_sentiment=False, n_components=2)
    assert all(name in fused.columns for name in MARKOV_FEATURE_NAMES)
    assert all(name in plain.columns for name in MARKOV_FEATURE_NAMES)
