"""Unit tests for the shared OLS helpers."""

import numpy as np
import pytest
from new_pipeline.tournament.ols import ols, with_intercept


def test_with_intercept_appends_ones_column():
    design = with_intercept(np.array([1.0, 2.0, 3.0]))
    assert design.shape == (3, 2)
    assert (design[:, 0] == [1.0, 2.0, 3.0]).all()  # the given column stays first
    assert (design[:, -1] == 1.0).all()  # intercept appended last


def test_ols_recovers_known_line():
    x = np.arange(10.0)
    coef, rss, rank = ols(with_intercept(x), 2.0 * x + 1.0)  # y = 2x + 1 exactly
    assert coef == pytest.approx([2.0, 1.0])
    assert rss == pytest.approx(0.0, abs=1e-18)
    assert rank == 2


def test_ols_rss_equals_residual_sum_of_squares():
    rng = np.random.default_rng(0)
    x = rng.normal(0, 1, 50)
    y = 0.5 * x + rng.normal(0, 1, 50)
    design = with_intercept(x)
    coef, rss, _ = ols(design, y)
    resid = y - design @ coef
    assert rss == pytest.approx(float(resid @ resid))
