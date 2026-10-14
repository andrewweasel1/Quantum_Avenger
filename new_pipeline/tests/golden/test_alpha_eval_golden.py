"""Golden numbers for per-signal alpha evaluation (offense roadmap P2).

Pins the IC/ICIR/t-stat of a signal with genuine (but imperfect) cross-sectional
edge and of a pure-noise signal, on a fixed seeded fixture, so a refactor that
silently changes the IC math is caught. See docs/OFFENSE_ROADMAP.md (P2).
"""

from datetime import date, timedelta

import numpy as np
import polars as pl
import pytest
from new_pipeline.evaluation.alpha_eval import information_coefficient


def _fixture() -> pl.DataFrame:
    rng = np.random.default_rng(13)
    n_dates, n_names = 20, 8
    rows = []
    for di in range(n_dates):
        base = rng.normal(0, 1, n_names)
        fwd = base + rng.normal(0, 1.5, n_names)  # noisy -> imperfect positive IC
        noise = rng.normal(0, 1, n_names)
        for i in range(n_names):
            rows.append(
                {
                    "date": date(2021, 1, 1) + timedelta(days=di),
                    "ticker": f"T{i}",
                    "good": float(base[i]),
                    "noise": float(noise[i]),
                    "fwd_ret": float(fwd[i]),
                    "close": 100.0 + i,
                }
            )
    return pl.DataFrame(rows)


def test_alpha_eval_golden():
    frame = _fixture()
    good = information_coefficient(frame, "good")
    assert good.mean_ic == pytest.approx(0.4571428571428572, rel=1e-9)
    assert good.icir == pytest.approx(1.2289949987605113, rel=1e-9)
    assert good.ic_t_stat == pytest.approx(5.496232722471547, rel=1e-9)
    assert good.n_periods == 20
    assert good.breadth == pytest.approx(8.0)
    assert good.hit_rate == pytest.approx(0.9)

    noise = information_coefficient(frame, "noise")
    assert noise.mean_ic == pytest.approx(0.05357142857142857, rel=1e-9)
    assert noise.icir == pytest.approx(0.11996352540861975, rel=1e-9)
