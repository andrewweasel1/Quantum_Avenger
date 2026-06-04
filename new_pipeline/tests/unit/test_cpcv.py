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
