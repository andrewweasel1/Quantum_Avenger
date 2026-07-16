"""Universe long-short sleeve end-to-end: artifacts, gauntlet, dashboard, runner."""

import json
from datetime import date

import polars as pl

from new_pipeline.config import base, reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.long_short import LONG_SHORT_KEY
from new_pipeline.tournament.pipeline import run_offline_pipeline


def test_ls_sleeve_through_gauntlet_registry_and_dashboard(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    monkeypatch.setenv("QA_LONG_SHORT__ENABLED", "true")
    monkeypatch.setenv("QA_LONG_SHORT__MIN_NAMES_PER_DAY", "2")
    monkeypatch.setenv("QA_LONG_SHORT__NULL_ITERATIONS", "4")
    reload_config()
    seed_everything(0)

    summary = run_offline_pipeline(
        tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=6
    )

    # Sleeve diagnostics surface in the summary; sector list stays sleeve-free.
    assert "long_short" in summary
    diag = summary["long_short"]
    assert diag["avg_names_per_leg"] >= 1.0
    assert LONG_SHORT_KEY not in summary["sectors"]
    assert LONG_SHORT_KEY in summary["promotions"]

    # Artifacts: native-daily matrix + unique sorted dates + phi paths + manifest.
    matrix = pl.read_parquet(tmp_path / "universe_long_short_returns_matrix.parquet")
    dates = pl.read_parquet(tmp_path / "universe_long_short_sample_dates.parquet")["date"]
    paths = pl.read_parquet(tmp_path / "universe_long_short_paths.parquet")
    assert matrix.height == dates.len() == paths.height
    assert dates.n_unique() == dates.len()  # native daily axis
    assert dates.is_sorted()
    manifest = json.loads((tmp_path / "universe_long_short_candidate.json").read_text())
    assert manifest["kind"] == "long_short"
    assert "breakeven_cost_bps" in manifest["diagnostics"]

    # Registry entry rides the same gauntlet with daily n_obs + canonical reason.
    registry = json.loads((tmp_path / "promotion_registry.json").read_text())
    ls_rows = [e for e in registry["promotions"] if e["sector"] == LONG_SHORT_KEY]
    assert len(ls_rows) == 1
    entry = ls_rows[0]
    assert entry["n_obs"] == dates.len()
    assert isinstance(entry["dsr"], float) and isinstance(entry["synthetic_sharpe"], float)

    # Dashboard: the sleeve auto-cards through the artifact glob, daily axis.
    from new_pipeline.api.results import parse_results

    run_dir = tmp_path.parent / f"{tmp_path.name}_run"
    run_dir.mkdir()
    (run_dir / "output").symlink_to(tmp_path)
    cards = {s["slug"]: s for s in parse_results(run_dir)["sectors"]}
    assert "universe_long_short" in cards
    card = cards["universe_long_short"]
    assert len(card["equity"]) == dates.len()
    assert set(card["metrics"]) >= {"sharpe", "max_drawdown", "win_rate"}


def test_evaluate_and_promote_never_loads_a_booster_for_ls(tmp_path, monkeypatch):
    """The L/S candidate.json is a manifest; the gauntlet must not try to load it
    as an XGBoost model (its synthetic stat comes from the permutation null)."""
    import numpy as np

    import new_pipeline.tournament.pipeline as pipe

    reload_config()
    n_days = 80
    rng = np.random.default_rng(0)
    from datetime import timedelta

    days = [date(2021, 1, 4) + timedelta(days=i) for i in range(n_days)]
    pl.DataFrame(
        {f"trial_{j}": rng.normal(0.001, 0.01, n_days) for j in range(2)}
    ).write_parquet(tmp_path / "universe_long_short_returns_matrix.parquet")
    pl.DataFrame({"date": days}).write_parquet(
        tmp_path / "universe_long_short_sample_dates.parquet"
    )
    (tmp_path / "universe_long_short_candidate.json").write_text(
        json.dumps({"kind": "long_short"})
    )

    def boom(path):
        raise AssertionError(f"load_booster called for {path}")

    monkeypatch.setattr(pipe, "load_booster", boom)
    entry = {
        "kind": "long_short",
        "selected_features": [],
        "best_params": {},
        "best_sharpe": 0.1,
        "trial_sharpes": [0.1, 0.05],
        "candidate_path": str(tmp_path / "universe_long_short_candidate.json"),
        "synthetic_margin": 0.25,
        "meta_labeling": None,
        "diagnostics": {},
    }
    decisions = pipe._evaluate_and_promote(
        pl.DataFrame(), {LONG_SHORT_KEY: entry}, tmp_path, base.get_config()
    )
    assert LONG_SHORT_KEY in decisions
    registry = json.loads((tmp_path / "promotion_registry.json").read_text())
    assert registry["promotions"][0]["synthetic_sharpe"] == 0.25


def test_trading_session_skips_champions_without_universe_symbols(tmp_path, monkeypatch):
    """A promoted portfolio-level champion (no tickers map to its 'sector') must
    not crash the live session by being loaded as a booster."""
    monkeypatch.setenv("QA_EXECUTION__LEDGER_DIR", str(tmp_path / "ledger"))
    reload_config()
    from new_pipeline.execution.runner import run_trading_session

    manifest = tmp_path / "universe_long_short_candidate.json"
    manifest.write_text(json.dumps({"kind": "long_short"}))
    (tmp_path / "promotion_registry.json").write_text(json.dumps({
        "promotions": [{"sector": LONG_SHORT_KEY, "dsr": 1.0, "promoted": True,
                        "reason": "true alpha"}],
        "active_champions": {LONG_SHORT_KEY: str(manifest)},
    }))
    summary = run_trading_session(
        tmp_path, start=date(2021, 1, 4), end=date(2021, 1, 15)
    )
    assert summary.decisions == 0  # skipped cleanly, no crash
