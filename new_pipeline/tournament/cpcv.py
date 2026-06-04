"""Combinatorial Purged Cross-Validation (López de Prado).

Splits a time-ordered index into ``n_groups`` contiguous blocks and forms every
C(n_groups, test_groups) combination as a test set. Training rows within
``purge`` positions before, or ``embargo`` positions after, any test block are
dropped to kill look-ahead leakage. With the defaults (6 groups, 2 test) this
yields the canonical 15 folds.
"""

import itertools
import math
from dataclasses import dataclass

import numpy as np

from new_pipeline.core.exceptions import CPCVSplitError


@dataclass
class CPCVSplitGenerator:
    n_groups: int = 6
    test_groups: int = 2
    purge: int = 5
    embargo: int = 5

    @property
    def n_folds(self) -> int:
        return math.comb(self.n_groups, self.test_groups)

    def split(self, n_samples: int) -> list[tuple[np.ndarray, np.ndarray]]:
        """Return ``n_folds`` (train_idx, test_idx) integer-position pairs."""
        if n_samples < self.n_groups:
            raise CPCVSplitError(f"n_samples={n_samples} < n_groups={self.n_groups}")
        groups = np.array_split(np.arange(n_samples), self.n_groups)
        folds: list[tuple[np.ndarray, np.ndarray]] = []
        for combo in itertools.combinations(range(self.n_groups), self.test_groups):
            test_idx = np.concatenate([groups[g] for g in combo])
            forbidden = set(test_idx.tolist())
            for g in combo:
                block = groups[g]
                start, end = int(block[0]), int(block[-1])
                forbidden.update(range(max(0, start - self.purge), start))
                forbidden.update(range(end + 1, min(n_samples, end + 1 + self.embargo)))
            train_idx = np.array(
                [i for i in range(n_samples) if i not in forbidden], dtype=np.int64
            )
            self._validate(train_idx, np.sort(test_idx))
            folds.append((train_idx, np.sort(test_idx)))
        return folds

    @staticmethod
    def _validate(train_idx: np.ndarray, test_idx: np.ndarray) -> None:
        if np.intersect1d(train_idx, test_idx).size > 0:
            raise CPCVSplitError("CPCV produced overlapping train/test indices")
