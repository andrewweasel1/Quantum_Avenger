from datetime import date, datetime

from new_pipeline.adapters.fakes import FakeNewsSource


def test_default_fetch_loops_headlines_inclusive():
    items = FakeNewsSource().fetch("AAPL", date(2021, 1, 4), date(2021, 1, 6))
    assert [it.timestamp.date() for it in items] == [
        date(2021, 1, 4), date(2021, 1, 5), date(2021, 1, 6)
    ]


def test_default_fetch_as_of_truncates():
    items = FakeNewsSource().fetch(
        "AAPL", date(2021, 1, 4), date(2021, 1, 6), as_of=datetime(2021, 1, 5, 12, 0)
    )
    # FakeNewsSource stamps midnight; as_of keeps days through 2021-01-05.
    assert [it.timestamp.date() for it in items] == [date(2021, 1, 4), date(2021, 1, 5)]
