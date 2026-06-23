import numpy as np
from new_pipeline.tournament.objectives import (
    asymmetric_financial_loss,
    asymmetric_loss_factory,
)
from new_pipeline.tournament.simulator import (
    sharpe_ratio,
    simulate_t1_returns,
    simulate_t1_returns_blockwise,
)


class _DMatrix:
    def __init__(self, labels, weights=None):
        self._labels = np.asarray(labels, dtype=np.float64)
        self._weights = np.asarray([] if weights is None else weights, dtype=np.float64)

    def get_label(self):
        return self._labels

    def get_weight(self):
        return self._weights


def test_asymmetric_loss_penalizes_false_positives_5x():
    grad, hess = asymmetric_financial_loss(np.array([0.0, 0.0]), _DMatrix([0.0, 1.0]))
    np.testing.assert_allclose(grad, [2.5, -0.5])  # p=0.5: (0.5-0)*5, (0.5-1)*1
    np.testing.assert_allclose(hess, [1.25, 0.25])  # 0.25*5, 0.25*1


def test_asymmetric_loss_applies_sample_weights():
    # Uniqueness weights multiply the class penalty in grad/hess.
    grad, hess = asymmetric_financial_loss(
        np.array([0.0, 0.0]), _DMatrix([0.0, 1.0], weights=[2.0, 3.0])
    )
    np.testing.assert_allclose(grad, [5.0, -1.5])  # (0.5-0)*5*2, (0.5-1)*1*3
    np.testing.assert_allclose(hess, [2.5, 0.75])  # 0.25*5*2, 0.25*1*3


def test_loss_factory_binds_penalties():
    objective = asymmetric_loss_factory(penalty_fp=3.0, penalty_fn=1.0)
    grad, _ = objective(np.array([0.0]), _DMatrix([0.0]))
    np.testing.assert_allclose(grad, [1.5])  # (0.5-0)*3


def test_simulator_stop_out_returns_negative():
    close = np.array([100.0, 100.0])
    low = np.array([100.0, 90.0])  # next-bar low pierces the stop at 98
    atr = np.array([1.0, 1.0])
    out = simulate_t1_returns(np.array([1, 0]), close, low, atr, 2.0, 0.02)
    assert out[0] < 0.0


def test_simulator_winning_trade_positive():
    close = np.array([100.0, 103.0])
    low = np.array([100.0, 102.0])
    atr = np.array([1.0, 1.0])
    out = simulate_t1_returns(np.array([1, 0]), close, low, atr, 2.0, 0.02)
    assert out[0] > 0.0


def test_simulator_no_lookahead_on_last_bar():
    close = np.array([100.0, 101.0])
    low = close - 1.0
    atr = np.full(2, 1.0)
    out = simulate_t1_returns(np.array([0, 1]), close, low, atr, 2.0, 0.02)
    assert out[-1] == 0.0  # a signal on the final bar has no t+1 -> no trade


def test_blockwise_sim_does_not_cross_ticker_boundary():
    # block A = [0,1], block B = [2,3]. A's last bar (idx 1) must not exit on B's
    # first bar (idx 2) — that would fabricate a stop-out from a different ticker.
    signals = np.array([1, 1, 0, 0])
    close = np.array([100.0, 102.0, 50.0, 60.0])
    low = np.array([99.0, 101.0, 49.0, 59.0])
    atr = np.array([1.0, 1.0, 1.0, 1.0])
    block_ids = np.array([0, 0, 1, 1])

    out = simulate_t1_returns_blockwise(signals, close, low, atr, block_ids, 2.0, 0.02)
    naive = simulate_t1_returns(signals, close, low, atr, 2.0, 0.02)

    assert out[0] > 0.0  # within-block trade still realizes on the next in-block bar
    assert out[1] == 0.0  # A's last bar: no cross-ticker t+1
    assert naive[1] != 0.0  # the naive concatenated sim leaks (idx2 stop-out)


def test_sharpe_zero_for_flat_series():
    assert sharpe_ratio(np.zeros(10)) == 0.0
