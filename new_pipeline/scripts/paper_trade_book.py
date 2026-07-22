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
"""

import argparse
import json
import logging
import os
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


def compute_targets(panel: pl.DataFrame, params: dict, state: dict,
                    market_by_date: dict, causal_span: int | None = 252) -> tuple[dict, dict]:
    """Target weights for the LAST date in ``panel`` under the champion
    mechanics, plus the evolved state file content.

    ``panel``: (date, ticker, sector, score, next-day scoring rows may carry
    null next_ret — realization is not needed to WEIGH). ``state`` carries
    ``held`` weights, ``unit_returns`` (trailing unit-book realized returns for
    the causal vol target), ``prev_longs``/``prev_shorts`` (band hysteresis)
    and ``last_rebalance_date``. Pure function — no I/O, no broker."""
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
        new_state = {**state, "held": {}, "prev_longs": [], "prev_shorts": [],
                     "last_rebalance_date": str(today)}
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
    unit_returns = state.get("unit_returns", [])
    if vol_target > 0.0 and len(unit_returns) >= vol_lookback:
        trailing = float(np.std(unit_returns[-vol_lookback:], ddof=1)) * np.sqrt(252.0)
        if trailing > 0.0:
            scalar = min(1.0, vol_target / trailing)

    weights = {t: scalar / (2 * k) for t in longs}
    for t in shorts:
        weights[t] = weights.get(t, 0.0) - scalar / (2 * k)
    new_state = {**state, "held": weights, "prev_longs": longs, "prev_shorts": shorts,
                 "last_rebalance_date": str(today)}
    return weights, new_state


def diff_orders(targets: dict, positions: dict, prices: dict, capital: float,
                min_order_notional: float = 25.0) -> list[dict]:
    """Market orders that move current share positions to target dollar
    weights; sub-``min_order_notional`` diffs are skipped (churn guard)."""
    orders = []
    for symbol in sorted(set(targets) | set(positions)):
        price = prices.get(symbol)
        if not price or price <= 0:
            continue
        target_shares = int(round(targets.get(symbol, 0.0) * capital / price))
        delta = target_shares - int(positions.get(symbol, 0))
        if delta == 0 or abs(delta) * price < min_order_notional:
            continue
        orders.append({"symbol": symbol, "qty": abs(delta),
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
    parser.add_argument("--lookback-days", type=int, default=90,
                        help="calendar warmup for smoothing/decoder history")
    parser.add_argument("--execute", action="store_true",
                        help="actually submit orders (default: dry-run print)")
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

    # Sector boosters: every OTHER active champion is a per-name scorer.
    boosters = {}
    for key, path in champions.items():
        if key == LONG_SHORT_KEY:
            continue
        selected = Path(path).with_name(Path(path).name.replace(
            "_candidate.json", "_candidate_features.json"))
        manifest_features = json.loads(selected.read_text())
        boosters[key] = (load_booster(path), manifest_features["features"])
    if not boosters:
        raise SystemExit("no sector boosters promoted; the book needs per-name "
                         "scores (promote with --all-sectors)")

    from new_pipeline.adapters import StaticUniverseProvider
    from new_pipeline.adapters.broker_alpaca import AlpacaBroker
    from new_pipeline.tournament.pipeline import build_training_frame

    universe = StaticUniverseProvider(
        Path(cfg.data.universe_path) if cfg.data.universe_path else None
    )
    sectors = universe.sectors()
    start = date.today() - timedelta(days=args.lookback_days)
    frame = build_training_frame(
        list(sectors), sectors, start, date.today(), cfg=cfg,
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
    targets, new_state = compute_targets(panel, params, state, market_by_date,
                                         causal_span=params.get("causal_window_days", 252))

    latest = frame.filter(pl.col("date") == frame["date"].max())
    prices = dict(latest.select("ticker", "close").iter_rows())
    capital = args.capital or cfg.execution.account_capital
    broker = AlpacaBroker(os.environ["QA_ALPACA__API_KEY"],
                         os.environ["QA_ALPACA__SECRET_KEY"], paper=True)
    positions = broker.get_positions()
    orders = diff_orders(targets, positions, prices, capital)

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
    for order in orders:
        receipt = broker.submit_order(order)
        _logger.info("submitted %s %s x%s -> %s", order['side'], order['symbol'],
                     order['qty'], receipt['status'])
    Path(args.state_file).parent.mkdir(parents=True, exist_ok=True)
    Path(args.state_file).write_text(json.dumps(new_state, indent=1))
    print(f"state saved -> {args.state_file}")


if __name__ == "__main__":  # pragma: no cover
    main()
