"""Causal regime states + regime-gated exposure + expert selection."""

from datetime import date, timedelta

import numpy as np
import polars as pl
from new_pipeline.tournament.long_short import build_long_short_book
from new_pipeline.tournament.regime_state import causal_market_regimes

D0 = date(2021, 1, 4)


def _panel(n_days, vol_fn):
    rng = np.random.default_rng(2)
    rows = []
    for d in range(n_days):
        day = D0 + timedelta(days=d)
        for i in range(6):
            rows.append((day, f"T{i}", "X", float(6 - i), float(rng.normal(0, vol_fn(d)))))
    return pl.DataFrame(rows, schema=["date", "ticker", "sector", "score", "next_ret"],
                        orient="row")


def test_states_are_causal_and_rank_by_trailing_vol():
    # calm first 60 days, violent last 60: late days must decode as top state.
    panel = _panel(120, lambda d: 0.001 if d < 60 else 0.05)
    states = causal_market_regimes(panel, vol_lookback=10, n_states=3)
    days = sorted(states)
    assert all(states[d] == 0 for d in days[:11])  # warmup -> state 0
    assert np.mean([states[d] == 2 for d in days[-30:]]) >= 0.7  # stress decoded
    # causality: state at day t unchanged if future rows are dropped
    trunc = causal_market_regimes(panel.filter(pl.col("date") <= days[70]),
                                  vol_lookback=10, n_states=3)
    assert all(trunc[d] == states[d] for d in days[:71])


def test_regime_scalars_flatten_stress_days():
    panel = _panel(100, lambda d: 0.001 if d < 50 else 0.05)
    states = causal_market_regimes(panel, vol_lookback=10, n_states=3)
    scalars = {d: [1.0, 1.0, 0.0][s] for d, s in states.items()}
    gated = build_long_short_book(panel, 0.34, 0.0, 4, False, 1, regime_scalars=scalars)
    plain = build_long_short_book(panel, 0.34, 0.0, 4, False, 1)
    flat_days = [i for i, d in enumerate(gated.dates) if scalars.get(d) == 0.0]
    assert flat_days and all(gated.gross[i] == 0.0 for i in flat_days)  # stood down
    assert gated.avg_gross_exposure < plain.avg_gross_exposure


def test_regime_breakdown_names_the_failing_state():
    from types import SimpleNamespace

    from new_pipeline.config import base, reload_config
    from new_pipeline.tournament.pipeline import _regime_breakdown

    reload_config()
    verdict = SimpleNamespace(
        per_regime={
            0: SimpleNamespace(dsr=0.99, sr_annual=1.4, n_obs=900),
            2: SimpleNamespace(dsr=0.31, sr_annual=-0.2, n_obs=300),
        },
        skipped_regimes=[1],
        states=np.array([0] * 900 + [1] * 40 + [2] * 300),
        effective_threshold=None,  # legacy verdicts fall back to cfg threshold
    )
    out = _regime_breakdown(verdict, base.get_config())
    assert out["per_regime"][0]["passes"] is True
    assert out["per_regime"][2]["passes"] is False  # THE failing regime, named
    assert out["per_regime"][2]["n_days"] == 300
    assert out["skipped_thin"] == [1]
    assert abs(out["per_regime"][0]["share"] - 900 / 1240) < 0.01
