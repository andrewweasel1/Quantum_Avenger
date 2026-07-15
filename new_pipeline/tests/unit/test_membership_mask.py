"""Point-in-time membership masking of training rows."""

from datetime import date, timedelta

import polars as pl
from new_pipeline.adapters.base import UniverseMember
from new_pipeline.tournament.pipeline import apply_membership_mask


def _frame(ticker: str, start: date, days: int) -> pl.DataFrame:
    return pl.DataFrame({
        "date": [start + timedelta(days=i) for i in range(days)],
        "ticker": [ticker] * days,
        "close": [1.0] * days,
    })


def test_mask_filters_rows_to_window():
    frame = _frame("AAA", date(2021, 1, 1), 10)
    members = [UniverseMember("AAA", "Energy", date(2021, 1, 4), date(2021, 1, 8))]
    out = apply_membership_mask(frame, members)
    dates = out["date"].to_list()
    assert min(dates) == date(2021, 1, 4)
    assert max(dates) == date(2021, 1, 7)  # end-exclusive


def test_mask_open_ended_membership_keeps_tail():
    frame = _frame("AAA", date(2021, 1, 1), 5)
    members = [UniverseMember("AAA", "Energy", date(2021, 1, 3), None)]
    out = apply_membership_mask(frame, members)
    assert out.height == 3 and max(out["date"].to_list()) == date(2021, 1, 5)


def test_mask_multiple_disjoint_intervals_reentry():
    # Exit + re-entry (e.g. AAL): the gap rows drop, both stints survive.
    frame = _frame("AAA", date(2021, 1, 1), 12)
    members = [
        UniverseMember("AAA", "Energy", date(2021, 1, 1), date(2021, 1, 4)),
        UniverseMember("AAA", "Energy", date(2021, 1, 9), None),
    ]
    out = apply_membership_mask(frame, members).sort("date")
    dates = out["date"].to_list()
    assert dates == [date(2021, 1, 1), date(2021, 1, 2), date(2021, 1, 3),
                     date(2021, 1, 9), date(2021, 1, 10), date(2021, 1, 11),
                     date(2021, 1, 12)]


def test_mask_drops_tickers_without_membership():
    # A PIT fixture defines the whole investable set: unknown ticker -> dropped.
    frame = pl.concat([_frame("AAA", date(2021, 1, 1), 3), _frame("ZZZ", date(2021, 1, 1), 3)])
    members = [UniverseMember("AAA", "Energy", date(2020, 1, 1), None)]
    out = apply_membership_mask(frame, members)
    assert set(out["ticker"].unique().to_list()) == {"AAA"}


def test_build_training_frame_membership_none_is_noop_and_masking_bites():
    from new_pipeline.adapters import FakeMarketDataSource
    from new_pipeline.config import base, reload_config
    from new_pipeline.tournament.pipeline import build_training_frame

    reload_config()
    cfg = base.get_config()
    sectors = {"AAPL": "Information Technology"}
    kwargs = dict(source=FakeMarketDataSource(), cfg=cfg)
    full = build_training_frame(["AAPL"], sectors, date(2021, 1, 1), date(2021, 6, 30), **kwargs)
    exit_date = date(2021, 4, 1)
    masked = build_training_frame(
        ["AAPL"], sectors, date(2021, 1, 1), date(2021, 6, 30),
        membership=[UniverseMember("AAPL", "Information Technology", date(2000, 1, 1), exit_date)],
        **kwargs,
    )
    assert masked.height < full.height
    assert max(masked["date"].to_list()) < exit_date  # nothing at/after the exit
