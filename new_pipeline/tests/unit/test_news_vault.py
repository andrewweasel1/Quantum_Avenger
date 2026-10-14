from datetime import date

from new_pipeline.adapters.news_static import StaticNewsSource, VaultNewsSource
from new_pipeline.adapters.universe_static import StaticUniverseProvider
from new_pipeline.data.news_vault import _active_symbols, ingest_news_vault, load_news_vault


def test_ingest_and_replay_round_trip(tmp_path):
    src = StaticNewsSource()
    universe = StaticUniverseProvider()
    out = tmp_path / "news.parquet"
    summary = ingest_news_vault(src, universe, date(2021, 1, 1), date(2021, 6, 30), out)
    assert out.exists() and summary["rows"] > 0

    frame = load_news_vault(out)
    assert list(frame.columns) == ["timestamp", "ticker", "headline"]

    vault = VaultNewsSource(out)
    assert len(vault.headlines("AAPL", date(2021, 1, 8))) == 2
    assert len(vault.fetch("XOM", date(2021, 1, 1), date(2021, 3, 31))) == len(
        src.fetch("XOM", date(2021, 1, 1), date(2021, 3, 31))
    )


def test_survivorship_excludes_inactive_members():
    active = _active_symbols(StaticUniverseProvider(), date(2021, 1, 1), date(2021, 6, 30))
    assert "AAPL" in active
    assert "LEH" not in active  # Lehman Brothers delisted 2008-09-15
