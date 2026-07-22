"""Forward extension of the Liquid PIT fixture: extend-vs-append semantics,
PIT-row protection, and the pre-floor history invariant."""

from datetime import date

import pytest
from new_pipeline.scripts.extend_liquid_universe import (
    assert_history_unchanged,
    fixture_rule_floor,
    merge_extend,
)


def _rows():
    return [
        {"ticker": "AAPL", "gics_sector": "Information Technology",
         "start_date": "2016-01-01", "end_date": ""},                    # PIT, open
        {"ticker": "XYZ", "gics_sector": "Small Cap Extended",
         "start_date": "2019-03-01", "end_date": "2026-02-01"},          # rule tail
        {"ticker": "OLD", "gics_sector": "Mid Cap Extended",
         "start_date": "2019-01-01", "end_date": "2021-06-01"},          # closed long ago
    ]


def test_floor_is_max_closed_end():
    assert fixture_rule_floor(_rows()) == date(2026, 2, 1)


def test_contiguous_extends_gap_appends_pit_skipped_new_labeled():
    rows = _rows()
    new = {
        "XYZ": [(date(2026, 2, 1), date(2026, 8, 1))],   # contiguous -> extend
        "OLD": [(date(2026, 3, 1), date(2026, 8, 1))],   # re-entry -> append
        "AAPL": [(date(2026, 2, 1), date(2026, 8, 1))],  # PIT ticker -> skip
        "NEWCO": [(date(2026, 2, 1), date(2026, 8, 1))],  # fresh -> append+label
    }
    merged, stats = merge_extend(rows, new, {"NEWCO": "Mid Cap Extended"},
                                 floor=date(2026, 2, 1))
    by = {(r["ticker"], r["start_date"]): r for r in merged}
    assert by[("XYZ", "2019-03-01")]["end_date"] == "2026-08-01"
    assert by[("OLD", "2026-03-01")]["end_date"] == "2026-08-01"
    assert by[("OLD", "2019-01-01")]["end_date"] == "2021-06-01"  # untouched
    assert ("AAPL", "2026-02-01") not in by
    assert by[("NEWCO", "2026-02-01")]["gics_sector"] == "Mid Cap Extended"
    assert stats == {"extended": 1, "appended": 2, "skipped_pit": 1, "new_tickers": 1}


def test_pre_floor_start_is_clamped_never_regenerated():
    rows = _rows()
    merged, stats = merge_extend(
        rows, {"OLD": [(date(2025, 6, 1), date(2026, 8, 1))]}, {},
        floor=date(2026, 2, 1),
    )
    row = [r for r in merged if r["ticker"] == "OLD" and r["end_date"] == "2026-08-01"][0]
    assert row["start_date"] == "2026-02-01"  # clamped to the floor


def test_history_invariant_catches_mutation():
    old = _rows()
    good, _ = merge_extend([dict(r) for r in old],
                           {"XYZ": [(date(2026, 2, 1), date(2026, 8, 1))]}, {},
                           floor=date(2026, 2, 1))
    assert_history_unchanged(old, good, date(2026, 2, 1))  # passes
    bad = [dict(r) for r in good]
    bad[1]["start_date"] = "2019-04-01"  # pre-floor mutation
    with pytest.raises(AssertionError):
        assert_history_unchanged(old, bad, date(2026, 2, 1))
