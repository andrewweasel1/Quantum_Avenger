import numpy as np
import pytest
from new_pipeline.core.exceptions import CPCVSplitError
from new_pipeline.tournament.cpcv import CPCVSplitGenerator


def test_canonical_fifteen_folds():
    gen = CPCVSplitGenerator()
    folds = gen.split(120)
    assert len(folds) == 15 == gen.n_folds


def test_no_train_test_overlap():
    for train_idx, test_idx in CPCVSplitGenerator().split(120):
        assert np.intersect1d(train_idx, test_idx).size == 0


def test_embargo_excludes_positions_after_test():
    for train_idx, test_idx in CPCVSplitGenerator(purge=5, embargo=5).split(120):
        train = set(train_idx.tolist())
        last = int(test_idx.max())
        for offset in range(1, 6):
            if last + offset < 120:
                assert last + offset not in train


def test_purge_excludes_positions_before_test():
    for train_idx, test_idx in CPCVSplitGenerator(purge=5, embargo=5).split(120):
        train = set(train_idx.tolist())
        test_set = set(test_idx.tolist())
        first = int(test_idx.min())
        for offset in range(1, 6):
            pos = first - offset
            if pos >= 0 and pos not in test_set:
                assert pos not in train


def test_raises_when_too_few_samples():
    with pytest.raises(CPCVSplitError):
        CPCVSplitGenerator(n_groups=6).split(3)


def test_path_count_canonical():
    # phi = C(n_groups-1, test_groups-1) = C(5, 1) = 5 for the canonical splitter.
    assert CPCVSplitGenerator().path_count == 5


def test_span_purge_drops_label_overlapping_train():
    # 3 groups of 3, label span = 2 bars ahead, only span-purge active.
    gen = CPCVSplitGenerator(n_groups=3, test_groups=1, purge=0, embargo=0)
    t1 = np.arange(9) + 2  # event ends 2 bars ahead
    folds = gen.split(9, t1=t1)
    # combos order is (0,), (1,), (2,); fold[1] tests the middle block [3,4,5].
    train_idx, test_idx = folds[1]
    assert test_idx.tolist() == [3, 4, 5]
    # Every train row before the block whose 2-ahead span reaches >= 3 is purged,
    # as is everything up to the block's furthest label end (5 -> 7); only 0 and 8 survive.
    assert train_idx.tolist() == [0, 8]


def test_fractional_embargo_widens_window():
    # embargo_pct dominates the fixed embargo: 10% of 100 = 10 positions.
    gen = CPCVSplitGenerator(purge=0, embargo=0, embargo_pct=0.1)
    for train_idx, test_idx in gen.split(100):
        train = set(train_idx.tolist())
        test = set(test_idx.tolist())
        last = int(test_idx.max())
        for offset in range(1, 11):
            pos = last + offset
            if pos < 100 and pos not in test:
                assert pos not in train


def test_assemble_paths_stitches_one_segment_per_group():
    gen = CPCVSplitGenerator(n_groups=4, test_groups=2)
    n = 8  # groups: [0,1] [2,3] [4,5] [6,7]
    # Each (combo, group) segment is filled with the combo index, so we can read
    # back which combination fed each group block of each reconstructed path.
    combos = gen.combinations()
    groups = np.array_split(np.arange(n), 4)
    segments = {
        (ci, g): np.full(groups[g].shape[0], float(ci))
        for ci, combo in enumerate(combos)
        for g in combo
    }
    paths = gen.assemble_paths(n, segments)
    assert paths.shape == (gen.path_count, n)  # (3, 8)
    # Group 0 is tested by combos [0, 1, 2]; group 1 by [0, 3, 4] (combo order).
    assert paths[0, 0:2].tolist() == [0.0, 0.0]
    assert paths[1, 0:2].tolist() == [1.0, 1.0]
    assert paths[2, 0:2].tolist() == [2.0, 2.0]
    assert paths[1, 2:4].tolist() == [3.0, 3.0]
