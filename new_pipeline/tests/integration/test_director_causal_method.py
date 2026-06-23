"""Director end-to-end on the causal feature-selection path (offline, seeded).

Mirrors test_director.py but flips feature_selection_method=causal and supplies
the fwd_ret / label_t1_offset columns the Granger screen + purged-CPCV MDA need.
"""

import numpy as np
import polars as pl

from new_pipeline.config import reload_config
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.director import run_sector_tournament

_FEATURES = ["f0", "f1", "f2"]


def _causal_frame(n: int = 120) -> pl.DataFrame:
    rng = np.random.default_rng(0)
    rows = []
    for sector in ["Tech", "Energy"]:
        f0 = rng.normal(size=n)
        f1 = rng.normal(size=n)
        f2 = rng.normal(size=n)
        fwd = np.zeros(n)
        fwd[1:] = 0.6 * f0[:-1] + rng.normal(0.0, 0.3, n - 1)  # f0 Granger-leads fwd_ret
        close = 100.0 + np.cumsum(rng.normal(0, 1, n))
        for i in range(n):
            rows.append(
                {
                    "sector": sector,
                    "f0": float(f0[i]),
                    "f1": float(f1[i]),
                    "f2": float(f2[i]),
                    "close": float(close[i]),
                    "low": float(close[i] - 1.0),
                    "atr": 1.0,
                    "target_label": float(fwd[i] > 0.0),
                    "fwd_ret": float(fwd[i]),
                    "label_t1_offset": 1.0,
                }
            )
    return pl.DataFrame(rows)


def test_director_causal_method_produces_candidates(tmp_path, monkeypatch):
    monkeypatch.setenv("QA_TOURNAMENT__NUM_BOOST_ROUND", "15")
    monkeypatch.setenv("QA_TOURNAMENT__FEATURE_SELECTION_METHOD", "causal")
    reload_config()
    seed_everything(0)

    results = run_sector_tournament(_causal_frame(), _FEATURES, tmp_path, use_cfs=True)

    assert set(results) == {"Tech", "Energy"}
    for sector, result in results.items():
        assert (tmp_path / f"{sector.lower()}_candidate.json").exists()
        assert (tmp_path / f"{sector.lower()}_returns_matrix.parquet").exists()
        # Causal path ran end to end: a non-empty subset of the inputs was kept.
        assert result["selected_features"]
        assert set(result["selected_features"]).issubset(set(_FEATURES))
