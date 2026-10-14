"""Mean-reversion mechanics: anchors, fill conventions, passive-fill honesty."""

from datetime import UTC, date, datetime, timedelta

import numpy as np
from new_pipeline.config import base, reload_config
from new_pipeline.intraday.calendar import Session
from new_pipeline.intraday.meanrev import MRCombo, session_anchor, trade_path

OPEN = datetime(2026, 3, 2, 14, 30, tzinfo=UTC)
CLOSE = datetime(2026, 3, 2, 21, 0, tzinfo=UTC)
SESSION = Session(date(2026, 3, 2), OPEN, CLOSE)
ATR = 0.02  # prior-day ATR = 2% of price


def _bars(rows):
    """rows: (minute, open, high, low, close[, volume])."""
    return {
        "ts": np.array([OPEN + timedelta(minutes=r[0]) for r in rows]),
        "open": np.array([r[1] for r in rows], dtype=float),
        "high": np.array([r[2] for r in rows], dtype=float),
        "low": np.array([r[3] for r in rows], dtype=float),
        "close": np.array([r[4] for r in rows], dtype=float),
        "volume": np.array([r[5] if len(r) > 5 else 1000 for r in rows], dtype=float),
    }


def test_anchors_are_causal_running_values():
    b = _bars([(0, 10.0, 10.0, 10.0, 10.0, 100), (1, 10.0, 12.0, 10.0, 12.0, 300)])
    vwap = session_anchor("vwap", b["open"], b["high"], b["low"], b["close"], b["volume"])
    # bar 0 sees only itself; bar 1 is the volume-weighted blend of both
    assert abs(vwap[0] - 10.0) < 1e-9
    assert abs(vwap[1] - (10.0 * 100 + (12 + 10 + 12) / 3 * 300) / 400) < 1e-9
    opens = session_anchor("open", b["open"], b["high"], b["low"], b["close"], b["volume"])
    assert (opens == 10.0).all()  # opening print, held flat
    # a later bar can never change an earlier anchor value
    b2 = _bars([(0, 10.0, 10.0, 10.0, 10.0, 100), (1, 10.0, 12.0, 10.0, 12.0, 300),
                (2, 12.0, 99.0, 12.0, 99.0, 9999)])
    v2 = session_anchor("vwap", b2["open"], b2["high"], b2["low"], b2["close"], b2["volume"])
    assert abs(v2[1] - vwap[1]) < 1e-9


def test_marketable_entry_fills_next_bar_and_targets_the_anchor():
    # flat at 10 then a dip to 9.6 (2 ATRs below the 10.0 anchor), then recovery
    b = _bars([(0, 10.0, 10.0, 10.0, 10.0), (1, 10.0, 10.0, 9.6, 9.6),
               (2, 9.7, 9.9, 9.7, 9.8), (3, 9.8, 10.4, 9.8, 10.3),
               (380, 10.3, 10.3, 10.2, 10.2)])
    combo = MRCombo("open", 1.5, "marketable", "anchor")
    path = trade_path(b, OPEN, CLOSE, combo, ATR, flatten_buffer_min=5)
    assert path.entry_idx == 2 and path.entry_px == 9.7  # next bar's OPEN
    assert path.entry_passive is False                   # crossed the spread
    assert path.exit_reason == "target" and path.exit_passive is True
    assert abs(path.exit_px - 10.0) < 1e-9               # the anchor


def test_passive_entry_requires_a_strict_trade_through():
    """A resting limit is not a wish: it fills only if the market actually
    trades BELOW it. Without a trade-through there is no trade at all — that
    exclusion is what keeps the passive advantage from being fictional."""
    dip = (1, 10.0, 10.0, 9.6, 9.6)
    combo = MRCombo("open", 1.5, "passive", "anchor")
    # price never revisits 9.6 -> no fill, no trade
    never = _bars([(0, 10.0, 10.0, 10.0, 10.0), dip,
                   (2, 9.7, 9.9, 9.65, 9.8), (3, 9.8, 10.4, 9.7, 10.3),
                   (380, 10.3, 10.3, 10.2, 10.2)])
    assert trade_path(never, OPEN, CLOSE, combo, ATR, flatten_buffer_min=5) is None
    # touching the limit exactly is still not a fill (queue position unknown)
    touch = _bars([(0, 10.0, 10.0, 10.0, 10.0), dip,
                   (2, 9.7, 9.9, 9.60, 9.8), (380, 10.3, 10.3, 10.2, 10.2)])
    assert trade_path(touch, OPEN, CLOSE, combo, ATR, flatten_buffer_min=5) is None
    # trading through it fills AT the limit, with no spread paid
    through = _bars([(0, 10.0, 10.0, 10.0, 10.0), dip,
                     (2, 9.7, 9.9, 9.55, 9.8), (3, 9.8, 10.4, 9.8, 10.3),
                     (380, 10.3, 10.3, 10.2, 10.2)])
    path = trade_path(through, OPEN, CLOSE, combo, ATR, flatten_buffer_min=5)
    assert path.entry_idx == 2 and path.entry_px == 9.6 and path.entry_passive is True


def test_passive_entry_expires_after_its_ttl():
    rows = [(0, 10.0, 10.0, 10.0, 10.0), (1, 10.0, 10.0, 9.6, 9.6)]
    rows += [(i, 9.8, 9.9, 9.7, 9.8) for i in range(2, 9)]      # 7 bars above
    rows += [(9, 9.7, 9.8, 9.5, 9.6), (380, 10.0, 10.1, 9.9, 10.0)]  # through, too late
    combo = MRCombo("open", 1.5, "passive", "anchor")
    b = _bars(rows)
    assert trade_path(b, OPEN, CLOSE, combo, ATR, flatten_buffer_min=5,
                      passive_ttl_min=3) is None
    filled = trade_path(b, OPEN, CLOSE, combo, ATR, flatten_buffer_min=5,
                        passive_ttl_min=10)
    assert filled is not None and filled.entry_px == 9.6


def test_stop_gap_through_and_half_target_and_flatten():
    combo_stop = MRCombo("open", 1.5, "marketable", "anchor")
    # entry 9.7, stop = 9.7 - 1 ATR = 9.506; a bar OPENING below fills there
    gap = _bars([(0, 10.0, 10.0, 10.0, 10.0), (1, 10.0, 10.0, 9.6, 9.6),
                 (2, 9.7, 9.75, 9.7, 9.72), (3, 9.3, 9.4, 9.2, 9.25),
                 (380, 9.3, 9.4, 9.2, 9.3)])
    path = trade_path(gap, OPEN, CLOSE, combo_stop, ATR, flatten_buffer_min=5)
    assert path.exit_reason == "stop" and path.exit_px == 9.3  # the OPEN, not the stop
    assert path.exit_passive is False                          # stops cross the spread
    # "half" target exits at the midpoint between entry and anchor
    half = _bars([(0, 10.0, 10.0, 10.0, 10.0), (1, 10.0, 10.0, 9.6, 9.6),
                  (2, 9.7, 9.75, 9.7, 9.72), (3, 9.75, 9.90, 9.74, 9.88),
                  (380, 9.9, 9.95, 9.85, 9.9)])
    p2 = trade_path(half, OPEN, CLOSE, MRCombo("open", 1.5, "marketable", "half"),
                    ATR, flatten_buffer_min=5)
    assert p2.exit_reason == "target" and abs(p2.exit_px - 9.85) < 1e-9
    # never reverting -> forced flatten at the close, marketable
    stuck = _bars([(0, 10.0, 10.0, 10.0, 10.0), (1, 10.0, 10.0, 9.6, 9.6),
                   (2, 9.7, 9.72, 9.65, 9.68), (380, 9.68, 9.70, 9.60, 9.66)])
    p3 = trade_path(stuck, OPEN, CLOSE, combo_stop, ATR, flatten_buffer_min=5)
    assert p3.exit_reason == "close" and p3.exit_passive is False


def test_no_signal_without_a_real_stretch_or_a_usable_scale():
    calm = _bars([(0, 10.0, 10.0, 10.0, 10.0), (1, 10.0, 10.02, 9.99, 10.0),
                  (2, 10.0, 10.01, 9.98, 9.99), (380, 10.0, 10.0, 9.99, 10.0)])
    combo = MRCombo("open", 1.5, "marketable", "anchor")
    assert trade_path(calm, OPEN, CLOSE, combo, ATR, flatten_buffer_min=5) is None
    dip = _bars([(0, 10.0, 10.0, 10.0, 10.0), (1, 10.0, 10.0, 9.6, 9.6),
                 (2, 9.7, 9.9, 9.7, 9.8), (380, 10.0, 10.0, 9.9, 10.0)])
    for bad in (float("nan"), 0.0, -0.01):  # no prior-day ATR -> unscalable
        assert trade_path(dip, OPEN, CLOSE, combo, bad, flatten_buffer_min=5) is None


def test_passive_legs_pay_no_spread_in_the_simulator():
    """The economic payload: a passive entry + target exit is charged impact
    only, while the same trade taken marketably pays the half-spread twice."""
    import polars as pl
    from new_pipeline.intraday.simulate import run_session

    reload_config()
    cfg = base.get_config()
    cfg.intraday.risk_bps = 50.0
    cfg.intraday.max_position_pct = 5.0
    cfg.intraday.spread_floor_bps = 5.0
    rows = [(0, 10.0, 10.0, 10.0, 10.0), (1, 10.0, 10.0, 9.6, 9.6),
            (2, 9.7, 9.9, 9.55, 9.8), (3, 9.8, 10.4, 9.8, 10.3),
            (380, 10.3, 10.3, 10.2, 10.2)]
    minutes = pl.DataFrame({
        "ticker": ["AAA"] * len(rows),
        "ts": [OPEN + timedelta(minutes=r[0]) for r in rows],
        "open": [r[1] for r in rows], "high": [r[2] for r in rows],
        "low": [r[3] for r in rows], "close": [r[4] for r in rows],
        "volume": [500_000] * len(rows),
    })
    stats = pl.DataFrame({"date": [SESSION.day], "ticker": ["AAA"],
                          "spread_bps": [40.0], "vol_minute": [0.0],
                          "atr_pct": [ATR]})
    combos = [MRCombo("open", 1.5, "passive", "anchor"),
              MRCombo("open", 1.5, "marketable", "anchor")]
    _, ledger = run_session(minutes, SESSION, ["AAA"], combos, stats, cfg,
                            equity=100_000.0)
    by = {t.combo_key: t for t in ledger}
    passive = by["open|z1.5|passive|anchor"]
    marketable = by["open|z1.5|marketable|anchor"]
    assert passive.cost_dollars == 0.0        # both legs supplied liquidity
    assert marketable.cost_dollars > 0.0      # entry crossed; exit was passive
    assert passive.net_pnl > marketable.net_pnl


def test_timing_null_preserves_the_entry_style():
    """The null destroys TIMING only. A passive combo's null must also rest a
    limit and risk non-fill — otherwise the null pays a spread the champion
    avoids and the margin is flattered."""
    rows = [(0, 10.0, 10.0, 10.0, 10.0), (1, 10.0, 10.0, 9.6, 9.6),
            (2, 9.7, 9.9, 9.55, 9.8), (3, 9.8, 10.4, 9.8, 10.3),
            (380, 10.3, 10.3, 10.2, 10.2)]
    b = _bars(rows)
    passive = MRCombo("open", 1.5, "passive", "anchor")
    # override at bar 2: the limit rests at bar 1's close (9.6) and bar 2
    # trades through to 9.55 -> filled passively, no spread
    forced = trade_path(b, OPEN, CLOSE, passive, ATR, flatten_buffer_min=5,
                        entry_override=2)
    assert forced is not None and forced.entry_passive is True
    assert forced.entry_px == 9.6
    # override at a bar whose limit is never traded through -> no fill at all,
    # exactly as a real resting order would fare (limit 9.8; later lows are
    # 9.8 and 10.2, and touching is not filling)
    assert trade_path(b, OPEN, CLOSE, passive, ATR, flatten_buffer_min=5,
                      entry_override=3) is None
    # a marketable combo's null still crosses at the next open
    mk = trade_path(b, OPEN, CLOSE, MRCombo("open", 1.5, "marketable", "anchor"),
                    ATR, flatten_buffer_min=5, entry_override=3)
    assert mk.entry_passive is False and mk.entry_px == 9.8


def test_live_credentials_never_render_in_a_config_repr():
    """A pytest assertion or traceback that touches the config used to print
    the real Alpaca key and secret in plaintext."""
    reload_config()
    cfg = base.get_config()
    cfg.alpaca.api_key = "PKSECRETKEYVALUE"
    cfg.alpaca.secret_key = "supersecretvalue"
    rendered = repr(cfg) + repr(cfg.alpaca)
    assert "PKSECRETKEYVALUE" not in rendered
    assert "supersecretvalue" not in rendered
    # ...while attribute access is untouched for the callers that need them
    assert cfg.alpaca.api_key == "PKSECRETKEYVALUE"


def test_cost_attribution_separates_spread_from_impact():
    """Every ledger row records WHICH term charged it. Without this the
    meanrev_v1 post-mortem could not tell a 54bps round trip apart from a
    5bps floor plus a runaway impact model."""
    import polars as pl
    from new_pipeline.intraday.simulate import run_session

    reload_config()
    cfg = base.get_config()
    cfg.intraday.spread_floor_bps = 5.0
    rows = [(0, 10.0, 10.0, 10.0, 10.0), (1, 10.0, 10.0, 9.6, 9.6),
            (2, 9.7, 9.9, 9.55, 9.8), (3, 9.8, 10.4, 9.8, 10.3),
            (380, 10.3, 10.3, 10.2, 10.2)]
    minutes = pl.DataFrame({
        "ticker": ["AAA"] * len(rows),
        "ts": [OPEN + timedelta(minutes=r[0]) for r in rows],
        "open": [r[1] for r in rows], "high": [r[2] for r in rows],
        "low": [r[3] for r in rows], "close": [r[4] for r in rows],
        "volume": [500_000] * len(rows),
    })
    # CS says the full spread is 80bps -> a 40bps half-spread dwarfs the floor
    stats = pl.DataFrame({"date": [SESSION.day], "ticker": ["AAA"],
                          "spread_bps": [80.0], "vol_minute": [0.0],
                          "atr_pct": [ATR]})
    _, ledger = run_session(minutes, SESSION, ["AAA"],
                            [MRCombo("open", 1.5, "marketable", "anchor")],
                            stats, cfg, equity=100_000.0)
    trade = ledger[0]
    assert trade.cs_spread_bps == 80.0
    assert trade.spread_bps == 40.0   # entry leg only; the target exit rested
    assert trade.impact_bps == 0.0    # vol_minute 0 -> no impact term
    # the recorded parts reconstruct the charged total
    notional = trade.shares * trade.entry_px
    assert abs(trade.cost_dollars - notional * 40.0 / 1e4) < 0.05


def _mr_frame():
    import polars as pl
    rows = [(0, 10.0, 10.0, 10.0, 10.0), (1, 10.0, 10.0, 9.6, 9.6),
            (2, 9.7, 9.9, 9.55, 9.8), (3, 9.8, 10.4, 9.8, 10.3),
            (380, 10.3, 10.3, 10.2, 10.2)]
    return pl.DataFrame({
        "ticker": ["AAA"] * len(rows),
        "ts": [OPEN + timedelta(minutes=r[0]) for r in rows],
        "open": [r[1] for r in rows], "high": [r[2] for r in rows],
        "low": [r[3] for r in rows], "close": [r[4] for r in rows],
        "volume": [500_000] * len(rows)})


def test_measured_spread_beats_the_corwin_schultz_fallback():
    """When the quote vault covers a name-month the MEASURED half-spread is
    charged; Corwin-Schultz — biased ~4x on these names — is only a fallback."""
    import polars as pl
    from new_pipeline.intraday.simulate import run_session

    reload_config()
    cfg = base.get_config()
    cfg.intraday.max_touch_participation = 100.0  # isolate the spread term
    # sizing defaults to "uncapped" in run_session; touch depth is huge below
    combo = [MRCombo("open", 1.5, "marketable", "anchor")]
    base_stats = {"date": [SESSION.day], "ticker": ["AAA"], "spread_bps": [80.0],
                  "vol_minute": [0.0], "atr_pct": [ATR]}
    # CS-only: charges 80/2 = 40bps on the entry leg
    _, cs_led = run_session(_mr_frame(), SESSION, ["AAA"], combo,
                            pl.DataFrame(base_stats), cfg, equity=100_000.0)
    assert cs_led[0].spread_bps == 40.0
    # measured: 5bps half-spread wins, and CS is ignored entirely
    measured = pl.DataFrame({**base_stats, "half_spread_bps": [5.0],
                             "touch_notional": [1e9]})
    _, m_led = run_session(_mr_frame(), SESSION, ["AAA"], combo, measured, cfg,
                           equity=100_000.0)
    assert m_led[0].spread_bps == 5.0
    assert m_led[0].cost_dollars < cs_led[0].cost_dollars


def test_impact_charges_book_walking_and_the_cap_prevents_it():
    """Impact is participation against DISPLAYED depth, not bar volume: an
    order 5x the touch crosses levels and pays; the participation cap sizes
    the order back inside the touch so it doesn't."""
    import polars as pl
    from new_pipeline.intraday.quotes import book_walk_impact_bps
    from new_pipeline.intraday.simulate import run_session

    # unit: 5x the touch at a 4bps half-spread -> 4 * (5-1)/2 = 8bps
    assert book_walk_impact_bps(5000.0, 4.0, 1000.0) == 8.0
    assert book_walk_impact_bps(900.0, 4.0, 1000.0) == 0.0  # fits inside

    reload_config()
    cfg = base.get_config()
    combo = [MRCombo("open", 1.5, "marketable", "anchor")]
    stats = pl.DataFrame({"date": [SESSION.day], "ticker": ["AAA"],
                          "spread_bps": [float("nan")], "vol_minute": [0.0],
                          "atr_pct": [ATR], "half_spread_bps": [5.0],
                          "touch_notional": [400.0]})
    _, big = run_session(_mr_frame(), SESSION, ["AAA"], combo, stats, cfg,
                         equity=100_000.0, sizing="uncapped")
    assert big[0].impact_bps > 0.0                 # it walked the book
    cfg.intraday.max_touch_participation = 1.0     # size back inside the touch
    _, capped = run_session(_mr_frame(), SESSION, ["AAA"], combo, stats, cfg,
                            equity=100_000.0, sizing="touch_cap")
    assert capped[0].impact_bps == 0.0
    assert capped[0].shares < big[0].shares
    # gross bps is size-invariant, so the capped trade is strictly better per $
    assert (capped[0].cost_dollars / (capped[0].shares * capped[0].entry_px)
            < big[0].cost_dollars / (big[0].shares * big[0].entry_px))


def test_sizing_models_are_priced_as_distinct_trials():
    """The three execution assumptions size the SAME signal differently and
    are judged side by side: working the order over a window, fitting inside
    the displayed touch, or firing it all and paying the book-walk."""
    import polars as pl
    from new_pipeline.intraday.simulate import run_session

    reload_config()
    cfg = base.get_config()
    cfg.intraday.volume_participation_rate = 0.10
    cfg.intraday.exec_window_min = 5
    cfg.intraday.max_touch_participation = 1.0
    combo = [MRCombo("open", 1.5, "marketable", "anchor")]
    stats = pl.DataFrame({"date": [SESSION.day], "ticker": ["AAA"],
                          "spread_bps": [float("nan")], "vol_minute": [0.0],
                          "atr_pct": [ATR], "half_spread_bps": [5.0],
                          "touch_notional": [150.0]})  # the measured reality
    out = {}
    for sizing in ("volume_part", "touch_cap", "uncapped"):
        _, led = run_session(_mr_frame(), SESSION, ["AAA"], combo, stats, cfg,
                             equity=100_000.0, sizing=sizing)
        out[sizing] = led[0]
    # touch_cap fits inside $150 of displayed depth -> tiny, and pays no walk
    assert out["touch_cap"].shares * out["touch_cap"].entry_px <= 160
    assert out["touch_cap"].impact_bps == 0.0
    # uncapped takes the full position and pays the book-walk for it
    assert out["uncapped"].shares > out["touch_cap"].shares
    assert out["uncapped"].impact_bps > 0.0
    # working the order sits between: real size, no walking
    assert out["volume_part"].shares > out["touch_cap"].shares
    assert out["volume_part"].impact_bps == 0.0
