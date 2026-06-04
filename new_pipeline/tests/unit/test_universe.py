from datetime import date

from new_pipeline.adapters import StaticUniverseProvider

_EXPECTED_SECTORS = {
    "Information Technology",
    "Health Care",
    "Financials",
    "Consumer Discretionary",
    "Communication Services",
    "Industrials",
    "Consumer Staples",
    "Energy",
    "Utilities",
    "Real Estate",
    "Materials",
}


def test_loads_all_eleven_gics_sectors():
    provider = StaticUniverseProvider()
    assert set(provider.sectors().values()) == _EXPECTED_SECTORS


def test_point_in_time_membership_is_survivorship_safe():
    provider = StaticUniverseProvider()
    # Lehman was in the index in 2007 but delisted by 2020.
    assert "LEH" in provider.symbols(date(2007, 6, 1))
    assert "LEH" not in provider.symbols(date(2020, 1, 1))
    # Alphabet class A only entered the universe in 2014.
    assert "GOOGL" not in provider.symbols(date(2007, 6, 1))
    assert "GOOGL" in provider.symbols(date(2020, 1, 1))


def test_members_without_as_of_returns_everything():
    provider = StaticUniverseProvider()
    assert len(provider.members()) == len(provider.symbols())
    assert len(provider.members()) >= 40
