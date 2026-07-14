"""Offline tests for the SEC fundamentals adapter (synthetic facts)."""

from datetime import date

import polars as pl
import pytest

from new_pipeline.adapters.fundamentals_sec import (
    build_fundamentals_features,
    merge_fundamentals,
    quarters_for_range,
)


def _facts(rows):
    return pl.DataFrame(
        rows,
        schema={
            "cik": pl.Int64, "adsh": pl.String, "form": pl.String, "filed": pl.Int64,
            "tag": pl.String, "ddate": pl.Int64, "qtrs": pl.Int64, "value": pl.Float64,
        },
        orient="row",
    )


def test_quarters_for_range_spans_boundaries():
    assert quarters_for_range(date(2025, 11, 1), date(2026, 2, 1)) == ["2025q4", "2026q1"]


def test_build_features_computes_ratios_from_primary_duration():
    facts = _facts(
        [
            # 10-Q: current quarter revenue 100, year-ago 80, NI 10, equity 50
            (1, "a-1", "10-Q", 20260210, "Revenues", 20251231, 1, 100.0),
            (1, "a-1", "10-Q", 20260210, "Revenues", 20241231, 1, 80.0),
            (1, "a-1", "10-Q", 20260210, "NetIncomeLoss", 20251231, 1, 10.0),
            (1, "a-1", "10-Q", 20260210, "StockholdersEquity", 20251231, 0, 50.0),
            # annual comparatives that must be ignored for a 10-Q
            (1, "a-1", "10-Q", 20260210, "Revenues", 20251231, 4, 400.0),
        ]
    )
    features = build_fundamentals_features(facts, {"AAA": 1})
    row = features.row(0, named=True)
    assert row["ticker"] == "AAA"
    assert row["filed"] == date(2026, 2, 10)
    assert row["fund_rev_yoy"] == pytest.approx(0.25)
    assert row["fund_net_margin"] == pytest.approx(0.10)
    assert row["fund_roe"] == pytest.approx(0.20)


def test_build_features_uses_annual_duration_for_10k():
    facts = _facts(
        [
            (2, "b-1", "10-K", 20260130, "Revenues", 20251231, 4, 400.0),
            (2, "b-1", "10-K", 20260130, "Revenues", 20241231, 4, 320.0),
            (2, "b-1", "10-K", 20260130, "NetIncomeLoss", 20251231, 4, 40.0),
            (2, "b-1", "10-K", 20260130, "StockholdersEquity", 20251231, 0, 200.0),
        ]
    )
    features = build_fundamentals_features(facts, {"BBB": 2})
    row = features.row(0, named=True)
    assert row["fund_rev_yoy"] == pytest.approx(0.25)
    assert row["fund_net_margin"] == pytest.approx(0.10)
    assert row["fund_roe"] == pytest.approx(0.20)


def test_revenue_tag_preference_order():
    facts = _facts(
        [
            (3, "c-1", "10-Q", 20260210, "RevenueFromContractWithCustomerExcludingAssessedTax",
             20251231, 1, 100.0),
            (3, "c-1", "10-Q", 20260210, "Revenues", 20251231, 1, 90.0),
            (3, "c-1", "10-Q", 20260210, "NetIncomeLoss", 20251231, 1, 9.0),
        ]
    )
    features = build_fundamentals_features(facts, {"CCC": 3})
    # "Revenues" outranks the contract-revenue tag
    assert features.row(0, named=True)["fund_net_margin"] == pytest.approx(0.10)


def test_merge_fundamentals_is_point_in_time():
    bars = pl.DataFrame(
        {
            "ticker": ["AAA"] * 3,
            "date": [date(2026, 2, 9), date(2026, 2, 10), date(2026, 2, 11)],
            "close": [1.0, 1.0, 1.0],
        }
    )
    features = pl.DataFrame(
        {
            "ticker": ["AAA"],
            "filed": [date(2026, 2, 10)],
            "fund_rev_yoy": [0.25],
            "fund_net_margin": [0.10],
            "fund_roe": [0.20],
        }
    )
    merged = merge_fundamentals(bars, features).sort("date")
    # the bar BEFORE the filing date must not see the filing (neutral 0.0)
    assert merged["fund_rev_yoy"].to_list() == [0.0, 0.25, 0.25]


def test_merge_fundamentals_empty_features_stays_neutral():
    bars = pl.DataFrame({"ticker": ["AAA"], "date": [date(2026, 1, 2)], "close": [1.0]})
    empty = build_fundamentals_features(
        _facts([]), {"AAA": 1}
    )
    merged = merge_fundamentals(bars, empty)
    assert merged["fund_net_margin"].to_list() == [0.0]
