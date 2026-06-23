"""Golden-number tests — pin quant outputs to fixed literals so refactors can't
silently drift. Seeded by the causal-feature-selection pass; the intent is to
grow this directory to cover ATR / vol√252 / Amihud / slippage / asymmetric
grad-hess / DSR / Kelly / triple-barrier / CPCV folds (rigor backlog item 4).
"""

import numpy as np
import pytest
from new_pipeline.tournament.causal_selection import granger_pvalue, purged_cpcv_mda
from new_pipeline.tournament.cpcv import CPCVSplitGenerator
from new_pipeline.tournament.sample_weights import (
    average_uniqueness,
    get_concurrency,
    sequential_bootstrap,
)


def test_granger_pvalue_golden():
    rng = np.random.default_rng(0)
    n = 200
    x = rng.normal(size=n)
    y = np.zeros(n)
    y[1:] = 0.5 * x[:-1] + rng.normal(0.0, 0.5, n)[1:]
    decoy = rng.normal(size=n)
    assert granger_pvalue(decoy, y, lags=2, horizon=1) == pytest.approx(
        0.38553315970103647, abs=1e-12
    )


def test_purged_cpcv_mda_golden():
    rng = np.random.default_rng(0)
    n = 160
    x = rng.normal(size=n)
    decoy = rng.normal(size=n)
    labels = (x > 0.0).astype(np.float64)
    matrix = np.column_stack([x, decoy])
    splitter = CPCVSplitGenerator(n_groups=4, test_groups=2, purge=0, embargo=0)

    def fit_fn(train_x, train_y):
        corr0 = abs(np.corrcoef(train_x[:, 0], train_y)[0, 1])
        corr1 = abs(np.corrcoef(train_x[:, 1], train_y)[0, 1])
        best = 0 if corr0 >= corr1 else 1
        return lambda test_x: (test_x[:, best] > 0.0).astype(np.float64)

    importances = purged_cpcv_mda(matrix, ["x", "decoy"], labels, fit_fn, splitter, seed=0)
    assert importances["x"] == pytest.approx(0.4666666666666666, abs=1e-12)
    assert importances["decoy"] == pytest.approx(0.0, abs=1e-12)


def test_sample_weights_golden():
    t1 = np.array([0, 2, 2, 4, 4, 4, 6, 6])
    assert get_concurrency(t1).tolist() == [1.0, 1.0, 2.0, 1.0, 2.0, 1.0, 1.0, 1.0]
    np.testing.assert_allclose(
        average_uniqueness(t1), [1.0, 0.75, 0.5, 0.75, 0.5, 1.0, 1.0, 1.0], atol=1e-12
    )
    assert sequential_bootstrap(t1, size=8, seed=7).tolist() == [5, 7, 5, 1, 2, 6, 0, 6]


def test_cpcv_folds_golden():
    folds = CPCVSplitGenerator().split(24)
    assert len(folds) == 15
    train0, test0 = folds[0]
    assert test0.tolist() == [0, 1, 2, 3, 4, 5, 6, 7]
    assert train0.tolist() == [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]
