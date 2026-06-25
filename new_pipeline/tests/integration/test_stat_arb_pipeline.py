"""Integration tests for stat-arb wired into the pipeline (offense roadmap P5).

The core cointegration/OU math is covered in tests/unit/test_stat_arb.py; here we
exercise the pipeline glue (_run_stat_arb): pivot the price panel, find within-sector
pairs, trade them, combine the date-indexed sleeves into a stat-arb book.
"""

from datetime import date, timedelta

import numpy as np
import polars as pl

from new_pipeline.config import get_config, reload_config
from new_pipeline.tournament.pipeline import _run_stat_arb


def _ar1_spread(rng, n, phi=0.9):
    spread = np.zeros(n)
    for t in range(1, n):
        spread[t] = phi * spread[t - 1] + rng.normal(0, 1)
    return spread


def _cointegrated_frame(n=200) -> pl.DataFrame:
    """Two sectors, each with a cointegrated pair (a random-walk leg + hedge*leg+spread)."""
    rng = np.random.default_rng(0)
    dates = [date(2021, 1, 1) + timedelta(days=i) for i in range(n)]
    series = {}
    for sector, (y_name, x_name, hedge) in {
        "Tech": ("TY", "TX", 1.5),
        "Fin": ("FY", "FX", 0.8),
    }.items():
        x = 100.0 + np.cumsum(rng.normal(0, 1, n))
        y = hedge * x + _ar1_spread(rng, n)
        series[(x_name, sector)] = x
        series[(y_name, sector)] = y
    rows = [
        {"date": dates[i], "ticker": ticker, "sector": sector, "close": float(values[i])}
        for (ticker, sector), values in series.items()
        for i in range(n)
    ]
    return pl.DataFrame(rows)


def test_run_stat_arb_validates_and_books(tmp_path):
    reload_config()
    cfg = get_config()
    cfg.stat_arb.min_obs = 50
    cfg.evaluation.reality_check_bootstrap = 100  # keep the test fast
    cfg.evaluation.dsr_promotion_threshold = 0.0  # accept any non-negative DSR so the book builds

    report = _run_stat_arb(_cointegrated_frame(), tmp_path, cfg)

    assert report is not None
    assert report["n_pairs"] >= 2 and report["n_candidates"] >= 2
    found = {frozenset((p["y"], p["x"])) for p in report["pairs"]}
    assert frozenset(("TY", "TX")) in found and frozenset(("FY", "FX")) in found
    for pair in report["pairs"]:  # every sleeve carries its validation
        assert "dsr" in pair and isinstance(pair["validated"], bool)
    assert 0.0 < report["reality_check_pvalue"] <= 1.0  # family multiple-testing guard
    assert report["n_validated"] >= 2 and "book_sharpe" in report  # validated -> exact book
    assert (tmp_path / "stat_arb.json").exists()


def test_run_stat_arb_per_pair_null_alignment(tmp_path):
    # a late-listing ticker (front-gap nulls) must NOT truncate a full-history pair:
    # under a universe-wide drop_nulls the panel would shrink to LATE's 55-row window
    # and the full TY/TX pair would fall below min_obs and be skipped.
    reload_config()
    cfg = get_config()
    cfg.stat_arb.min_obs = 50
    rng = np.random.default_rng(0)
    n = 200
    dates = [date(2021, 1, 1) + timedelta(days=i) for i in range(n)]
    tx = 100 + np.cumsum(rng.normal(0, 1, n))
    ty = 1.5 * tx + _ar1_spread(rng, n)
    late = 100 + np.cumsum(rng.normal(0, 1, n))  # independent; "listed" only last 55 days
    rows = []
    for i in range(n):
        rows.append({"date": dates[i], "ticker": "TX", "sector": "Tech", "close": float(tx[i])})
        rows.append({"date": dates[i], "ticker": "TY", "sector": "Tech", "close": float(ty[i])})
        if i >= n - 55:
            rows.append(
                {"date": dates[i], "ticker": "LATE", "sector": "Tech", "close": float(late[i])}
            )

    report = _run_stat_arb(pl.DataFrame(rows), tmp_path, cfg)
    assert report is not None
    found = {frozenset((p["y"], p["x"])) for p in report["pairs"]}
    assert frozenset(("TY", "TX")) in found  # full-history pair survives the late listing


def test_run_stat_arb_none_when_panel_too_short(tmp_path):
    # fewer observations than min_obs -> graceful None (deterministic guard).
    reload_config()
    cfg = get_config()
    cfg.stat_arb.min_obs = 10_000
    assert _run_stat_arb(_cointegrated_frame(n=100), tmp_path, cfg) is None
