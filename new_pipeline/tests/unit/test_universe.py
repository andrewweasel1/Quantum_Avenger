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


def test_sp500_fixture_loads_and_sectors_match_engine_names():
    """The S&P 500 snapshot must load and use exactly the engine's GICS names."""
    from pathlib import Path

    from new_pipeline.adapters.universe_static import StaticUniverseProvider
    from new_pipeline.config import get_config

    provider = StaticUniverseProvider(Path("new_pipeline/data/universe/sp500.csv"))
    sectors = provider.sectors()
    assert len(sectors) > 400  # a real index-scale universe
    engine_sectors = set(get_config().tournament.sectors)
    assert set(sectors.values()) <= engine_sectors  # no misspelled sector can slip in


def test_universe_path_config_selects_fixture(monkeypatch):
    from new_pipeline.adapters.factory import _build_universe
    from new_pipeline.config import reload_config

    monkeypatch.setenv("QA_DATA__UNIVERSE_PATH", "new_pipeline/data/universe/sp500.csv")
    cfg = reload_config()
    assert len(_build_universe(cfg).sectors()) > 400

    monkeypatch.delenv("QA_DATA__UNIVERSE_PATH")
    cfg = reload_config()
    assert len(_build_universe(cfg).sectors()) == 41  # packaged default
