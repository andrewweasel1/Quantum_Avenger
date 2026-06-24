"""Golden numbers for meta-labeling scoring (offense roadmap P3).

Pins the exact primary-vs-meta precision/recall/F1 on a fixed hand-constructed case
so a refactor of the scoring math is caught. Deterministic and version-independent
(no model training). See docs/OFFENSE_ROADMAP.md (P3).
"""

import pytest
from new_pipeline.tournament.meta_labeling import evaluate_meta_labeling

# primary fires on bars 0-3 (2 true / 2 false); meta keeps only the high-proba 2 wins.
_OUTCOMES = [1, 1, 0, 0, 1, 0]
_PRIMARY = [1, 1, 1, 1, 0, 0]
_META_PROBA = [0.9, 0.8, 0.2, 0.1, 0.5, 0.5]


def test_meta_labeling_scoring_golden():
    verdict = evaluate_meta_labeling(_OUTCOMES, _PRIMARY, _META_PROBA, meta_threshold=0.5)
    assert verdict.precision_primary == pytest.approx(0.5, rel=1e-9)
    assert verdict.recall_primary == pytest.approx(0.6666666666666666, rel=1e-9)
    assert verdict.f1_primary == pytest.approx(0.5714285714285715, rel=1e-9)
    assert verdict.precision_meta == pytest.approx(1.0, rel=1e-9)
    assert verdict.recall_meta == pytest.approx(0.6666666666666666, rel=1e-9)
    assert verdict.f1_meta == pytest.approx(0.8, rel=1e-9)
    assert verdict.improved is True
