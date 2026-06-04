import numpy as np
import polars as pl

from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.director import run_sector_tournament

_FEATURES = ["f0", "f1", "f2"]


def _frame(n: int = 120) -> pl.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    for sector in ["Tech", "Energy"]:
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


def test_director_produces_candidates_per_sector(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "15")
    reload_config()
    seed_everything(0)

    results = run_sector_tournament(_frame(), _FEATURES, tmp_path, use_cfs=True)

    assert set(results) == {"Tech", "Energy"}
    for sector, result in results.items():
        slug = sector.lower()
        assert (tmp_path / f"{slug}_candidate.json").exists()
        assert (tmp_path / f"{slug}_candidate_features.json").exists()
        assert (tmp_path / f"{slug}_returns_matrix.parquet").exists()
        assert result["selected_features"]
        assert set(result["selected_features"]).issubset(set(_FEATURES))
