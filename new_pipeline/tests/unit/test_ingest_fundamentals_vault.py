"""Fundamentals vault ingest: merge schema + resume + coverage (pure helpers)."""

from new_pipeline.scripts.ingest_fundamentals_vault import (
    coverage_table,
    load_cik_overrides,
    merge_vault,
    write_ticker_csv,
)


def test_merge_writes_static_source_schema_and_sorts(tmp_path):
    by = tmp_path / "by_ticker"
    by.mkdir()
    write_ticker_csv(by / "BBB.csv", "BBB", [
        {"as_of": "2021-05-01", "book_value_per_share": 5.0,
         "earnings_per_share": 1.0, "return_on_equity": 0.1},
    ])
    write_ticker_csv(by / "AAA.csv", "AAA", [
        {"as_of": "2021-08-01", "book_value_per_share": 7.0,
         "earnings_per_share": 2.0, "return_on_equity": 0.2},
        {"as_of": "2021-05-01", "book_value_per_share": 6.0,
         "earnings_per_share": 1.5, "return_on_equity": 0.15},
    ])
    out = tmp_path / "snapshots.csv"
    assert merge_vault(by, out) == 3

    from datetime import date

    from new_pipeline.adapters.fundamentals_static import StaticFundamentalsSource

    source = StaticFundamentalsSource(out)
    snaps = source.history("AAA", date(2021, 1, 1), date(2021, 12, 31))
    assert [s.as_of.isoformat() for s in snaps] == ["2021-05-01", "2021-08-01"]
    assert snaps[0].book_value_per_share == 6.0


def test_coverage_table_counts_by_sector(tmp_path):
    class _Uni:
        def sectors(self):
            return {"AAA": "Energy", "BBB": "Energy", "CCC": "Utilities"}

    table = coverage_table(_Uni(), covered={"AAA"})
    assert ("Energy", 1, 2) in table and ("Utilities", 0, 1) in table


def test_load_cik_overrides(tmp_path):
    path = tmp_path / "overrides.csv"
    path.write_text("ticker,cik\nTWTR,1418091\n")
    assert load_cik_overrides(str(path)) == {"TWTR": 1418091}
    assert load_cik_overrides("") == {}
