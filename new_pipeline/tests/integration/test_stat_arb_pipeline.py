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


def test_run_stat_arb_finds_pairs_and_combines_book(tmp_path):
    reload_config()
    cfg = get_config()
    cfg.stat_arb.min_obs = 50

    report = _run_stat_arb(_cointegrated_frame(), tmp_path, cfg)

    assert report is not None
    assert report["n_pairs"] >= 2  # one cointegrated pair per sector
    found = {frozenset((p["y"], p["x"])) for p in report["pairs"]}
    assert frozenset(("TY", "TX")) in found and frozenset(("FY", "FX")) in found
    assert report["n_sleeves"] >= 2 and "book_sharpe" in report  # date-aligned -> exact book
    assert (tmp_path / "stat_arb.json").exists()


def test_run_stat_arb_none_when_panel_too_short(tmp_path):
    # fewer observations than min_obs -> graceful None (deterministic guard).
    reload_config()
    cfg = get_config()
    cfg.stat_arb.min_obs = 10_000
    assert _run_stat_arb(_cointegrated_frame(n=100), tmp_path, cfg) is None
