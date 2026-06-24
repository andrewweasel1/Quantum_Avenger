"""Integration tests for meta-labeling wired into the director + pipeline (P3).

The pure scoring logic is covered in tests/unit/test_meta_labeling.py; here we
exercise the director glue (train a primary, derive signals, train the meta model,
return a verdict) end-to-end with real XGBoost, plus the default-off pipeline wiring.
"""

import json
from datetime import date

import numpy as np

from new_pipeline.config import get_config, reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.director import _meta_labeling
from new_pipeline.tournament.pipeline import run_offline_pipeline


def test_director_meta_labeling_produces_verdict():
    reload_config()
    cfg = get_config()
    # symmetric penalties + a 0.5 cutoff make the primary fire on some losers too, so
    # the fired set is mixed-class and the meta model has something to learn.
    cfg.tournament.penalty_fp = 1.0
    cfg.tournament.penalty_fn = 1.0
    cfg.execution.confidence_threshold = 0.5
    seed_everything(0)

    rng = np.random.default_rng(1)
    n = 400
    label = rng.integers(0, 2, n).astype(float)
    feature = label + rng.normal(0, 1.5, n)  # predictive but noisy -> imperfect primary
    matrix = np.column_stack([feature, rng.normal(0, 1, n)])

    verdict = _meta_labeling(matrix, label, None, None, cfg)
    assert verdict is not None
    assert {
        "precision_primary", "precision_meta", "f1_primary", "f1_meta",
        "improved", "n_fired_train", "n_fired_test",
    } <= set(verdict)
    assert verdict["n_fired_train"] > 0 and verdict["n_fired_test"] > 0
    assert 0.0 <= verdict["precision_meta"] <= 1.0
    assert isinstance(verdict["improved"], bool)


def test_director_meta_labeling_thin_returns_none():
    reload_config()
    verdict = _meta_labeling(np.zeros((10, 2)), np.zeros(10), None, None, get_config())
    assert verdict is None  # below the 80/20 split minimum


def test_offline_pipeline_meta_labeling_records_field(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    monkeypatch.setenv("QA_TOURNAMENT__ENABLE_META_LABELING", "true")
    reload_config()
    seed_everything(0)

    summary = run_offline_pipeline(
        tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=2
    )

    assert summary["sectors"]
    manifests = list(tmp_path.glob("*_candidate_features.json"))
    assert manifests
    for manifest in manifests:
        # the meta-labeling field rides along in the manifest (value may be null when
        # the fired set is single-class on this clean synthetic data).
        assert "meta_labeling" in json.loads(manifest.read_text())["metadata"]
