"""Artifact parsing: a synthetic run dir -> chart-ready per-sector results."""

import json

import numpy as np
import polars as pl
from new_pipeline.api.results import parse_results


def _write_run(run_dir, *, slug="information_technology", n_obs=60, n_trials=3, n_paths=15,
               n_dates=None):
    output = run_dir / "output"
    output.mkdir(parents=True)
    rng = np.random.default_rng(0)
    matrix = rng.normal(0.0, 0.01, size=(n_obs, n_trials))
    matrix[:, 1] += 0.004  # trial 1 is the clear champion (highest mean -> Sharpe)
    pl.DataFrame(matrix, schema=[f"t{j}" for j in range(n_trials)]).write_parquet(
        output / f"{slug}_returns_matrix.parquet"
    )
    if n_dates:  # pooled ticker-major sample dates: each date repeats n_obs/n_dates times
        from datetime import date, timedelta

        days = [date(2021, 1, 4) + timedelta(days=i) for i in range(n_dates)]
        sample_dates = [days[i % n_dates] for i in range(n_obs)]
        pl.DataFrame({"date": sample_dates}).write_parquet(
            output / f"{slug}_sample_dates.parquet"
        )
    paths = rng.normal(0.0, 0.01, size=(n_obs, n_paths))
    pl.DataFrame(paths, schema=[f"p{j}" for j in range(n_paths)]).write_parquet(
        output / f"{slug}_paths.parquet"
    )
    (output / f"{slug}_candidate_features.json").write_text(json.dumps(
        {"features": ["a", "b"],
         "metadata": {"meta_labeling": {"precision": 0.6, "recall": 0.5, "f1": 0.54}}}
    ))
    (output / "promotion_registry.json").write_text(json.dumps(
        {"promotions": [{"sector": "Information Technology", "dsr": 0.97}],
         "active_champions": {"Information Technology": f"{slug}_candidate.json"}}
    ))
    (output / "alpha_eval.json").write_text(json.dumps({"xf_low_vol": {"ic": 0.03}}))
    (output / "portfolio.json").write_text(json.dumps({"method": "hrp", "weights": {}}))
    (output / "stat_arb.json").write_text(json.dumps({"pairs": []}))
    (run_dir / "summary.json").write_text(
        json.dumps({"sectors": [slug], "promotions": {slug: True}})
    )
    return slug


def test_parse_results_aggregates_every_artifact(tmp_path):
    _write_run(tmp_path)
    result = parse_results(tmp_path)

    assert result["run_id"] == tmp_path.name
    assert result["summary"]["sectors"] == ["information_technology"]
    assert result["promotions"][0]["dsr"] == 0.97
    assert "Information Technology" in result["active_champions"]
    assert result["alpha_eval"]["xf_low_vol"]["ic"] == 0.03
    assert result["portfolio"]["method"] == "hrp"
    assert result["stat_arb"] == {"pairs": []}


def test_parse_results_recovers_champion_equity_and_metrics(tmp_path):
    _write_run(tmp_path, n_obs=60, n_trials=3)
    sector = parse_results(tmp_path)["sectors"][0]

    assert sector["sector"] == "Information Technology"
    assert sector["n_trials"] == 3
    assert len(sector["equity"]) == 60  # cumulative-return curve, one point per bar
    assert set(sector["metrics"]) == {"sharpe", "sortino", "max_drawdown",
                                      "win_rate", "profit_factor"}
    assert sector["metrics"]["sharpe"] > 0.0  # the champion column is the positive-drift one


def test_parse_results_caps_cpcv_paths(tmp_path):
    _write_run(tmp_path, n_paths=20)  # more than the _MAX_PATHS=12 cap
    sector = parse_results(tmp_path)["sectors"][0]
    assert len(sector["paths"]) == 12
    assert sector["meta_labeling"]["f1"] == 0.54


def test_parse_results_handles_missing_output_dir(tmp_path):
    (tmp_path / "summary.json").write_text(json.dumps({"sectors": []}))
    result = parse_results(tmp_path)
    assert result["sectors"] == []
    assert result["promotions"] == []
    assert result["alpha_eval"] is None


def test_sample_dates_collapse_equity_to_calendar_days(tmp_path):
    # 60 pooled samples over 12 distinct dates (5 "tickers" per day) -> the
    # served equity/paths shrink to one point per calendar day, and the
    # champion is picked on the collapsed (daily) Sharpe.
    _write_run(tmp_path, n_obs=60, n_dates=12)
    sector = parse_results(tmp_path)["sectors"][0]
    assert len(sector["equity"]) == 12
    assert all(len(p) == 12 for p in sector["paths"])
    assert sector["metrics"]["sharpe"] > 0.0  # trial 1 still the champion


def test_sample_dates_length_mismatch_falls_back_to_pooled(tmp_path):
    _write_run(tmp_path, n_obs=60, n_dates=12)
    # Corrupt the dates artifact so its height no longer matches the matrix.
    import polars as pl_  # noqa: PLC0415 - test-local alias

    out = tmp_path / "output" / "information_technology_sample_dates.parquet"
    pl_.DataFrame({"date": pl_.read_parquet(out)["date"][:10]}).write_parquet(out)
    sector = parse_results(tmp_path)["sectors"][0]
    assert len(sector["equity"]) == 60  # pooled behavior, not a crash
