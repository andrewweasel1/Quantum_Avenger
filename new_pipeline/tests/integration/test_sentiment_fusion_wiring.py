"""Config-gated sentiment-fusion wiring, exercised end-to-end offline.

Covers the three opt-in paths from the offline-core pass: the micro rolling-HMM
features in the build path (``fusion.enabled``), and the per-regime DSR promotion
gate plus N_eff deflation in the tournament (``evaluation.regime_gate_enabled`` /
``use_effective_trials``). Defaults leave all of this off, so the rest of the
suite is unaffected; here we turn it on and assert the chain still runs.
"""

from datetime import date

from new_pipeline.config import get_config, reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.features.markov_regime import MARKOV_FEATURE_NAMES
from new_pipeline.tournament.pipeline import build_training_frame, run_offline_pipeline


def test_build_training_frame_adds_markov_features_when_fusion_enabled(monkeypatch):
    monkeypatch.setenv("QA_FUSION__ENABLED", "true")
    reload_config()
    seed_everything(0)
    cfg = get_config()
    assert cfg.fusion.enabled

    frame = build_training_frame(
        ["AAA", "BBB"],
        {"AAA": "Tech", "BBB": "Tech"},
        date(2021, 1, 1),
        date(2021, 6, 30),
        cfg=cfg,
    )
    for name in MARKOV_FEATURE_NAMES:
        assert name in frame.columns


def test_regime_gate_and_neff_pipeline_runs(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    monkeypatch.setenv("QA_FUSION__ENABLED", "true")
    monkeypatch.setenv("QA_EVALUATION__REGIME_GATE_ENABLED", "true")
    reload_config()
    seed_everything(0)

    summary = run_offline_pipeline(
        tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=2
    )

    assert summary["sectors"]
    assert set(summary["promotions"]).issubset(set(summary["sectors"]))
    assert (tmp_path / "promotion_registry.json").exists()
