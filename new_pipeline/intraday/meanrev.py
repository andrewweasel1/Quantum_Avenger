"""Intraday mean reversion: fade a stretch away from a session anchor.

Long-only v1: when price is stretched far BELOW the anchor (session VWAP or
the opening price), buy the dislocation and exit on reversion. Scale is the
prior day's ATR% — strictly causal and stable, so the z-score means the same
thing across names and days.

The economic case that distinguishes this family from breakouts: a reversion
entry can REST inside the spread instead of crossing it. That is modelled as
a priced axis, not assumed:

- ``marketable`` — cross the spread, fill at the next bar's open (ORB's
  convention). Pays the half-spread on entry.
- ``passive`` — rest a limit at the signal price for ``ttl`` bars. Fills ONLY
  if a later bar trades strictly THROUGH the limit, which builds adverse
  selection into the model for free: we are filled exactly when sellers keep
  pressing, and the subsequent path is whatever really happened. Pays no
  spread, because we supplied the liquidity.

Exits mirror the same logic: the reversion target is a resting sell limit
(passive, no spread) that fills only on a strict trade-through; stops and the
forced close cross the spread (marketable), and a stop that gaps through
fills at the bar's open, never at the stop price.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

import numpy as np

from new_pipeline.intraday.orb import TradePath, _cutoff

ANCHORS = ("vwap", "open")
ENTRY_STYLES = ("marketable", "passive")
EXIT_TARGETS = ("anchor", "half")


@dataclass(frozen=True)
class MRCombo:
    anchor: str        # "vwap" | "open"
    entry_z: float     # enter when price is this many prior-day ATRs below anchor
    entry_style: str   # "marketable" | "passive"
    exit_target: str   # "anchor" | "half"

    @property
    def key(self) -> str:
        return f"{self.anchor}|z{self.entry_z:g}|{self.entry_style}|{self.exit_target}"


def session_anchor(anchor: str, open_: np.ndarray, high: np.ndarray,
                   low: np.ndarray, close: np.ndarray, volume: np.ndarray,
                   vwap: np.ndarray | None = None) -> np.ndarray:
    """Per-bar anchor level, causal: bar t's anchor uses bars 0..t only.

    ``vwap`` is the running session VWAP (the feed's per-minute VWAP weighted
    by volume when available, else the typical price); ``open`` is the session
    opening print held flat, the simplest possible anchor."""
    if anchor == "open":
        return np.full(close.shape, float(open_[0]))
    price = vwap if vwap is not None else (high + low + close) / 3.0
    vol = np.clip(volume.astype(float), 0.0, None)
    num = np.cumsum(price * vol)
    den = np.cumsum(vol)
    # Zero-volume warmup bars fall back to the typical price of the bar.
    out = np.where(den > 0, num / np.where(den > 0, den, 1.0), price)
    return out


def trade_path(bars: dict, session_open: datetime, session_close: datetime,
               combo: MRCombo, atr_pct: float, flatten_buffer_min: int,
               passive_ttl_min: int = 5, stop_atr: float = 1.0,
               entry_override: int | None = None) -> TradePath | None:
    """One (symbol, session) mean-reversion lifecycle, or None.

    ``atr_pct`` is the prior-day ATR as a fraction of price (strictly prior);
    a name without it cannot be scaled and is skipped. ``entry_override``
    is the timing-null seam: enter at that bar under the same anchor-derived
    stop/target, so the null destroys the ENTRY TIMING and nothing else."""
    ts, open_, high = bars["ts"], bars["open"], bars["high"]
    low, close = bars["low"], bars["close"]
    volume = bars.get("volume", np.ones_like(close))
    if not np.isfinite(atr_pct) or atr_pct <= 0 or len(ts) < 3:
        return None

    tradable = ts < _cutoff(ts, session_close - timedelta(minutes=flatten_buffer_min))
    flatten_idx = int(tradable.sum()) - 1
    if flatten_idx <= 1:
        return None
    anchor = session_anchor(combo.anchor, open_, high, low, close, volume,
                            bars.get("vwap"))

    if entry_override is not None:
        signal_idx = int(entry_override) - 1
        if not (0 <= signal_idx < flatten_idx):
            return None
    else:
        scale = atr_pct * close
        stretch = (close - anchor) <= -combo.entry_z * scale
        stretch[flatten_idx:] = False
        fired = np.flatnonzero(stretch)
        if fired.size == 0:
            return None
        signal_idx = int(fired[0])

    # --- entry -----------------------------------------------------------
    # The null randomizes WHEN the signal fires, never HOW it is filled: a
    # passive combo's null must also rest a limit and risk not being filled,
    # or the null would pay a spread the champion doesn't and flatter it.
    if combo.entry_style == "passive":
        # Rest a limit at the signal bar's close; fill only if a later bar
        # trades strictly through it, within the order's lifetime.
        limit = float(close[signal_idx])
        last = min(signal_idx + passive_ttl_min, flatten_idx)
        hit = np.flatnonzero(low[signal_idx + 1:last + 1] < limit)
        if hit.size == 0:
            return None  # never filled — the dip did not come to us
        entry_idx = signal_idx + 1 + int(hit[0])
        entry_px, entry_passive = limit, True
    else:
        entry_idx = signal_idx + 1
        if entry_idx > flatten_idx:
            return None
        entry_px, entry_passive = float(open_[entry_idx]), False

    stop_px = entry_px - stop_atr * atr_pct * entry_px
    if stop_px <= 0:
        return None

    # --- exit ------------------------------------------------------------
    for j in range(entry_idx, flatten_idx + 1):
        if float(open_[j]) <= stop_px:  # gapped through: fill at the open
            return TradePath(entry_idx, entry_px, j, float(open_[j]), "stop",
                             stop_px, entry_passive=entry_passive)
        if float(low[j]) <= stop_px:  # stop before target inside the bar
            return TradePath(entry_idx, entry_px, j, stop_px, "stop",
                             stop_px, entry_passive=entry_passive)
        target = (float(anchor[j]) if combo.exit_target == "anchor"
                  else entry_px + (float(anchor[j]) - entry_px) / 2.0)
        if target > entry_px and float(high[j]) > target:  # strict trade-through
            return TradePath(entry_idx, entry_px, j, target, "target",
                             stop_px, entry_passive=entry_passive, exit_passive=True)
    return TradePath(entry_idx, entry_px, flatten_idx, float(close[flatten_idx]),
                     "close", stop_px, entry_passive=entry_passive)


def combos_from_config(cfg) -> list[MRCombo]:
    return [MRCombo(anchor, z, style, target)
            for anchor in cfg.intraday.mr_anchors
            for z in cfg.intraday.mr_entry_z
            for style in cfg.intraday.mr_entry_styles
            for target in cfg.intraday.mr_exit_targets]
