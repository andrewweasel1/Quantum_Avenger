"""HMM synthetic-data gauntlet: does the model survive regimes it never saw?

Fit a 3-state Gaussian HMM to the benchmark returns, sample a *synthetic* return
path (the HMM carries regime/volatility autocorrelation), run the model's signals
on a **stationary block-bootstrapped** feature path, and require a positive Sharpe.

The feature rows are drawn with a Politis–Romano stationary bootstrap — contiguous,
geometrically-sized blocks of whole rows — so the synthetic feature sequence keeps
both its cross-feature correlation (whole rows; the legacy per-column resample was
a bug) *and* its temporal autocorrelation (blocks; an IID row bootstrap destroyed
it). Features and the HMM-sampled returns are independent, so this is a
regime-robustness gate (the model must not bleed under unseen regimes), not a
skill test.
"""

import numpy as np
from hmmlearn.hmm import GaussianHMM

from new_pipeline.core.seeding import active_seed
from new_pipeline.tournament.simulator import sharpe_ratio


def stationary_bootstrap_indices(n_history: int, n_samples: int, avg_block: int, rng) -> np.ndarray:
    """Politis–Romano stationary-bootstrap row indices into ``[0, n_history)``.

    Start at a random row; each step continue to the next row (wrapping
    circularly) with probability ``1 - 1/avg_block``, else jump to a fresh random
    row. Drawing contiguous blocks preserves local temporal autocorrelation;
    ``avg_block == 1`` degenerates to an IID row bootstrap.
    """
    if n_history <= 0 or n_samples <= 0:
        return np.zeros(0, dtype=np.int64)
    jump_prob = 1.0 / max(avg_block, 1)
    indices = np.empty(n_samples, dtype=np.int64)
    current = int(rng.integers(0, n_history))
    for step in range(n_samples):
        indices[step] = current
        if rng.random() < jump_prob:
            current = int(rng.integers(0, n_history))  # start a new block
        else:
            current = (current + 1) % n_history  # continue the current block
    return indices


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
    block_size=10,
):
    """``predict_fn`` maps a feature matrix to per-row probabilities."""
    rng_seed = active_seed() if seed is None else seed
    model = fit_regime_hmm(benchmark_returns, n_states, n_iter, rng_seed)

    n_samples = len(benchmark_returns)
    synthetic_returns, _ = model.sample(n_samples, random_state=rng_seed)
    synthetic_returns = synthetic_returns.ravel()

    feature_matrix = np.asarray(features, dtype=np.float64)
    rng = np.random.default_rng(rng_seed)
    # Stationary block bootstrap: keep cross-feature correlation AND autocorrelation.
    rows = stationary_bootstrap_indices(feature_matrix.shape[0], n_samples, block_size, rng)
    sampled = feature_matrix[rows]

    proba = np.asarray(predict_fn(sampled), dtype=np.float64)
    signals = (proba > confidence_threshold).astype(np.float64)
    return sharpe_ratio(signals * synthetic_returns)
