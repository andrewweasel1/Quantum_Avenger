"""Golden-number tests — pin quant outputs to fixed literals so refactors can't
silently drift. Seeded by the causal-feature-selection pass; the intent is to
grow this directory to cover ATR / vol√252 / Amihud / slippage / asymmetric
grad-hess / DSR / Kelly / triple-barrier / CPCV folds (rigor backlog item 4).
"""

import numpy as np
import pytest
from new_pipeline.tournament.causal_selection import granger_pvalue, purged_cpcv_mda
from new_pipeline.tournament.cpcv import CPCVSplitGenerator


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
