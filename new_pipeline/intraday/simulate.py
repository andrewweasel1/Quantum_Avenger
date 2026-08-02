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

from dataclasses import dataclass
from datetime import date

import numpy as np
import polars as pl

from new_pipeline.features.microstructure import corwin_schultz
from new_pipeline.features.slippage import hydrodynamic_slippage_bps
from new_pipeline.intraday.calendar import Session
from new_pipeline.intraday.orb import Combo, trade_path

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
        frames.append(pl.DataFrame({
            "date": sub["date"],
            "ticker": ticker if isinstance(ticker, str) else ticker[0],
            "spread_bps": np.roll(cs, 1) * 1e4,   # strictly prior
            "vol_minute": np.roll(vol, 1),
        }).with_row_index("_i").filter(pl.col("_i") > 0).drop("_i"))
    if not frames:
        return pl.DataFrame(schema={"date": pl.Date, "ticker": pl.Utf8,
                                    "spread_bps": pl.Float64, "vol_minute": pl.Float64})
    return pl.concat(frames)


def _side_cost_bps(notional: float, spread_bps: float, vol_minute: float,
                   bar_dollar_vol: float, spread_floor_bps: float,
                   slippage_constant: float) -> float:
    half_spread = max(spread_bps / 2.0 if np.isfinite(spread_bps) else 0.0,
                      spread_floor_bps)
    impact = hydrodynamic_slippage_bps(
        notional, vol_minute if np.isfinite(vol_minute) else 0.0,
        max(bar_dollar_vol, 1.0), constant=slippage_constant)
    return half_spread + min(impact, 250.0)  # cap the model, never negative edge


def run_session(minutes: pl.DataFrame, session: Session, picks: list[str],
                combos: list[Combo], stats: pl.DataFrame, cfg,
                equity: float) -> tuple[dict[str, float], list[Trade]]:
    """One session across all combos. Returns ({combo_key: session_return},
    trade ledger). ``minutes`` is the session-filtered frame for this day."""
    icfg = cfg.intraday
    day_stats = {r["ticker"]: r for r in
                 stats.filter(pl.col("date") == session.day).iter_rows(named=True)}
    arrays = {}
    for ticker, sub in minutes.group_by("ticker", maintain_order=True):
        key = ticker if isinstance(ticker, str) else ticker[0]
        sub = sub.sort("ts")
        arrays[key] = {c: sub[c].to_numpy() for c in ("open", "high", "low", "close", "volume")}
        arrays[key]["ts"] = sub["ts"].to_numpy()

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
            path = trade_path(bars["ts"], bars["open"], bars["high"], bars["low"],
                              bars["close"], session.open_utc, session.close_utc,
                              combo, icfg.entry_buffer_bps, icfg.flatten_buffer_min)
            if path is not None:
                candidates.append((ticker, path))
        candidates.sort(key=lambda tp: (tp[1].entry_idx, tp[0]))
        admitted = candidates[:icfg.max_concurrent]

        pnl = 0.0
        for ticker, path in admitted:
            per_share_risk = max(path.entry_px - path.stop_px, 1e-9)
            shares = int(min(risk_dollars / per_share_risk,
                             max_notional / path.entry_px))
            if shares < 1:
                continue
            bars = arrays[ticker]
            row = day_stats.get(ticker, {})
            spread = float(row.get("spread_bps", float("nan")))
            volm = float(row.get("vol_minute", float("nan")))
            entry_notional = shares * path.entry_px
            exit_notional = shares * path.exit_px
            entry_bar_dv = float(bars["volume"][path.entry_idx]) * path.entry_px
            exit_bar_dv = float(bars["volume"][path.exit_idx]) * path.exit_px
            entry_bps = _side_cost_bps(entry_notional, spread, volm, entry_bar_dv,
                                       icfg.spread_floor_bps, cfg.features.slippage_constant)
            exit_bps = _side_cost_bps(exit_notional, spread, volm, exit_bar_dv,
                                      icfg.spread_floor_bps, cfg.features.slippage_constant)
            gross = shares * (path.exit_px - path.entry_px)
            cost = (entry_notional * entry_bps + exit_notional * exit_bps) / 1e4
            pnl += gross - cost
            ledger.append(Trade(
                day=session.day, ticker=ticker, combo_key=combo.key,
                entry_ts=bars["ts"][path.entry_idx], exit_ts=bars["ts"][path.exit_idx],
                entry_px=path.entry_px, exit_px=path.exit_px, shares=shares,
                exit_reason=path.exit_reason, gross_pnl=gross,
                cost_dollars=cost, net_pnl=gross - cost))
        session_returns[combo.key] = pnl / equity
    return session_returns, ledger


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
