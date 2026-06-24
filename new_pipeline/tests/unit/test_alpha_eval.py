"""Unit tests for per-signal alpha evaluation (offense roadmap P2).

Correctness of the cross-sectional IC: perfect/inverse factors, the thin-universe
and zero-dispersion guards, the ICIR/t-stat relationship, signal ranking, and the
decay/report shapes. Golden number pins live in tests/golden/test_alpha_eval_golden.py.
"""

import math
from datetime import date, timedelta

import polars as pl
import pytest
from new_pipeline.evaluation.alpha_eval import (
    alpha_eval_report,
    evaluate_signals,
    ic_decay,
    information_coefficient,
)


def _grid(n_names, n_dates=2) -> pl.DataFrame:
    """``n_dates`` dates x ``n_names`` names; ``good`` ranks fwd_ret, ``bad`` inverts it."""
    rows = []
    for d in range(n_dates):
        for i in range(n_names):
            rows.append(
                {
                    "date": date(2021, 1, 1) + timedelta(days=d),
                    "ticker": f"T{i}",
                    "good": float(i),
                    "bad": float(n_names - 1 - i),
                    "fwd_ret": 0.01 * i,
                    "close": 100.0 + i,
                }
            )
    return pl.DataFrame(rows)


def test_perfect_factor_ic_is_one():
    report = information_coefficient(_grid(6), "good", min_names=5)
    assert report.mean_ic == pytest.approx(1.0)
    assert report.hit_rate == 1.0
    assert report.n_periods == 2
    assert report.breadth == pytest.approx(6.0)
    assert report.icir == 0.0  # zero IC dispersion -> guarded, not NaN


def test_inverse_factor_ic_is_negative_one():
    report = information_coefficient(_grid(6), "bad", min_names=5)
    assert report.mean_ic == pytest.approx(-1.0)
    assert report.hit_rate == 0.0


def test_thin_universe_is_graceful_zero():
    # fewer names than min_names -> every date filtered -> all-zero report, no NaN.
    report = information_coefficient(_grid(3), "good", min_names=5)
    assert report.n_periods == 0
    assert report.mean_ic == 0.0 and report.icir == 0.0 and report.breadth == 0.0


def test_zero_dispersion_date_is_dropped():
    # one usable date + one constant-factor date (Spearman NaN) -> only the first counts.
    rows = []
    for i in range(5):
        rows.append(
            {"date": date(2021, 1, 1), "ticker": f"T{i}", "good": float(i), "fwd_ret": 0.01 * i}
        )
        rows.append(
            {"date": date(2021, 1, 2), "ticker": f"T{i}", "good": 7.0, "fwd_ret": 0.01 * i}
        )
    report = information_coefficient(pl.DataFrame(rows), "good", min_names=5)
    assert report.n_periods == 1
    assert report.mean_ic == pytest.approx(1.0)


def test_tstat_equals_icir_times_sqrt_n():
    # invariant across any fixture with dispersion.
    frame = _grid(6, n_dates=4).with_columns(
        (pl.col("good") + pl.col("date").dt.day()).alias("good")  # vary ranks across dates
    )
    report = information_coefficient(frame, "good", min_names=5)
    assert report.ic_t_stat == pytest.approx(report.icir * math.sqrt(report.n_periods))


def test_evaluate_signals_ranks_and_filters_absent():
    # strong: IC=1 every date; weak: IC=+1 on even dates, -1 on odd -> mean ~0.
    rows = []
    for d in range(4):
        for i in range(6):
            rows.append(
                {
                    "date": date(2021, 1, 1) + timedelta(days=d),
                    "ticker": f"T{i}",
                    "strong": float(i),
                    "weak": float(i if d % 2 == 0 else 5 - i),
                    "fwd_ret": 0.01 * i,
                }
            )
    ranked = evaluate_signals(pl.DataFrame(rows), ["weak", "strong", "absent"], min_names=5)
    assert list(ranked) == ["strong", "weak"]  # |mean_ic| desc; absent column skipped
    assert ranked["strong"]["mean_ic"] == pytest.approx(1.0)


def test_evaluate_signals_empty_is_empty():
    assert evaluate_signals(_grid(6), []) == {}


def test_ic_decay_shape():
    decay = ic_decay(_grid(8, n_dates=30), "good", horizons=(1, 5), min_names=5)
    assert set(decay) == {1, 5}
    assert all(-1.0 <= v <= 1.0 for v in decay.values())


def test_alpha_eval_report_structure():
    report = alpha_eval_report(_grid(6, n_dates=10), ["good", "bad"], factor_signals=["good"])
    assert set(report) == {"ic", "decay", "min_names", "n_signals"}
    assert report["n_signals"] == 2
    assert set(report["decay"]) == {"good"}  # decay only for the requested factor subset


def test_alpha_eval_report_no_decay_without_price():
    frame = _grid(6).drop("close", "ticker")  # decay needs close + ticker
    report = alpha_eval_report(frame, ["good"], factor_signals=["good"])
    assert report["decay"] == {}
