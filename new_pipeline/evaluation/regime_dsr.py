"""Per-regime Deflated-Sharpe promotion gate.

Replaces a raw-Sharpe regime check with a real, multiple-testing-aware DSR
computed *within each macro regime*. A Gaussian HMM decodes regimes from the
fused ``[returns, volatility, (sentiment)]`` space; states are relabeled by
volatility (:func:`order_states_by_volatility`) so regime ids are deterministic
(no ``means_[4]`` / ``sorted_indices[4]`` index bugs). A model is promoted only
if its DSR clears the threshold in every *testable* regime.

Thin-regime policy: a regime with fewer than ``min_regime_obs`` observations --
or one where the strategy never traded (zero return variance) -- cannot clear a
0.95 bar on sample size alone, so auto-vetoing it is a Type-II error ("didn't
trade" != "lost money"). Such regimes are excluded under
:attr:`ThinRegimePolicy.SKIP` (default) or fail the model under
:attr:`ThinRegimePolicy.VETO`.

Reuses :func:`new_pipeline.evaluation.dsr.deflated_sharpe_report` (the canonical
DSR) -- it does not re-implement the statistic.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum

import numpy as np
from hmmlearn import hmm

from new_pipeline.core.seeding import active_seed
from new_pipeline.evaluation.dsr import DSRResult, deflated_sharpe_report
from new_pipeline.features.regime_fusion import (
    build_observation_matrix,
    order_states_by_volatility,
)

logger = logging.getLogger(__name__)


class ThinRegimePolicy(str, Enum):
    SKIP = "skip"  # under-sampled regimes are excluded from the gate (recommended)
    VETO = "veto"  # any under-sampled regime fails the model (ultra-conservative)


@dataclass(frozen=True)
class RegimeVerdict:
    promoted: bool
    per_regime: dict[int, DSRResult]
    skipped_regimes: list[int]


class QuantitativeEvaluator:
    """Macro-regime decode + per-regime DSR promotion gate."""

    def __init__(
        self,
        min_dsr_threshold: float = 0.95,
        n_components: int = 3,
        min_regime_obs: int = 60,
        thin_policy: ThinRegimePolicy = ThinRegimePolicy.SKIP,
        periods_per_year: int = 252,
        random_state: int | None = None,
    ) -> None:
        self.min_dsr_threshold = min_dsr_threshold
        self.n_components = n_components
        self.min_regime_obs = min_regime_obs
        self.thin_policy = thin_policy
        self.periods_per_year = periods_per_year
        self.random_state = random_state

    def evaluate_model_robustness(
        self,
        strategy_returns,
        market_volatility,
        n_trials,
        trial_sharpes=None,
        sentiment=None,
    ) -> RegimeVerdict:
        """Decode regimes and require DSR > threshold in every testable regime.

        ``n_trials`` / ``trial_sharpes`` come from the tournament. Pass
        ``sentiment`` to decode regimes in the fused 3-D space.
        """
        returns = np.asarray(strategy_returns, dtype=np.float64)
        volatility = np.asarray(market_volatility, dtype=np.float64)
        sent = None if sentiment is None else np.asarray(sentiment, dtype=np.float64)

        states = self._decode_regimes(returns, volatility, sent)
        if states is None:
            return RegimeVerdict(False, {}, [])

        per_regime: dict[int, DSRResult] = {}
        skipped: list[int] = []
        promoted = True

        for state in np.unique(states):
            state_returns = returns[states == state]
            # "Didn't trade" (zero variance) is treated like under-sampled, not a loss.
            thin = state_returns.size < self.min_regime_obs or np.std(state_returns) == 0.0
            if thin:
                skipped.append(int(state))
                logger.warning(
                    "Regime %d under-sampled/flat (%d obs) -> policy=%s",
                    state, state_returns.size, self.thin_policy.value,
                )
                if self.thin_policy is ThinRegimePolicy.VETO:
                    promoted = False
                continue

            res = deflated_sharpe_report(
                state_returns,
                n_trials=n_trials,
                trial_sharpes=trial_sharpes,
                periods_per_year=self.periods_per_year,
                min_obs=self.min_regime_obs,
            )
            per_regime[int(state)] = res
            if res.dsr < self.min_dsr_threshold:
                promoted = False
                logger.warning(
                    "VETO: regime %d DSR=%.3f < %.2f (SR_ann=%.2f, T=%d)",
                    state, res.dsr, self.min_dsr_threshold, res.sr_annual, res.n_obs,
                )

        if not per_regime:
            promoted = False  # no regime had enough observations to test
            logger.warning("VETO: no regime had enough observations to test.")

        return RegimeVerdict(promoted, per_regime, skipped)

    # ----------------------------------------------------------------- private
    def _decode_regimes(self, returns, volatility, sentiment) -> np.ndarray | None:
        if sentiment is not None:
            obs = build_observation_matrix(returns, volatility, sentiment, standardize=True)
        else:
            obs = np.column_stack([returns, volatility])
            obs = np.nan_to_num(obs, nan=0.0)
            mu, sd = obs.mean(0), obs.std(0)
            sd[sd == 0.0] = 1.0  # HMM means/covars are scale-sensitive
            obs = (obs - mu) / sd

        model = hmm.GaussianHMM(
            n_components=self.n_components,
            covariance_type="full",
            n_iter=200,
            random_state=active_seed() if self.random_state is None else self.random_state,
        )
        try:
            model.fit(obs)
            states = model.predict(obs)
        except Exception as exc:  # pragma: no cover - convergence is data-dependent
            logger.error("Macro HMM failed to converge: %s", exc)
            return None

        # Relabel so regime id is ascending in volatility (deterministic, no [4] bug).
        order = order_states_by_volatility(model.covars_)
        remap = {int(old): new for new, old in enumerate(order)}
        return np.array([remap[int(s)] for s in states])
