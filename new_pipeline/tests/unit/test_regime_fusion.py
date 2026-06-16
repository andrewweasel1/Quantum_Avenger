import numpy as np
from new_pipeline.features.regime_fusion import (
    build_observation_matrix,
    order_states_by_volatility,
)


def test_observation_matrix_shape():
    n = 50
    rng = np.random.default_rng(0)
    obs = build_observation_matrix(
        rng.normal(size=n), np.abs(rng.normal(size=n)), rng.normal(size=n),
        sentiment_lag=0, standardize=False,
    )
    assert obs.shape == (n, 3)


def test_sentiment_is_lagged_causally():
    sent = np.arange(1.0, 6.0)  # [1, 2, 3, 4, 5]
    obs = build_observation_matrix(
        np.zeros(5), np.zeros(5), sent, sentiment_lag=1, standardize=False
    )
    # leading bar filled neutral, rest shifted forward one bar (no look-ahead)
    assert list(obs[:, 2]) == [0.0, 1.0, 2.0, 3.0, 4.0]


def test_standardize_gives_zero_mean_unit_std():
    rng = np.random.default_rng(3)
    obs = build_observation_matrix(
        rng.normal(size=500), rng.normal(size=500), rng.normal(size=500),
        sentiment_lag=0, standardize=True,
    )
    assert np.allclose(obs.mean(axis=0), 0.0, atol=1e-9)
    assert np.allclose(obs.std(axis=0), 1.0, atol=1e-9)


def test_nans_are_zeroed():
    obs = build_observation_matrix(
        np.zeros(3), np.zeros(3), np.array([1.0, np.nan, 3.0]),
        sentiment_lag=0, standardize=False,
    )
    assert not np.isnan(obs).any()


def test_order_states_by_volatility_diag():
    covars = np.array([[3.0, 0.0], [0.5, 0.5], [2.0, 0.0]])  # total variance 3, 1, 2
    assert list(order_states_by_volatility(covars)) == [1, 2, 0]


def test_order_states_by_volatility_full():
    full = np.array([np.diag([3.0, 0.0]), np.diag([0.5, 0.5]), np.diag([2.0, 0.0])])
    assert list(order_states_by_volatility(full)) == [1, 2, 0]  # traces 3, 1, 2
