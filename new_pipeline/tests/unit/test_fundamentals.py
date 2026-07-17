"""Unit tests for the point-in-time fundamentals data layer (Phase C)."""

from datetime import date

import polars as pl
from new_pipeline.adapters.factory import build_fundamentals_source
from new_pipeline.adapters.fakes import FakeFundamentalsSource
from new_pipeline.adapters.fundamentals_static import StaticFundamentalsSource
from new_pipeline.config import get_config, reload_config
from new_pipeline.data.fundamentals import FUNDAMENTAL_COLUMNS, attach_fundamentals


def test_fake_fundamentals_deterministic_and_quarterly():
    fake = FakeFundamentalsSource()
    first = fake.history("AAPL", date(2021, 1, 1), date(2021, 12, 31))
    assert first == fake.history("AAPL", date(2021, 1, 1), date(2021, 12, 31))  # deterministic
    assert first and all(snap.as_of.month in (1, 4, 7, 10) for snap in first)  # quarterly
    assert all(snap.book_value_per_share > 0 and snap.return_on_equity > 0 for snap in first)
    assert fake.history("AAPL", date(2021, 1, 1), date(2020, 1, 1)) == []  # end < start


def test_attach_fundamentals_is_point_in_time():
    frame = pl.DataFrame(
        {"ticker": ["AAA", "AAA"], "date": [date(2021, 2, 15), date(2021, 5, 15)],
         "close": [100.0, 100.0]}
    )
    out = attach_fundamentals(frame, FakeFundamentalsSource())
    for column in FUNDAMENTAL_COLUMNS:
        assert column in out.columns
    # the Feb row uses the latest snapshot knowable then (Jan), never a future one.
    knowable = FakeFundamentalsSource().history("AAA", date(2021, 2, 15), date(2021, 2, 15))[-1]
    feb = out.filter(pl.col("date") == date(2021, 2, 15))
    assert feb["book_value_per_share"][0] == knowable.book_value_per_share


def test_attach_fundamentals_no_snapshots_yields_null_columns():
    class _Empty:
        def history(self, *_args):
            return []

    out = attach_fundamentals(
        pl.DataFrame({"ticker": ["A"], "date": [date(2021, 1, 1)], "close": [1.0]}), _Empty()
    )
    assert out["book_value_per_share"].is_null().all()


def test_attach_fundamentals_tolerates_datetime_date_column():
    """A Datetime `date` column (e.g. after the markov pandas round-trip) must
    still join: source.history compares against date-typed as_of, so datetime
    bounds are normalized rather than raising date-vs-datetime TypeError."""
    frame = pl.DataFrame(
        {"ticker": ["AAA", "AAA"], "date": [date(2021, 2, 15), date(2021, 5, 15)],
         "close": [100.0, 100.0]}
    ).with_columns(pl.col("date").cast(pl.Datetime))
    out = attach_fundamentals(frame, FakeFundamentalsSource())
    assert out["book_value_per_share"].null_count() == 0  # joined, no crash


def test_static_fundamentals_fixture():
    stat = StaticFundamentalsSource()
    snaps = stat.history("AAPL", date(2020, 1, 1), date(2021, 12, 31))
    assert len(snaps) == 3 and snaps[0].as_of < snaps[-1].as_of  # loaded + sorted
    assert stat.history("NOPE", date(2020, 1, 1), date(2021, 12, 31)) == []  # unknown ticker


def test_build_fundamentals_source_offline_is_fake():
    reload_config()
    assert isinstance(build_fundamentals_source(get_config()), FakeFundamentalsSource)


def test_edgar_fundamentals_maps_injected_records():
    from new_pipeline.adapters.fundamentals_edgar import EdgarFundamentalsSource

    records = [
        {"as_of": date(2021, 6, 30), "book_value_per_share": 4.2,
         "earnings_per_share": 1.6, "return_on_equity": 0.31},
        {"as_of": date(2021, 3, 31), "book_value_per_share": 4.0,
         "earnings_per_share": 1.5, "return_on_equity": 0.30},
        {"as_of": "2022-06-30", "book_value_per_share": 9.9,
         "earnings_per_share": 9.9, "return_on_equity": 0.9},  # after `end` -> dropped
    ]
    source = EdgarFundamentalsSource(fetch=lambda symbol, start, end: records)
    snaps = source.history("X", date(2021, 1, 1), date(2021, 12, 31))
    assert len(snaps) == 2  # the 2022 record is excluded
    assert snaps[0].as_of < snaps[1].as_of  # sorted ascending
    assert snaps[0].earnings_per_share == 1.5


def test_build_fundamentals_source_prefers_fixture_in_live_modes(monkeypatch):
    """Vault-first: a set fixture_path replays with zero network even in paper
    mode — fundamentals are never re-fetched inline inside a backtest."""
    from new_pipeline.adapters.factory import build_fundamentals_source
    from new_pipeline.adapters.fundamentals_static import StaticFundamentalsSource
    from new_pipeline.config import base, reload_config

    reload_config()
    cfg = base.get_config()
    cfg.system.run_mode = "paper"
    cfg.fundamentals.fixture_path = "new_pipeline/data/fundamentals/snapshots.csv"
    source = build_fundamentals_source(cfg)
    assert isinstance(source, StaticFundamentalsSource)
