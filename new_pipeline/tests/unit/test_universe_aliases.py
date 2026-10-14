from datetime import date

from new_pipeline.adapters.universe_static import StaticUniverseProvider


def test_aliases_returns_gazetteer():
    aliases = StaticUniverseProvider().aliases()
    assert isinstance(aliases["AAPL"], list)
    assert "Apple" in aliases["AAPL"]


def test_missing_fixture_is_empty(tmp_path):
    provider = StaticUniverseProvider(aliases_path=tmp_path / "nope.csv")
    assert provider.aliases() == {}


def test_as_of_filters_to_active_members():
    # LEH (Lehman Brothers) de-listed 2008-09-15; gone by 2020.
    active = StaticUniverseProvider().aliases(as_of=date(2020, 1, 1))
    assert "AAPL" in active
    assert "LEH" not in active
