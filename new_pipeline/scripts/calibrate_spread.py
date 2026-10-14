"""Calibrate the intraday spread floor against REAL NBBO quotes.

``intraday.spread_floor_bps`` is the single largest term in the intraday cost
model — in the ORB runs ~80% of trades paid within a few bps of the floor, so
the verdict rests on an assumption rather than a measurement. This tool
replaces the assumption with data: it samples actual fill events from a
committed trade ledger, pulls the SIP quote stream around each fill, and
reports what a marketable order would really have paid.

Measured per event, at the fill minute:
  half_spread_bps = (ask - bid) / 2 / mid * 1e4   — cost vs mid for one side
  depth_ratio     = order notional / displayed notional at the touch

A quoted half-spread is the right estimate only while the order fits inside
displayed size; ``depth_ratio`` > 1 means the fill would walk the book and the
quoted figure UNDERSTATES cost, so the report keeps the two separate rather
than blending them into one number.

  python -m new_pipeline.scripts.calibrate_spread
      --ledger models/prod/evidence/orb_v2/intraday_orb_ledger.parquet
      --combo 'cheap_gap|k15|or_low|none' --sample 400
"""

from __future__ import annotations

import argparse
import json
import os
import time
from datetime import timedelta
from pathlib import Path

import numpy as np
import polars as pl
from new_pipeline.config import get_config


def _quote_stats(client, symbol: str, ts, notional: float, side: str,
                 window_s: int) -> dict | None:
    """Median quoted half-spread (bps) and depth ratio in [ts, ts+window]."""
    from alpaca.data.requests import StockQuotesRequest

    request = StockQuotesRequest(
        symbol_or_symbols=symbol, start=ts,
        end=ts + timedelta(seconds=window_s), feed="sip")
    try:
        quotes = client.get_stock_quotes(request).data.get(symbol, [])
    except Exception:
        return None
    halves, depths = [], []
    for q in quotes:
        bid, ask = float(q.bid_price or 0), float(q.ask_price or 0)
        if bid <= 0 or ask <= 0 or ask < bid:
            continue
        mid = (ask + bid) / 2.0
        halves.append((ask - bid) / 2.0 / mid * 1e4)
        # Alpaca stock quote sizes are SHARES, not round lots (verified: Ford's
        # touch would otherwise hold 879% of a full minute's volume).
        touch_shares = float(q.ask_size or 0) if side == "buy" else float(q.bid_size or 0)
        touch_price = ask if side == "buy" else bid
        if touch_shares > 0:
            depths.append(notional / (touch_shares * touch_price))
    if not halves:
        return None
    return {"half_spread_bps": float(np.median(halves)),
            "depth_ratio": float(np.median(depths)) if depths else None,
            "n_quotes": len(halves)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ledger", required=True)
    parser.add_argument("--combo", default=None)
    parser.add_argument("--sample", type=int, default=400, help="fill events to price")
    parser.add_argument("--window-seconds", type=int, default=60)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--sleep", type=float, default=0.05)
    parser.add_argument("--out", default=None)
    args = parser.parse_args()
    cfg = get_config()

    from alpaca.data.historical import StockHistoricalDataClient
    client = StockHistoricalDataClient(os.environ["QA_ALPACA__API_KEY"],
                                       os.environ["QA_ALPACA__SECRET_KEY"])

    ledger = pl.read_parquet(args.ledger)
    if args.combo:
        ledger = ledger.filter(pl.col("combo_key") == args.combo)
    ledger = ledger.with_columns((pl.col("shares") * pl.col("entry_px")).alias("notional"))
    # Both legs pay: sample entries (buys) and exits (sells) alike.
    legs = pl.concat([
        ledger.select(pl.col("ticker"), pl.col("entry_ts").alias("ts"),
                      pl.col("notional"), pl.lit("buy").alias("side")),
        ledger.select(pl.col("ticker"), pl.col("exit_ts").alias("ts"),
                      pl.col("notional"), pl.lit("sell").alias("side")),
    ]).sample(n=min(args.sample, 2 * ledger.height), seed=args.seed)

    rows, misses = [], 0
    for i, leg in enumerate(legs.iter_rows(named=True)):
        stats = _quote_stats(client, leg["ticker"], leg["ts"], leg["notional"],
                             leg["side"], args.window_seconds)
        if stats is None:
            misses += 1
        else:
            rows.append({**leg, **stats})
        time.sleep(args.sleep)
        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{legs.height} priced ({misses} without quotes)", flush=True)

    if not rows:
        raise SystemExit("no quotes returned — check SIP entitlement / window")
    frame = pl.DataFrame(rows)
    half = frame["half_spread_bps"].to_numpy()
    floor = cfg.intraday.spread_floor_bps
    qs = {f"p{int(q * 100)}": float(np.quantile(half, q))
          for q in (0.1, 0.25, 0.5, 0.75, 0.9, 0.95)}

    print(f"\nsampled {frame.height} fill events ({misses} without quotes)")
    print("REAL quoted half-spread (bps, one side):")
    print("  " + "  ".join(f"{k} {v:.1f}" for k, v in qs.items()))
    print(f"  mean {half.mean():.1f} | configured floor {floor:.1f}")
    print(f"  share of fills BELOW the configured floor: "
          f"{float((half < floor).mean()):.1%}")
    depth = frame["depth_ratio"].drop_nulls().to_numpy()
    if depth.size:
        print(f"\ndepth ratio (order notional / displayed at touch): "
              f"median {np.median(depth):.2f} | p90 {np.quantile(depth, 0.9):.2f}")
        print(f"  share of fills LARGER than displayed size: "
              f"{float((depth > 1).mean()):.1%} (these walk the book)")
    report = {"n_events": frame.height, "n_missing": misses,
              "half_spread_bps": qs, "half_spread_mean": float(half.mean()),
              "configured_floor_bps": floor,
              "share_below_floor": float((half < floor).mean()),
              "depth_ratio_median": float(np.median(depth)) if depth.size else None,
              "share_over_displayed": float((depth > 1).mean()) if depth.size else None,
              "window_seconds": args.window_seconds, "sample_seed": args.seed}
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(report, indent=1))
        print(f"\nreport -> {args.out}")


if __name__ == "__main__":
    main()
