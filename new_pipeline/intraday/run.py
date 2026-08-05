"""Official intraday ORB run: vault -> universe -> simulate -> gauntlet.

Two-pass over the window to keep memory flat at Liquid-scale: pass A builds
the session-daily aggregates for the whole window (light) and fixes each
session's scanner picks and trailing stats from them; pass B re-loads minute
bars month by month, RETAINS only each session's picked tickers (the only
names the book can touch), simulates, and hands the retained subset to the
evaluator so the timing null replays the identical data.

Usage:
  python -m new_pipeline.intraday.run --start 2024-09-01 --end 2026-07-31 \
      [--output-dir data/intraday_runs/<id>] [--equity 100000]
"""

from __future__ import annotations

import argparse
import json
import secrets
from datetime import UTC, date, datetime
from pathlib import Path

import polars as pl

from new_pipeline.config import get_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.intraday.calendar import load_sessions
from new_pipeline.intraday.data import (
    filter_to_sessions,
    load_minutes,
    months_between,
    session_daily,
)
from new_pipeline.intraday.evaluate import REGISTRY_KEY, evaluate_orb, record
from new_pipeline.intraday.orb import trials_from_config
from new_pipeline.intraday.quotes import load_quote_vault, quote_stats_for
from new_pipeline.intraday.scanner import apply_floors, build_signal_frame, scan_day
from new_pipeline.intraday.simulate import run_backtest_trials, trailing_stats
from new_pipeline.intraday.universe import segment_symbols

SLUG = "intraday_orb"


def _month_window(year: int, month: int) -> tuple[datetime, datetime]:
    start = datetime(year, month, 1, tzinfo=UTC)
    end = (datetime(year + 1, 1, 1, tzinfo=UTC) if month == 12
           else datetime(year, month + 1, 1, tzinfo=UTC))
    return start, end


def run(start: date, end: date, output_dir: Path, equity: float, seed: int = 0) -> dict:
    cfg = get_config()
    seed_everything(seed)
    sessions_all = load_sessions()
    sessions = {d: s for d, s in sessions_all.items() if start <= d <= end}
    symbols = segment_symbols(cfg)
    vault = Path(cfg.intraday.vault_dir)
    print(f"{SLUG}: {len(symbols)} symbols, {len(sessions)} sessions, vault={vault}")

    # Pass A: dailies for the whole window (+1 month back for trailing warmup).
    daily_frames = []
    months = months_between(start, end)
    warm_y, warm_m = ((months[0][0] - 1, 12) if months[0][1] == 1
                      else (months[0][0], months[0][1] - 1))
    for year, month in [(warm_y, warm_m), *months]:
        w_start, w_end = _month_window(year, month)
        chunk = load_minutes(vault, symbols, w_start, w_end)
        regular = filter_to_sessions(chunk, sessions_all)
        if not regular.is_empty():
            daily_frames.append(session_daily(regular))
    if not daily_frames:
        raise SystemExit("no minute data in the window — run ingest_minute_vault first")
    daily = pl.concat(daily_frames).sort(["ticker", "date"])
    print(f"dailies: {daily.height} rows, {daily['ticker'].n_unique()} names")

    signals = apply_floors(build_signal_frame(daily), cfg.intraday.min_adv_dollars,
                           cfg.intraday.min_price)
    picks_by_variant: dict[str, dict] = {}
    for variant in cfg.intraday.scanner_variants:
        picks_by_variant[variant] = {
            day: scan_day(signals, day, cfg.intraday.scanner_top_n, weights=variant)
            for day in sorted(sessions)}
    stats = trailing_stats(daily)
    # Join the MEASURED quote statistics; where a name-month has no cell the
    # Corwin-Schultz fallback applies and the coverage share is reported, so a
    # thin vault is visible in the manifest rather than silently assumed away.
    quote_vault = load_quote_vault(Path(cfg.intraday.quote_vault_dir))
    qs = quote_stats_for(quote_vault, sorted(sessions))
    if not qs.is_empty():
        stats = stats.join(qs, on=["date", "ticker"], how="left")
        covered = float(stats["half_spread_bps"].is_not_null().mean())
    else:
        covered = 0.0
    print(f"quote vault: {quote_vault.height} cells, "
          f"measured-spread coverage {covered:.1%} of name-days"
          + ("" if covered else " — FALLING BACK to Corwin-Schultz (~4x biased)"))
    for variant, picks in picks_by_variant.items():
        active = sum(1 for p in picks.values() if p)
        print(f"scanner[{variant}]: {active}/{len(sessions)} sessions, "
              f"top {cfg.intraday.scanner_top_n}")

    # Pass B: minute bars for picked names only, month by month.
    minutes_by_day: dict[date, pl.DataFrame] = {}
    for year, month in months:
        w_start, w_end = _month_window(year, month)
        month_days = [d for d in sessions if d.year == year and d.month == month]
        needed = sorted({t for picks in picks_by_variant.values()
                         for d in month_days for t in picks.get(d, [])})
        if not needed:
            continue
        chunk = filter_to_sessions(load_minutes(vault, needed, w_start, w_end), sessions_all)
        if chunk.is_empty():
            continue
        for day, sub in chunk.partition_by("session_date", as_dict=True).items():
            key = day[0] if isinstance(day, tuple) else day
            if key in sessions:
                minutes_by_day[key] = sub

    trials = trials_from_config(cfg)
    matrix, days, ledger = run_backtest_trials(minutes_by_day, sessions,
                                               picks_by_variant, trials, stats,
                                               cfg, equity)
    print(f"simulated: {matrix.shape[0]} sessions x {matrix.shape[1]} trials "
          f"({len(cfg.intraday.scanner_variants)} scanners x "
          f"{len(trials) // max(len(cfg.intraday.scanner_variants), 1)} constructions), "
          f"{len(ledger)} trades")

    result = evaluate_orb(matrix, days, trials, ledger, daily, minutes_by_day,
                          sessions, picks_by_variant, stats, cfg, equity, seed=seed)

    output_dir.mkdir(parents=True, exist_ok=True)
    keys = [t.key for t in trials]
    pl.DataFrame({"date": days, **{k: matrix[:, j] for j, k in enumerate(keys)}}
                 ).write_parquet(output_dir / f"{SLUG}_returns_matrix.parquet")
    pl.DataFrame({"date": days}).write_parquet(output_dir / f"{SLUG}_sample_dates.parquet")
    if ledger:
        def _ts(v):  # numpy datetime64 -> python datetime for a typed column
            return v.astype("datetime64[us]").item() if hasattr(v, "astype") else v
        pl.DataFrame({
            "day": [t.day for t in ledger],
            "ticker": [t.ticker for t in ledger],
            "combo_key": [t.combo_key for t in ledger],
            "entry_ts": [_ts(t.entry_ts) for t in ledger],
            "exit_ts": [_ts(t.exit_ts) for t in ledger],
            "entry_px": [t.entry_px for t in ledger],
            "exit_px": [t.exit_px for t in ledger],
            "shares": [t.shares for t in ledger],
            "exit_reason": [t.exit_reason for t in ledger],
            "gross_pnl": [t.gross_pnl for t in ledger],
            "cost_dollars": [t.cost_dollars for t in ledger],
            "net_pnl": [t.net_pnl for t in ledger],
            "spread_bps": [t.spread_bps for t in ledger],
            "impact_bps": [t.impact_bps for t in ledger],
            "cs_spread_bps": [t.cs_spread_bps for t in ledger],
        }).write_parquet(output_dir / f"{SLUG}_ledger.parquet")

    verdict = result["verdict"]
    manifest = {
        "kind": "intraday_orb",
        "key": REGISTRY_KEY,
        "best_params": {"trial": result["champion"].key,
                        "scanner_variant": result["champion"].variant,
                        "scanner_variants_priced": cfg.intraday.scanner_variants,
                        "prior_trials_searched": cfg.intraday.prior_trials_searched,
                        **{f: getattr(cfg.intraday, f) for f in
                           ("entry_buffer_bps", "risk_bps", "max_position_pct",
                            "max_concurrent", "flatten_buffer_min", "spread_floor_bps",
                            "scanner_top_n", "min_adv_dollars", "min_price")}},
        "diagnostics": result["diagnostics"],
        "regime_breakdown": {
            "effective_threshold": getattr(verdict, "effective_threshold", None),
            "per_regime": {int(s): {"dsr": round(r.dsr, 4),
                                    "sr_period": round(r.sr_period, 4),
                                    "n_obs": r.n_obs}
                           for s, r in verdict.per_regime.items()},
        },
        "window": {"start": str(start), "end": str(end), "equity": equity, "seed": seed},
        "cost_model": {"measured_spread_coverage": round(covered, 4),
                       "quote_vault_cells": quote_vault.height,
                       "max_touch_participation": cfg.intraday.max_touch_participation,
                       "cs_fallback_allowed": cfg.intraday.allow_cs_fallback},
    }
    candidate_path = output_dir / f"{SLUG}_candidate.json"
    candidate_path.write_text(json.dumps(manifest, indent=1))
    row = record(output_dir / "promotion_registry.json", result, str(candidate_path))
    print(f"verdict: promoted={row['promoted']} reason={row['reason']!r} "
          f"dsr={row['dsr']:.4f} null_margin={row['synthetic_sharpe']:.3f} "
          f"pbo={row['pbo']:.3f}")
    return {"row": row, "manifest": manifest, "output_dir": str(output_dir)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--start", required=True)
    parser.add_argument("--end", required=True)
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--equity", type=float, default=None)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args()
    cfg = get_config()
    out = Path(args.output_dir) if args.output_dir else (
        Path("data/intraday_runs") / secrets.token_hex(6))
    run(date.fromisoformat(args.start), date.fromisoformat(args.end), out,
        args.equity or cfg.execution.account_capital, seed=args.seed)


if __name__ == "__main__":
    main()
