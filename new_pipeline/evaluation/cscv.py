"""Combinatorially Symmetric Cross-Validation (CSCV) splitter.

Bailey, Borwein, López de Prado & Zhu (2014), "Pseudo-Mathematics and Financial
Charlatanism". Partition the observation axis of a (n_obs x n_trials) returns
matrix into ``S`` disjoint, contiguous submatrices, then enumerate every
C(S, S/2) way of choosing half the partitions as in-sample (IS); the complement
is out-of-sample (OOS). Because each split's complement is *also* enumerated,
the construction is symmetric — the property that makes the downstream
overfitting estimate (PBO) unbiased.
"""

import math
from itertools import combinations

import numpy as np


def cscv_partition_indices(n_obs: int, n_partitions: int) -> list[np.ndarray]:
    """Split ``range(n_obs)`` into ``n_partitions`` contiguous index blocks."""
    if n_partitions < 2 or n_partitions % 2 != 0:
        raise ValueError("n_partitions must be an even integer >= 2")
    if n_obs < n_partitions:
        raise ValueError("need at least one observation per partition")
    return [block.astype(np.int64) for block in np.array_split(np.arange(n_obs), n_partitions)]


def n_cscv_splits(n_partitions: int) -> int:
    """Number of IS/OOS splits = C(S, S/2)."""
    return math.comb(n_partitions, n_partitions // 2)


def cscv_splits(n_obs: int, n_partitions: int):
    """Yield ``(is_index, oos_index)`` arrays over every C(S, S/2) IS/OOS choice."""
    blocks = cscv_partition_indices(n_obs, n_partitions)
    half = n_partitions // 2
    for chosen in combinations(range(n_partitions), half):
        is_set = set(chosen)
        is_index = np.concatenate([blocks[i] for i in range(n_partitions) if i in is_set])
        oos_index = np.concatenate([blocks[i] for i in range(n_partitions) if i not in is_set])
        yield np.sort(is_index), np.sort(oos_index)
