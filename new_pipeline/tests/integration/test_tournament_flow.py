"""End-to-end offline chain: fixtures -> features -> candidate -> DSR -> promotion.

The Milestone M3 capstone. Runs with no network, fully seeded, using the fake
market source and the real tournament/evaluation stack.
"""

from datetime import date

import numpy as np
import polars as pl

from new_pipeline.adapters import FakeMarketDataSource
from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.evaluation.dsr import compute_deflated_sharpe_ratio
from new_pipeline.evaluation.hmm_gauntlet import run_hmm_synthetic_gauntlet
from new_pipeline.evaluation.promotion import PromotionRegistry, assess_promotion
from new_pipeline.features.polars_engine import add_features
from new_pipeline.tournament.grid_search import run_grid_search
from new_pipeline.tournament.trainer import predict_proba, save_candidate, train_booster

_FEATURE_COLS = ["returns", "atr", "adv_20", "volatility", "spread_pct", "amihud"]


def test_offline_end_to_end_pipeline(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "20")  # keep the suite fast
    reload_config()
    seed_everything(42)

    # 1) fixtures -> vectorized features
    bars = FakeMarketDataSource().history("AAPL", date(2022, 1, 1), date(2022, 6, 30))
    frame = pl.DataFrame(
        [
            {
                "date": bar.day,
                "ticker": "AAPL",
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            for bar in bars
        ]
    )
    feats = add_features(frame).drop_nulls()
    features = feats.select(_FEATURE_COLS).to_numpy()
    close = feats["close"].to_numpy()
    low = feats["low"].to_numpy()
    atr = feats["atr"].to_numpy()
    forward = np.zeros(len(close))
    forward[:-1] = close[1:] / close[:-1] - 1.0
    labels = (forward > 0.0).astype(np.float64)  # friction-aware proxy label

    # 2) tournament -> returns matrix + champion series
    result = run_grid_search(features, labels, {"close": close, "low": low, "atr": atr})
    assert result.returns_matrix.shape[0] == 4
    champion_returns = result.returns_matrix[int(np.argmax(result.trial_sharpes))]

    # CPCV paths: phi = C(5, 1) = 5 for the canonical 6/2 splitter, and the mean
    # of the champion's paths equals its canonical per-sample OOS average.
    assert result.path_count == 5
    assert result.paths.shape == (5, features.shape[0])
    np.testing.assert_allclose(result.paths.mean(axis=0), champion_returns, rtol=1e-9, atol=1e-12)

    booster = train_booster(features, labels, num_boost_round=20)
    candidate_path = tmp_path / "AAPL_candidate.json"
    save_candidate(booster, candidate_path)
    assert candidate_path.exists()

    # 3) evaluation -> DSR + HMM synthetic gauntlet
    dsr = compute_deflated_sharpe_ratio(champion_returns, result.trial_sharpes)
    synthetic_sr = run_hmm_synthetic_gauntlet(
        forward, features, lambda f: predict_proba(booster, f), n_iter=20, seed=42
    )
    assert 0.0 <= dsr <= 1.0
    assert isinstance(synthetic_sr, float)

    # 4) promotion -> immutable registry
    registry = PromotionRegistry(tmp_path / "promotion_registry.json")
    decision = assess_promotion("Information Technology", dsr, synthetic_sr)
    registry.record(
        decision, model_path=str(candidate_path) if decision.promoted else None
    )
    assert len(registry.promotions) == 1
    assert (tmp_path / "promotion_registry.json").exists()
