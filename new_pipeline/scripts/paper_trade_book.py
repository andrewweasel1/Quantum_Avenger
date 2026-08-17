"""Daily paper-trading executor for the Universe Long Short champion book.

The gauntlet's book is built from OUT-OF-SAMPLE bagged probabilities that only
exist inside a backtest; live, each name is scored by its sector's deployed
candidate booster (the standard train/serve approximation — documented, not
hidden). The book mechanics mirror the frozen champion spec exactly: per-ticker
5-day score smoothing, within-(date, sector) z-scores, one global top/bottom
``quantile`` cliff with the rank-hysteresis exit band, the calm-state policy on
the rolling-252 causal vol decoder, causal 5%% vol targeting, and the same
5-trading-day rebalance grid — carried across days by a small state file.

Safety: PAPER ONLY. The tool refuses to run unless the Alpaca key pair looks
like a paper key (``PK…``) and always constructs the broker with
``paper=True``. Dry-run is the default; pass ``--execute`` to submit orders.

    # after promoting the book + sector boosters:
    python -m new_pipeline.scripts.promote_candidates --run-dir <run>/output \
        --key "Universe Long Short" --all-sectors
    # then daily (cron ~30 min before the close):
    python -m new_pipeline.scripts.paper_trade_book --execute

RUNTIME: ~14 minutes end to end (measured 2026-08-05: 13m52s), almost all of
it in ``build_training_frame`` over the 420-day lookback for ~2,000 tickers.
Orders are submitted only AFTER that frame is built, so START BY 15:30 ET at
the latest for a 16:00 close, and run it detached — a 10-minute foreground
timeout kills it mid-frame, before it writes state or submits anything (that
failure is clean, but it costs the session's window).

Do NOT shorten --lookback-days to make it fit: under 252 trading days the
momentum/seasonality features starve and the scored universe collapses.
"""

import argparse
import json
import logging
import os
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import polars as pl
from new_pipeline.evaluation.promotion import PromotionRegistry
from new_pipeline.tournament.long_short import (
    LONG_SHORT_KEY,
    _band_leg,
    sector_neutral_scores,
    smooth_scores,
)
from new_pipeline.tournament.regime_state import causal_states_from_series
from new_pipeline.tournament.trainer import load_booster, predict_proba

_logger = logging.getLogger(__name__)

# Unit-return history retained in the state file: enough for the vol
# lookback many times over, bounded so the file cannot grow forever.
_UNIT_RETURN_HISTORY = 260

# Calendar span of per-session returns handed to compute_targets so a gap
# between runs can be caught up. Comfortably longer than any realistic
# outage, and bounded so the frame scan stays cheap.
_BACKFILL_WINDOW_DAYS = 120

# A flip submits a close then an open on the SAME symbol. Alpaca reserves the
# position against the pending close (held_for_orders == existing_qty), so an
# open fired immediately behind it sees available: 0 and is rejected — 22 of
# the 31 skips on the 2026-08-17 rebalance, every one of them a short leg that
# failed to open, which biases a dollar-neutral book long. Wait for the close
# to leave the pending states before releasing its open.
_FLIP_FILL_TIMEOUT_S = 20.0
_FLIP_POLL_S = 0.4
_TERMINAL_ORDER_STATES = {"filled", "canceled", "cancelled", "expired", "rejected"}


def await_close_fill(broker, order_id: str, timeout_s: float = _FLIP_FILL_TIMEOUT_S,
                     poll_s: float = _FLIP_POLL_S, now=time.monotonic,
                     sleep=time.sleep) -> str:
    """Block until ``order_id`` reaches a terminal state; returns that state.

    Returns "timeout" if it never settles — the caller must treat anything
    other than "filled" as "the shares are still reserved", because releasing
    the paired open then would simply be rejected again."""
    if not order_id:
        return "unknown"
    deadline = now() + timeout_s
    status = broker.order_status(order_id)
    while status not in _TERMINAL_ORDER_STATES:
        if now() >= deadline:
            return "timeout"
        sleep(poll_s)
        status = broker.order_status(order_id)
    return status


def compute_targets(panel: pl.DataFrame, params: dict, state: dict,
                    market_by_date: dict, causal_span: int | None = 252,
                    returns_by_date: dict | None = None) -> tuple[dict, dict]:
    """Target weights for the LAST date in ``panel`` under the champion
    mechanics, plus the evolved state file content.

    ``panel``: (date, ticker, sector, score, next-day scoring rows may carry
    null next_ret — realization is not needed to WEIGH). ``state`` carries
    ``held`` weights, ``unit_held`` (the UNSCALED shadow book), ``unit_returns``
    (trailing unit-book realized returns for the causal vol target),
    ``prev_longs``/``prev_shorts`` (band hysteresis) and
    ``last_rebalance_date``. Pure function — no I/O, no broker.

    ``returns_by_date`` maps session date -> {ticker: realized return}. Every
    session after ``last_return_date`` up to today is appended, one unit
    observation each, which is what the vol target measures. The backtest
    appends on EVERY day using the forward ``next_ret`` of the book it just
    set; live we cannot see forward, so the causal translation appends what
    the PREVIOUS book earned, before re-targeting — the same series shifted
    one period.

    Backfilling the gap is sound precisely because the book is STATIC between
    runs: no trades happen unless this script runs, so the weights held on a
    skipped session are the ones still in ``unit_held``. Without the backfill
    the estimator advances once per RUN rather than once per session — on
    2026-08-17 six sessions had elapsed and the series held two observations,
    so a 20-observation lookback would have taken months of calendar time and
    sampled the tape irregularly."""
    quantile = params["quantile"]
    band = params.get("rebalance_band", 0.0)
    calm_band = params.get("calm_rebalance_band")
    calm_days = params.get("calm_rebalance_days")
    rebalance_days = params.get("rebalance_days", 5)
    vol_target = params.get("vol_target_annual", 0.0)
    vol_lookback = params.get("vol_lookback_days", 20)
    min_names = params.get("min_names_per_day", 20)

    panel = smooth_scores(panel, params.get("score_smoothing_days", 5))
    panel = sector_neutral_scores(panel.drop_nulls(["score"]))
    day = panel.filter(pl.col("date") == panel["date"].max())
    today = day["date"][0]

    # Advance the unscaled shadow book BEFORE deciding today's action, so the
    # vol estimator gets one observation per session rather than one per
    # rebalance. Names with no return today are forced exits, mirroring
    # long_short.build_long_short_book.
    unit_held = dict(state.get("unit_held", {}))
    unit_returns = list(state.get("unit_returns", []))
    if not unit_held and state.get("held"):
        # Migration: a state file written before the shadow book existed has
        # `held` but no `unit_held`. Without this the shadow book stays empty
        # until the next rebalance and every hold day until then appends a
        # spurious 0.0, understating trailing vol exactly when the estimator
        # is filling. Renormalizing `held` to unit gross recovers the unscaled
        # book whatever scalar was in force when it was written.
        gross = sum(abs(w) for w in state["held"].values())
        if gross > 0:
            unit_held = {t: w / gross for t, w in state["held"].items()}
    last_ret_date = state.get("last_return_date")
    if returns_by_date:
        sessions = sorted(d for d in returns_by_date if str(d) <= str(today))
        # No recorded cursor means no history to reconstruct: take only the
        # latest session rather than inventing returns for a book whose
        # holdings on those days are unknown.
        pending = ([d for d in sessions if str(d) > str(last_ret_date)]
                   if last_ret_date else sessions[-1:])
        for session in pending:
            rets = returns_by_date[session]
            for name in [t for t in unit_held if t not in rets]:
                unit_held.pop(name)
            unit_returns.append(
                float(sum(w * rets[t] for t, w in unit_held.items())))
            last_ret_date = str(session)
        unit_returns = unit_returns[-_UNIT_RETURN_HISTORY:]
    state = {**state, "unit_held": unit_held, "unit_returns": unit_returns,
             "last_return_date": last_ret_date}

    all_days = sorted(market_by_date)
    states = causal_states_from_series(
        all_days, [market_by_date[d] for d in all_days], span=causal_span
    )
    is_calm = states.get(today, 0) == 0

    last_reb = state.get("last_rebalance_date")
    days_since = (
        np.busday_count(np.datetime64(last_reb, "D"), np.datetime64(today, "D"))
        if last_reb else 10**6
    )
    spacing = calm_days if (is_calm and calm_days) else rebalance_days
    if days_since < spacing:
        _logger.info("hold day (%sd since rebalance < %sd spacing%s)",
                     days_since, spacing, ", calm" if is_calm else "")
        return dict(state.get("held", {})), state

    n = day.height
    if n < min_names:
        _logger.warning("thin day (%d names < %d) -> flat", n, min_names)
        new_state = {**state, "held": {}, "unit_held": {}, "prev_longs": [],
                     "prev_shorts": [], "last_rebalance_date": str(today)}
        return {}, new_state

    ranked = day.sort("score", descending=True)["ticker"].to_list()
    k = max(1, int(n * quantile))
    effective_band = calm_band if (is_calm and calm_band is not None) else band
    if effective_band > 0.0:
        k_exit = max(k, int(n * quantile * (1.0 + effective_band)))
        rank = {t: i for i, t in enumerate(ranked)}
        longs = _band_leg(state.get("prev_longs", []), ranked, rank, k, k_exit, n, False)
        shorts = _band_leg(state.get("prev_shorts", []), ranked, rank, k, k_exit, n, True)
    else:
        longs, shorts = ranked[:k], ranked[n - k:]

    scalar = 1.0
    if vol_target > 0.0 and len(unit_returns) >= vol_lookback:
        trailing = float(np.std(unit_returns[-vol_lookback:], ddof=1)) * np.sqrt(252.0)
        if trailing > 0.0:
            scalar = min(1.0, vol_target / trailing)

    base = {t: 1.0 / (2 * k) for t in longs}
    for t in shorts:
        base[t] = base.get(t, 0.0) - 1.0 / (2 * k)
    weights = {t: w * scalar for t, w in base.items()}
    # unit_held is the shadow book at scalar 1: what the vol target measures.
    new_state = {**state, "held": weights, "unit_held": base,
                 "prev_longs": longs, "prev_shorts": shorts,
                 "last_rebalance_date": str(today)}
    return weights, new_state


def diff_orders(targets: dict, positions: dict, prices: dict, capital: float,
                min_order_notional: float = 25.0,
                fractionable: set | None = None) -> list[dict]:
    """Market orders that move current positions to target dollar weights.

    Integer share rounding at ~$185/name mis-sized the first live fill: the
    long leg's names average ~$300 (winners are expensive), so 1-share
    rounding overshot it to $83k vs the $50k target (+$34k net-long tilt).
    Long-side targets on ``fractionable`` names therefore trade in fractional
    quantities (3 decimals); Alpaca forbids fractional SHORT opens, so
    short-side targets stay integer (cheap losers round finely anyway).
    Sub-``min_order_notional`` diffs are skipped (churn guard).

    Side flips (long->short or short->long) split into a close order followed
    by an open order: Alpaca rejects a single order crossing through zero, and
    a fractional held long can only cross via an exact fractional close."""
    fractionable = fractionable or set()
    orders = []
    for symbol in sorted(set(targets) | set(positions)):
        price = prices.get(symbol)
        if not price or price <= 0:
            continue
        target_w = targets.get(symbol, 0.0)
        held = positions.get(symbol, 0.0)
        raw_shares = target_w * capital / price
        can_fraction = symbol in fractionable and target_w >= 0.0
        target_shares = round(raw_shares, 3) if can_fraction else int(round(raw_shares))
        if held and target_shares and (held > 0) != (target_shares > 0):
            close_qty = round(abs(held), 3) if held > 0 else int(round(abs(held)))
            if close_qty > 0:
                orders.append({"symbol": symbol, "qty": close_qty,
                               "side": "sell" if held > 0 else "buy",
                               "tif": "day", "flip": "close"})
            open_qty = (round(abs(target_shares), 3) if can_fraction
                        else int(abs(target_shares)))
            if open_qty > 0 and abs(target_shares) * price >= min_order_notional:
                orders.append({"symbol": symbol, "qty": open_qty,
                               "side": "buy" if target_shares > 0 else "sell",
                               "tif": "day", "flip": "open"})
            continue
        delta = round(target_shares - held, 3)
        if abs(delta) * price < min_order_notional:
            continue
        # Executable units: fractional only while the whole move stays on the
        # fractionable long side; otherwise whole shares, and a diff that
        # rounds to zero shares is unfillable dust — suppress, don't submit.
        frac_ok = can_fraction and held >= 0
        qty = round(abs(delta), 3) if frac_ok else int(round(abs(delta)))
        # A REDUCING order can never ask for more than the position holds.
        # int-rounding a fractional 1.732-share holding UP to 2 is rejected
        # outright ("insufficient qty available for order"), and because the
        # rejection is only logged the position silently survives the
        # rebalance — 31 of 38 skips on 2026-08-07 were exactly this. A full
        # exit therefore sells the EXACT holding (closing a fractional
        # position is always permitted, even on a non-fractionable symbol);
        # a partial reduce is clamped to what is there.
        reducing = held != 0.0 and (delta > 0.0) != (held > 0.0)
        if reducing:
            available = round(abs(held), 3)
            qty = available if target_shares == 0 else min(qty, available)
        if qty <= 0:
            continue
        orders.append({"symbol": symbol, "qty": qty,
                       "side": "buy" if delta > 0 else "sell", "tif": "day"})
    return orders


def _assert_paper(cfg) -> None:
    key = os.environ.get("QA_ALPACA__API_KEY", "")
    if not key.startswith("PK"):
        raise SystemExit(
            "refusing to run: QA_ALPACA__API_KEY does not look like a PAPER key "
            "(PK…). This tool only ever trades the paper account."
        )


def main() -> None:  # pragma: no cover - operational I/O around tested core
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--registry", default="./models/prod/promotion_registry.json")
    parser.add_argument("--state-file", default="./models/prod/book_state.json")
    parser.add_argument("--capital", type=float, default=None,
                        help="book notional (default execution.account_capital)")
    parser.add_argument("--lookback-days", type=int, default=420,
                        help="calendar warmup for features/smoothing/decoder history "
                             "(must cover the 252-trading-day momentum/seasonality "
                             "warmup; 90d starves them on real data and collapses "
                             "the scored universe)")
    parser.add_argument("--execute", action="store_true",
                        help="actually submit orders (default: dry-run print)")
    parser.add_argument("--force-rebalance", action="store_true",
                        help="ignore the grid spacing and re-target the full book "
                             "today (recovery tool, e.g. after a mis-scored book)")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    # Score under the FROZEN CHAMPION's config (feature families, factors,
    # events, fundamentals fixture, universe) — library defaults would build a
    # frame missing the columns the deployed boosters select. News/sentiment
    # features are not in any deployed manifest (causal screen dropped them),
    # so fusion stays off here: the neutral sentiment_score column suffices.
    from new_pipeline.api.overrides import build_overridden_config

    body = json.loads(Path("new_pipeline/config/champion_run_body.json").read_text())
    overrides = body["overrides"]
    overrides.pop("news", None)
    overrides.setdefault("fusion", {})["enabled"] = False
    overrides.setdefault("system", {})["run_mode"] = "paper"
    cfg = build_overridden_config(overrides)
    _assert_paper(cfg)
    registry = PromotionRegistry(args.registry)
    champions = registry.active_champions()
    if LONG_SHORT_KEY not in champions:
        raise SystemExit(f"{LONG_SHORT_KEY!r} is not promoted in {args.registry}; "
                         "run scripts.promote_candidates first")
    manifest = json.loads(Path(champions[LONG_SHORT_KEY]).read_text())
    params = manifest["best_params"]

    # Sector boosters are the book's SCORERS, loaded from the book's own
    # deployed directory — independent of champion status, so retiring the
    # sector champions from standalone trading does not blind the book.
    book_dir = Path(champions[LONG_SHORT_KEY]).parent
    boosters = {}
    for candidate in sorted(book_dir.glob("*_candidate.json")):
        if candidate.name.startswith("universe_long_short"):
            continue
        selected = candidate.with_name(candidate.name.replace(
            "_candidate.json", "_candidate_features.json"))
        manifest_features = json.loads(selected.read_text())
        key = manifest_features.get("metadata", {}).get("sector", candidate.stem)
        boosters[key] = (load_booster(candidate), manifest_features["features"])
    if not boosters:
        raise SystemExit("no sector boosters promoted; the book needs per-name "
                         "scores (promote with --all-sectors)")

    from new_pipeline.adapters import StaticUniverseProvider
    from new_pipeline.adapters.broker_alpaca import AlpacaBroker
    from new_pipeline.tournament.pipeline import build_training_frame

    universe = StaticUniverseProvider(
        Path(cfg.data.universe_path) if cfg.data.universe_path else None
    )
    from new_pipeline.adapters.factory import build_fundamentals_source

    fundamentals_source = build_fundamentals_source(cfg, universe)
    sectors = universe.sectors()
    start = date.today() - timedelta(days=args.lookback_days)
    frame = build_training_frame(
        list(sectors), sectors, start, date.today(), cfg=cfg,
        fundamentals_source=fundamentals_source,
        membership=universe.members(),
    )
    market_by_date = dict(
        frame.select("date", "market_next_ret").drop_nulls().unique(subset=["date"])
        .sort("date").iter_rows()
    )
    rows = []
    for key, (booster, selected) in boosters.items():
        sub = frame.filter(pl.col("sector") == key).with_columns(
            pl.col(selected).fill_nan(None)).drop_nulls(subset=selected)
        if sub.is_empty():
            continue
        proba = predict_proba(booster, sub.select(selected).to_numpy())
        rows.append(sub.select("date", "ticker", "sector").with_columns(
            pl.Series("score", proba)))
    panel = pl.concat(rows)

    state = (json.loads(Path(args.state_file).read_text())
             if Path(args.state_file).exists() else {})
    if args.force_rebalance:
        _logger.warning("--force-rebalance: ignoring grid spacing, full re-target")
        state.pop("last_rebalance_date", None)
    # Per-name returns for every recent session, so the shadow book can catch
    # up on sessions where this script did not run (it advances per SESSION,
    # not per run). Bounded to the trailing window the vol target can use.
    latest_date = frame["date"].max()
    recent = (
        frame.select("date", "ticker", "close").sort(["ticker", "date"])
        .with_columns((pl.col("close") / pl.col("close").shift(1).over("ticker") - 1.0)
                      .alias("ret"))
        .drop_nulls("ret")
        .filter(pl.col("date") > latest_date - timedelta(days=_BACKFILL_WINDOW_DAYS))
    )
    returns_by_date: dict = {}
    for row in recent.select("date", "ticker", "ret").iter_rows():
        returns_by_date.setdefault(row[0], {})[row[1]] = row[2]
    targets, new_state = compute_targets(panel, params, state, market_by_date,
                                         causal_span=params.get("causal_window_days", 252),
                                         returns_by_date=returns_by_date)
    _logger.info("shadow book: %d unit names, %d unit returns through %s (vol target needs %d)",
                 len(new_state.get("unit_held", {})), len(new_state.get("unit_returns", [])),
                 new_state.get("last_return_date"), params.get("vol_lookback_days", 20))

    latest = frame.filter(pl.col("date") == latest_date)
    prices = dict(latest.select("ticker", "close").iter_rows())
    capital = args.capital or cfg.execution.account_capital
    broker = AlpacaBroker(os.environ["QA_ALPACA__API_KEY"],
                         os.environ["QA_ALPACA__SECRET_KEY"], paper=True)
    positions = broker.get_positions()
    # Sizing-price sanity gate: the frame's closes size every order, so a feed
    # regression (the fake-source fallback priced ASML at $107 vs $1,655 live
    # and silently mis-sized the book 15x) must abort, not trade. Held names
    # carry a live mark from the broker — compare where both sides exist.
    marks = {p.symbol: float(p.current_price)
             for p in broker._client.get_all_positions() if float(p.current_price) > 0}
    checked = [(s, prices[s] / marks[s]) for s in marks if prices.get(s)]
    bad = [(s, r) for s, r in checked if not 0.5 <= r <= 2.0]
    if checked and len(bad) > max(2, 0.02 * len(checked)):
        worst = sorted(bad, key=lambda x: abs(x[1] - 1.0), reverse=True)[:5]
        raise SystemExit(
            f"refusing to trade: {len(bad)}/{len(checked)} sizing prices diverge "
            f">2x from live marks (worst: {worst}) — data feed regression?")
    try:
        from alpaca.trading.enums import AssetClass, AssetStatus
        from alpaca.trading.requests import GetAssetsRequest
        assets = broker._client.get_all_assets(
            GetAssetsRequest(status=AssetStatus.ACTIVE, asset_class=AssetClass.US_EQUITY))
        fractionable = {a.symbol for a in assets if getattr(a, "fractionable", False)}
    except Exception as exc:
        _logger.warning("fractionable lookup failed (%s); integer sizing", exc)
        fractionable = set()
    orders = diff_orders(targets, positions, prices, capital, fractionable=fractionable)

    print(f"book: {len([w for w in targets.values() if w > 0])} longs / "
          f"{len([w for w in targets.values() if w < 0])} shorts, "
          f"gross {sum(abs(w) for w in targets.values()):.2f}, "
          f"{len(orders)} orders vs {len(positions)} open positions")
    for order in orders[:20]:
        print(" ", order)
    if len(orders) > 20:
        print(f"  ... {len(orders) - 20} more")
    if not args.execute:
        print("DRY RUN — pass --execute to submit to the paper account")
        return
    # Persist the new anchors BEFORE submitting: new_state depends only on the
    # targets (not the fills), and a mid-loop crash previously lost the state
    # write, leaving the next run diffing against stale anchors.
    Path(args.state_file).parent.mkdir(parents=True, exist_ok=True)
    Path(args.state_file).write_text(json.dumps(new_state, indent=1))
    print(f"state saved -> {args.state_file}")
    submitted, skipped = 0, []
    failed_closes = set()
    for order in orders:
        if order.get("flip") == "open" and order["symbol"] in failed_closes:
            # the paired close didn't fill-submit; the open would be an
            # illegal zero-crossing order — hold the position until it can.
            skipped.append((order["symbol"], order["side"], "flip close failed"))
            _logger.warning("SKIPPED %s %s: flip close failed", order['side'], order['symbol'])
            continue
        try:
            receipt = broker.submit_order(order)
            submitted += 1
            _logger.info("submitted %s %s x%s -> %s", order['side'], order['symbol'],
                         order['qty'], receipt['status'])
            if order.get("flip") == "close" and receipt.get("status") not in ("filled",):
                # Hold the paired open until the close actually settles.
                state_ = await_close_fill(broker, receipt.get("order_id"))
                if state_ != "filled":
                    failed_closes.add(order["symbol"])
                    _logger.warning("flip close %s ended %s; holding its open leg",
                                    order["symbol"], state_)
        except Exception as exc:  # not-shortable / halted / rejected: skip, keep going
            if order.get("flip") == "close":
                failed_closes.add(order["symbol"])
            skipped.append((order["symbol"], order["side"], str(exc)[:90]))
            _logger.warning("SKIPPED %s %s: %s", order['side'], order['symbol'], exc)
    print(f"submitted {submitted}/{len(orders)} orders; skipped {len(skipped)}")
    if skipped:
        from collections import Counter
        reasons = Counter(m.split('"message":')[-1][:40] for _, _, m in skipped)
        print("  top skip reasons:", dict(reasons.most_common(3)))


if __name__ == "__main__":  # pragma: no cover
    main()
