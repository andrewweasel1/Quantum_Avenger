"""Regime-gate decode basis: pinned once at the raw PIT layer as a per-date
constant, so the gate's "world" survives any downstream row filtering and has
exactly one definition, with the causal expanding-percentile cross-check
recorded beside the HMM verdict. Motivated by the audit on run 083aa78a529f:
the HMM partition is knife-edge-sensitive to basis composition (two defensible
constructions moved the calm state from 933 to 251 days)."""

from datetime import date
from types import SimpleNamespace

import numpy as np
import polars as pl
from new_pipeline.adapters.fakes import FakeMarketDataSource
from new_pipeline.config import base, reload_config
from new_pipeline.tournament.pipeline import (
    _market_return_by_date,
    _regime_breakdown,
    build_training_frame,
)
from new_pipeline.tournament.regime_state import (
    causal_market_regimes,
    causal_states_from_series,
)

D1, D2 = date(2021, 1, 4), date(2021, 1, 5)


def _frame_with(factor_set):
    reload_config()
    cfg = base.get_config()
    cfg = cfg.model_copy(
        update={"features": cfg.features.model_copy(update={"factor_set": factor_set})}
    )
    sectors = {"AAA": "Information Technology", "BBB": "Information Technology",
               "CCC": "Financials"}
    return build_training_frame(
        list(sectors), sectors, date(2021, 1, 1), date(2022, 12, 31),
        source=FakeMarketDataSource(), cfg=cfg,
    )


def test_market_basis_is_pinned_and_survives_row_filtering():
    plain = _frame_with([])
    factored = _frame_with(["mom_12_1", "reversal_21", "low_vol"])
    m_plain = _market_return_by_date(plain)
    assert _market_return_by_date(factored) == m_plain  # factor_set-invariant
    # the pin is per-date constant on every row
    per_date = factored.group_by("date").agg(pl.col("market_next_ret").n_unique().alias("u"))
    assert per_date["u"].max() == 1
    # arbitrary downstream row filtering (warmup drops, per-sector slices, ...)
    # must NOT move the basis: the pinned values hold while a survivors-mean
    # recompute would drift — the knife-edge the audit documented.
    filtered = factored.filter(
        pl.col("xf_mom_12_1").is_not_null() & (pl.col("ticker") != "CCC")
    )
    assert filtered.height < factored.height
    m_filtered = _market_return_by_date(filtered)
    assert all(abs(m_filtered[d] - m_plain[d]) < 1e-15 for d in m_filtered)
    survivors_mean = _market_return_by_date(filtered.drop("market_next_ret"))
    drifted = [d for d in m_filtered if abs(survivors_mean[d] - m_plain[d]) > 1e-12]
    assert drifted  # without the pin, the same filtering DOES move the basis


def test_market_return_by_date_prefers_pinned_column():
    frame = pl.DataFrame({
        "date": [D1, D1, D2],
        "next_ret": [0.10, 0.30, 0.50],
        "market_next_ret": [0.70, 0.70, 0.90],  # pinned value != row mean
    })
    assert _market_return_by_date(frame) == {D1: 0.70, D2: 0.90}
    legacy = _market_return_by_date(frame.drop("market_next_ret"))
    assert abs(legacy[D1] - 0.20) < 1e-15 and abs(legacy[D2] - 0.50) < 1e-15


def test_causal_states_from_series_matches_panel_decoder():
    rng = np.random.default_rng(3)
    days = [date(2020, 1, 1 + i) for i in range(28)] + [date(2020, 2, 1 + i) for i in range(28)]
    rows = [
        {"date": d, "ticker": t, "next_ret": float(rng.normal(0, 0.005 if i < 28 else 0.03))}
        for i, d in enumerate(days) for t in ("A", "B", "C")
    ]
    panel = pl.DataFrame(rows)
    via_panel = causal_market_regimes(panel)
    daily = (
        panel.group_by("date").agg(pl.col("next_ret").mean().alias("m")).sort("date")
    )
    via_series = causal_states_from_series(daily["date"].to_list(), daily["m"])
    assert via_panel == via_series
    assert max(via_series.values()) == 2  # the vol jump reaches the top bucket


def test_regime_breakdown_carries_causal_cross_check():
    reload_config()
    verdict = SimpleNamespace(
        per_regime={0: SimpleNamespace(dsr=0.99, sr_annual=1.0, n_obs=100)},
        skipped_regimes=[], states=np.zeros(100), effective_threshold=0.857375,
    )
    causal = {0: {"sr_annual": 0.5, "n_days": 60, "share": 0.6},
              1: {"sr_annual": 1.2, "n_days": 40, "share": 0.4}}
    out = _regime_breakdown(verdict, base.get_config(), causal=causal)
    assert out["causal_states"] == causal
    assert "causal_states" not in _regime_breakdown(verdict, base.get_config())


def test_rolling_span_reanchors_calm_prevalence_across_vol_eras():
    """The adoption rationale, pinned: after a secular vol re-rating, the
    EXPANDING decoder almost never labels the new era calm (the old ultra-calm
    era owns the low percentiles), while a rolling window re-anchors and keeps
    ~1/3 of each era in the calm tercile. span=None stays bit-identical to the
    legacy decoder."""
    rng = np.random.default_rng(7)
    days = [date.fromordinal(date(2017, 1, 2).toordinal() + i) for i in range(1000)]
    # era 1: ultra-calm (vol 3e-3); era 2: re-rated 3x higher, internally varied
    market = np.concatenate([
        rng.normal(0, 3e-3, 400),
        rng.normal(0, 9e-3, 200), rng.normal(0, 1.5e-2, 200), rng.normal(0, 9e-3, 200),
    ])
    expanding = causal_states_from_series(days, market, span=None)
    legacy = causal_states_from_series(days, market)  # default span arg is None
    assert expanding == legacy
    rolling = causal_states_from_series(days, market, span=252)
    era2 = days[500:]
    calm_exp = np.mean([expanding[d] == 0 for d in era2])
    calm_roll = np.mean([rolling[d] == 0 for d in era2])
    assert calm_exp < 0.10  # old anchor starves the new era of calm labels
    assert 0.15 < calm_roll < 0.55  # rolling window restores era-relative terciles
