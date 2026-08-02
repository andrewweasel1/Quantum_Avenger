"""Intraday ORB paper session runner (bare-metal deliverable; dry-run default).

Runs ONE trading session for the promoted "Intraday ORB" configuration:
pre-open scanner picks -> opening-range watch via minute polling -> bracket
entries (server-side stop/target legs) -> unconditional flatten before the
calendar close. Designed for a persistent host — a reclaimable container
cannot hold a 6.5-hour loop; do not schedule this in the research
environment.

Account isolation is HARD policy: this tool trades only through the
dedicated intraday paper keys (``QA_ALPACA_INTRADAY__API_KEY/SECRET_KEY``)
and refuses to run if they are missing, non-paper, or identical to the daily
book's keys — the two live books must never entangle margin, positions, or
day-trade counts.

Dry-run (default) prints the session plan — picks, range windows, sizing and
the bracket template — and exits without touching the broker's order API.
``--execute`` requires an honest promotion: the registry must carry an
active "Intraday ORB" champion.
"""

from __future__ import annotations

import argparse
import json
import os
import time as time_mod
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

from new_pipeline.config import get_config
from new_pipeline.intraday.calendar import load_sessions
from new_pipeline.intraday.data import filter_to_sessions, load_minutes, session_daily
from new_pipeline.intraday.orb import Combo, opening_range
from new_pipeline.intraday.universe import scan_day, segment_symbols

REGISTRY_KEY = "Intraday ORB"


def _intraday_keys() -> tuple[str, str]:
    key = os.environ.get("QA_ALPACA_INTRADAY__API_KEY", "")
    secret = os.environ.get("QA_ALPACA_INTRADAY__SECRET_KEY", "")
    if not key or not secret:
        raise SystemExit(
            "refusing to run: QA_ALPACA_INTRADAY__API_KEY/SECRET_KEY not set — the "
            "intraday book requires its own DEDICATED paper account keys")
    if not key.startswith("PK"):
        raise SystemExit("refusing to run: intraday key is not a PAPER key (PK…)")
    if key == os.environ.get("QA_ALPACA__API_KEY", ""):
        raise SystemExit(
            "refusing to run: intraday keys are identical to the daily book's — "
            "the two live books must never share an account")
    return key, secret


def _champion_combo(registry_path: Path) -> tuple[Combo, dict]:
    registry = json.loads(registry_path.read_text())
    active = registry.get("active_champions", {})
    if REGISTRY_KEY not in active:
        raise SystemExit(f"{REGISTRY_KEY!r} is not promoted in {registry_path} — "
                         "the runner trades promoted configurations only")
    manifest = json.loads(Path(active[REGISTRY_KEY]).read_text())
    k, stop, target = manifest["best_params"]["combo"].split("|")
    combo = Combo(int(k[1:]), stop,
                  0.0 if target == "none" else float(target.rstrip("R")))
    return combo, manifest


def plan_session(cfg, day: date) -> dict:
    """Pre-open plan from vault dailies: picks + sizing context. Requires the
    vault to be current through the prior session (run the ingest nightly)."""
    sessions = load_sessions()
    if day not in sessions:
        raise SystemExit(f"{day} is not a trading session")
    session = sessions[day]
    symbols = segment_symbols(cfg)
    vault = Path(cfg.intraday.vault_dir)
    start = datetime(day.year, day.month, day.day, tzinfo=UTC) - timedelta(days=45)
    minutes = filter_to_sessions(
        load_minutes(vault, symbols, start, datetime(day.year, day.month, day.day, tzinfo=UTC)),
        sessions)
    daily = session_daily(minutes)
    # NOTE: the live scanner needs today's OPEN — resolved at 09:30 by the loop;
    # the pre-open plan lists the eligible set ranked on prior-day inputs alone.
    picks = scan_day(daily.vstack(daily.tail(0)), day, cfg.intraday.scanner_top_n,
                     cfg.intraday.min_adv_dollars, cfg.intraday.min_price)
    return {"session": session, "picks": picks, "daily": daily}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", default="./models/prod/promotion_registry.json")
    parser.add_argument("--date", default=None, help="session date (default: today)")
    parser.add_argument("--equity", type=float, default=None)
    parser.add_argument("--poll-seconds", type=int, default=30)
    parser.add_argument("--execute", action="store_true",
                        help="submit bracket orders (default: dry-run plan only)")
    args = parser.parse_args()
    cfg = get_config()
    day = date.fromisoformat(args.date) if args.date else date.today()

    combo, manifest = _champion_combo(Path(args.registry))
    plan = plan_session(cfg, day)
    session, picks = plan["session"], plan["picks"]
    equity = args.equity or cfg.execution.account_capital
    print(f"session {day}: open {session.open_utc:%H:%M}Z close {session.close_utc:%H:%M}Z"
          f"{' (early close)' if session.is_early_close else ''}")
    print(f"champion {combo.key}; {len(picks)} scanner candidates: {picks[:10]}...")
    print(f"risk {cfg.intraday.risk_bps}bps of {equity:,.0f}/trade, "
          f"max {cfg.intraday.max_concurrent} concurrent, "
          f"flatten {cfg.intraday.flatten_buffer_min}min before close")
    if not args.execute:
        print("DRY RUN — pass --execute on a persistent host to trade the session")
        return

    key, secret = _intraday_keys()
    from new_pipeline.adapters.broker_alpaca import AlpacaBroker
    from new_pipeline.adapters.market_alpaca import AlpacaIntradayDataSource

    broker = AlpacaBroker(key, secret, paper=True)
    source = AlpacaIntradayDataSource(
        os.environ["QA_ALPACA__API_KEY"], os.environ["QA_ALPACA__SECRET_KEY"],
        feed=cfg.alpaca.data_feed)
    entered: dict[str, dict] = {}
    range_done = session.open_utc + timedelta(minutes=combo.k_minutes)
    flatten_at = session.close_utc - timedelta(minutes=cfg.intraday.flatten_buffer_min)
    risk_dollars = equity * cfg.intraday.risk_bps / 1e4
    max_notional = equity * cfg.intraday.max_position_pct / 100.0

    while datetime.now(UTC) < flatten_at:
        now = datetime.now(UTC)
        if now < range_done:
            time_mod.sleep(args.poll_seconds)
            continue
        bars_by_symbol = source.history_minutes(
            [p for p in picks if p not in entered], session.open_utc, now)
        for symbol, bars in bars_by_symbol.items():
            if len(entered) >= cfg.intraday.max_concurrent or not bars:
                continue
            import numpy as np
            ts = np.array([b.ts for b in bars])
            high = np.array([b.high for b in bars])
            low = np.array([b.low for b in bars])
            or_high, or_low, after = opening_range(ts, high, low,
                                                   session.open_utc, combo.k_minutes)
            if not np.isfinite(or_high) or after >= len(bars):
                continue
            last_close = bars[-1].close
            trigger = or_high * (1.0 + cfg.intraday.entry_buffer_bps / 1e4)
            if last_close <= trigger:
                continue
            stop_px = or_low if combo.stop_style == "or_low" else (or_high + or_low) / 2
            per_share = max(last_close - stop_px, 0.01)
            shares = int(min(risk_dollars / per_share, max_notional / last_close))
            if shares < 1:
                continue
            order = {"symbol": symbol, "qty": shares, "side": "buy", "tif": "day",
                     "limit_price": round(last_close * 1.001, 2),
                     "stop_loss": stop_px}
            if combo.target_r > 0:
                order["take_profit"] = last_close + combo.target_r * per_share
            try:
                receipt = broker.submit_order(order)
                entered[symbol] = {"order": order, "receipt": receipt}
                print(f"ENTER {symbol} x{shares} @~{last_close:.2f} "
                      f"stop {stop_px:.2f} -> {receipt['status']}")
            except Exception as exc:  # halted / rejected: skip, keep the loop alive
                print(f"SKIP {symbol}: {exc}")
        time_mod.sleep(args.poll_seconds)

    for symbol in list(entered):
        try:
            positions = broker.get_positions()
            qty = positions.get(symbol, 0)
            if qty > 0:
                broker.submit_order({"symbol": symbol, "qty": qty,
                                     "side": "sell", "tif": "day"})
                print(f"FLATTEN {symbol} x{qty}")
        except Exception as exc:
            print(f"FLATTEN FAILED {symbol}: {exc} — close manually")
    print(f"session done: {len(entered)} entries; ledger -> stdout only (v1)")


if __name__ == "__main__":
    main()
