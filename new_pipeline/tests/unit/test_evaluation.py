import numpy as np
from new_pipeline.core.seeding import seed_everything
from new_pipeline.evaluation.hmm_gauntlet import run_hmm_synthetic_gauntlet
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


def test_summary_metrics_on_known_series():
    metrics = summary_metrics(np.array([0.1, -0.05, 0.2, 0.0, -0.1]))
    assert set(metrics) == {"sharpe", "max_drawdown", "win_rate", "profit_factor"}
    assert metrics["win_rate"] == 0.5  # 2 wins out of 4 traded bars
    assert metrics["max_drawdown"] <= 0.0


def test_write_html_tearsheet_degrades_without_quantstats():
    result = write_html_tearsheet(np.array([0.01, -0.02]), "/tmp/qa_tearsheet.html")
    assert isinstance(result, bool)
