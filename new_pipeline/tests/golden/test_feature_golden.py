"""Golden numbers for the feature engine, risk shield, slippage, and labels.

Pins the exact output of each quant formula on a fixed, deterministic input so a
refactor that silently changes the math is caught. Part of the tests/golden/
harness (see test_causal_golden.py for the causal/weighting pins).
"""

from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest
from new_pipeline.features.labels import add_labels
from new_pipeline.features.polars_engine import add_features
from new_pipeline.features.shields import calculate_kelly_position_size, evaluate_risk_veto_gates
from new_pipeline.features.slippage import adjust_slippage_by_regime, hydrodynamic_slippage_bps


def _ohlc(n: int = 70) -> pl.DataFrame:
    rng = np.random.default_rng(7)
    close = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    high = close + np.abs(rng.normal(0, 0.5, n))
    low = close - np.abs(rng.normal(0, 0.5, n))
    openp = close + rng.normal(0, 0.3, n)
    volume = (1e6 + rng.integers(0, 5e5, n)).astype(float)
    days = [date(2022, 1, 3) + timedelta(days=i) for i in range(n)]
    return pl.DataFrame(
        {
            "date": days, "ticker": ["AAA"] * n, "open": openp,
            "high": high, "low": low, "close": close, "volume": volume,
        }
    )


def test_feature_engine_golden():
    f = add_features(_ohlc())
    assert f["atr"][64] == pytest.approx(1.180290339609545, rel=1e-9)
    assert f["volatility"][64] == pytest.approx(0.16768705499569983, rel=1e-9)
    assert f["amihud"][64] == pytest.approx(8.136683889897013e-11, rel=1e-9)
    assert f["spread_pct"][64] == pytest.approx(0.018318529424462743, rel=1e-9)
    assert f["roll_spread"][64] == pytest.approx(0.009984836838560192, rel=1e-9)
    assert f["ncskew"][64] == pytest.approx(-0.0518461380748401, rel=1e-9)
    assert f["duvol"][64] == pytest.approx(0.20555069637316312, rel=1e-9)


def test_triple_barrier_labels_golden():
    labeled = add_labels(add_features(_ohlc()), horizon=5, cost_bps=10.0, pt_mult=2.0, sl_mult=2.0)
    assert labeled["target_label"][10] == 1.0
    assert labeled["fwd_ret"][10] == pytest.approx(0.002009665101054159, rel=1e-9)
    assert labeled["label_t1_offset"][10] == 5.0


def test_slippage_golden():
    bps = hydrodynamic_slippage_bps(50000.0, 0.3, 2_000_000.0, 0.5, 10000.0)
    assert bps == pytest.approx(237.17082451262843, rel=1e-9)
    assert adjust_slippage_by_regime(bps, 1) == pytest.approx(474.34164902525686, rel=1e-9)


def test_kelly_and_shield_golden():
    assert calculate_kelly_position_size(100.0, 2.0, 2.0, 100_000.0, 0.02) == 500.0
    base = (100.0, 2.0, 2.0, 100_000.0, 0.02, 0.0, 5_000_000.0, 2_000_000.0)
    veto_approved, veto_size = evaluate_risk_veto_gates(*base, 0.3)  # high vol -> slippage veto
    assert not veto_approved and veto_size == 0.0
    ok_approved, ok_size = evaluate_risk_veto_gates(*base, 0.02)  # low vol -> approved
    assert ok_approved and ok_size == 500.0
