"""HMM synthetic-data gauntlet: does the model survive regimes it never saw?

Fit a 3-state Gaussian HMM to benchmark returns, sample a *synthetic* return
path, evaluate the model's signals on bootstrapped feature rows (whole rows, to
preserve cross-feature correlation — the legacy bug resampled per column), and
require a positive Sharpe on the synthetic path.
"""

import numpy as np
from hmmlearn.hmm import GaussianHMM

from new_pipeline.core.seeding import active_seed
from new_pipeline.tournament.simulator import sharpe_ratio


def fit_regime_hmm(benchmark_returns, n_states=3, n_iter=100, seed=None):
    series = np.asarray(benchmark_returns, dtype=np.float64).reshape(-1, 1)
    model = GaussianHMM(
        n_components=n_states,
        covariance_type="full",
        n_iter=n_iter,
        random_state=active_seed() if seed is None else seed,
    )
    model.fit(series)
    return model


def run_hmm_synthetic_gauntlet(
    benchmark_returns,
    features,
    predict_fn,
    n_states=3,
    n_iter=100,
    confidence_threshold=0.5,
    seed=None,
):
    """``predict_fn`` maps a feature matrix to per-row probabilities."""
    rng_seed = active_seed() if seed is None else seed
    model = fit_regime_hmm(benchmark_returns, n_states, n_iter, rng_seed)

    n_samples = len(benchmark_returns)
    synthetic_returns, _ = model.sample(n_samples, random_state=rng_seed)
    synthetic_returns = synthetic_returns.ravel()

    feature_matrix = np.asarray(features, dtype=np.float64)
    rng = np.random.default_rng(rng_seed)
    rows = rng.integers(0, feature_matrix.shape[0], size=n_samples)  # whole-row bootstrap
    sampled = feature_matrix[rows]

    proba = np.asarray(predict_fn(sampled), dtype=np.float64)
    signals = (proba > confidence_threshold).astype(np.float64)
    return sharpe_ratio(signals * synthetic_returns)
