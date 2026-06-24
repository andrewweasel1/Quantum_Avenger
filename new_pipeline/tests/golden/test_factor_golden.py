"""Golden numbers for cross-sectional alpha factors (offense roadmap P0).

Pins the exact ``xf_*`` output on a fixed, deterministic multi-ticker fixture so a
refactor that silently changes the factor math or the cross-sectional z-score is
caught. Companion to test_feature_golden.py (per-ticker engine) — this is the
cross-sectional axis. See docs/OFFENSE_ROADMAP.md (P0).
"""

from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest
from new_pipeline.features.factors import add_cross_sectional_factors
from new_pipeline.features.polars_engine import compile_features


def _fixture() -> pl.DataFrame:
    tickers = ["AAA", "BBB", "CCC"]
    n = 30
    rng = np.random.default_rng(11)
    rows = []
    for ticker in tickers:
        close = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
        high = close + np.abs(rng.normal(0, 0.5, n))
        low = close - np.abs(rng.normal(0, 0.5, n))
        openp = close + rng.normal(0, 0.3, n)
        volume = (1e6 + rng.integers(0, 5e5, n)).astype(float)
        days = [date(2021, 1, 4) + timedelta(days=i) for i in range(n)]
        for i in range(n):
            rows.append(
                {
                    "date": days[i], "ticker": ticker, "open": openp[i],
                    "high": high[i], "low": low[i], "close": close[i], "volume": volume[i],
                }
            )
    featured = compile_features(pl.DataFrame(rows))
    sectors = pl.DataFrame({"ticker": tickers, "sector": ["S1", "S1", "S2"]})
    return featured.join(sectors, on="ticker", how="left")


def test_cross_sectional_factor_golden():
    out = add_cross_sectional_factors(_fixture(), ["reversal_21", "low_vol"], sector_neutral=False)
    aaa = out.filter(pl.col("ticker") == "AAA").sort("date")
    assert aaa["xf_reversal_21"][27] == pytest.approx(1.1507534709728335, rel=1e-9)
    assert aaa["xf_low_vol"][27] == pytest.approx(-0.09123467206638575, rel=1e-9)
