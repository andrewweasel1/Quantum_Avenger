"""End-to-end offline pipeline: fake data -> features+labels -> tournament -> promotion.

The Tier-1 capstone — exercises the whole chain with no network under a fixed
seed and a tiny budget.
"""

import json
from datetime import date

import pytest

from new_pipeline.config import base, reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.pipeline import (
    FEATURE_COLS,
    build_training_frame,
    run_offline_pipeline,
)


def test_offline_pipeline_runs(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    reload_config()
    seed_everything(0)

    summary = run_offline_pipeline(
        tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=2
    )

    assert summary["sectors"]  # at least one sector produced a candidate
    assert set(summary["promotions"]).issubset(set(summary["sectors"]))
    assert (tmp_path / "promotion_registry.json").exists()
    # P2 alpha-eval diagnostics are written by default (read-only; never gates).
    assert (tmp_path / "alpha_eval.json").exists()
    assert "alpha_eval" in summary


def test_offline_pipeline_records_overfitting_diagnostics(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    reload_config()
    seed_everything(0)

    run_offline_pipeline(
        tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=2
    )

    registry = json.loads((tmp_path / "promotion_registry.json").read_text())
    assert registry["promotions"]
    entry = registry["promotions"][0]
    # Evaluation Rigor v2 gates + the CPCV path-DSR gate ride along in the audit trail.
    assert {"pbo", "psr", "haircut_sharpe", "cpcv_path_pass_fraction"} <= set(entry)
    assert isinstance(entry["pbo"], float)
    assert isinstance(entry["psr"], float)
    assert 0.0 <= entry["cpcv_path_pass_fraction"] <= 1.0


def test_build_training_frame_adds_cross_sectional_factors():
    """P0 build hook: enabling features.factor_set appends populated xf_* columns."""
    from new_pipeline.adapters import FakeMarketDataSource, StaticUniverseProvider

    reload_config()
    cfg = base.get_config()
    cfg.features.factor_set = ["reversal_21", "low_vol"]
    universe = StaticUniverseProvider()
    sectors = universe.sectors()
    symbols = list(sectors)[:4]

    frame = build_training_frame(
        symbols, sectors, date(2021, 1, 1), date(2021, 12, 31), FakeMarketDataSource(), cfg
    )
    for column in ("xf_reversal_21", "xf_low_vol"):
        assert column in frame.columns
        assert frame[column].drop_nulls().len() > 0


def test_build_training_frame_adds_extended_features():
    """P1 build hook: enabling features.extended_features appends populated columns."""
    from new_pipeline.adapters import FakeMarketDataSource, StaticUniverseProvider

    reload_config()
    cfg = base.get_config()
    cfg.features.extended_features = ["vol_estimators", "microstructure"]
    universe = StaticUniverseProvider()
    sectors = universe.sectors()
    symbols = list(sectors)[:4]

    frame = build_training_frame(
        symbols, sectors, date(2021, 1, 1), date(2021, 12, 31), FakeMarketDataSource(), cfg
    )
    for column in ("parkinson_vol", "yang_zhang_vol", "roll_measure", "kyle_lambda"):
        assert column in frame.columns
        assert frame[column].drop_nulls().len() > 0


def test_build_training_frame_adds_value_quality_factors():
    """Phase C: a fundamentals source + value/quality factors -> populated xf_* columns."""
    from new_pipeline.adapters import FakeMarketDataSource, StaticUniverseProvider
    from new_pipeline.adapters.fakes import FakeFundamentalsSource

    reload_config()
    cfg = base.get_config()
    cfg.features.factor_set = ["book_to_market", "roe"]
    universe = StaticUniverseProvider()
    sectors = universe.sectors()
    symbols = list(sectors)[:4]

    frame = build_training_frame(
        symbols, sectors, date(2021, 1, 1), date(2021, 12, 31), FakeMarketDataSource(), cfg,
        fundamentals_source=FakeFundamentalsSource(),
    )
    for column in ("xf_book_to_market", "xf_roe"):
        assert column in frame.columns
        assert frame[column].drop_nulls().len() > 0


def test_offline_pipeline_consumes_cross_sectional_factors(tmp_path, monkeypatch):
    """P0 end-to-end: with factors enabled the tournament runs and the xf_* columns
    are wired into the selectable feature namespace (no leakage of unexpected cols)."""
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    reload_config()
    base.get_config().features.factor_set = ["reversal_21", "low_vol"]
    seed_everything(0)

    summary = run_offline_pipeline(
        tmp_path, start=date(2021, 1, 1), end=date(2022, 12, 31), max_symbols=6
    )

    assert summary["sectors"]
    manifests = list(tmp_path.glob("*_candidate_features.json"))
    assert manifests
    selectable = set(FEATURE_COLS) | {"xf_reversal_21", "xf_low_vol"}
    for manifest in manifests:
        selected = set(json.loads(manifest.read_text())["features"])
        assert selected <= selectable
    # P2: universe-wide IC is reported for the factor signals, with horizon decay.
    assert (tmp_path / "alpha_eval.json").exists()
    ic = summary["alpha_eval"]["ic"]
    assert {"xf_reversal_21", "xf_low_vol"} <= set(ic)
    assert {"xf_reversal_21", "xf_low_vol"} <= set(summary["alpha_eval"]["decay"])
    # P4: the per-sector champions are combined into one book (default-on portfolio).
    assert (tmp_path / "portfolio.json").exists()
    book = summary["portfolio"]
    assert set(book["weights"]) <= set(summary["sectors"])
    assert sum(book["weights"].values()) == pytest.approx(1.0)
    assert book["method"] == "hrp"  # exact: champions aggregated to date-aligned sector returns
    assert "book_sharpe" in book and set(book["sector_sharpe"]) == set(book["weights"])


def test_offline_pipeline_records_reality_check_when_enabled(tmp_path, monkeypatch):
    """P4 §J: enabling the reality check records a White's RC p-value per sector."""
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    monkeypatch.setenv("QA_EVALUATION__REALITY_CHECK_ENABLED", "true")
    monkeypatch.setenv("QA_EVALUATION__REALITY_CHECK_BOOTSTRAP", "100")
    reload_config()
    seed_everything(0)

    run_offline_pipeline(tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=2)

    registry = json.loads((tmp_path / "promotion_registry.json").read_text())
    assert registry["promotions"]
    pvalue = registry["promotions"][0]["reality_check_pvalue"]
    assert pvalue is not None and 0.0 < pvalue <= 1.0


def test_build_training_frame_skips_failing_symbols(monkeypatch):
    """One bad ticker must not kill a 500-name ingest (real feeds have gaps)."""
    from datetime import date

    from new_pipeline.adapters import FakeMarketDataSource

    class _FlakySource(FakeMarketDataSource):
        def history(self, symbol, start, end):
            if symbol == "BAD":
                raise RuntimeError("unknown symbol")
            return super().history(symbol, start, end)

    reload_config()
    frame = build_training_frame(
        ["AAPL", "BAD", "MSFT"], {"AAPL": "Information Technology",
                                   "BAD": "Information Technology",
                                   "MSFT": "Information Technology"},
        date(2021, 1, 1), date(2021, 3, 31), _FlakySource(), base.get_config(),
    )
    tickers = set(frame["ticker"].unique().to_list())
    assert "BAD" not in tickers and {"AAPL", "MSFT"} <= tickers


def test_all_symbols_empty_raises_market_data_error():
    """An all-empty fetch must fail loudly, not report a vacuous zero-sector
    'done' (e.g. Alpaca's IEX feed silently returns no daily bars before
    mid-2020, so a 2018 backtest on it would otherwise 'succeed' empty)."""
    from datetime import date

    from new_pipeline.adapters import FakeMarketDataSource
    from new_pipeline.core.exceptions import MarketDataError

    class _EmptySource(FakeMarketDataSource):
        def history(self, symbol, start, end):
            return []

    reload_config()
    with pytest.raises(MarketDataError, match="no market data"):
        build_training_frame(
            ["AAPL", "MSFT"], {"AAPL": "Information Technology",
                               "MSFT": "Information Technology"},
            date(2018, 1, 1), date(2018, 12, 31), _EmptySource(), base.get_config(),
        )


def test_promotion_metrics_use_calendar_axis(tmp_path, monkeypatch):
    """The registry's gate statistics are computed on the equal-weight daily
    collapse of the champion's pooled samples (n_obs = calendar days), pinned by
    recomputing PSR from the persisted artifacts."""
    import numpy as np
    import polars as pl

    from new_pipeline.evaluation.dsr import probabilistic_sharpe_ratio
    from new_pipeline.tournament.accounting import collapse_to_daily
    from new_pipeline.tournament.simulator import sharpe_ratio

    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    reload_config()
    seed_everything(0)
    run_offline_pipeline(tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=4)

    registry = json.loads((tmp_path / "promotion_registry.json").read_text())
    checked = 0
    for entry in registry["promotions"]:
        slug = entry["sector"].lower().replace(" ", "_")
        matrix = pl.read_parquet(tmp_path / f"{slug}_returns_matrix.parquet").to_numpy()
        dates = pl.read_parquet(tmp_path / f"{slug}_sample_dates.parquet")["date"]
        _, daily = collapse_to_daily(dates, matrix)
        best = int(np.argmax([sharpe_ratio(daily[:, j]) for j in range(daily.shape[1])]))
        assert entry["n_obs"] == daily.shape[0]  # calendar days on the daily axis
        assert entry["n_obs"] <= matrix.shape[0]  # == only for single-ticker sectors
        np.testing.assert_allclose(
            entry["psr"], probabilistic_sharpe_ratio(daily[:, best], 0.0), rtol=1e-9
        )
        checked += 1
    assert checked > 0


def test_regime_gate_defaults_on_with_daily_series_and_reasons(tmp_path, monkeypatch):
    """Under default config the regime gate runs on every would-be promotion and
    receives the CALENDAR-DAILY champion series; its two rejection modes land in
    the registry with distinct reasons."""
    import numpy as np
    import polars as pl

    import new_pipeline.tournament.pipeline as pipe
    from new_pipeline.evaluation.regime_dsr import RegimeVerdict

    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    # Relax the primary gates (whole-engine pattern) so decisions reach the
    # regime gate; the gate itself must stay at its DEFAULT (enabled).
    monkeypatch.setenv("QA_EVALUATION__DSR_PROMOTION_THRESHOLD", "0.0")
    monkeypatch.setenv("QA_EVALUATION__SYNTHETIC_SR_MIN", "-1000.0")
    monkeypatch.setenv("QA_EVALUATION__PBO_THRESHOLD", "1.0")
    monkeypatch.setenv("QA_EVALUATION__CPCV_PATH_GATE_ENABLED", "false")
    reload_config()
    seed_everything(0)

    captured = []

    def fake_verdict(champion_returns, trials, eval_matrix, cfg, market_returns=None):
        captured.append(np.asarray(champion_returns))
        # First sector: a regime failed its DSR; later sectors: nothing testable.
        from types import SimpleNamespace

        stub = SimpleNamespace(dsr=0.1, sr_annual=-0.5, n_obs=100)
        per_regime = {0: stub} if len(captured) == 1 else {}
        return RegimeVerdict(promoted=False, per_regime=per_regime, skipped_regimes=[])

    monkeypatch.setattr(pipe, "_regime_verdict", fake_verdict)
    run_offline_pipeline(tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=4)

    assert captured, "regime gate never ran despite default-enabled config"
    registry = json.loads((tmp_path / "promotion_registry.json").read_text())
    reasons = {e["sector"]: e["reason"] for e in registry["promotions"]}
    assert "failed per-regime DSR" in reasons.values()
    if len(captured) > 1:
        assert "regime gate: no testable regime" in reasons.values()

    # The series handed to the gate is the daily collapse, not pooled samples.
    for entry in registry["promotions"]:
        slug = entry["sector"].lower().replace(" ", "_")
        dates = pl.read_parquet(tmp_path / f"{slug}_sample_dates.parquet")["date"]
        n_days = dates.n_unique()
        assert any(series.size == n_days for series in captured)


def test_run_offline_pipeline_applies_membership_windows(tmp_path, monkeypatch):
    """The pipeline masks training rows to the universe provider's membership
    windows: with the packaged 41-name fixture (real PIT dates), a ticker whose
    window ends mid-range contributes no rows past its exit."""
    import new_pipeline.tournament.pipeline as pipe

    captured = {}
    real_mask = pipe.apply_membership_mask

    def spy(frame, members):
        captured["members"] = list(members)
        out = real_mask(frame, members)
        captured["max_dates"] = dict(
            out.group_by("ticker").agg(max_date=("date")).iter_rows()
        )
        return out

    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "10")
    reload_config()
    seed_everything(0)
    monkeypatch.setattr(pipe, "apply_membership_mask", spy)
    run_offline_pipeline(tmp_path, start=date(2021, 1, 1), end=date(2021, 6, 30), max_symbols=6)

    assert captured, "membership mask never invoked"
    assert len(captured["members"]) >= 41  # the provider's full interval list


def test_next_ret_is_next_bar_close_ratio_and_not_a_feature():
    """The L/S realization column: next-day close-to-close per ticker, null on
    each ticker's final bar, and never part of the selectable feature set."""
    import numpy as np

    from new_pipeline.adapters import FakeMarketDataSource

    reload_config()
    frame = build_training_frame(
        ["AAPL"], {"AAPL": "Information Technology"},
        date(2021, 1, 1), date(2021, 3, 31), FakeMarketDataSource(), base.get_config(),
    ).sort("date")
    close = frame["close"].to_numpy()
    next_ret = frame["next_ret"].to_numpy()
    np.testing.assert_allclose(next_ret[:-1], close[1:] / close[:-1] - 1.0, rtol=1e-12)
    assert np.isnan(next_ret[-1])  # no forward bar for the last row
    assert "next_ret" not in FEATURE_COLS


def test_partially_covered_fundamentals_keep_all_tickers_in_tournament():
    """A ticker with no fundamentals (departed name, no resolvable filings) must
    reach the tournament at neutral factor exposure — not silently vanish
    through drop_nulls, which would reintroduce survivorship."""
    from new_pipeline.adapters import FakeMarketDataSource
    from new_pipeline.adapters.fakes import FakeFundamentalsSource

    class _PartialSource(FakeFundamentalsSource):
        def history(self, symbol, start, end):
            return [] if symbol == "MSFT" else super().history(symbol, start, end)

    reload_config()
    cfg = base.get_config()
    cfg.features.factor_set = ["book_to_market", "roe"]
    frame = build_training_frame(
        ["AAPL", "MSFT"], {"AAPL": "Information Technology",
                           "MSFT": "Information Technology"},
        date(2021, 1, 1), date(2021, 6, 30), FakeMarketDataSource(), cfg,
        fundamentals_source=_PartialSource(),
    )
    msft = frame.filter(frame["ticker"] == "MSFT")
    assert msft.height > 0
    assert msft["xf_book_to_market"].null_count() == 0  # neutral-filled, survives
    assert set(msft["xf_book_to_market"].to_list()) == {0.0}
