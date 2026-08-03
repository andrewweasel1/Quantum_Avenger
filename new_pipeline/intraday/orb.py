"""Opening range breakout mechanics: pure functions over one (symbol, session).

Conventions chosen for honesty over optimism, pinned by tests:
- Signals fire on bar CLOSES; entries fill at the NEXT bar's OPEN (no
  same-bar clairvoyance).
- On the exit walk, the STOP is checked before the target within a bar — when
  a single minute touches both, the fill assumes the adverse ordering.
- A bar that OPENS through the stop fills at that open (gap-through), never
  at the stop price.
- Everything still open is flattened at the close of the last bar at or
  before ``session_close - flatten_buffer`` — the exchange calendar's close,
  so early-close sessions flatten at 12:55 ET, not a fictional 15:55.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import numpy as np


def _cutoff(ts: np.ndarray, when: datetime):
    """Comparable cutoff for a bar-timestamp array: polars hands numpy
    tz-naive datetime64 (UTC-normalized), python fixtures hand object arrays
    of aware datetimes — the cutoff must match either representation."""
    if np.issubdtype(ts.dtype, np.datetime64):
        return np.datetime64(when.astimezone(UTC).replace(tzinfo=None))
    return when


@dataclass(frozen=True)
class Combo:
    k_minutes: int
    stop_style: str  # "or_low" | "or_mid"
    target_r: float  # 0.0 -> no profit target

    @property
    def key(self) -> str:
        target = "none" if self.target_r <= 0 else f"{self.target_r:g}R"
        return f"k{self.k_minutes}|{self.stop_style}|{target}"


@dataclass(frozen=True)
class TradePath:
    entry_idx: int
    entry_px: float
    exit_idx: int
    exit_px: float
    exit_reason: str  # "stop" | "target" | "close"
    stop_px: float
    # ORB range context; mean reversion leaves these at nan.
    or_high: float = float("nan")
    or_low: float = float("nan")
    # Liquidity-PROVIDING legs (a resting limit the market traded through) pay
    # no spread; liquidity-TAKING legs cross it. Breakouts take on both sides,
    # so these default False and the ORB path is unchanged.
    entry_passive: bool = False
    exit_passive: bool = False


def opening_range(ts: np.ndarray, high: np.ndarray, low: np.ndarray,
                  session_open: datetime, k_minutes: int) -> tuple[float, float, int]:
    """(or_high, or_low, first_index_after_range). Range bars are those whose
    OPEN timestamp falls before ``session_open + k``; thin tapes with zero
    range bars return (nan, nan, len) — no range, no trade."""
    in_range = ts < _cutoff(ts, session_open + timedelta(minutes=k_minutes))
    n_range = int(in_range.sum())
    if n_range == 0:
        return float("nan"), float("nan"), len(ts)
    return float(high[:n_range].max()), float(low[:n_range].min()), n_range


def trade_path(ts: np.ndarray, open_: np.ndarray, high: np.ndarray,
               low: np.ndarray, close: np.ndarray, session_open: datetime,
               session_close: datetime, combo: Combo, entry_buffer_bps: float,
               flatten_buffer_min: int,
               entry_override: int | None = None) -> TradePath | None:
    """The full long-only ORB lifecycle for one symbol-session, or None.

    Entry: first bar CLOSE above or_high*(1+buffer) after the range completes
    fires the signal; the fill is the NEXT bar's open. Entries are only taken
    while there is still room to exit (the fill bar must precede the flatten
    bar). At most one trade per symbol per session.

    ``entry_override`` (timing-null seam): skip the breakout scan and enter at
    that bar index instead — same range-derived stop/target, same flatten —
    so the null destroys exactly one thing, the breakout TIMING."""
    or_high, or_low, after = opening_range(ts, high, low, session_open, combo.k_minutes)
    if not np.isfinite(or_high) or after >= len(ts):
        return None
    tradable = ts < _cutoff(ts, session_close - timedelta(minutes=flatten_buffer_min))
    flatten_idx = int(tradable.sum()) - 1  # last bar strictly before the buffer
    if flatten_idx <= after:
        return None

    if entry_override is not None:
        entry_idx = int(entry_override)
        if not (after < entry_idx <= flatten_idx):
            return None
    else:
        trigger = or_high * (1.0 + entry_buffer_bps / 1e4)
        fired = np.flatnonzero(close[after:flatten_idx] > trigger)
        if fired.size == 0:
            return None
        entry_idx = after + int(fired[0]) + 1  # next-bar fill
        if entry_idx > flatten_idx:
            return None
    entry_px = float(open_[entry_idx])

    stop_px = or_low if combo.stop_style == "or_low" else (or_high + or_low) / 2.0
    if entry_px <= stop_px:  # gapped straight back through the range
        return TradePath(entry_idx, entry_px, entry_idx, entry_px, "stop",
                         stop_px, or_high, or_low)
    risk = entry_px - stop_px
    target_px = entry_px + combo.target_r * risk if combo.target_r > 0 else float("inf")

    for j in range(entry_idx, flatten_idx + 1):
        if float(open_[j]) <= stop_px:  # gap-through: fill at the open
            return TradePath(entry_idx, entry_px, j, float(open_[j]), "stop",
                             stop_px, or_high, or_low)
        if float(low[j]) <= stop_px:  # stop before target inside the bar
            return TradePath(entry_idx, entry_px, j, stop_px, "stop",
                             stop_px, or_high, or_low)
        if float(high[j]) >= target_px:
            return TradePath(entry_idx, entry_px, j, target_px, "target",
                             stop_px, or_high, or_low)
    return TradePath(entry_idx, entry_px, flatten_idx, float(close[flatten_idx]),
                     "close", stop_px, or_high, or_low)


def combos_from_config(cfg) -> list[Combo]:
    """The ORB construction axes, in a stable order."""
    return [Combo(k, stop, target)
            for k in cfg.intraday.range_minutes
            for stop in cfg.intraday.stop_styles
            for target in cfg.intraday.target_r_multiples]


@dataclass(frozen=True)
class Trial:
    """One priced experiment: a scanner weighting crossed with a construction.

    Making the SCANNER an axis of the trial family is the honest way to search
    "which signals should the scanner look at" — every weighting tried enters
    the same deflation, so a winner has to beat the bar the whole search set
    implies, not the bar its own slice would have."""

    variant: str
    combo: Combo

    @property
    def key(self) -> str:
        return f"{self.variant}|{self.combo.key}"


def constructions_from_config(cfg) -> list:
    """The configured strategy family's construction axes."""
    if getattr(cfg.intraday, "strategy", "orb") == "meanrev":
        from new_pipeline.intraday.meanrev import combos_from_config as mr_combos

        return mr_combos(cfg)
    return combos_from_config(cfg)


def trials_from_config(cfg) -> list[Trial]:
    return [Trial(variant, combo)
            for variant in cfg.intraday.scanner_variants
            for combo in constructions_from_config(cfg)]
