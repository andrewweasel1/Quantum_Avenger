"""Unit tests for the portfolio combination layer (offense roadmap P4, §F/§H).

HRP weights, inverse-variance, covariance denoising (RMT) and shrinkage, and the
combine_returns book. Golden HRP weights live in tests/golden/test_portfolio_golden.py.
"""

import numpy as np
import pytest
from new_pipeline.portfolio import (
    clean_covariance,
    combine_returns,
    cov_to_corr,
    denoise_covariance,
    hrp_weights,
    inverse_variance_weights,
    portfolio_weights,
)


def _two_cluster_returns(seed=0, t=500):
    """Assets (0,1) share factor f1, (2,3) share f2; clusters independent; vols differ."""
    rng = np.random.default_rng(seed)
    f1, f2 = rng.normal(0, 1, t), rng.normal(0, 1, t)
    return np.column_stack(
        [
            0.01 * (f1 + 0.3 * rng.normal(0, 1, t)),
            0.02 * (f1 + 0.6 * rng.normal(0, 1, t)),
            0.01 * (f2 + 0.3 * rng.normal(0, 1, t)),
            0.03 * (f2 + 0.6 * rng.normal(0, 1, t)),
        ]
    )


def test_hrp_weights_sum_to_one_and_positive():
    cov = np.cov(_two_cluster_returns(), rowvar=False)
    w = hrp_weights(cov)
    assert w.sum() == pytest.approx(1.0)
    assert (w > 0).all()


def test_hrp_lower_vol_gets_more_weight_within_cluster():
    cov = np.cov(_two_cluster_returns(), rowvar=False)
    w = hrp_weights(cov)
    assert w[0] > w[1]  # asset 0 lower vol than 1 (same cluster)
    assert w[2] > w[3]


def test_hrp_degenerate_sizes():
    assert hrp_weights(np.zeros((0, 0))).shape == (0,)
    assert hrp_weights(np.array([[0.04]])) == pytest.approx([1.0])


def test_inverse_variance_weights():
    cov = np.diag([0.01, 0.04])  # second asset 4x the variance
    w = inverse_variance_weights(cov)
    assert w.sum() == pytest.approx(1.0)
    assert w[0] == pytest.approx(0.8) and w[1] == pytest.approx(0.2)


def test_denoise_preserves_variances():
    cov = np.cov(_two_cluster_returns(), rowvar=False)
    denoised = denoise_covariance(cov, 500)
    assert np.allclose(np.diag(denoised), np.diag(cov))


def test_denoise_reduces_conditioning_when_noisy():
    rng = np.random.default_rng(3)
    cov = np.cov(rng.normal(0, 0.02, (60, 25)), rowvar=False)  # N close to T -> noisy
    assert np.linalg.cond(denoise_covariance(cov, 60)) < np.linalg.cond(cov)


def test_denoise_noop_when_obs_not_exceed_vars():
    cov = np.cov(_two_cluster_returns(), rowvar=False)
    assert np.allclose(denoise_covariance(cov, 4), cov)  # n_obs == n_vars


def test_clean_covariance_methods_shapes():
    returns = _two_cluster_returns()
    assert clean_covariance(returns, "sample").shape == (4, 4)
    assert clean_covariance(returns, "rmt").shape == (4, 4)
    lw = pytest.importorskip("sklearn")  # ships with hmmlearn
    assert clean_covariance(returns, "ledoit_wolf").shape == (4, 4)
    del lw


def test_cov_to_corr_roundtrip():
    cov = np.cov(_two_cluster_returns(), rowvar=False)
    corr, std = cov_to_corr(cov)
    assert np.allclose(np.diag(corr), 1.0)
    assert np.allclose(corr * np.outer(std, std), cov)


def test_flat_sleeve_dropped_no_nan():
    # a zero-variance (dead) sleeve must not poison the book: it gets 0 weight.
    real = np.random.default_rng(0).normal(0, 0.01, 200)
    weights, book = combine_returns(
        np.column_stack([real, np.zeros(200)]), method="hrp", cov_method="sample"
    )
    assert np.isfinite(book).all()
    assert weights[1] == 0.0 and weights[0] == pytest.approx(1.0)


def test_kyle_lambda_ddof_consistent():
    # slope = Cov(x,y)/Var(x) with matched ddof — equals an independent OLS fit.
    from new_pipeline.features.microstructure import kyle_lambda

    rng = np.random.default_rng(1)
    close = 100 + np.cumsum(rng.normal(0, 0.5, 120))
    volume = 1e6 + rng.integers(0, 5e5, 120).astype(float)
    lam = kyle_lambda(close, volume, 20)
    delta = np.diff(close, prepend=close[0])
    signed = np.sign(delta) * volume
    t = 119
    expected = np.polyfit(signed[t - 19 : t + 1], delta[t - 19 : t + 1], 1)[0]
    assert lam[t] == pytest.approx(expected, rel=1e-9)


def test_combine_returns_single_column_is_identity():
    col = np.array([0.1, -0.2, 0.3])
    weights, book = combine_returns(col)
    assert weights == pytest.approx([1.0])
    assert book == pytest.approx(col)


def test_combine_returns_shape_and_book():
    returns = _two_cluster_returns()
    weights, book = combine_returns(returns, method="hrp", cov_method="rmt")
    assert weights.sum() == pytest.approx(1.0)
    assert book.shape == (500,)
    assert book == pytest.approx(returns @ weights)


def test_equal_weights():
    assert portfolio_weights(_two_cluster_returns(), method="equal") == pytest.approx([0.25] * 4)


def test_portfolio_weights_inverse_variance():
    w = portfolio_weights(_two_cluster_returns(), method="inverse_variance", cov_method="sample")
    assert w.sum() == pytest.approx(1.0)
    assert w[0] > w[1]  # lower-vol asset gets more weight


def test_portfolio_weights_1d_input_is_single_sleeve():
    assert portfolio_weights(np.array([0.1, -0.2, 0.3])) == pytest.approx([1.0])


def test_clean_covariance_1d_input():
    cov = clean_covariance(np.array([0.1, -0.2, 0.3, 0.0]))
    assert np.asarray(cov).ndim == 2  # atleast_2d scalar variance


def test_hrp_unbalanced_tree_three_assets():
    # an odd-sized, unbalanced tree exercises the leaf+cluster expansion path.
    rng = np.random.default_rng(1)
    shared = rng.normal(0, 1, 400)
    returns = np.column_stack(
        [
            0.01 * (shared + 0.2 * rng.normal(0, 1, 400)),
            0.01 * (shared + 0.2 * rng.normal(0, 1, 400)),  # correlated with col 0
            0.02 * rng.normal(0, 1, 400),  # independent
        ]
    )
    w = hrp_weights(np.cov(returns, rowvar=False))
    assert w.sum() == pytest.approx(1.0)
    assert (w > 0).all() and w.shape == (3,)
