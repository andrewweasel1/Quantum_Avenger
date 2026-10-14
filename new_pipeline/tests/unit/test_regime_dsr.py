import numpy as np
from new_pipeline.evaluation.regime_dsr import (
    QuantitativeEvaluator,
    RegimeVerdict,
    ThinRegimePolicy,
)


def _two_regime_series(seed: int = 0):
    """Low-vol then high-vol, both with positive drift -> two separable regimes."""
    rng = np.random.default_rng(seed)
    returns = np.concatenate([rng.normal(0.008, 0.003, 600), rng.normal(0.008, 0.03, 600)])
    volatility = np.concatenate([np.full(600, 0.003), np.full(600, 0.03)])
    volatility = volatility + rng.normal(0.0, 1e-4, volatility.size)
    return returns, volatility


def test_strong_alpha_promotes_across_regimes():
    returns, volatility = _two_regime_series()
    trials = list(np.linspace(0.0, 0.05, 9))
    evaluator = QuantitativeEvaluator(n_components=2, min_regime_obs=60, random_state=0)
    verdict = evaluator.evaluate_model_robustness(returns, volatility, len(trials), trials)
    assert isinstance(verdict, RegimeVerdict)
    assert verdict.per_regime  # at least one testable regime
    assert verdict.promoted
    assert all(0.0 <= res.dsr <= 1.0 for res in verdict.per_regime.values())


def test_thin_regimes_skipped_block_promotion():
    returns, volatility = _two_regime_series()
    evaluator = QuantitativeEvaluator(n_components=2, min_regime_obs=10_000, random_state=0)
    verdict = evaluator.evaluate_model_robustness(returns, volatility, 5)
    assert verdict.per_regime == {}        # every regime is under-sampled
    assert verdict.skipped_regimes         # ...and recorded as skipped
    assert not verdict.promoted            # nothing testable -> not promoted


def test_veto_policy_fails_on_thin_regime():
    returns, volatility = _two_regime_series()
    evaluator = QuantitativeEvaluator(
        n_components=2, min_regime_obs=10_000,
        thin_policy=ThinRegimePolicy.VETO, random_state=0,
    )
    verdict = evaluator.evaluate_model_robustness(returns, volatility, 5)
    assert verdict.skipped_regimes
    assert not verdict.promoted


def test_too_short_input_returns_unpromoted_verdict():
    evaluator = QuantitativeEvaluator(n_components=3, random_state=0)
    verdict = evaluator.evaluate_model_robustness(
        np.array([0.01, 0.02]), np.array([0.01, 0.02]), 5
    )
    assert isinstance(verdict, RegimeVerdict)
    assert not verdict.promoted


def test_daily_scale_series_with_thin_regime_skipped():
    """At realistic calendar-time lengths (~750 daily obs) a sparse regime falls
    under min_regime_obs and is skipped; the verdict is decided by the testable
    regimes alone."""
    import pandas as pd

    rng = np.random.default_rng(11)
    calm = rng.normal(0.004, 0.005, 700)   # long, strongly positive regime
    burst = rng.normal(0.0, 0.05, 50)      # short high-vol burst: < 60 obs
    returns = np.concatenate([calm, burst])
    vol = pd.Series(returns).rolling(10).std().bfill().to_numpy()

    evaluator = QuantitativeEvaluator(
        min_dsr_threshold=0.95, n_components=2, min_regime_obs=60, random_state=7
    )
    verdict = evaluator.evaluate_model_robustness(returns, vol, n_trials=4)
    assert verdict.skipped_regimes  # the 50-obs burst regime was too thin to test
    assert verdict.per_regime  # the calm regime was testable
    assert verdict.promoted is True  # and clears DSR on ~700 high-Sharpe days
