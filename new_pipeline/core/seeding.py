"""Central reproducibility helper.

A single :func:`seed_everything` call seeds every RNG source the pipeline uses
so backtests, model training, and tests are deterministic (principle G6). Heavy
optional libraries (e.g. ``torch``) are seeded only when importable, keeping the
offline / CPU-only sandbox lightweight.
"""

import os
import random

import numpy as np

DEFAULT_SEED = 42

_active_seed = DEFAULT_SEED


def seed_everything(seed: int = DEFAULT_SEED) -> int:
    """Seed all known RNG sources and return the seed that was applied."""
    global _active_seed
    _active_seed = seed
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    _seed_torch(seed)
    return seed


def active_seed() -> int:
    """Return the most recently applied seed."""
    return _active_seed


def _seed_torch(seed: int) -> None:
    """Seed torch if it is installed; a no-op otherwise."""
    try:
        import torch
    except ImportError:
        return
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
