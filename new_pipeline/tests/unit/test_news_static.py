from datetime import date, datetime

from new_pipeline.adapters.news_static import StaticNewsSource


def test_multi_headline_day():
    items = StaticNewsSource().headlines("AAPL", date(2021, 1, 8))
    assert len(items) == 2  # two intraday AAPL headlines that day
    assert all(it.symbol == "AAPL" for it in items)


def test_fetch_range_filters_by_date():
    jan = StaticNewsSource().fetch("AAPL", date(2021, 1, 1), date(2021, 1, 31))
    assert len(jan) >= 4
    assert all(it.timestamp.date().month == 1 for it in jan)  # February excluded


def test_as_of_cutoff_truncates_intraday():
    early = StaticNewsSource().fetch(
        "AAPL", date(2021, 1, 8), date(2021, 1, 8), as_of=datetime(2021, 1, 8, 10, 0)
    )
    assert len(early) == 1  # only the 09:30 item, not the 15:00 one


def test_missing_fixture_is_empty(tmp_path):
    src = StaticNewsSource(tmp_path / "nope.csv")
    assert src.headlines("AAPL", date(2021, 1, 8)) == []
    assert src.fetch("AAPL", date(2021, 1, 1), date(2021, 12, 31)) == []
