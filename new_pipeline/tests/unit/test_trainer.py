import numpy as np
import polars as pl
import xgboost as xgb
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.data_iterator import ParquetDataIter
from new_pipeline.tournament.trainer import (
    load_booster,
    predict_proba,
    save_candidate,
    train_booster,
)


def _xy(n: int = 120, seed: int = 0):
    rng = np.random.default_rng(seed)
    features = rng.normal(size=(n, 4))
    labels = (features[:, 0] > 0).astype(np.float64)
    return features, labels


def test_train_and_predict_proba_in_unit_interval():
    seed_everything(0)
    features, labels = _xy()
    booster = train_booster(features, labels, num_boost_round=20)
    proba = predict_proba(booster, features)
    assert proba.shape == (len(labels),)
    assert proba.min() >= 0.0
    assert proba.max() <= 1.0


def test_save_load_roundtrip(tmp_path):
    features, labels = _xy()
    booster = train_booster(features, labels, num_boost_round=10)
    path = tmp_path / "candidate.json"
    save_candidate(booster, path)
    reloaded = load_booster(path)
    np.testing.assert_allclose(predict_proba(booster, features), predict_proba(reloaded, features))


def test_parquet_data_iter_feeds_xgboost(tmp_path):
    features, labels = _xy(n=200)
    columns = {f"f{i}": features[:, i] for i in range(4)}
    frame = pl.DataFrame({**columns, "label": labels})
    path = tmp_path / "data.parquet"
    frame.write_parquet(path, row_group_size=50)  # -> 4 row-groups
    iterator = ParquetDataIter(path, [f"f{i}" for i in range(4)], "label")
    dmatrix = xgb.QuantileDMatrix(iterator)
    assert dmatrix.num_row() == 200
    assert dmatrix.num_col() == 4
