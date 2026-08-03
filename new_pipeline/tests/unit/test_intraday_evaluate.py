"""Session-return gauntlet + full ORB run integration on a synthetic vault."""

import json
from datetime import UTC, date, datetime, timedelta

import numpy as np
import polars as pl
from new_pipeline.config import base, reload_config
from new_pipeline.intraday.calendar import Session, write_fixture
from new_pipeline.intraday.evaluate import evaluate_orb, market_series, record
from new_pipeline.intraday.orb import Combo
from new_pipeline.scripts.ingest_minute_vault import _write_symbol_month


def _sessions(n, start=date(2026, 1, 5)):
    out, d = {}, start
    while len(out) < n:
        if d.weekday() < 5:
            out[d] = Session(d, datetime(d.year, d.month, d.day, 14, 30, tzinfo=UTC),
                             datetime(d.year, d.month, d.day, 21, 0, tzinfo=UTC))
        d += timedelta(days=1)
    return out


def _session_minutes(day, ticker, drift):
    """Deterministic winning ORB session: breakout after a 5-min range, close
    drifting up by ``drift`` — hand-checkable and HMM-decodable across days."""
    o = datetime(day.year, day.month, day.day, 14, 30, tzinfo=UTC)
    rows = [(0, 10.0, 10.5, 9.8, 10.2), (4, 10.2, 10.7, 10.0, 10.4),
            (6, 10.5, 10.9, 10.4, 10.8), (7, 10.85, 11.0, 10.8, 10.9),
            (200, 10.9, 11.1, 10.85, 10.95 + drift),
            (380, 11.0 + drift, 11.1 + drift, 10.9, 11.0 + drift)]
    return pl.DataFrame({
        "ticker": [ticker] * len(rows),
        "ts": [o + timedelta(minutes=m) for m, *_ in rows],
        "open": [r[1] for r in rows], "high": [r[2] for r in rows],
        "low": [r[3] for r in rows], "close": [float(r[4]) for r in rows],
        "volume": [500_000] * len(rows),
        "session_date": [day] * len(rows),
    })


def _daily_from(minutes_by_day, ticker="AAA"):
    rows = []
    for day, frame in sorted(minutes_by_day.items()):
        sub = frame.filter(pl.col("ticker") == ticker).sort("ts")
        rows.append((day, ticker, sub["open"][0], sub["high"].max(), sub["low"].min(),
                     sub["close"][-1], int(sub["volume"].sum()),
                     float(sub["close"][-1] * sub["volume"].sum())))
    return pl.DataFrame(rows, schema=["date", "ticker", "open", "high", "low",
                                      "close", "volume", "dollar_vol"], orient="row")


def test_market_series_aligns_to_days():
    daily = pl.DataFrame({
        "date": [date(2026, 1, 5), date(2026, 1, 6), date(2026, 1, 7)] * 2,
        "ticker": ["A"] * 3 + ["B"] * 3,
        "close": [10.0, 11.0, 11.0, 20.0, 18.0, 18.0],
    })
    rets, vol = market_series(daily, [date(2026, 1, 6), date(2026, 1, 7)])
    assert abs(rets[0] - ((0.1 + (-0.1)) / 2)) < 1e-12  # equal-weight mean
    assert rets[1] == 0.0 and len(vol) == 2


def test_evaluate_orb_planted_edge_and_registry_row(tmp_path):
    reload_config()
    cfg = base.get_config()
    cfg.intraday.entry_buffer_bps = 0.0
    cfg.evaluation.min_regime_obs = 10
    cfg.long_short.null_iterations = 4
    sessions = _sessions(90)
    rng = np.random.default_rng(0)
    minutes_by_day = {d: _session_minutes(d, "AAA", drift=float(rng.normal(0.05, 0.02)))
                      for d in sessions}
    daily = _daily_from(minutes_by_day)
    picks = {d: ["AAA"] for d in sessions}
    stats = pl.DataFrame({"date": list(sessions), "ticker": ["AAA"] * len(sessions),
                          "spread_bps": [30.0] * len(sessions),
                          "vol_minute": [0.0] * len(sessions)})
    combos = [Combo(5, "or_low", 0.0), Combo(30, "or_low", 0.0)]
    from new_pipeline.intraday.simulate import run_backtest
    matrix, days, ledger = run_backtest(minutes_by_day, sessions, picks, combos,
                                        stats, cfg, equity=100_000.0)
    assert matrix.shape == (90, 2) and (matrix[:, 0] > 0).mean() > 0.9

    result = evaluate_orb(matrix, days, combos, ledger, daily, minutes_by_day,
                          sessions, picks, stats, cfg, equity=100_000.0, seed=0)
    assert result["report"].dsr > 0.9  # planted edge survives deflation
    # a bare combo list rides the compat path as a single "default" variant
    assert result["champion"].key == "default|k5|or_low|none"
    assert result["champion"].combo.k_minutes == 5
    diag = result["diagnostics"]
    assert diag["n_trades"] == 90 and 0 < diag["cost_share_of_gross"] < 1
    assert len(diag["timing_null_sharpes"]) == 4
    row = record(tmp_path / "registry.json", result,
                 model_path=str(tmp_path / "cand.json"))
    assert row["sector"] == "Intraday ORB"
    saved = json.loads((tmp_path / "registry.json").read_text())
    assert saved["promotions"][0]["synthetic_sharpe"] == row["synthetic_sharpe"]


def test_full_run_cli_on_synthetic_vault(tmp_path, monkeypatch):
    """End-to-end: vault files -> run() -> artifacts + registry, deterministic."""
    reload_config()
    cfg = base.get_config()
    vault = tmp_path / "vault"
    fixture = tmp_path / "sessions.csv"
    sessions = _sessions(40, start=date(2026, 3, 2))
    write_fixture(list(sessions.values()), fixture)
    monkeypatch.setattr("new_pipeline.intraday.run.load_sessions",
                        lambda: dict(sessions))
    monkeypatch.setattr("new_pipeline.intraday.run.segment_symbols",
                        lambda _cfg: ["AAA", "BBB"])
    cfg.intraday.vault_dir = str(vault)
    cfg.intraday.entry_buffer_bps = 0.0
    cfg.intraday.min_adv_dollars = 1000.0
    cfg.intraday.min_price = 1.0
    cfg.evaluation.min_regime_obs = 10
    cfg.long_short.null_iterations = 2

    from new_pipeline.adapters.base import MinuteBar
    rng = np.random.default_rng(1)
    for sym in ("AAA", "BBB"):
        by_month: dict[tuple[int, int], list] = {}
        for day in sessions:
            frame = _session_minutes(day, sym, drift=float(rng.normal(0.03, 0.03)))
            bars = [MinuteBar(r["ts"], r["open"], r["high"], r["low"], r["close"],
                              r["volume"], r["close"]) for r in frame.iter_rows(named=True)]
            by_month.setdefault((day.year, day.month), []).extend(bars)
        for (y, m), bars in by_month.items():
            _write_symbol_month(vault, sym, y, m, bars)

    from new_pipeline.intraday.run import run
    out = tmp_path / "run_out"
    days = sorted(sessions)
    res = run(days[0], days[-1], out, equity=100_000.0, seed=0)
    assert (out / "intraday_orb_returns_matrix.parquet").exists()
    assert (out / "intraday_orb_candidate.json").exists()
    assert (out / "promotion_registry.json").exists()
    assert res["row"]["sector"] == "Intraday ORB"
    matrix1 = pl.read_parquet(out / "intraday_orb_returns_matrix.parquet")
    assert matrix1.height == len(sessions)
    # determinism: identical rerun reproduces the matrix bit-for-bit
    out2 = tmp_path / "run_out2"
    run(days[0], days[-1], out2, equity=100_000.0, seed=0)
    matrix2 = pl.read_parquet(out2 / "intraday_orb_returns_matrix.parquet")
    assert matrix1.equals(matrix2)


def test_trial_family_crosses_scanners_and_constructions():
    """The scanner weighting is a real experimental axis: each variant trades
    its OWN pick list, every (variant x construction) pair is a priced column,
    and the ledger tags trades with the variant that generated them."""
    reload_config()
    cfg = base.get_config()
    cfg.intraday.entry_buffer_bps = 0.0
    cfg.intraday.scanner_variants = ["attention", "tradable"]
    from new_pipeline.intraday.orb import Trial, trials_from_config
    from new_pipeline.intraday.simulate import run_backtest_trials

    sessions = _sessions(6)
    minutes_by_day = {}
    for d in sessions:
        minutes_by_day[d] = pl.concat([_session_minutes(d, "AAA", 0.05),
                                       _session_minutes(d, "BBB", 0.02)])
    # attention picks AAA only, tradable picks BBB only -> different books
    picks_by_variant = {"attention": {d: ["AAA"] for d in sessions},
                        "tradable": {d: ["BBB"] for d in sessions}}
    stats = pl.DataFrame({"date": list(sessions) * 2,
                          "ticker": ["AAA"] * len(sessions) + ["BBB"] * len(sessions),
                          "spread_bps": [30.0] * (2 * len(sessions)),
                          "vol_minute": [0.0] * (2 * len(sessions))})
    trials = [Trial("attention", Combo(5, "or_low", 0.0)),
              Trial("tradable", Combo(5, "or_low", 0.0))]
    matrix, days, ledger = run_backtest_trials(minutes_by_day, sessions,
                                               picks_by_variant, trials, stats,
                                               cfg, equity=100_000.0)
    assert matrix.shape == (6, 2)
    assert not np.allclose(matrix[:, 0], matrix[:, 1])  # different picks, different P&L
    tagged = {t.combo_key for t in ledger}
    assert tagged == {"attention|k5|or_low|none", "tradable|k5|or_low|none"}
    assert {t.ticker for t in ledger if t.combo_key.startswith("attention")} == {"AAA"}
    # the config cross is the full family, and it follows the strategy family
    cfg.intraday.scanner_variants = ["attention", "tradable"]
    cfg.intraday.strategy = "orb"
    assert len(trials_from_config(cfg)) == 24   # 2 scanners x 12 ORB combos
    cfg.intraday.strategy = "meanrev"
    assert len(trials_from_config(cfg)) == 32   # 2 scanners x 16 MR combos
    assert all(t.combo.key.count("|") == 3 for t in trials_from_config(cfg))
