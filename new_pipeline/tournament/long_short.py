"""Universe-wide cross-sectional long-short sleeve (the breadth strategy).

The audit's verdict: single-name long-only entries cannot clear a regime-robust
DSR when the best signals carry |IC| ~ 0.01 — but ~500 investable names per day
can (fundamental law: IR ~ IC * sqrt(breadth)). This sleeve ranks every name
daily by the model's genuine OUT-OF-SAMPLE probability (the ``{slug}_oos_proba``
artifacts captured in the CPCV grid loop), holds the top quantile against the
bottom quantile dollar-neutral, books next-day close-to-close returns net of a
turnover-based transaction cost, and rides the SAME promotion gauntlet as the
sector champions under the registry key :data:`LONG_SHORT_KEY`.

Design points (all deliberate):
- ONE universe-wide book, not 11 sector books: sector books hold ~10 names per
  leg (idiosyncratic noise, and eleven correlated shots at the gates); the
  universe book holds ~100 per leg. Scores are z-scored within (date, sector)
  first, so the book stays approximately sector-neutral without losing breadth.
- The trials axis is the SHARED grid-combo index: ``_DEFAULT_GRID`` is global,
  so combo j means the same hyperparameters in every sector — four genuine L/S
  trial series with no pre-selection (the per-sector argmax is never reused).
- The synthetic-gauntlet slot is filled by a within-date permutation null:
  destroy the score-return link while preserving each date's breadth and return
  cross-section, and require the champion to beat the 95th percentile of its
  own informationless null (recorded as ``synthetic_margin``; the existing
  ``synthetic_sharpe <= synthetic_min`` gate applies verbatim).
"""

import itertools
import json
import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import polars as pl

from new_pipeline.core.seeding import active_seed
from new_pipeline.tournament.grid_search import _DEFAULT_GRID
from new_pipeline.tournament.simulator import sharpe_ratio

_logger = logging.getLogger(__name__)

LONG_SHORT_KEY = "Universe Long Short"
_SLUG = "universe_long_short"


@dataclass(frozen=True)
class LongShortBook:
    """One realized daily book: net-of-cost returns plus its honesty diagnostics."""

    dates: list
    net: np.ndarray
    gross: np.ndarray
    turnover: np.ndarray  # one-way-ish: 0.5 * sum |delta weight| per day
    avg_names_per_leg: float
    avg_gross_exposure: float = 1.0  # mean sum|w|; < 1 when vol-targeting de-risks


def sector_neutral_scores(panel: pl.DataFrame, score_col: str = "score") -> pl.DataFrame:
    """Z-score ``score_col`` within (date, sector); degenerate dispersion -> 0.0.

    Mirrors ``features.factors._zscore`` semantics so the book ranks names
    against their sector peers before the global quantile cut."""
    mean = pl.col(score_col).mean().over(["date", "sector"])
    std = pl.col(score_col).std().over(["date", "sector"])
    z = (
        pl.when(pl.col(score_col).is_null())
        .then(None)
        .when(std.is_null() | (std == 0.0))
        .then(0.0)
        .otherwise((pl.col(score_col) - mean) / std)
    )
    return panel.with_columns(z.alias(score_col))


def smooth_scores(panel: pl.DataFrame, days: int) -> pl.DataFrame:
    """Trailing per-ticker rolling mean of the score (look-back only, so no
    leakage). Smoothing dampens day-to-day rank churn — the main turnover lever
    identified by the alpha-arc diagnostics."""
    if days <= 1:
        return panel
    return panel.sort(["ticker", "date"]).with_columns(
        pl.col("score").rolling_mean(window_size=days, min_samples=1).over("ticker")
    )


def build_long_short_book(
    panel: pl.DataFrame,
    quantile: float,
    cost_bps: float,
    min_names: int,
    sector_neutral: bool = True,
    rebalance_days: int = 1,
    vol_target_annual: float = 0.0,
    vol_lookback: int = 20,
) -> LongShortBook:
    """Dollar-neutral rank book from a (date, ticker, sector, score, next_ret)
    panel, re-ranked every ``rebalance_days`` trading days.

    On a REBALANCE day with n >= ``min_names`` scored names: long the top
    ``k = max(1, int(n * quantile))`` at +1/(2k), short the bottom k at -1/(2k)
    (unit gross); a thin rebalance day goes flat (unwind charged). Between
    rebalances the book HOLDS its weights — a held name missing from the panel
    is force-exited that day (its unwind is charged; delistings are real).
    ``gross_t = sum(w_held * next_ret_t)``; ``turnover_t = 0.5 * sum|delta w|``;
    ``net_t = gross_t - cost_bps/1e4 * turnover_t``. ``rebalance_days=1``
    reproduces the daily-rebalanced book exactly.

    ``vol_target_annual > 0`` de-risks (never levers): at each rebalance the
    weights are scaled by ``min(1, target / trailing_vol)``, where trailing vol
    is the CAUSAL annualized std of the UNIT-gross book's last ``vol_lookback``
    returns (strictly prior days; the estimator never sees its own scaling).
    Returns in hostile regimes shrink toward zero instead of staying
    large-and-wrong — the standard cure for regime-concentrated risk."""
    clean = panel.drop_nulls(["score", "next_ret"]).sort(["date", "ticker"])
    if sector_neutral and "sector" in clean.columns:
        clean = sector_neutral_scores(clean)
    dates, gross, turnover, leg_sizes, exposures = [], [], [], [], []
    held: dict[str, float] = {}
    unit_held: dict[str, float] = {}  # unscaled shadow book: the vol estimator
    unit_grosses: list[float] = []
    for index, day in enumerate(clean.partition_by("date", maintain_order=True)):
        tickers = day["ticker"].to_list()
        rets = dict(zip(tickers, day["next_ret"].to_list(), strict=True))
        day_turnover = 0.0
        # Forced exits first: a held name with no row today can't be held on.
        for name in [t for t in held if t not in rets]:
            day_turnover += 0.5 * abs(held.pop(name))
        for name in [t for t in unit_held if t not in rets]:
            unit_held.pop(name)
        if index % rebalance_days == 0:
            n = day.height
            base: dict[str, float] = {}
            if n >= min_names:
                order = day.sort("score", descending=True)
                ranked = order["ticker"].to_list()
                k = max(1, int(n * quantile))
                for i in range(k):
                    base[ranked[i]] = 1.0 / (2 * k)
                    base[ranked[n - 1 - i]] = base.get(ranked[n - 1 - i], 0.0) - 1.0 / (
                        2 * k
                    )
                leg_sizes.append(k)
            scalar = 1.0
            if vol_target_annual > 0.0 and len(unit_grosses) >= vol_lookback:
                trailing = float(np.std(unit_grosses[-vol_lookback:], ddof=1)) * np.sqrt(252.0)
                if trailing > 0.0:
                    scalar = min(1.0, vol_target_annual / trailing)
            target = {t: w * scalar for t, w in base.items()}
            day_turnover += 0.5 * sum(
                abs(target.get(t, 0.0) - held.get(t, 0.0)) for t in target.keys() | held.keys()
            )
            held = target
            unit_held = base
        day_gross = float(sum(w * rets[t] for t, w in held.items()))
        unit_grosses.append(float(sum(w * rets[t] for t, w in unit_held.items())))
        dates.append(day["date"][0])
        gross.append(day_gross)
        turnover.append(day_turnover)
        exposures.append(sum(abs(w) for w in held.values()))
    gross_arr = np.asarray(gross, dtype=np.float64)
    turn_arr = np.asarray(turnover, dtype=np.float64)
    net = gross_arr - (cost_bps / 1e4) * turn_arr
    return LongShortBook(
        dates=dates,
        net=net,
        gross=gross_arr,
        turnover=turn_arr,
        avg_names_per_leg=float(np.mean(leg_sizes)) if leg_sizes else 0.0,
        avg_gross_exposure=float(np.mean(exposures)) if exposures else 0.0,
    )


def permutation_null_margin(
    panel: pl.DataFrame,
    quantile: float,
    cost_bps: float,
    min_names: int,
    sector_neutral: bool,
    n_iter: int,
    null_quantile: float,
    champion_sharpe: float,
    rebalance_days: int = 1,
    vol_target_annual: float = 0.0,
    vol_lookback: int = 20,
) -> tuple[float, list[float]]:
    """Champion Sharpe minus the ``null_quantile`` of its informationless null.

    Each iteration permutes the (already-smoothed) score column WITHIN each
    date (breadth and the return cross-section preserved exactly; the
    score-return link destroyed) and rebuilds the net-of-cost book under the
    SAME mechanics — including the rebalance cadence, so a slow book is judged
    against slow-book nulls."""
    rng = np.random.default_rng(active_seed())
    null_sharpes = []
    for _ in range(n_iter):
        permuted = panel.with_columns(
            pl.col("score").shuffle(seed=int(rng.integers(0, 2**31))).over("date")
        )
        book = build_long_short_book(
            permuted, quantile, cost_bps, min_names, sector_neutral, rebalance_days,
            vol_target_annual, vol_lookback,
        )
        null_sharpes.append(sharpe_ratio(book.net))
    margin = champion_sharpe - float(np.quantile(null_sharpes, null_quantile))
    return margin, null_sharpes


def _proba_layout(columns: list[str]) -> tuple[int, int]:
    """(n_combos, phi) recovered from proba_c{j}_p{p} column names."""
    combos = {int(c.split("_")[1][1:]) for c in columns if c.startswith("proba_c")}
    paths = {int(c.split("_")[2][1:]) for c in columns if c.startswith("proba_c")}
    return len(combos), len(paths)


def run_universe_long_short(results: dict, output_dir, cfg) -> dict | None:
    """Assemble the universe book from every sector's OOS-proba artifact, run
    the combo trials + champion paths, persist the gauntlet artifacts, and
    return the ``_evaluate_and_promote``-shaped results entry (None when no
    sector artifacts exist or breadth never reaches ``min_names_per_day``)."""
    ls = cfg.long_short
    panels = []
    layout: tuple[int, int] | None = None
    for sector, result in results.items():
        path = Path(result["candidate_path"].replace("_candidate.json", "_oos_proba.parquet"))
        if not path.exists():
            _logger.warning("long-short: no OOS proba artifact for %s; skipping", sector)
            continue
        frame = pl.read_parquet(path).with_columns(pl.lit(sector).alias("sector"))
        this_layout = _proba_layout(frame.columns)
        if layout is None:
            layout = this_layout
        elif layout != this_layout:  # shared-grid invariant: combo j means the same params
            raise ValueError(
                f"long-short: proba layout mismatch for {sector}: {this_layout} != {layout}"
            )
        panels.append(frame)
    if not panels or layout is None:
        return None
    n_combos, phi = layout
    universe = pl.concat(panels)

    rebalance_days = getattr(ls, "rebalance_days", 1)
    smoothing = getattr(ls, "score_smoothing_days", 1)
    vol_target = getattr(ls, "vol_target_annual", 0.0)
    vol_lookback = getattr(ls, "vol_lookback_days", 20)

    def panel_for(score_expr: pl.Expr) -> pl.DataFrame:
        panel = universe.select(
            "date", "ticker", "sector", score_expr.alias("score"), "next_ret"
        )
        return smooth_scores(panel, smoothing)

    def book_for(score_expr: pl.Expr) -> LongShortBook:
        return build_long_short_book(
            panel_for(score_expr), ls.quantile, ls.cost_bps, ls.min_names_per_day,
            ls.sector_neutral, rebalance_days, vol_target, vol_lookback,
        )

    combo_mean = [
        pl.mean_horizontal([pl.col(f"proba_c{j}_p{p}") for p in range(phi)])
        for j in range(n_combos)
    ]
    books = [book_for(expr) for expr in combo_mean]
    if all(b.avg_names_per_leg == 0.0 for b in books):
        _logger.warning("long-short: breadth never reached min_names_per_day; sleeve skipped")
        return None
    trial_sharpes = [sharpe_ratio(b.net) for b in books]
    best = int(np.argmax(trial_sharpes))
    champion = books[best]

    path_books = [
        book_for(pl.col(f"proba_c{best}_p{p}")) for p in range(phi)
    ]
    champion_panel = panel_for(combo_mean[best])  # smoothed: the null permutes the book input
    margin, null_sharpes = permutation_null_margin(
        champion_panel, ls.quantile, ls.cost_bps, ls.min_names_per_day, ls.sector_neutral,
        ls.null_iterations, ls.null_quantile, trial_sharpes[best],
        rebalance_days=rebalance_days, vol_target_annual=vol_target, vol_lookback=vol_lookback,
    )

    output = Path(output_dir)
    pl.DataFrame(
        {f"trial_{j}": books[j].net for j in range(n_combos)}
    ).write_parquet(output / f"{_SLUG}_returns_matrix.parquet")
    pl.DataFrame({"date": champion.dates}).write_parquet(
        output / f"{_SLUG}_sample_dates.parquet"
    )
    pl.DataFrame(
        {f"path_{p}": path_books[p].net for p in range(phi)}
    ).write_parquet(output / f"{_SLUG}_paths.parquet")

    combos = [
        dict(zip(_DEFAULT_GRID, values, strict=True))
        for values in itertools.product(*_DEFAULT_GRID.values())
    ]
    gross_sharpe = sharpe_ratio(champion.gross)
    avg_turnover = float(champion.turnover.mean())
    diagnostics = {
        "net_sharpe": trial_sharpes[best],
        "gross_sharpe": gross_sharpe,
        "avg_daily_turnover": avg_turnover,
        "avg_names_per_leg": champion.avg_names_per_leg,
        "avg_gross_exposure": champion.avg_gross_exposure,
        # cost level (bps per unit turnover) at which the mean net return hits 0
        "breakeven_cost_bps": (
            float(champion.gross.mean() / avg_turnover * 1e4) if avg_turnover > 0 else None
        ),
        "synthetic_margin": margin,
        "null_sharpes": null_sharpes,
        "n_days": int(champion.net.size),
        "sectors": sorted(results),
    }
    candidate_path = output / f"{_SLUG}_candidate.json"
    candidate_path.write_text(
        json.dumps(
            {
                "kind": "long_short",
                "best_params": {
                    **(combos[best] if best < len(combos) else {"combo_index": best}),
                    "quantile": ls.quantile,
                    "cost_bps": ls.cost_bps,
                    "min_names_per_day": ls.min_names_per_day,
                    "sector_neutral": ls.sector_neutral,
                    "rebalance_days": rebalance_days,
                    "score_smoothing_days": smoothing,
                    "vol_target_annual": vol_target,
                    "vol_lookback_days": vol_lookback,
                },
                "diagnostics": diagnostics,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {
        "kind": "long_short",
        "selected_features": [],
        "best_params": combos[best] if best < len(combos) else {"combo_index": best},
        "best_sharpe": trial_sharpes[best],
        "trial_sharpes": trial_sharpes,
        "candidate_path": str(candidate_path),
        "synthetic_margin": margin,
        "meta_labeling": None,
        "diagnostics": diagnostics,
    }
