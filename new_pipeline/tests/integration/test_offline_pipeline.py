"""End-to-end offline pipeline: fake data -> features+labels -> tournament -> promotion.

The Tier-1 capstone — exercises the whole chain with no network under a fixed
seed and a tiny budget.
"""

import json
from datetime import date

import pytest

from new_pipeline.config import base, reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.pipeline import (
    FEATURE_COLS,
    build_training_frame,
    run_offline_pipeline,
)


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
    # P2 alpha-eval diagnostics are written by default (read-only; never gates).
    assert (tmp_path / "alpha_eval.json").exists()
    assert "alpha_eval" in summary


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
    # Evaluation Rigor v2 gates + the CPCV path-DSR gate ride along in the audit trail.
    assert {"pbo", "psr", "haircut_sharpe", "cpcv_path_pass_fraction"} <= set(entry)
    assert isinstance(entry["pbo"], float)
    assert isinstance(entry["psr"], float)
    assert 0.0 <= entry["cpcv_path_pass_fraction"] <= 1.0


def test_build_training_frame_adds_cross_sectional_factors():
    """P0 build hook: enabling features.factor_set appends populated xf_* columns."""
    from new_pipeline.adapters import FakeMarketDataSource, StaticUniverseProvider

    reload_config()
    cfg = base.get_config()
    cfg.features.factor_set = ["reversal_21", "low_vol"]
    universe = StaticUniverseProvider()
    sectors = universe.sectors()
    symbols = list(sectors)[:4]

    frame = build_training_frame(
        symbols, sectors, date(2021, 1, 1), date(2021, 12, 31), FakeMarketDataSource(), cfg
    )
    for column in ("xf_reversal_21", "xf_low_vol"):
        assert column in frame.columns
        assert frame[column].drop_nulls().len() > 0


def test_build_training_frame_adds_extended_features():
    """P1 build hook: enabling features.extended_features appends populated columns."""
    from new_pipeline.adapters import FakeMarketDataSource, StaticUniverseProvider

    reload_config()
    cfg = base.get_config()
    cfg.features.extended_features = ["vol_estimators", "microstructure"]
    universe = StaticUniverseProvider()
    sectors = universe.sectors()
    symbols = list(sectors)[:4]

    frame = build_training_frame(
        symbols, sectors, date(2021, 1, 1), date(2021, 12, 31), FakeMarketDataSource(), cfg
    )
    for column in ("parkinson_vol", "yang_zhang_vol", "roll_measure", "kyle_lambda"):
        assert column in frame.columns
        assert frame[column].drop_nulls().len() > 0


def test_build_training_frame_adds_value_quality_factors():
    """Phase C: a fundamentals source + value/quality factors -> populated xf_* columns."""
    from new_pipeline.adapters import FakeMarketDataSource, StaticUniverseProvider
    from new_pipeline.adapters.fakes import FakeFundamentalsSource

    reload_config()
    cfg = base.get_config()
    cfg.features.factor_set = ["book_to_market", "roe"]
    universe = StaticUniverseProvider()
    sectors = universe.sectors()
    symbols = list(sectors)[:4]

    frame = build_training_frame(
        symbols, sectors, date(2021, 1, 1), date(2021, 12, 31), FakeMarketDataSource(), cfg,
        fundamentals_source=FakeFundamentalsSource(),
    )
    for column in ("xf_book_to_market", "xf_roe"):
        assert column in frame.columns
        assert frame[column].drop_nulls().len() > 0


def test_offline_pipeline_consumes_cross_sectional_factors(tmp_path, monkeypatch):
    """P0 end-to-end: with factors enabled the tournament runs and the xf_* columns
    are wired into the selectable feature namespace (no leakage of unexpected cols)."""
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    reload_config()
    base.get_config().features.factor_set = ["reversal_21", "low_vol"]
    seed_everything(0)

    summary = run_offline_pipeline(
        tmp_path, start=date(2021, 1, 1), end=date(2022, 12, 31), max_symbols=6
    )

    assert summary["sectors"]
    manifests = list(tmp_path.glob("*_candidate_features.json"))
    assert manifests
    selectable = set(FEATURE_COLS) | {"xf_reversal_21", "xf_low_vol"}
    for manifest in manifests:
        selected = set(json.loads(manifest.read_text())["features"])
        assert selected <= selectable
    # P2: universe-wide IC is reported for the factor signals, with horizon decay.
    assert (tmp_path / "alpha_eval.json").exists()
    ic = summary["alpha_eval"]["ic"]
    assert {"xf_reversal_21", "xf_low_vol"} <= set(ic)
    assert {"xf_reversal_21", "xf_low_vol"} <= set(summary["alpha_eval"]["decay"])
    # P4: the per-sector champions are combined into one book (default-on portfolio).
    assert (tmp_path / "portfolio.json").exists()
    book = summary["portfolio"]
    assert set(book["weights"]) <= set(summary["sectors"])
    assert sum(book["weights"].values()) == pytest.approx(1.0)
    assert book["method"] == "hrp"  # exact: champions aggregated to date-aligned sector returns
    assert "book_sharpe" in book and set(book["sector_sharpe"]) == set(book["weights"])


def test_offline_pipeline_records_reality_check_when_enabled(tmp_path, monkeypatch):
    """P4 §J: enabling the reality check records a White's RC p-value per sector."""
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    monkeypatch.setenv("QA_EVALUATION__REALITY_CHECK_ENABLED", "true")
    monkeypatch.setenv("QA_EVALUATION__REALITY_CHECK_BOOTSTRAP", "100")
    reload_config()
    seed_everything(0)

    run_offline_pipeline(tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=2)

    registry = json.loads((tmp_path / "promotion_registry.json").read_text())
    assert registry["promotions"]
    pvalue = registry["promotions"][0]["reality_check_pvalue"]
    assert pvalue is not None and 0.0 < pvalue <= 1.0
