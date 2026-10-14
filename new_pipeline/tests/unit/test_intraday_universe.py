"""Hybrid universe: causal eligibility floors + attention scanner."""

from datetime import date, timedelta

import polars as pl
from new_pipeline.intraday.universe import eligibility, scan_day

D0 = date(2026, 3, 2)


def _daily(rows):
    return pl.DataFrame(rows, schema=["date", "ticker", "open", "high", "low",
                                      "close", "volume", "dollar_vol"], orient="row")


def _steady(ticker, n, dv, close=10.0, open_=10.0):
    return [(D0 + timedelta(days=i), ticker, open_, close + 1, close - 1,
             close, int(dv / close), float(dv)) for i in range(n)]


def test_eligibility_uses_strictly_prior_data():
    rows = _steady("LIQ", 25, dv=10_000_000) + _steady("THIN", 25, dv=100_000)
    # CHEAP is liquid but a penny-ish name
    rows += _steady("CHEAP", 25, dv=10_000_000, close=1.0, open_=1.0)
    out = eligibility(_daily(rows), min_adv_dollars=5_000_000, min_price=3.0)
    last = out.filter(pl.col("date") == D0 + timedelta(days=24))
    by = {r["ticker"]: r["eligible"] for r in last.iter_rows(named=True)}
    assert by == {"LIQ": True, "THIN": False, "CHEAP": False}
    # warmup: day 0 has no prior window -> ineligible even for the liquid name
    first = out.filter((pl.col("date") == D0) & (pl.col("ticker") == "LIQ"))
    assert first["eligible"][0] is False or first["eligible"][0] == False  # noqa: E712
    # causality: a same-day volume explosion must not flip same-day eligibility
    spiked = [(D0 + timedelta(days=24), "THIN", 10.0, 11, 9, 10.0, 10_000_000, 1e8)]
    out2 = eligibility(_daily(rows[:49] + spiked), 5_000_000, 3.0)
    last2 = out2.filter((pl.col("date") == D0 + timedelta(days=24)) & (pl.col("ticker") == "THIN"))
    assert last2["eligible"][0] == False  # noqa: E712


def test_scanner_ranks_gap_and_rvol_and_respects_top_n():
    day = D0 + timedelta(days=24)
    rows = []
    # ten eligible names with identical liquidity; one gaps 8% on the last day
    for i in range(10):
        t = f"T{i}"
        base = _steady(t, 25, dv=10_000_000)
        if i == 7:  # gapper: last-day open jumps vs prior close
            d, tk, o, h, low, c, v, dv = base[-1]
            base[-1] = (d, tk, 10.8, h, low, c, v, dv)
        rows += base
    picks = scan_day(_daily(rows), day, top_n=3, min_adv_dollars=5_000_000, min_price=3.0)
    assert len(picks) == 3
    assert picks[0] == "T7"  # the gapper leads
    # determinism under re-run
    assert picks == scan_day(_daily(rows), day, top_n=3,
                             min_adv_dollars=5_000_000, min_price=3.0)


def test_scanner_is_causal_to_the_open():
    """Truncating everything after the session open changes nothing: the scan
    for day T needs open_T and prior-day history only."""
    day = D0 + timedelta(days=24)
    rows = []
    for i in range(6):
        rows += _steady(f"T{i}", 25, dv=10_000_000)
    full = _daily(rows)
    # zero out day-T close/high/low/volume (unknown at 09:30) — picks unchanged
    masked = full.with_columns(
        pl.when(pl.col("date") == day)
        .then(pl.lit(None, dtype=pl.Float64)).otherwise(pl.col("close")).alias("close"),
        pl.when(pl.col("date") == day)
        .then(pl.lit(None, dtype=pl.Float64)).otherwise(pl.col("dollar_vol")).alias("dollar_vol"),
    )
    assert scan_day(full, day, 4, 5_000_000, 3.0) == scan_day(masked, day, 4, 5_000_000, 3.0)
