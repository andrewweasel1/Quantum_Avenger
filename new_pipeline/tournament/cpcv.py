"""Combinatorial Purged Cross-Validation (López de Prado).

Splits a time-ordered index into ``n_groups`` contiguous blocks and forms every
C(n_groups, test_groups) combination as a test set. With the defaults (6 groups,
2 test) this yields the canonical 15 folds.

Leakage hygiene comes in two layers:

* **Purge** — training rows whose label window overlaps a test block are
  dropped. When per-sample event-end positions (``t1``) are supplied, the purge
  is *span-based* (getTrainTimes): a train row ``i`` with label span ``[i,
  t1[i]]`` is dropped if it overlaps any test block's span. This ties the purge
  to the real label horizon instead of a fixed margin. A fixed ``purge`` count
  before each block is kept as a floor.
* **Embargo** — training rows immediately *after* a test block are dropped to
  kill serial-correlation leakage. The window is ``max(embargo, ceil(embargo_pct
  * n_samples))`` positions.

The C(n_groups, test_groups) combinations also reconstruct ``φ = C(n_groups-1,
test_groups-1)`` full-length **backtest paths** (:meth:`assemble_paths`): each
group is tested in exactly ``φ`` combinations, so stitching one test segment per
group across the combinations yields ``φ`` independent OOS paths whose Sharpe
distribution feeds the Deflated-Sharpe gate.
"""

import itertools
import math
from dataclasses import dataclass

import numpy as np

from new_pipeline.core.exceptions import CPCVSplitError


def block_end_index(block_ids) -> np.ndarray:
    """For each row, the index of the last row in its contiguous block (run).

    ``block_ids`` is a per-row block id (e.g. a ticker run id); rows of the same
    block are assumed contiguous. Used to cap label spans / simulation at a block
    boundary so they never cross into another ticker.
    """
    ids = np.asarray(block_ids)
    n = ids.size
    if n == 0:
        return np.zeros(0, dtype=np.int64)
    run_ends = np.append(np.flatnonzero(ids[1:] != ids[:-1]), n - 1)
    return run_ends[np.searchsorted(run_ends, np.arange(n), side="left")]


def absolute_t1(t1_offset, n_samples: int, block_ids=None) -> np.ndarray | None:
    """Per-row 'bars ahead to first touch' offsets -> clamped absolute event-end
    positions for CPCV purging. Clamps each span to the end of its contiguous
    block (e.g. ticker run) when ``block_ids`` is given, else to ``n-1``; clamping
    only shrinks a span, so it never crosses a block boundary into another ticker."""
    if t1_offset is None:
        return None
    offsets = np.nan_to_num(np.asarray(t1_offset, dtype=np.float64), nan=0.0).astype(np.int64)
    raw = np.arange(n_samples) + offsets
    ceiling = (n_samples - 1) if block_ids is None else block_end_index(block_ids)
    return np.minimum(raw, ceiling)


@dataclass
class CPCVSplitGenerator:
    n_groups: int = 6
    test_groups: int = 2
    purge: int = 5
    embargo: int = 5
    embargo_pct: float = 0.0

    @property
    def n_folds(self) -> int:
        return math.comb(self.n_groups, self.test_groups)

    @property
    def path_count(self) -> int:
        """Number of reconstructable backtest paths ``φ = C(N-1, k-1)``."""
        return math.comb(self.n_groups - 1, self.test_groups - 1)

    def combinations(self) -> list[tuple[int, ...]]:
        """Test-group combinations, in the same order :meth:`split` emits folds."""
        return list(itertools.combinations(range(self.n_groups), self.test_groups))

    def group_bounds(self, n_samples: int) -> list[tuple[int, int]]:
        """Inclusive ``(start, end)`` index bounds of each contiguous group block."""
        groups = np.array_split(np.arange(n_samples), self.n_groups)
        return [(int(block[0]), int(block[-1])) for block in groups]

    def _effective_embargo(self, n_samples: int) -> int:
        return max(self.embargo, math.ceil(self.embargo_pct * n_samples))

    def split(self, n_samples: int, t1: np.ndarray | None = None):
        """Return ``n_folds`` (train_idx, test_idx) integer-position pairs.

        ``t1`` (optional) is the per-sample event-end position (``t1[i] >= i``);
        when given, the purge drops train rows whose label span overlaps a test
        block's span — the horizon-aware purge.
        """
        if n_samples < self.n_groups:
            raise CPCVSplitError(f"n_samples={n_samples} < n_groups={self.n_groups}")
        spans = None
        if t1 is not None:
            spans = np.asarray(t1, dtype=np.int64)
            if spans.shape != (n_samples,):
                raise CPCVSplitError(f"t1 length {spans.shape} != n_samples {n_samples}")
            spans = np.clip(spans, np.arange(n_samples), n_samples - 1)

        groups = np.array_split(np.arange(n_samples), self.n_groups)
        embargo = self._effective_embargo(n_samples)
        positions = np.arange(n_samples)
        folds: list[tuple[np.ndarray, np.ndarray]] = []
        for combo in itertools.combinations(range(self.n_groups), self.test_groups):
            test_idx = np.concatenate([groups[g] for g in combo])
            forbidden = set(test_idx.tolist())
            for g in combo:
                block = groups[g]
                start, end = int(block[0]), int(block[-1])
                forbidden.update(range(max(0, start - self.purge), start))
                forbidden.update(range(end + 1, min(n_samples, end + 1 + embargo)))
                if spans is not None:
                    # Span-based purge: drop train rows whose [i, t1[i]] overlaps
                    # this block's label span [start, max t1 over the block].
                    block_end = int(spans[block].max())
                    overlap = (positions <= block_end) & (spans >= start)
                    forbidden.update(positions[overlap].tolist())
            train_idx = np.array(sorted(set(range(n_samples)) - forbidden), dtype=np.int64)
            self._validate(train_idx, np.sort(test_idx))
            folds.append((train_idx, np.sort(test_idx)))
        return folds

    def assemble_paths(self, n_samples: int, segment_returns: dict) -> np.ndarray:
        """Stitch per-(combination, group) OOS segments into ``φ`` backtest paths.

        ``segment_returns`` maps ``(combo_index, group)`` -> the return array for
        that group's test rows in that combination. Returns a ``(φ, n_samples)``
        matrix; row ``p`` is the ``p``-th backtest path.
        """
        groups = np.array_split(np.arange(n_samples), self.n_groups)
        combos = self.combinations()
        phi = self.path_count
        paths = np.zeros((phi, n_samples), dtype=np.float64)
        for g in range(self.n_groups):
            combos_with_g = [ci for ci, combo in enumerate(combos) if g in combo]
            if len(combos_with_g) != phi:  # defensive; combinatorics guarantee this
                raise CPCVSplitError(f"group {g} in {len(combos_with_g)} combos, expected {phi}")
            block = groups[g]
            for path_index, combo_index in enumerate(combos_with_g):
                segment = np.asarray(segment_returns[(combo_index, g)], dtype=np.float64)
                if segment.shape[0] != block.shape[0]:
                    raise CPCVSplitError(
                        f"segment ({combo_index},{g}) has length "
                        f"{segment.shape[0]}, expected {block.shape[0]}"
                    )
                paths[path_index, block] = segment
        return paths

    @staticmethod
    def _validate(train_idx: np.ndarray, test_idx: np.ndarray) -> None:
        if np.intersect1d(train_idx, test_idx).size > 0:
            raise CPCVSplitError("CPCV produced overlapping train/test indices")
