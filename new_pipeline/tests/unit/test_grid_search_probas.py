"""OOS probability capture in the grid search: positional stitching + artifact."""

import numpy as np
import polars as pl
from new_pipeline.config import reload_config
from new_pipeline.tournament.cpcv import CPCVSplitGenerator
from new_pipeline.tournament.grid_search import GridSearchResult, run_grid_search


def test_proba_paths_stitching_is_positionally_exact(monkeypatch):
    """proba_paths[j, p, i] must hold the OOS prediction from exactly the fold
    that tested sample i's group on CPCV path p under combo j — pinned with a
    fold-counter stub whose id is recoverable from every cell."""
    import new_pipeline.tournament.grid_search as gs

    reload_config()
    counter = {"n": 0}

    def fake_train(*args, **kwargs):
        counter["n"] += 1
        return counter["n"]  # booster id == global fold counter

    monkeypatch.setattr(gs, "train_booster", fake_train)
    monkeypatch.setattr(
        gs, "predict_proba", lambda booster, x: np.full(len(x), float(booster))
    )

    n = 120
    rng = np.random.default_rng(0)
    features = rng.normal(size=(n, 2))
    labels = (rng.random(n) > 0.5).astype(np.float64)
    ones = np.ones(n)
    prices = {"close": ones, "low": ones * 0.99, "atr": ones * 0.01}

    result = run_grid_search(features, labels, prices)
    assert isinstance(result, GridSearchResult)

    splitter = CPCVSplitGenerator()
    combo_groups = splitter.combinations()  # fold k tests groups combo_groups[k]
    bounds = splitter.group_bounds(n)
    n_folds = len(combo_groups)
    n_combos, phi, n_out = result.proba_paths.shape
    assert (phi, n_out) == (splitter.path_count, n)

    for j in range(n_combos):
        for g, (gstart, gend) in enumerate(bounds):
            # folds that test group g, in order == path index assignment
            ks = [k for k, groups in enumerate(combo_groups) if g in groups]
            assert len(ks) == phi
            for p, k in enumerate(ks):
                expected_id = j * n_folds + k + 1  # counter order of train calls
                cell = result.proba_paths[j, p, gstart : gend + 1]
                np.testing.assert_array_equal(cell, float(expected_id))


def test_persist_writes_row_aligned_oos_proba_artifact(tmp_path):
    """_persist emits {slug}_oos_proba.parquet with date/ticker/next_ret plus one
    f32 column per (combo, path), row-aligned with the returns matrix."""
    from datetime import date, timedelta

    from new_pipeline.tournament.director import _persist
    from new_pipeline.tournament.trainer import train_booster

    n, n_combos, phi = 12, 2, 5
    rng = np.random.default_rng(1)
    search = GridSearchResult(
        best_params={"max_depth": 1, "learning_rate": 0.01},
        best_sharpe=0.0,
        returns_matrix=np.zeros((n_combos, n)),
        trial_sharpes=[0.0, 0.0],
        paths=np.zeros((phi, n)),
        path_count=phi,
        proba_paths=rng.random((n_combos, phi, n)),
    )
    booster = train_booster(rng.normal(size=(20, 2)), (rng.random(20) > 0.5).astype(float),
                            num_boost_round=2)
    days = [date(2021, 1, 4) + timedelta(days=i // 2) for i in range(n)]
    tickers = ["AAA" if i % 2 == 0 else "BBB" for i in range(n)]
    next_ret = rng.normal(0, 0.01, n)

    _persist(tmp_path, "Information Technology", booster, ["returns"], search,
             sample_dates=pl.Series(days), tickers=pl.Series(tickers),
             next_ret=pl.Series(next_ret))

    out = pl.read_parquet(tmp_path / "information_technology_oos_proba.parquet")
    assert out.height == n
    proba_cols = [f"proba_c{j}_p{p}" for j in range(n_combos) for p in range(phi)]
    assert list(out.columns) == ["date", "ticker", "next_ret", *proba_cols]
    assert out["proba_c0_p0"].dtype == pl.Float32
    np.testing.assert_allclose(
        out["proba_c1_p4"].to_numpy(), search.proba_paths[1, 4, :], rtol=1e-6
    )
    np.testing.assert_allclose(out["next_ret"].to_numpy(), next_ret)
