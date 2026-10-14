"""The honest gauntlet on SESSION returns: same gates, intraday axis.

One return per session per combo is the native shape the daily gauntlet
already consumes — deflated DSR with N_eff over the combo family (all
per-period units; nothing annualized except display), PBO via CSCV, PSR,
the Harvey-Liu multiple-testing HAIRCUT, White's REALITY CHECK over the
whole trial matrix, the family-wise per-regime HMM gate decoded on the
DAILY market series (bar T^K = 0.95^3), and the ORB analog of the
permutation null: a TIMING null that re-runs the same picks with random
entry minutes and identical range-derived exits/costs, recorded in the
standard ``synthetic_sharpe`` slot with its verbatim <=0 veto.

Two deliberate divergences from the daily stack, both disclosed:

* **No CPCV path gate.** It needs per-fold OOS probability paths from a
  trained model; a rule-based book has neither a model nor probabilities,
  so there is nothing to reconstruct paths from. Left None rather than
  faked.
* **Reality Check is always COMPUTED here** (it is cheap on a
  sessions x trials matrix and its absence was a real reporting gap),
  while the daily stack computes it only when enabled. Gating still
  honours ``reality_check_gate_enabled`` exactly as the daily stack does,
  so this changes what is recorded, never what is promoted.

The haircut prices ``len(trials) + intraday.prior_trials_searched``. The
second term exists because each run deflates only its OWN trials, while a
champion is the product of a search spanning runs: touch_cap was chosen in
v3, z2.5 in v3's sweep, top-50 in v4, the attention scanner in v5/v6.
Leaving it at 0 understates the real search — v7 priced 32 trials against
776 actually searched — so it is an explicit, recorded number rather than
a silent default.
"""

from __future__ import annotations

import numpy as np
import polars as pl

from new_pipeline.evaluation.dsr import deflated_sharpe_report, effective_number_of_trials
from new_pipeline.evaluation.haircut import haircut_sharpe_ratio
from new_pipeline.evaluation.pbo import evaluate_cscv
from new_pipeline.evaluation.promotion import PromotionRegistry, assess_promotion
from new_pipeline.evaluation.reality_check import whites_reality_check
from new_pipeline.evaluation.regime_dsr import QuantitativeEvaluator, ThinRegimePolicy
from new_pipeline.intraday.simulate import run_session

REGISTRY_KEY = "Intraday ORB"


def _per_period_sharpe(column: np.ndarray) -> float:
    std = column.std(ddof=1)
    return float(column.mean() / std) if std > 0 else 0.0


def timing_null_margin(minutes_by_day, sessions, picks_by_day, combo, stats,
                       cfg, equity: float, n_iter: int, seed: int,
                       champion_sharpe: float,
                       sizing: str = "uncapped") -> tuple[float, list[float]]:
    """Null for the ENTRY TIMING only: the champion's own scanner picks and
    construction, entered at random in-session minutes."""
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
                                      [combo], stats, cfg, equity, entry_rng=rng,
                                      sizing=sizing)
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


def evaluate_orb(matrix: np.ndarray, days: list, trials, ledger, daily: pl.DataFrame,
                 minutes_by_day, sessions, picks_by_variant, stats, cfg,
                 equity: float, seed: int = 0) -> dict:
    """Full gauntlet verdict + manifest diagnostics for the champion trial.

    ``trials`` are (scanner variant x construction) pairs and ``picks_by_variant``
    maps each variant to its own {day: picks}; a plain combo list with a single
    {day: picks} dict still works (single-variant runs)."""
    from new_pipeline.intraday.orb import Trial

    trials = [t if isinstance(t, Trial) else Trial("default", t) for t in trials]
    if not picks_by_variant or not isinstance(next(iter(picks_by_variant.values())), dict):
        picks_by_variant = {"default": picks_by_variant}
    per_combo_sr = np.array([_per_period_sharpe(matrix[:, j])
                             for j in range(matrix.shape[1])])
    # ACTIVITY FLOOR. Champion selection is an argmax over trials, and a trial
    # that barely trades can post an extreme Sharpe off a handful of wins
    # sitting in a sea of zero-return sessions. meanrev_v1 crowned a 3-trade
    # trial (0.6% of sessions) at +1.16 annualized while every trial that
    # genuinely traded was negative — so ineligible trials cannot be champion.
    icfg = cfg.intraday
    trade_counts: dict[str, int] = {}
    for t in ledger:
        trade_counts[t.combo_key] = trade_counts.get(t.combo_key, 0) + 1
    eligible = []
    activity = {}
    for j, trial in enumerate(trials):
        n_tr = trade_counts.get(trial.key, trade_counts.get(trial.combo.key, 0))
        active = float((matrix[:, j] != 0).mean())
        activity[trial.key] = {"n_trades": n_tr, "active_frac": round(active, 4)}
        if n_tr >= icfg.min_trades and active >= icfg.min_active_session_frac:
            eligible.append(j)
    if eligible:
        champ_idx = max(eligible, key=lambda j: per_combo_sr[j])
    else:
        champ_idx = int(np.argmax(per_combo_sr))  # reported, but vetoed below
    champion = trials[champ_idx]
    champ_sessions = matrix[:, champ_idx]
    champ_picks = picks_by_variant.get(champion.variant, {})

    n_eff = effective_number_of_trials(matrix.T)  # one trial per row
    report = deflated_sharpe_report(champ_sessions, n_eff,
                                    trial_sharpes=per_combo_sr.tolist())
    cscv = evaluate_cscv(matrix, n_partitions=cfg.evaluation.pbo_partitions)
    margin, nulls = timing_null_margin(
        minutes_by_day, sessions, champ_picks, champion.combo, stats, cfg, equity,
        n_iter=cfg.long_short.null_iterations, seed=seed,
        champion_sharpe=float(per_combo_sr[champ_idx]),
        sizing=champion.sizing)

    # Harvey-Liu haircut: what survives once the champion is discounted for
    # having been the best of the search. sr_annual matches the daily stack's
    # convention (it passes an annualized Sharpe with periods_per_year=252).
    # prior_trials_searched prices the axes fixed by EARLIER runs, which this
    # run's own trial count cannot see.
    priced_trials = len(trials) + max(int(getattr(icfg, "prior_trials_searched", 0)), 0)
    haircut = haircut_sharpe_ratio(
        report.sr_annual, len(days), priced_trials, cfg.evaluation.mt_method)
    # White's Reality Check over the FULL trial matrix: is the best column's
    # edge real, or the luckiest draw from the search? Always computed here.
    reality_p = float(whites_reality_check(
        matrix, cfg.evaluation.reality_check_bootstrap,
        cfg.evaluation.reality_check_block, seed=seed))

    mkt_rets, mkt_vol = market_series(daily, days)
    evaluator = QuantitativeEvaluator(
        cfg.evaluation.dsr_promotion_threshold, cfg.evaluation.hmm_states,
        cfg.evaluation.min_regime_obs, ThinRegimePolicy(cfg.evaluation.thin_regime_policy),
        random_state=0, family_wise=cfg.evaluation.regime_family_wise)
    verdict = evaluator.evaluate_model_robustness(
        champ_sessions, mkt_vol, n_eff, trial_sharpes=per_combo_sr.tolist(),
        decode_returns=mkt_rets)

    half = len(days) // 2
    # Trial runs tag ledger rows "<variant>|<combo>"; the single-variant compat
    # path leaves them bare — accept either spelling of the champion's trades.
    champ_keys = {champion.key, champion.combo.key}
    champ_trades = [t for t in ledger if t.combo_key in champ_keys]
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
        "scanner_variant": champion.variant,
        "sizing_model": champion.sizing,
        "gross_bps_mean": (
            float(np.mean([t.gross_pnl / max(t.shares * t.entry_px, 1e-9) * 1e4
                           for t in champ_trades])) if champ_trades else 0.0),
        "trial_sharpes": {t.key: float(s)
                          for t, s in zip(trials, per_combo_sr, strict=True)},
        "regime_promoted": bool(verdict.promoted),
        "haircut_sharpe": haircut.adjusted_sharpe,
        "haircut_fraction": haircut.haircut_fraction,
        "haircut_adjusted_pvalue": haircut.adjusted_pvalue,
        "haircut_observed_tstat": haircut.observed_tstat,
        "reality_check_pvalue": reality_p,
        "trials_priced_for_haircut": priced_trials,
        "prior_trials_searched": priced_trials - len(trials),
        "n_eligible_trials": len(eligible),
        "activity_floor": {"min_trades": icfg.min_trades,
                           "min_active_session_frac": icfg.min_active_session_frac},
        "trial_activity": activity,
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
        haircut_sharpe=haircut.adjusted_sharpe,
        reality_check_pvalue=reality_p,
        reality_check_gate_enabled=cfg.evaluation.reality_check_gate_enabled,
        reality_check_threshold=cfg.evaluation.reality_check_threshold,
        n_trades=len(champ_trades),
        n_obs=len(days),
    )
    from dataclasses import replace
    if not eligible:
        decision = replace(
            decision, promoted=False,
            reason=(f"no trial met the activity floor (>={icfg.min_trades} trades "
                    f"and >={icfg.min_active_session_frac:.0%} of sessions)"))
    elif decision.promoted and not verdict.promoted:
        decision = replace(decision, promoted=False, reason="failed per-regime DSR")
    return {"decision": decision, "verdict": verdict, "report": report,
            "diagnostics": diagnostics, "champion": champion}


def record(registry_path, result, model_path: str | None) -> dict:
    registry = PromotionRegistry(registry_path)
    return registry.record(result["decision"],
                           model_path=model_path if result["decision"].promoted else None)
