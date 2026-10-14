"""Measured quote statistics: the intraday cost model's spread and depth.

Corwin-Schultz — a range-based estimator inferred from daily high/low —
overstated the spread on gap-selected small caps by ~4x (median 21.2 bps
implied half-spread vs 5.1 bps of real NBBO at the same fill timestamps).
The estimator sets almost the entire intraday trading cost, so it is
replaced here by a MEASUREMENT: sampled SIP quotes, stored per (symbol,
month).

Two numbers per cell, both medians over the sampled quotes:

``half_spread_bps``  (ask - bid) / 2 / mid * 1e4 — what a marketable leg
                     pays versus mid while it fits inside the touch.
``touch_notional``   displayed size at the touch, in dollars. Orders larger
                     than this walk the book, which is where the real
                     size-dependent cost lives (our meanrev orders ran a
                     median 6.77x the touch).

Sampling is deliberate and disclosed: K windows per month, spread across
sessions and across times of day, batched across symbols. A monthly median
cannot capture the spread at one specific dislocation — it is a large
improvement on a 4x-biased estimator, not a tick-accurate reconstruction.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

import numpy as np
import polars as pl

QUOTE_COLUMNS = ("symbol", "year", "month", "half_spread_bps",
                 "touch_notional", "n_quotes")


def cell_file(vault_dir: Path, year: int, month: int) -> Path:
    return Path(vault_dir) / "by_month" / f"quotes_{year:04d}{month:02d}.parquet"


def summarize_quotes(quotes, symbol: str) -> dict | None:
    """Median half-spread (bps) and displayed touch notional ($) for one
    symbol's sampled quotes. Crossed/locked or zero-priced quotes are dropped;
    Alpaca stock quote sizes are SHARES (verified against minute volume)."""
    halves, touch = [], []
    for q in quotes:
        bid, ask = float(q.bid_price or 0), float(q.ask_price or 0)
        if bid <= 0 or ask <= 0 or ask < bid:
            continue
        mid = (ask + bid) / 2.0
        halves.append((ask - bid) / 2.0 / mid * 1e4)
        size = min(float(q.bid_size or 0), float(q.ask_size or 0))
        if size > 0:
            touch.append(size * mid)
    if not halves:
        return None
    return {"symbol": symbol,
            "half_spread_bps": float(np.median(halves)),
            "touch_notional": float(np.median(touch)) if touch else 0.0,
            "n_quotes": len(halves)}


def load_quote_vault(vault_dir: Path) -> pl.DataFrame:
    """All committed cells as one frame; empty (not an error) when absent so a
    caller can fall back and say so."""
    files = sorted(Path(vault_dir).glob("by_month/quotes_*.parquet"))
    if not files:
        return pl.DataFrame(schema={"symbol": pl.Utf8, "year": pl.Int32, "month": pl.Int32,
                                    "half_spread_bps": pl.Float64,
                                    "touch_notional": pl.Float64, "n_quotes": pl.Int64})
    return pl.concat([pl.read_parquet(f) for f in files])


def quote_stats_for(vault: pl.DataFrame, days: list[date]) -> pl.DataFrame:
    """(date, ticker, half_spread_bps, touch_notional) — the monthly cell
    broadcast to each session in that month, ready to join a trading frame."""
    if vault.is_empty() or not days:
        return pl.DataFrame(schema={"date": pl.Date, "ticker": pl.Utf8,
                                    "half_spread_bps": pl.Float64,
                                    "touch_notional": pl.Float64})
    calendar = pl.DataFrame({"date": days}).with_columns(
        pl.col("date").dt.year().cast(pl.Int32).alias("year"),
        pl.col("date").dt.month().cast(pl.Int32).alias("month"))
    return (calendar.join(vault, on=["year", "month"], how="inner")
            .select("date", pl.col("symbol").alias("ticker"),
                    "half_spread_bps", "touch_notional"))


def book_walk_impact_bps(notional: float, half_spread_bps: float,
                         touch_notional: float) -> float:
    """Cost of walking the book beyond the displayed touch, in bps.

    Filling ``notional`` against a touch displaying ``touch_notional`` consumes
    about ``notional / touch_notional`` price levels. Near the touch those
    levels sit roughly one half-spread apart, so the AVERAGE fill lands about
    ``half_spread * (ratio - 1) / 2`` beyond the touch price. Orders that fit
    inside the displayed size pay nothing extra.

    This replaces the bar-volume hydrodynamic term for the intraday stack: a
    minute bar's traded volume says nothing about how much size is RESTING at
    the touch, which is what a marketable order actually eats. It is an
    approximation pending fill-level calibration — the honest way to tighten
    it is to fit realized paper fills against decision-time mid."""
    if touch_notional <= 0 or notional <= touch_notional:
        return 0.0
    ratio = notional / touch_notional
    return max(half_spread_bps, 0.0) * (ratio - 1.0) / 2.0


def max_participation_shares(touch_notional: float, price: float,
                             max_touch_participation: float) -> float:
    """Share cap from displayed depth. Our meanrev orders ran a median 6.77x
    the touch — a sizing decision, not a market fact. Gross bps is
    size-invariant while impact bps is not, so capping participation improves
    net directly, at the cost of deploying fewer dollars."""
    if touch_notional <= 0 or price <= 0 or max_touch_participation <= 0:
        return float("inf")  # no measurement -> no cap (the caller discloses it)
    return max_touch_participation * touch_notional / price
