"""Session simulator: ORB paths -> sized, costed trades -> session returns.

Cost model is spread-dominated and charged per SIDE at the fill bar:
``max(corwin_schultz/2, spread_floor) + hydrodynamic impact`` — the
Corwin-Schultz estimate comes from trailing DAILY high/low pairs (strictly
prior), the impact term prices the order against the fill bar's own minute
dollar volume. Stops additionally inherit the gap-through fill convention
from `orb.trade_path`.

Sizing is fixed-fractional: ``risk_bps`` of a FIXED equity base against the
stop distance, capped at ``max_position_pct`` of equity. Equity does not
compound during the backtest so session returns are comparable across time.

Concurrency (disclosed v1 simplification): per combo and session, the first
``max_concurrent`` candidate trades ORDERED BY ENTRY TIME are admitted —
a first-come admission rather than full interval accounting; the admitted
set is deterministic and never exceeds the cap at any instant it binds.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date

import numpy as np
import polars as pl

from new_pipeline.features.microstructure import corwin_schultz
from new_pipeline.features.slippage import hydrodynamic_slippage_bps
from new_pipeline.intraday.calendar import Session
from new_pipeline.intraday.meanrev import MRCombo
from new_pipeline.intraday.meanrev import trade_path as mr_trade_path
from new_pipeline.intraday.orb import Combo, trade_path
from new_pipeline.intraday.quotes import book_walk_impact_bps, max_participation_shares

_MINUTES_PER_SESSION = 390.0


@dataclass(frozen=True)
class Trade:
    day: date
    ticker: str
    combo_key: str
    entry_ts: object
    exit_ts: object
    entry_px: float
    exit_px: float
    shares: int
    exit_reason: str
    gross_pnl: float
    cost_dollars: float
    net_pnl: float
    # Cost attribution, round trip: which term actually charged the trade.
    spread_bps: float = 0.0      # half-spread legs (0 when both legs rested)
    impact_bps: float = 0.0      # hydrodynamic size-vs-liquidity term
    cs_spread_bps: float = 0.0   # the raw Corwin-Schultz FULL-spread estimate


def trailing_stats(daily: pl.DataFrame, window: int = 20) -> pl.DataFrame:
    """(date, ticker, spread_bps, vol_minute) from STRICTLY PRIOR daily bars:
    Corwin-Schultz full-spread estimate (bps) and a per-minute return vol
    proxy (daily close-to-close vol / sqrt(390))."""
    frames = []
    for ticker, sub in daily.sort("date").group_by("ticker", maintain_order=True):
        highs = sub["high"].to_numpy()
        lows = sub["low"].to_numpy()
        closes = sub["close"].to_numpy()
        cs = corwin_schultz(highs, lows, window=window)
        rets = np.diff(np.log(np.clip(closes, 1e-9, None)), prepend=np.nan)
        vol = (pl.Series(rets).rolling_std(window_size=window)
               .to_numpy() / np.sqrt(_MINUTES_PER_SESSION))
        highs_a, lows_a, closes_a = highs, lows, closes
        atr = (pl.Series((highs_a - lows_a) / np.clip(closes_a, 1e-9, None))
               .rolling_mean(window_size=window).to_numpy())
        frames.append(pl.DataFrame({
            "date": sub["date"],
            "ticker": ticker if isinstance(ticker, str) else ticker[0],
            "spread_bps": np.roll(cs, 1) * 1e4,   # strictly prior
            "vol_minute": np.roll(vol, 1),
            "atr_pct": np.roll(atr, 1),           # prior-day ATR%, the MR scale
        }).with_row_index("_i").filter(pl.col("_i") > 0).drop("_i"))
    if not frames:
        return pl.DataFrame(schema={"date": pl.Date, "ticker": pl.Utf8,
                                    "spread_bps": pl.Float64, "vol_minute": pl.Float64,
                                    "atr_pct": pl.Float64})
    return pl.concat(frames)


def _side_cost_bps(notional: float, spread_bps: float, vol_minute: float,
                   bar_dollar_vol: float, spread_floor_bps: float,
                   slippage_constant: float, passive: bool = False,
                   measured_half_bps: float = float("nan"),
                   touch_notional: float = 0.0) -> tuple[float, float]:
    """(half_spread_bps, impact_bps) for one leg — returned SEPARATELY so every
    ledger row records which term drove its cost. Storing only the total made
    the meanrev_v1 post-mortem guesswork: a 54 bps round trip is unexplainable
    against a 5 bps floor without knowing whether the Corwin-Schultz estimate
    or the impact model produced it."""
    # Spread: the MEASURED NBBO half-spread when the quote vault covers this
    # name-month, else the Corwin-Schultz fallback (~4x biased on small caps).
    if np.isfinite(measured_half_bps):
        half_spread = 0.0 if passive else max(measured_half_bps, 0.0)
    else:
        half_spread = 0.0 if passive else max(
            spread_bps / 2.0 if np.isfinite(spread_bps) else 0.0, spread_floor_bps)
    # Impact: book-walking beyond the DISPLAYED touch — what a marketable order
    # actually eats. A minute bar's traded volume never described resting size,
    # which is why the old term charged ~2bps where reality was 10-20. Passive
    # legs add liquidity and never walk. Falls back to the hydrodynamic term
    # only when depth is unmeasured.
    if touch_notional > 0:
        impact = 0.0 if passive else book_walk_impact_bps(
            notional, measured_half_bps if np.isfinite(measured_half_bps) else half_spread,
            touch_notional)
    else:
        impact = hydrodynamic_slippage_bps(
            notional, vol_minute if np.isfinite(vol_minute) else 0.0,
            max(bar_dollar_vol, 1.0), constant=slippage_constant)
    return half_spread, min(impact, 250.0)  # cap the model, never negative edge


def run_session(minutes: pl.DataFrame, session: Session, picks: list[str],
                combos: list[Combo], stats: pl.DataFrame, cfg,
                equity: float,
                entry_rng: np.random.Generator | None = None
                ) -> tuple[dict[str, float], list[Trade]]:
    """One session across all combos. Returns ({combo_key: session_return},
    trade ledger). ``minutes`` is the session-filtered frame for this day.
    ``entry_rng`` switches every entry to a RANDOM in-session bar (the timing
    null): same names, same range-derived stops, same costs — only the
    breakout timing is destroyed."""
    icfg = cfg.intraday
    day_stats = {r["ticker"]: r for r in
                 stats.filter(pl.col("date") == session.day).iter_rows(named=True)}
    arrays = {}
    for ticker, sub in minutes.group_by("ticker", maintain_order=True):
        key = ticker if isinstance(ticker, str) else ticker[0]
        sub = sub.sort("ts")
        arrays[key] = {c: sub[c].to_numpy() for c in ("open", "high", "low", "close", "volume")}
        arrays[key]["ts"] = sub["ts"].to_numpy()
        if "vwap" in sub.columns:  # feed VWAP anchors mean reversion when present
            arrays[key]["vwap"] = sub["vwap"].to_numpy()

    session_returns: dict[str, float] = {}
    ledger: list[Trade] = []
    risk_dollars = equity * icfg.risk_bps / 1e4
    max_notional = equity * icfg.max_position_pct / 100.0

    for combo in combos:
        candidates = []
        for ticker in picks:
            bars = arrays.get(ticker)
            if bars is None or len(bars["ts"]) == 0:
                continue
            override = None
            if entry_rng is not None:
                override = int(entry_rng.integers(1, len(bars["ts"])))
            if isinstance(combo, MRCombo):
                path = mr_trade_path(
                    bars, session.open_utc, session.close_utc, combo,
                    atr_pct=float(day_stats.get(ticker, {}).get("atr_pct", float("nan"))),
                    flatten_buffer_min=icfg.flatten_buffer_min,
                    passive_ttl_min=icfg.mr_passive_ttl_min,
                    stop_atr=icfg.mr_stop_atr, entry_override=override)
            else:
                path = trade_path(bars["ts"], bars["open"], bars["high"], bars["low"],
                                  bars["close"], session.open_utc, session.close_utc,
                                  combo, icfg.entry_buffer_bps, icfg.flatten_buffer_min,
                                  entry_override=override)
            if path is not None:
                candidates.append((ticker, path))
        candidates.sort(key=lambda tp: (tp[1].entry_idx, tp[0]))
        admitted = candidates[:icfg.max_concurrent]

        pnl = 0.0
        for ticker, path in admitted:
            per_share_risk = max(path.entry_px - path.stop_px, 1e-9)
            row = day_stats.get(ticker, {})
            touch = float(row.get("touch_notional", 0.0) or 0.0)
            shares = int(min(risk_dollars / per_share_risk,
                             max_notional / path.entry_px,
                             max_participation_shares(touch, path.entry_px,
                                                      icfg.max_touch_participation)))
            if shares < 1:
                continue
            bars = arrays[ticker]
            measured_half = float(row.get("half_spread_bps", float("nan")) or float("nan"))
            spread = float(row.get("spread_bps", float("nan")))
            volm = float(row.get("vol_minute", float("nan")))
            entry_notional = shares * path.entry_px
            exit_notional = shares * path.exit_px
            entry_bar_dv = float(bars["volume"][path.entry_idx]) * path.entry_px
            exit_bar_dv = float(bars["volume"][path.exit_idx]) * path.exit_px
            # A resting limit the market traded through SUPPLIED liquidity: no
            # spread, impact only. Crossing legs pay the half-spread as before.
            entry_spread, entry_impact = _side_cost_bps(
                entry_notional, spread, volm, entry_bar_dv, icfg.spread_floor_bps,
                cfg.features.slippage_constant, passive=path.entry_passive,
                measured_half_bps=measured_half, touch_notional=touch)
            exit_spread, exit_impact = _side_cost_bps(
                exit_notional, spread, volm, exit_bar_dv, icfg.spread_floor_bps,
                cfg.features.slippage_constant, passive=path.exit_passive,
                measured_half_bps=measured_half, touch_notional=touch)
            entry_bps, exit_bps = entry_spread + entry_impact, exit_spread + exit_impact
            gross = shares * (path.exit_px - path.entry_px)
            cost = (entry_notional * entry_bps + exit_notional * exit_bps) / 1e4
            pnl += gross - cost
            ledger.append(Trade(
                day=session.day, ticker=ticker, combo_key=combo.key,
                entry_ts=bars["ts"][path.entry_idx], exit_ts=bars["ts"][path.exit_idx],
                entry_px=path.entry_px, exit_px=path.exit_px, shares=shares,
                exit_reason=path.exit_reason, gross_pnl=gross,
                cost_dollars=cost, net_pnl=gross - cost,
                spread_bps=entry_spread + exit_spread,
                impact_bps=entry_impact + exit_impact,
                cs_spread_bps=float(spread) if np.isfinite(spread) else float("nan")))
        session_returns[combo.key] = pnl / equity
    return session_returns, ledger


def run_backtest_trials(minutes_by_day, sessions: dict[date, Session],
                        picks_by_variant: dict[str, dict[date, list[str]]],
                        trials, stats: pl.DataFrame, cfg, equity: float):
    """(scanner variant x construction) trial family -> ((n_sessions x n_trials)
    matrix, days, ledger). Each variant supplies its own pick list, so the
    scanner weighting is a genuine experimental axis and not a fixed input."""
    days = sorted(d for d in minutes_by_day if d in sessions)
    matrix = np.zeros((len(days), len(trials)))
    ledger: list[Trade] = []
    by_variant: dict[str, list[Combo]] = {}
    for trial in trials:
        by_variant.setdefault(trial.variant, []).append(trial.combo)
    column = {t.key: j for j, t in enumerate(trials)}

    for i, day in enumerate(days):
        for variant, combos in by_variant.items():
            picks = picks_by_variant.get(variant, {}).get(day, [])
            if not picks:
                continue
            rets, trades = run_session(minutes_by_day[day], sessions[day], picks,
                                       combos, stats, cfg, equity)
            for combo in combos:
                matrix[i, column[f"{variant}|{combo.key}"]] = rets.get(combo.key, 0.0)
            for trade in trades:
                ledger.append(replace(trade, combo_key=f"{variant}|{trade.combo_key}"))
    return matrix, days, ledger


def run_backtest(minutes_by_day, sessions: dict[date, Session],
                 picks_by_day: dict[date, list[str]], combos: list[Combo],
                 stats: pl.DataFrame, cfg, equity: float):
    """All sessions -> ((n_sessions x n_combos) matrix, session dates, ledger).
    Sessions with no picks or no data contribute a flat 0.0 row — a day the
    book stood aside is still a day in the record."""
    days = sorted(d for d in minutes_by_day if d in sessions)
    matrix = np.zeros((len(days), len(combos)))
    ledger: list[Trade] = []
    keys = [c.key for c in combos]
    for i, day in enumerate(days):
        picks = picks_by_day.get(day, [])
        if not picks:
            continue
        rets, trades = run_session(minutes_by_day[day], sessions[day], picks,
                                   combos, stats, cfg, equity)
        matrix[i, :] = [rets.get(k, 0.0) for k in keys]
        ledger.extend(trades)
    return matrix, days, ledger
