import numpy as np
from new_pipeline.core.seeding import DEFAULT_SEED, active_seed, seed_everything


def test_seed_everything_is_deterministic():
    seed_everything(123)
    first = np.random.rand(5).tolist()
    seed_everything(123)
    second = np.random.rand(5).tolist()
    assert first == second


def test_seed_everything_returns_and_records_seed():
    assert seed_everything(7) == 7
    assert active_seed() == 7


def test_default_seed_applied():
    assert seed_everything() == DEFAULT_SEED
