"""PIT fixture builder: interval sweep, symbol normalization, sector joining."""

from datetime import date

import pytest
from new_pipeline.scripts.build_pit_universe import (
    build_rows,
    load_intervals,
    normalize_ticker,
    validate_fixture,
)


def test_normalize_ticker_class_share_and_renames():
    assert normalize_ticker("BRK-B") == "BRK.B"
    assert normalize_ticker(" fb ") == "META"  # rename folded after upper/strip
    assert normalize_ticker("BK") == "BNY"
    assert normalize_ticker("AAPL") == "AAPL"


def _history(rows: list[tuple[str, str]]) -> str:
    return "date,tickers\n" + "\n".join(f'{d},"{t}"' for d, t in rows)


def test_load_intervals_sweeps_membership_windows():
    text = _history([
        ("2016-01-04", "AAA,BBB"),
        ("2018-06-01", "AAA"),        # BBB exits (end-exclusive on this date)
        ("2020-03-02", "AAA,BBB"),    # BBB re-enters
        ("2021-01-04", "AAA,BBB"),
    ])
    intervals = load_intervals(text)
    assert intervals["AAA"] == [(date(2016, 1, 4), None)]
    assert intervals["BBB"] == [
        (date(2016, 1, 4), date(2018, 6, 1)),
        (date(2020, 3, 2), None),
    ]


def test_load_intervals_folds_renames_into_continuous_membership():
    # FB -> META mid-stream: one continuous open-ended interval under META.
    text = _history([
        ("2016-01-04", "FB,AAA"),
        ("2022-06-09", "META,AAA"),
        ("2023-01-03", "META,AAA"),
    ])
    intervals = load_intervals(text)
    assert intervals["META"] == [(date(2016, 1, 4), None)]
    assert "FB" not in intervals


def test_load_intervals_drops_pre_window_and_duplicate_classes():
    text = _history([
        ("2010-01-04", "AAA,GONE,GOOG"),
        ("2012-06-01", "AAA,GOOG"),   # GONE exits well before the 2015 window
        ("2021-01-04", "AAA,GOOG"),
    ])
    intervals = load_intervals(text)
    assert "GONE" not in intervals  # interval entirely before WINDOW_START
    assert "GOOG" not in intervals  # dropped second share class
    assert intervals["AAA"] == [(date(2010, 1, 4), None)]


def test_build_rows_hard_errors_on_unmapped_ticker():
    intervals = {"AAA": [(date(2020, 1, 2), None)]}
    with pytest.raises(SystemExit, match="AAA"):
        build_rows(intervals, sectors={})


def test_validate_fixture_rejects_overlapping_intervals():
    good = {
        "TSLA": [(date(2020, 12, 21), None)],
        "TWTR": [(date(2018, 6, 7), date(2022, 11, 1))],
        "FRC": [(date(2019, 1, 2), date(2023, 5, 4))],
    }
    good.update({f"T{i:03d}": [(date(2016, 1, 4), None)] for i in range(490)})
    validate_fixture(good)  # structural asserts pass

    bad = dict(good)
    bad["DUP"] = [(date(2016, 1, 4), date(2020, 1, 2)), (date(2019, 6, 3), None)]
    with pytest.raises(AssertionError, match="overlap"):
        validate_fixture(bad)
