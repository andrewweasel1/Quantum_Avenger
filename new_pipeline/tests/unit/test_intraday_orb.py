"""ORB mechanics + session simulator: every fill convention pinned by hand."""

from datetime import UTC, date, datetime, timedelta

import numpy as np
import polars as pl
from new_pipeline.config import base, reload_config
from new_pipeline.intraday.calendar import Session
from new_pipeline.intraday.orb import Combo, opening_range, trade_path
from new_pipeline.intraday.simulate import run_backtest, run_session

OPEN = datetime(2026, 3, 2, 14, 30, tzinfo=UTC)
CLOSE = datetime(2026, 3, 2, 21, 0, tzinfo=UTC)
SESSION = Session(date(2026, 3, 2), OPEN, CLOSE)


def _bars(rows):
    """rows: (minute_offset, open, high, low, close). Returns numpy columns."""
    ts = np.array([OPEN + timedelta(minutes=m) for m, *_ in rows])
    cols = np.array([[o, h, lo, c] for _, o, h, lo, c in rows], dtype=float)
    return ts, cols[:, 0], cols[:, 1], cols[:, 2], cols[:, 3]


def test_opening_range_and_next_bar_entry():
    ts, o, h, lo, c = _bars([
        (0, 10.0, 10.5, 9.8, 10.2),   # range bars (K=5 -> minutes 0-4)
        (2, 10.2, 10.6, 10.0, 10.4),
        (4, 10.4, 10.7, 10.2, 10.3),  # or_high 10.7, or_low 9.8
        (6, 10.3, 10.6, 10.2, 10.6),  # close 10.6 < trigger, no fire
        (8, 10.6, 10.9, 10.5, 10.8),  # close 10.8 > 10.7 -> signal
        (9, 10.85, 11.0, 10.7, 10.9),  # ENTRY at this bar's open 10.85
        (10, 10.9, 11.1, 10.8, 11.0),
        (380, 11.0, 11.05, 10.9, 11.02),  # flatten region
    ])
    or_high, or_low, after = opening_range(ts, h, lo, OPEN, 5)
    assert (or_high, or_low, after) == (10.7, 9.8, 3)
    path = trade_path(ts, o, h, lo, c, OPEN, CLOSE,
                      Combo(5, "or_low", 0.0), 0.0, 5)
    assert path.entry_idx == 5 and path.entry_px == 10.85
    assert path.exit_reason == "close" and path.exit_px == 11.02  # flattened


def test_stop_conventions_gap_through_and_intrabar():
    rows = [(0, 10.0, 10.5, 9.8, 10.2), (4, 10.2, 10.7, 10.0, 10.4),
            (6, 10.5, 10.9, 10.4, 10.8),   # signal (trigger 10.7)
            (7, 10.85, 10.9, 10.8, 10.85)]  # entry at 10.85, stop or_low=9.8
    # intrabar stop: low touches 9.8 while the open stays above
    ts, o, h, lo, c = _bars(rows + [(8, 10.0, 10.1, 9.7, 9.9), (380, 9.9, 10, 9.8, 9.9)])
    path = trade_path(ts, o, h, lo, c, OPEN, CLOSE, Combo(5, "or_low", 0.0), 0.0, 5)
    assert path.exit_reason == "stop" and path.exit_px == 9.8  # stop price fill
    # gap-through: the bar OPENS below the stop -> fill at the open, not the stop
    ts, o, h, lo, c = _bars(rows + [(8, 9.5, 9.6, 9.4, 9.5), (380, 9.5, 9.6, 9.4, 9.5)])
    path = trade_path(ts, o, h, lo, c, OPEN, CLOSE, Combo(5, "or_low", 0.0), 0.0, 5)
    assert path.exit_reason == "stop" and path.exit_px == 9.5


def test_stop_beats_target_within_one_bar_and_target_fills():
    rows = [(0, 10.0, 10.5, 9.9, 10.2), (4, 10.2, 10.7, 10.0, 10.4),
            (6, 10.5, 10.9, 10.4, 10.8),
            (7, 11.0, 11.0, 10.9, 11.0)]  # entry 11.0; stop or_mid=(10.7+9.9)/2=10.3
    # 2R target = 11.0 + 2*(11.0-10.3) = 12.4; a wide bar touches both -> stop wins
    ts, o, h, lo, c = _bars(rows + [(8, 11.0, 12.5, 10.2, 11.5), (380, 11, 12, 10.9, 11)])
    path = trade_path(ts, o, h, lo, c, OPEN, CLOSE, Combo(5, "or_mid", 2.0), 0.0, 5)
    assert path.exit_reason == "stop" and path.exit_px == 10.3
    # clean target touch fills at the target price
    ts, o, h, lo, c = _bars(rows + [(8, 11.2, 12.45, 11.1, 12.4), (380, 12.4, 12.5, 12.3, 12.4)])
    path = trade_path(ts, o, h, lo, c, OPEN, CLOSE, Combo(5, "or_mid", 2.0), 0.0, 5)
    assert path.exit_reason == "target" and abs(path.exit_px - 12.4) < 1e-9


def test_early_close_flatten_and_no_late_entries():
    early = Session(date(2026, 11, 27), datetime(2026, 11, 27, 14, 30, tzinfo=UTC),
                    datetime(2026, 11, 27, 18, 0, tzinfo=UTC))  # 13:00 ET close
    base_ts = early.open_utc
    rows = [(0, 10.0, 10.5, 9.8, 10.2), (4, 10.2, 10.7, 10.0, 10.4),
            (6, 10.5, 10.9, 10.4, 10.8), (7, 10.85, 10.9, 10.8, 10.85),
            (200, 10.9, 11.0, 10.8, 10.95),   # 17:50 UTC — inside buffer window
            (208, 11.0, 11.1, 10.9, 11.05)]   # 17:58 — after 17:55 cutoff
    ts = np.array([base_ts + timedelta(minutes=m) for m, *_ in rows])
    cols = np.array([r[1:] for r in rows], dtype=float)
    path = trade_path(ts, cols[:, 0], cols[:, 1], cols[:, 2], cols[:, 3],
                      early.open_utc, early.close_utc, Combo(5, "or_low", 0.0), 0.0, 5)
    # flatten at the last bar before 17:55 UTC (= 12:55 ET on the half day)
    assert path.exit_reason == "close" and path.exit_px == 10.95


def _session_frame(ticker, entry_px=10.85):
    rows = [(0, 10.0, 10.5, 9.8, 10.2), (4, 10.2, 10.7, 10.0, 10.4),
            (6, 10.5, 10.9, 10.4, 10.8), (7, entry_px, 11.0, 10.8, 10.9),
            (380, 11.0, 11.05, 10.9, 11.0)]
    return pl.DataFrame({
        "ticker": [ticker] * len(rows),
        "ts": [OPEN + timedelta(minutes=m) for m, *_ in rows],
        "open": [r[1] for r in rows], "high": [r[2] for r in rows],
        "low": [r[3] for r in rows], "close": [r[4] for r in rows],
        "volume": [200_000] * len(rows),
    })


def test_run_session_sizing_costs_and_concurrency():
    reload_config()
    cfg = base.get_config()
    cfg.intraday.risk_bps = 50.0          # $500 risk on 100k
    cfg.intraday.max_position_pct = 5.0   # $5k notional cap
    cfg.intraday.max_concurrent = 2
    cfg.intraday.entry_buffer_bps = 0.0
    cfg.intraday.spread_floor_bps = 15.0
    minutes = pl.concat([_session_frame("AAA"), _session_frame("BBB"),
                         _session_frame("CCC")])
    stats = pl.DataFrame({"date": [SESSION.day] * 3, "ticker": ["AAA", "BBB", "CCC"],
                          "spread_bps": [40.0] * 3, "vol_minute": [0.0] * 3})
    rets, ledger = run_session(minutes, SESSION, ["AAA", "BBB", "CCC"],
                               [Combo(5, "or_low", 0.0)], stats, cfg, equity=100_000.0)
    assert len(ledger) == 2  # concurrency cap admitted first two by entry time
    t = ledger[0]
    # sizing: risk $500 / (10.85-9.8)=1.05 -> 476; notional cap 5000/10.85 -> 460 binds
    assert t.shares == 460
    # costs: half-spread max(40/2, 15)=20bps per side, zero impact (vol_minute 0)
    expected_cost = (460 * 10.85 * 20 + 460 * 11.0 * 20) / 1e4
    assert abs(t.cost_dollars - expected_cost) < 1e-6
    assert abs(t.gross_pnl - 460 * (11.0 - 10.85)) < 1e-9
    assert abs(rets["k5|or_low|none"] - (2 * t.net_pnl) / 100_000.0) < 1e-12


def test_run_backtest_matrix_shape_and_flat_days():
    reload_config()
    cfg = base.get_config()
    cfg.intraday.entry_buffer_bps = 0.0
    day2 = date(2026, 3, 3)
    sessions = {SESSION.day: SESSION,
                day2: Session(day2, OPEN + timedelta(days=1), CLOSE + timedelta(days=1))}
    minutes_by_day = {SESSION.day: _session_frame("AAA"), day2: _session_frame("AAA")}
    picks = {SESSION.day: ["AAA"]}  # day2 has no picks -> flat row
    stats = pl.DataFrame({"date": [SESSION.day], "ticker": ["AAA"],
                          "spread_bps": [30.0], "vol_minute": [0.0]})
    combos = [Combo(5, "or_low", 0.0), Combo(5, "or_mid", 2.0)]
    matrix, days, ledger = run_backtest(minutes_by_day, sessions, picks, combos,
                                        stats, cfg, equity=100_000.0)
    assert matrix.shape == (2, 2) and days == [SESSION.day, day2]
    assert matrix[1, 0] == 0.0 and matrix[1, 1] == 0.0  # stood aside, still a row
    assert matrix[0, 0] != 0.0
    assert all(t.day == SESSION.day for t in ledger)
