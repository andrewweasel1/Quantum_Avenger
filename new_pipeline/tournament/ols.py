"""Small shared OLS helpers (numpy ``lstsq``).

Several call sites (the Granger F-test in ``causal_selection`` and the ADF /
Engle-Granger / Ornstein-Uhlenbeck fits in ``stat_arb``) hand-rolled the same
"build a design with an intercept, least-squares fit, recompute the residual sum
of squares" idiom. These two functions centralize it.
"""

import numpy as np


def ols(design, response):
    """Least-squares fit of ``response`` on ``design``: returns ``(coef, rss, rank)``
    where ``rss`` is the residual sum of squares and ``rank`` the design's rank."""
    coef, _residuals, rank, _sv = np.linalg.lstsq(
        np.asarray(design, dtype=np.float64), np.asarray(response, dtype=np.float64), rcond=None
    )
    resid = response - design @ coef
    return coef, float(resid @ resid), int(rank)


def with_intercept(*columns) -> np.ndarray:
    """Column-stack the given 1-D arrays and append an intercept column of ones."""
    cols = [np.asarray(column, dtype=np.float64) for column in columns]
    return np.column_stack([*cols, np.ones(cols[0].size)])
