"""Deflation-unit contract: annualized trial Sharpes must be de-annualized
before entering any DSR benchmark, and the regime gate mirrors the full gate's
effective trial count. Regression for the sqrt(252) bug that made the
per-regime gate unclearable (run 57e4507c774f: slices with OOS annualized
Sharpe 2.7 rejected at DSR 0.005 against implied hurdles of 2.4-4.7 annual)."""

from types import SimpleNamespace

import numpy as np
from new_pipeline.evaluation.dsr import (
    compute_deflated_sharpe_ratio,
    deflated_sharpe_report,
    effective_number_of_trials,
    probabilistic_sharpe_ratio,
)
from new_pipeline.tournament.pipeline import (
    _deflated_sharpe,
    _per_period_trials,
    _regime_verdict,
)

ANNUAL_TRIALS = [0.6, 1.5, 0.9, 2.1]  # realistic grid dispersion, ANNUALIZED


def _cfg(use_effective_trials, family_wise=True):
    return SimpleNamespace(
        evaluation=SimpleNamespace(
            use_effective_trials=use_effective_trials,
            dsr_promotion_threshold=0.95,
            hmm_states=3,
            min_regime_obs=60,
            thin_regime_policy="skip",
            regime_family_wise=family_wise,
        )
    )


def _panel(sr_daily=0.25, n_per=300, seed=7):
    """Three PERSISTENT vol blocks (like real vol clustering) so the HMM decodes
    contiguous regimes instead of day-level sign partitions of iid noise; each
    block carries the same per-period Sharpe ``sr_daily``."""
    rng = np.random.default_rng(seed)
    vols = [5e-3, 1.2e-2, 2.5e-2]
    champ = np.concatenate([rng.normal(sr_daily * v, v, n_per) for v in vols])
    matrix = np.column_stack(
        [champ + rng.normal(0, 1e-5, 3 * n_per) for _ in range(4)]
    )
    return champ, matrix


def test_deflated_sharpe_deannualizes_trial_variance():
    champ, matrix = _panel()
    fixed = _deflated_sharpe(champ, ANNUAL_TRIALS, matrix, _cfg(False))
    expected = compute_deflated_sharpe_ratio(
        champ, np.asarray(ANNUAL_TRIALS) / np.sqrt(252.0)
    )
    assert fixed == expected
    buggy = compute_deflated_sharpe_ratio(champ, ANNUAL_TRIALS)  # old behavior
    assert buggy < 0.05 < fixed  # annualized variance made the benchmark absurd


def test_regime_gate_mirrors_full_gate_deflation_inputs():
    champ, matrix = _panel()
    cfg = _cfg(True)
    verdict = _regime_verdict(champ, ANNUAL_TRIALS, matrix, cfg)
    n_eff = effective_number_of_trials(matrix.T)
    states = np.asarray(verdict.states)
    trials_pp = _per_period_trials(ANNUAL_TRIALS)
    assert verdict.per_regime, "no testable regime in a 900-day series"
    for s, res in verdict.per_regime.items():
        seg = champ[states == s]
        independent = deflated_sharpe_report(seg, n_eff, trial_sharpes=trials_pp)
        assert res.dsr == independent.dsr  # same N_eff + per-period variance
        # near-perfectly-correlated combos: N_eff ~ 1 -> SR0 = 0 -> DSR == PSR-vs-0
        assert res.dsr == probabilistic_sharpe_ratio(seg, 0.0)


def test_exogenous_decode_states_track_market_not_strategy():
    """Regimes are states of the WORLD: with decode_returns = the market series,
    (a) two different strategies get IDENTICAL state sequences, and (b) the
    states follow the market's persistent vol blocks — not the strategy's own
    up/down days (the sign-partition degeneracy recorded on Liquid-1500)."""
    import pandas as pd
    from new_pipeline.evaluation.regime_dsr import QuantitativeEvaluator, ThinRegimePolicy

    rng = np.random.default_rng(5)
    market = np.concatenate([rng.normal(0.0004, v, 300) for v in (4e-3, 9e-3, 2.2e-2)])
    # mirror the pipeline: the decode's vol input is a SMOOTH rolling std
    vol = pd.Series(market).rolling(10).std().bfill().fillna(0.0).to_numpy()
    strat_a = rng.normal(0.0004, 0.002, market.size)  # smooth book A
    strat_b = rng.normal(-0.0002, 0.004, market.size)  # different book B
    ev = QuantitativeEvaluator(0.95, 3, 60, ThinRegimePolicy.SKIP, random_state=0)
    pp = np.array([0.5] * 4) / np.sqrt(252)
    va = ev.evaluate_model_robustness(strat_a, vol, 4, trial_sharpes=pp, decode_returns=market)
    vb = ev.evaluate_model_robustness(strat_b, vol, 4, trial_sharpes=pp, decode_returns=market)
    np.testing.assert_array_equal(np.asarray(va.states), np.asarray(vb.states))
    # persistence: market-block decode yields long runs, not 1-2 day sign flips
    st = np.asarray(va.states)
    st_runs = []
    for s in np.unique(st):
        m = (st == s).astype(int)
        e = np.flatnonzero(np.diff(np.concatenate([[0], m, [0]])))
        st_runs.append(float(np.mean(e.reshape(-1, 2)[:, 1] - e.reshape(-1, 2)[:, 0])))
    assert max(st_runs) > 20  # at least one genuinely persistent state


def test_decode_returns_length_mismatch_raises():
    from new_pipeline.evaluation.regime_dsr import QuantitativeEvaluator, ThinRegimePolicy

    ev = QuantitativeEvaluator(0.95, 3, 60, ThinRegimePolicy.SKIP, random_state=0)
    with np.testing.assert_raises(ValueError):
        ev.evaluate_model_robustness(
            np.zeros(100), np.ones(100), 4,
            trial_sharpes=[0.01] * 4, decode_returns=np.zeros(99),
        )


def test_realistic_slice_flips_from_veto_to_pass_dead_slice_still_fails():
    """The bug's signature, pinned with run 57e4507c774f's Health Care numbers:
    a 418-day regime slice at daily SR ~0.169 (annualized ~2.7) was vetoed at
    DSR ~0.005 because the deflation benchmark was built from ANNUALIZED trial
    Sharpes (std 0.28 -> implied hurdle ~4.7 annualized). Same slice under the
    corrected inputs (per-period variance, N_eff) is clearly promotable, while
    a genuinely edge-less slice still fails."""
    rng = np.random.default_rng(3)
    raw = rng.normal(0.0, 1.0, 418)
    shaped = (raw - raw.mean()) / raw.std(ddof=1)  # exact sample moments
    slice_ret = shaped * 9e-3 + 0.169 * 9e-3  # sample daily SR == 0.169 exactly
    hc_trials = [0.9056, 1.3766, 0.9128, 1.4127]  # annualized, from the real run

    old = deflated_sharpe_report(slice_ret, 4, trial_sharpes=hc_trials)
    fixed = deflated_sharpe_report(
        slice_ret, 1.11, trial_sharpes=_per_period_trials(hc_trials)
    )
    assert abs(old.sr0_period - 0.2953) < 1e-3  # the recorded impossible hurdle
    assert old.dsr < 0.05  # reproduces the recorded ~0.005 veto
    assert fixed.dsr >= 0.95

    dead = shaped * 9e-3  # sample daily SR == 0 exactly
    dead_dsr = deflated_sharpe_report(
        dead, 1.11, trial_sharpes=_per_period_trials(hc_trials)
    ).dsr
    assert dead_dsr < 0.95


# --------------------------------------------------------------- family-wise
def _family_verdict(sr_daily_by_state, family_wise, n=300, seed=11):
    """Evaluator verdict on 3 exact-sample-Sharpe blocks with a STUBBED decode
    (state = block, deterministically), zero trial variance -> DSR = PSR-vs-0,
    so each state's DSR ~= Phi(SR*sqrt(n-1)) by construction."""
    from new_pipeline.evaluation.regime_dsr import QuantitativeEvaluator, ThinRegimePolicy

    rng = np.random.default_rng(seed)
    blocks = []
    for sr in sr_daily_by_state:
        raw = rng.normal(0.0, 1.0, n)
        shaped = (raw - raw.mean()) / raw.std(ddof=1)  # exact sample moments
        blocks.append(shaped * 9e-3 + sr * 9e-3)
    champ = np.concatenate(blocks)
    states = np.repeat(np.arange(len(blocks)), n)
    ev = QuantitativeEvaluator(
        0.95, 3, 60, ThinRegimePolicy.SKIP, random_state=0, family_wise=family_wise
    )
    ev._decode_regimes = lambda r, v, s: states
    return ev.evaluate_model_robustness(
        champ, np.ones(champ.size), 4, trial_sharpes=[0.03] * 4
    )


def test_family_wise_bar_is_threshold_to_the_k():
    """The calibrated bar: K conjunctive 0.95-tests are jointly ~0.95^K, so the
    per-state bar is T**K (0.857 for K=3). Per-state DSRs ~{0.90, 0.97, 0.94}
    (the honest Liquid-1500 L/S profile) fail the legacy flat-0.95 rule in two
    states yet clear the family-wise bar in all three."""
    fw = _family_verdict([0.0741, 0.1100, 0.0899], family_wise=True)
    legacy = _family_verdict([0.0741, 0.1100, 0.0899], family_wise=False)
    dsrs = sorted(r.dsr for r in fw.per_regime.values())
    assert dsrs[0] > 0.95**3 and dsrs[1] < 0.95  # genuinely between the bars
    assert legacy.effective_threshold == 0.95
    assert not legacy.promoted  # the miscalibrated conjunction vetoes
    assert abs(fw.effective_threshold - 0.95**3) < 1e-12
    assert fw.promoted


def test_family_wise_still_vetoes_dead_and_losing_states():
    """The lower per-state bar is NOT a softening: an edge-less state (daily
    SR 0.02 -> DSR ~0.64) and a losing state both still fail the gate."""
    dead = _family_verdict([0.0741, 0.1100, 0.02], family_wise=True)
    assert not dead.promoted
    assert min(r.dsr for r in dead.per_regime.values()) < dead.effective_threshold
    losing = _family_verdict([0.0741, 0.1100, -0.05], family_wise=True)
    assert not losing.promoted  # negative-edge state can never hide behind T**K
    assert any(r.sr_period < 0 for r in losing.per_regime.values())


def test_regime_breakdown_reports_the_applied_bar():
    """The breakdown's threshold/passes must reflect the bar the gate ACTUALLY
    applied (T**K), not the nominal config threshold — a 0.90-DSR state that
    cleared the family-wise gate must display passes=True."""
    from new_pipeline.tournament.pipeline import _regime_breakdown

    fw = _family_verdict([0.0741, 0.1100, 0.0899], family_wise=True)
    out = _regime_breakdown(fw, _cfg(True))
    assert out["threshold"] == round(0.95**3, 6)
    assert all(v["passes"] for v in out["per_regime"].values())
    legacy = _family_verdict([0.0741, 0.1100, 0.0899], family_wise=False)
    out_legacy = _regime_breakdown(legacy, _cfg(True, family_wise=False))
    assert out_legacy["threshold"] == 0.95
    assert sum(v["passes"] for v in out_legacy["per_regime"].values()) == 1
