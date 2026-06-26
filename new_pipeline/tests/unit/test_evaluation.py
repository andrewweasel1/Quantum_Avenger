import numpy as np
from new_pipeline.core.seeding import seed_everything
from new_pipeline.evaluation.hmm_gauntlet import (
    run_hmm_synthetic_gauntlet,
    stationary_bootstrap_indices,
)
from new_pipeline.evaluation.tearsheet import summary_metrics, write_html_tearsheet


def _predict(features):
    return 1.0 / (1.0 + np.exp(-features[:, 0]))


def test_hmm_gauntlet_returns_float_and_is_reproducible():
    seed_everything(7)
    rng = np.random.default_rng(0)
    benchmark = rng.normal(0.0, 0.01, 200)
    features = rng.normal(size=(200, 3))
    first = run_hmm_synthetic_gauntlet(benchmark, features, _predict, n_iter=20, seed=7)
    second = run_hmm_synthetic_gauntlet(benchmark, features, _predict, n_iter=20, seed=7)
    assert isinstance(first, float)
    assert first == second  # deterministic under a fixed seed


def test_stationary_bootstrap_preserves_autocorrelation():
    n_history, n_samples = 50, 400
    idx = stationary_bootstrap_indices(n_history, n_samples, 20, np.random.default_rng(0))
    assert idx.shape == (n_samples,)
    assert idx.min() >= 0 and idx.max() < n_history
    # determinism under a fixed seed
    again = stationary_bootstrap_indices(n_history, n_samples, 20, np.random.default_rng(0))
    assert np.array_equal(idx, again)
    # large avg_block -> contiguous blocks (autocorrelation preserved) ...
    contiguous = np.mean(idx[1:] == (idx[:-1] + 1) % n_history)
    assert contiguous > 0.85
    # ... avg_block == 1 degenerates to an IID row bootstrap (almost never contiguous)
    iid = stationary_bootstrap_indices(n_history, n_samples, 1, np.random.default_rng(0))
    assert np.mean(iid[1:] == (iid[:-1] + 1) % n_history) < 0.15


def test_summary_metrics_on_known_series():
    metrics = summary_metrics(np.array([0.1, -0.05, 0.2, 0.0, -0.1]))
    assert set(metrics) == {"sharpe", "sortino", "max_drawdown", "win_rate", "profit_factor"}
    assert metrics["win_rate"] == 0.5  # 2 wins out of 4 traded bars
    assert metrics["max_drawdown"] <= 0.0
    # Downside deviation <= total stdev for this positive-mean series -> Sortino >= Sharpe > 0.
    assert metrics["sortino"] >= metrics["sharpe"] > 0.0


def test_write_html_tearsheet_degrades_without_quantstats():
    result = write_html_tearsheet(np.array([0.01, -0.02]), "/tmp/qa_tearsheet.html")
    assert isinstance(result, bool)
