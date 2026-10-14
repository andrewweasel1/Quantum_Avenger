"""Golden numbers for the P1 extended feature families (offense roadmap P1).

Pins fractional differentiation, the range vol estimators, and the microstructure
proxies on a fixed seeded OHLCV fixture so a refactor of the math is caught. See
docs/quantitative_math.md Part II §A/§D/§E.
"""

from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest
from new_pipeline.features.fracdiff import add_fracdiff
from new_pipeline.features.microstructure import add_microstructure
from new_pipeline.features.vol_estimators import add_vol_estimators


def _fixture(n=300) -> pl.DataFrame:
    rng = np.random.default_rng(7)
    close = 100.0 + np.cumsum(rng.normal(0, 1.0, n))
    high = close + np.abs(rng.normal(0, 0.5, n))
    low = close - np.abs(rng.normal(0, 0.5, n))
    openp = close + rng.normal(0, 0.3, n)
    volume = (1e6 + rng.integers(0, 5e5, n)).astype(float)
    days = [date(2021, 1, 4) + timedelta(days=i) for i in range(n)]
    return pl.DataFrame(
        {"date": days, "ticker": ["AAA"] * n, "open": openp, "high": high,
         "low": low, "close": close, "volume": volume}
    )


def test_fracdiff_golden():
    frame = add_fracdiff(_fixture())  # d=0.4, threshold=1e-3
    assert frame["fracdiff"][250] == pytest.approx(0.4712376329549448, rel=1e-9)


def test_vol_estimators_golden():
    frame = add_vol_estimators(_fixture(), window=20)
    assert frame["parkinson_vol"][250] == pytest.approx(0.11855720205207956, rel=1e-9)
    assert frame["yang_zhang_vol"][250] == pytest.approx(0.37382025127627827, rel=1e-9)


def test_microstructure_golden():
    frame = add_microstructure(_fixture(), window=20)
    assert frame["corwin_schultz"][250] == pytest.approx(0.0006116746276739036, rel=1e-9)
    assert frame["kyle_lambda"][250] == pytest.approx(7.627795252040916e-07, rel=1e-9)
