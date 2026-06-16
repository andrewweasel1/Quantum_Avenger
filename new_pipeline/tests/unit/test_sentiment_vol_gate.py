import pytest
from new_pipeline.features.shields import (
    DEFAULT_SENTIMENT_ALPHA,
    sentiment_volatility_gate,
)

ENTRY, ATR, MULT, CAP, RISK = 100.0, 2.0, 3.0, 100_000.0, 0.01
BASELINE = CAP * RISK / (MULT * ATR)  # neutral-sentiment risk-based size


def test_neutral_sentiment_is_baseline_size():
    approved, size = sentiment_volatility_gate(ENTRY, ATR, MULT, CAP, RISK, 0.0)
    assert approved
    assert size == pytest.approx(BASELINE)


def test_positive_sentiment_scales_up_capped():
    approved, size = sentiment_volatility_gate(ENTRY, ATR, MULT, CAP, RISK, 1.0)
    assert approved
    assert size == pytest.approx(BASELINE * (1.0 + DEFAULT_SENTIMENT_ALPHA))


def test_negative_sentiment_full_veto():
    assert sentiment_volatility_gate(ENTRY, ATR, MULT, CAP, RISK, -1.0) == (False, 0.0)


def test_negative_sentiment_shrinks_size_and_tightens_stop():
    approved, size = sentiment_volatility_gate(ENTRY, ATR, MULT, CAP, RISK, -0.5)
    assert approved
    # g = 0.5, effective ATR multiple tightened to 0.8x -> size = baseline * 0.5/0.8
    assert size < BASELINE
    assert size == pytest.approx(BASELINE * (0.5 / 0.8))


def test_stop_floor_binds_under_extreme_tightening():
    # beta keeps g > 0 (approved); gamma drives the multiple below the floor.
    approved, size = sentiment_volatility_gate(
        ENTRY, ATR, MULT, CAP, RISK, -1.0, beta=0.5, gamma=2.0, min_stop_frac=0.25
    )
    assert approved
    expected = CAP * RISK / (0.25 * MULT * ATR) * 0.5  # multiple floored at 0.25x
    assert size == pytest.approx(expected)


def test_stop_below_entry_vetoes():
    assert sentiment_volatility_gate(1.0, 10.0, 3.0, CAP, RISK, 0.0) == (False, 0.0)


def test_invalid_inputs_veto():
    assert sentiment_volatility_gate(100.0, 0.0, 3.0, CAP, RISK, 0.0) == (False, 0.0)
    assert sentiment_volatility_gate(100.0, 2.0, 3.0, 0.0, RISK, 0.0) == (False, 0.0)
