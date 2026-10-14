"""Calendar-time collapse: pooled ticker-major samples -> equal-weight daily means."""

from datetime import date

import numpy as np
from new_pipeline.tournament.accounting import collapse_to_daily

D1, D2, D3 = date(2021, 1, 4), date(2021, 1, 5), date(2021, 1, 6)


def test_collapse_averages_per_date_per_column():
    # Two tickers, ticker-major order (dates repeat, non-monotonic overall).
    dates = [D1, D2, D1, D2]
    matrix = np.array([[0.10, 1.0], [0.20, 2.0], [0.30, 3.0], [0.40, 4.0]])
    day, out = collapse_to_daily(dates, matrix)
    assert day.to_list() == [D1, D2]
    np.testing.assert_allclose(out, [[0.20, 2.0], [0.30, 3.0]])  # per-date column means


def test_collapse_sorts_nonmonotonic_ticker_major_dates():
    dates = [D2, D3, D1, D2]  # ticker A: D2,D3; ticker B: D1,D2
    values = np.array([2.0, 3.0, 1.0, 4.0])
    day, out = collapse_to_daily(dates, values)
    assert day.to_list() == [D1, D2, D3]  # sorted calendar axis
    np.testing.assert_allclose(out, [1.0, 3.0, 3.0])  # D2 = mean(2.0, 4.0)


def test_vector_call_matches_matrix_column():
    # The shared-axis property: collapsing a column alone == that column of the
    # whole-matrix collapse (one group_by keeps every trial row-aligned).
    rng = np.random.default_rng(7)
    dates = [D1, D2, D3, D1, D2, D3, D1]
    matrix = rng.normal(size=(7, 3))
    _, whole = collapse_to_daily(dates, matrix)
    for j in range(3):
        _, single = collapse_to_daily(dates, matrix[:, j])
        np.testing.assert_allclose(single, whole[:, j])
        assert single.ndim == 1  # vector in -> vector out


def test_length_mismatch_raises():
    import pytest

    with pytest.raises(ValueError, match="dates length"):
        collapse_to_daily([D1, D2], np.zeros(3))
