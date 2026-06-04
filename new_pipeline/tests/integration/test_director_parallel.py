import numpy as np
import polars as pl

from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.director import run_sector_tournament

_FEATURES = ["f0", "f1", "f2"]


def _frame(n: int = 120) -> pl.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    for sector in ["Tech", "Energy", "Health"]:
        close = 100.0 + np.cumsum(rng.normal(0, 1, n))
        for i in range(n):
            rows.append(
                {
                    "sector": sector,
                    "f0": float(rng.normal()),
                    "f1": float(rng.normal()),
                    "f2": float(rng.normal()),
                    "close": float(close[i]),
                    "low": float(close[i] - 1.0),
                    "atr": 1.0,
                    "target_label": float(rng.integers(0, 2)),
                }
            )
    return pl.DataFrame(rows)


def test_parallel_sectors_produce_all_candidates(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "12")
    reload_config()
    seed_everything(0)

    results = run_sector_tournament(
        _frame(), _FEATURES, tmp_path, use_cfs=False, max_workers=3
    )

    assert set(results) == {"Tech", "Energy", "Health"}
    for sector in results:
        assert (tmp_path / f"{sector.lower()}_candidate.json").exists()
