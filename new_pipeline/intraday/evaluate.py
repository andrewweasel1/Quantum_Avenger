"""The honest gauntlet on SESSION returns: same gates, intraday axis.

One return per session per combo is the native shape the daily gauntlet
already consumes — deflated DSR with N_eff over the 12-combo family (all
per-period units; nothing annualized except display), PBO via CSCV, the
family-wise per-regime HMM gate decoded on the DAILY market series (bar
T^K = 0.95^3), and the ORB analog of the permutation null: a TIMING null
that re-runs the same picks with random entry minutes and identical
range-derived exits/costs, recorded in the standard ``synthetic_sharpe``
slot with its verbatim <=0 veto. No CPCV path gate: there is no trained
model and no OOS-probability path axis in a rule-based book (disclosed).
"""

from __future__ import annotations

import numpy as np
import polars as pl

from new_pipeline.evaluation.dsr import deflated_sharpe_report, effective_number_of_trials
from new_pipeline.evaluation.pbo import evaluate_cscv
from new_pipeline.evaluation.promotion import PromotionRegistry, assess_promotion
from new_pipeline.evaluation.regime_dsr import QuantitativeEvaluator, ThinRegimePolicy
from new_pipeline.intraday.simulate import run_session

REGISTRY_KEY = "Intraday ORB"


def _per_period_sharpe(column: np.ndarray) -> float:
    std = column.std(ddof=1)
    return float(column.mean() / std) if std > 0 else 0.0


def timing_null_margin(minutes_by_day, sessions, picks_by_day, combo, stats,
                       cfg, equity: float, n_iter: int, seed: int,
                       champion_sharpe: float) -> tuple[float, list[float]]:
    """champion_sharpe - Q95 of the random-entry null Sharpe distribution."""
    rng = np.random.default_rng(seed)
    days = sorted(d for d in minutes_by_day if d in sessions)
    nulls = []
    for _ in range(n_iter):
        rets = []
        for day in days:
            picks = picks_by_day.get(day, [])
            if not picks:
                rets.append(0.0)
                continue
            by_combo, _ = run_session(minutes_by_day[day], sessions[day], picks,
                                      [combo], stats, cfg, equity, entry_rng=rng)
            rets.append(by_combo.get(combo.key, 0.0))
        nulls.append(_per_period_sharpe(np.asarray(rets)))
    return champion_sharpe - float(np.quantile(nulls, 0.95)), nulls


def market_series(daily: pl.DataFrame, days: list) -> tuple[np.ndarray, np.ndarray]:
    """(equal-weight market daily returns, rolling vol) aligned to ``days`` —
    the regime decoder's inputs, from the same session-daily aggregates the
    rest of the stack uses."""
    mkt = (daily.sort(["ticker", "date"])
           .with_columns((pl.col("close") / pl.col("close").shift(1).over("ticker") - 1.0)
                         .alias("ret"))
           .drop_nulls("ret")
           .group_by("date").agg(pl.col("ret").mean()).sort("date"))
    aligned = {r["date"]: r["ret"] for r in mkt.iter_rows(named=True)}
    rets = np.asarray([aligned.get(d, 0.0) for d in days], dtype=float)
    vol = (pl.Series(rets).rolling_std(window_size=20).fill_null(strategy="backward")
           .fill_null(0.0).to_numpy())
    return rets, vol


def evaluate_orb(matrix: np.ndarray, days: list, combos, ledger, daily: pl.DataFrame,
                 minutes_by_day, sessions, picks_by_day, stats, cfg,
                 equity: float, seed: int = 0) -> dict:
    """Full gauntlet verdict + manifest diagnostics for the champion combo."""
    per_combo_sr = np.array([_per_period_sharpe(matrix[:, j])
                             for j in range(matrix.shape[1])])
    champ_idx = int(np.argmax(per_combo_sr))
    champion = combos[champ_idx]
    champ_sessions = matrix[:, champ_idx]

    n_eff = effective_number_of_trials(matrix.T)  # one trial per row
    report = deflated_sharpe_report(champ_sessions, n_eff,
                                    trial_sharpes=per_combo_sr.tolist())
    cscv = evaluate_cscv(matrix, n_partitions=cfg.evaluation.pbo_partitions)
    margin, nulls = timing_null_margin(
        minutes_by_day, sessions, picks_by_day, champion, stats, cfg, equity,
        n_iter=cfg.long_short.null_iterations, seed=seed,
        champion_sharpe=float(per_combo_sr[champ_idx]))

    mkt_rets, mkt_vol = market_series(daily, days)
    evaluator = QuantitativeEvaluator(
        cfg.evaluation.dsr_promotion_threshold, cfg.evaluation.hmm_states,
        cfg.evaluation.min_regime_obs, ThinRegimePolicy(cfg.evaluation.thin_regime_policy),
        random_state=0, family_wise=cfg.evaluation.regime_family_wise)
    verdict = evaluator.evaluate_model_robustness(
        champ_sessions, mkt_vol, n_eff, trial_sharpes=per_combo_sr.tolist(),
        decode_returns=mkt_rets)

    half = len(days) // 2
    champ_trades = [t for t in ledger if t.combo_key == champion.key]
    diagnostics = {
        "combo": champion.key,
        "session_sharpe": float(per_combo_sr[champ_idx]),
        "sr_annual_display": report.sr_annual,
        "n_sessions": len(days),
        "n_trades": len(champ_trades),
        "win_rate": (float(np.mean([t.net_pnl > 0 for t in champ_trades]))
                     if champ_trades else 0.0),
        "avg_cost_dollars": (float(np.mean([t.cost_dollars for t in champ_trades]))
                             if champ_trades else 0.0),
        "cost_share_of_gross": (
            float(sum(t.cost_dollars for t in champ_trades)
                  / max(sum(abs(t.gross_pnl) for t in champ_trades), 1e-9))),
        "first_half_sharpe": _per_period_sharpe(champ_sessions[:half]),
        "second_half_sharpe": _per_period_sharpe(champ_sessions[half:]),
        "timing_null_sharpes": nulls,
        "trial_sharpes": {c.key: float(s)
                          for c, s in zip(combos, per_combo_sr, strict=True)},
        "regime_promoted": bool(verdict.promoted),
    }

    decision = assess_promotion(
        REGISTRY_KEY,
        dsr=report.dsr,
        synthetic_sharpe=margin,
        dsr_threshold=cfg.evaluation.dsr_promotion_threshold,
        synthetic_min=cfg.evaluation.synthetic_sr_min,
        pbo=cscv.pbo,
        pbo_threshold=cfg.evaluation.pbo_threshold,
        psr=report.psr_vs_zero,
        haircut_sharpe=None,
        n_trades=len(champ_trades),
        n_obs=len(days),
    )
    if decision.promoted and not verdict.promoted:
        from dataclasses import replace
        decision = replace(decision, promoted=False, reason="failed per-regime DSR")
    return {"decision": decision, "verdict": verdict, "report": report,
            "diagnostics": diagnostics, "champion": champion}


def record(registry_path, result, model_path: str | None) -> dict:
    registry = PromotionRegistry(registry_path)
    return registry.record(result["decision"],
                           model_path=model_path if result["decision"].promoted else None)
