"""Triple-barrier target labels (López de Prado) + friction fallback.

The supervised target is forward-looking by construction. For each entry bar
``t`` (entered at ``close[t]``) three barriers race over the next ``horizon``
bars:

* upper / profit-take ``close[t] + pt_mult * atr[t]`` — touched when ``high`` ≥ it,
* lower / stop-loss    ``close[t] - sl_mult * atr[t]`` — touched when ``low`` ≤ it,
* vertical / time      at ``t + horizon``.

The label is the outcome of whichever barrier is hit *first*: ``1`` if the
profit-take is hit first, ``0`` if the stop is hit first, and at the vertical
barrier ``1`` iff the close-to-close return clears ``cost_bps`` else ``0``. The
stop barrier mirrors the t+1 simulator's ATR stop (``sl_mult`` defaults to the
execution ``atr_stop_multiplier``), so the label and the realised trade
mechanics agree. When both horizontals are touched on the same bar the order is
unknowable intrabar, so we resolve conservatively to the stop (label ``0``).

Alongside the label we emit ``fwd_ret`` (the realised entry→first-touch return)
and ``t1_offset`` (bars ahead to the first touch) — the per-sample event span
that CPCV purges on, so train rows whose label window overlaps a test fold are
dropped. The final ``horizon`` rows have no vertical window and are NaN for the
caller to drop.

``friction_aware_labels`` (plain horizon-return-beats-cost) is retained as the
fallback used when intrabar high/low/ATR are unavailable.
"""

from dataclasses import dataclass

import numpy as np
import polars as pl


def friction_aware_labels(close, horizon: int = 1, cost_bps: float = 10.0) -> np.ndarray:
    """Binary label array: forward return over ``horizon`` beats round-trip cost."""
    prices = np.asarray(close, dtype=np.float64)
    n = prices.size
    labels = np.full(n, np.nan, dtype=np.float64)
    if horizon < 1 or n <= horizon:
        return labels
    forward_return = prices[horizon:] / prices[:-horizon] - 1.0
    labels[:-horizon] = (forward_return > cost_bps / 10000.0).astype(np.float64)
    return labels


def _horizon_forward_return(close, horizon: int) -> np.ndarray:
    """Close-to-close forward return over ``horizon`` bars; NaN-tailed."""
    prices = np.asarray(close, dtype=np.float64)
    n = prices.size
    out = np.full(n, np.nan, dtype=np.float64)
    if horizon >= 1 and n > horizon:
        out[:-horizon] = prices[horizon:] / prices[:-horizon] - 1.0
    return out


@dataclass(frozen=True)
class TripleBarrierResult:
    """Per-bar triple-barrier outcome arrays (NaN where no full window exists)."""

    label: np.ndarray      # {0.0, 1.0, NaN}
    fwd_ret: np.ndarray    # realised entry->first-touch return
    t1_offset: np.ndarray  # bars ahead to the first touch (event span), float w/ NaN tail


def triple_barrier_labels(
    high,
    low,
    close,
    atr,
    horizon: int = 1,
    pt_mult: float = 2.0,
    sl_mult: float = 2.0,
    cost_bps: float = 10.0,
) -> TripleBarrierResult:
    """First-touch triple-barrier labels with ATR-scaled profit-take/stop barriers."""
    highs = np.asarray(high, dtype=np.float64)
    lows = np.asarray(low, dtype=np.float64)
    closes = np.asarray(close, dtype=np.float64)
    atrs = np.asarray(atr, dtype=np.float64)
    n = closes.size

    label = np.full(n, np.nan, dtype=np.float64)
    fwd_ret = np.full(n, np.nan, dtype=np.float64)
    t1_offset = np.full(n, np.nan, dtype=np.float64)
    if horizon < 1 or n <= horizon:
        return TripleBarrierResult(label, fwd_ret, t1_offset)

    cost = cost_bps / 10000.0
    last_entry = n - horizon - 1
    for i in range(last_entry + 1):
        entry = closes[i]
        if entry <= 0.0:
            continue
        atr_i = atrs[i] if atrs[i] > 0.0 else 0.0
        upper = entry + pt_mult * atr_i
        lower = entry - sl_mult * atr_i

        touched = False
        for s in range(i + 1, i + horizon + 1):
            hit_stop = atr_i > 0.0 and lows[s] <= lower
            hit_take = atr_i > 0.0 and highs[s] >= upper
            if hit_stop:  # conservative: same-bar ties resolve to the stop
                label[i], fwd_ret[i], t1_offset[i] = 0.0, lower / entry - 1.0, float(s - i)
                touched = True
                break
            if hit_take:
                label[i], fwd_ret[i], t1_offset[i] = 1.0, upper / entry - 1.0, float(s - i)
                touched = True
                break
        if not touched:  # vertical barrier: friction-aware sign of the horizon return
            ret = closes[i + horizon] / entry - 1.0
            label[i] = 1.0 if ret > cost else 0.0
            fwd_ret[i], t1_offset[i] = ret, float(horizon)

    return TripleBarrierResult(label, fwd_ret, t1_offset)


def add_labels(
    frame: pl.DataFrame,
    horizon: int = 1,
    cost_bps: float = 10.0,
    pt_mult: float = 2.0,
    sl_mult: float = 2.0,
    method: str = "triple_barrier",
) -> pl.DataFrame:
    """Add ``target_label`` + ``fwd_ret`` + ``label_t1_offset`` per ticker.

    Uses the triple-barrier labeller when ``method == "triple_barrier"`` and
    intrabar ``high``/``low``/``atr`` are present; otherwise falls back to the
    plain friction-aware horizon label (with a fixed ``horizon`` event span).
    """
    use_tb = method == "triple_barrier" and all(c in frame.columns for c in ("high", "low", "atr"))
    groups = []
    for _, group in frame.sort("date").group_by("ticker", maintain_order=True):
        if use_tb:
            res = triple_barrier_labels(
                group["high"].to_numpy(),
                group["low"].to_numpy(),
                group["close"].to_numpy(),
                group["atr"].to_numpy(),
                horizon,
                pt_mult,
                sl_mult,
                cost_bps,
            )
            label, fwd, t1 = res.label, res.fwd_ret, res.t1_offset
        else:
            close = group["close"].to_numpy()
            label = friction_aware_labels(close, horizon, cost_bps)
            fwd = _horizon_forward_return(close, horizon)
            t1 = np.where(np.isnan(label), np.nan, float(horizon))
        groups.append(
            group.with_columns(
                pl.Series("target_label", label),
                pl.Series("fwd_ret", fwd),
                pl.Series("label_t1_offset", t1),
            )
        )
    return pl.concat(groups) if groups else frame
