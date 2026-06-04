import numpy as np
from new_pipeline.core.seeding import seed_everything
from new_pipeline.tournament.trainer import train_booster


def test_early_stopping_sets_best_iteration():
    seed_everything(0)
    rng = np.random.default_rng(0)
    features = rng.normal(size=(200, 4))
    labels = (features[:, 0] > 0).astype(float)
    booster = train_booster(
        features[:160],
        labels[:160],
        num_boost_round=80,
        eval_features=features[160:],
        eval_labels=labels[160:],
        early_stopping_rounds=5,
    )
    assert isinstance(booster.best_iteration, int)
    assert 0 <= booster.best_iteration <= 79
