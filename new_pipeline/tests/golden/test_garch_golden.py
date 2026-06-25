"""Golden numbers for GARCH(1,1) conditional volatility (offense roadmap §D).

Pins the conditional vol on a fixed series with a volatility burst. The fit is by
``scipy.optimize`` Nelder-Mead, so the tolerance is looser than the closed-form
goldens (optimizer micro-variation across scipy versions). See
docs/quantitative_math.md Part II §D.
"""

import numpy as np
import pytest
from new_pipeline.features.garch import garch_conditional_volatility


def _series() -> np.ndarray:
    rng = np.random.default_rng(7)
    returns = rng.normal(0, 0.01, 300)
    returns[150:180] *= 4.0  # a volatility burst -> clustering
    return returns


def test_garch_golden():
    gv = garch_conditional_volatility(_series(), fit_window=100, annualize=True)
    assert gv[200] == pytest.approx(0.14289376552397165, rel=1e-6)
    assert gv[250] == pytest.approx(0.14292861295944873, rel=1e-6)
