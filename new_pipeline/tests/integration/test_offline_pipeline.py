"""End-to-end offline pipeline: fake data -> features+labels -> tournament -> promotion.

The Tier-1 capstone — exercises the whole chain with no network under a fixed
seed and a tiny budget.
"""

import json
from datetime import date

from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.pipeline import run_offline_pipeline


def test_offline_pipeline_runs(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    reload_config()
    seed_everything(0)

    summary = run_offline_pipeline(
        tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=2
    )

    assert summary["sectors"]  # at least one sector produced a candidate
    assert set(summary["promotions"]).issubset(set(summary["sectors"]))
    assert (tmp_path / "promotion_registry.json").exists()


def test_offline_pipeline_records_overfitting_diagnostics(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    reload_config()
    seed_everything(0)

    run_offline_pipeline(
        tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=2
    )

    registry = json.loads((tmp_path / "promotion_registry.json").read_text())
    assert registry["promotions"]
    entry = registry["promotions"][0]
    # Evaluation Rigor v2 gates ride along in the audit trail.
    assert {"pbo", "psr", "haircut_sharpe"} <= set(entry)
    assert isinstance(entry["pbo"], float)
    assert isinstance(entry["psr"], float)
