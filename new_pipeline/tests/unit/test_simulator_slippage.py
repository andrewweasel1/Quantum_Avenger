"""Net-of-slippage t+1 simulator: exact round-trip cost, illiquid veto, and
byte-for-byte parity with the gross path when costs are negligible/off."""

import numpy as np
from new_pipeline.features.slippage import hydrodynamic_slippage_bps
from new_pipeline.tournament.simulator import (
    simulate_t1_returns,
    simulate_t1_returns_blockwise,
    simulate_t1_returns_blockwise_net,
    simulate_t1_returns_net,
)

ATR_MULT, MAX_RISK, CAP = 2.0, 0.02, 100_000.0
C, SCALER, CEIL = 0.5, 10_000.0, 50.0


def _win_series():
    # 3 bars: fire at 0, up move to bar 1 (no stop hit). entry=100, atr=1 ->
    # stop=98, risk_distance=0.02, size_fraction = 0.02/0.02 = 1.0.
    sig = np.array([1, 0, 0], dtype=np.int64)
    close = np.array([100.0, 103.0, 103.0])
    low = np.array([100.0, 101.0, 101.0])
    atr = np.array([1.0, 1.0, 1.0])
    return sig, close, low, atr


def test_net_isolated_trade_pays_round_trip_split_across_entry_and_exit():
    # Fire only at bar 0: enter at close[0], hold [0,1], flat at bar 1.
    # Turnover cost = one-way at entry (bar 0) + one-way at exit (bar 1) =
    # a full round-trip, but SPLIT across the two bars (not both on bar 0).
    sig, close, low, atr = _win_series()
    adv = np.array([2.0e8, 2.0e8, 2.0e8])   # $200M dollar ADV
    vol = np.array([0.30, 0.30, 0.30])       # annualized
    sf = 1.0
    gross0 = simulate_t1_returns(sig, close, low, atr, ATR_MULT, MAX_RISK)[0]
    net = simulate_t1_returns_net(
        sig, close, low, atr, adv, vol, ATR_MULT, MAX_RISK, CAP, C, SCALER, CEIL
    )
    one_way = hydrodynamic_slippage_bps(sf * CAP, 0.30, 2.0e8, C, SCALER)
    leg = one_way / 10_000.0 * sf  # one-way turnover cost, sf traded
    assert gross0 == 0.03  # gross bar-0 move
    np.testing.assert_allclose(net[0], gross0 - leg, rtol=1e-12)   # entry leg
    np.testing.assert_allclose(net[1], -leg, rtol=1e-12)           # exit leg
    np.testing.assert_allclose(net[0] + net[1], gross0 - 2.0 * leg, rtol=1e-12)
    assert 0.0 < one_way < CEIL  # liquid: charged, not vetoed


def test_net_held_position_pays_no_mid_hold_cost():
    # Fire on bars 0 AND 1 with identical size -> position is HELD from 0->2,
    # so bar 1 incurs ZERO turnover cost (only entry@0 and exit@2 are charged).
    sig = np.array([1, 1, 0, 0], dtype=np.int64)
    close = np.array([100.0, 101.0, 102.0, 102.0])
    low = np.array([100.0, 100.5, 101.5, 101.5])
    atr = np.array([1.0, 1.0, 1.0, 1.0])     # constant -> constant size_fraction
    adv = np.full(4, 2.0e8)
    vol = np.full(4, 0.30)
    net = simulate_t1_returns_net(
        sig, close, low, atr, adv, vol, ATR_MULT, MAX_RISK, CAP, C, SCALER, CEIL
    )
    sf = 1.0
    one_way = hydrodynamic_slippage_bps(sf * CAP, 0.30, 2.0e8, C, SCALER)
    leg = one_way / 10_000.0 * sf
    g0 = (101.0 - 100.0) / 100.0        # bar-0 hold move
    g1 = (102.0 - 101.0) / 101.0        # bar-1 hold move
    np.testing.assert_allclose(net[0], g0 - leg, rtol=1e-12)   # entry only
    np.testing.assert_allclose(net[1], g1, rtol=1e-12)         # HELD: no cost
    np.testing.assert_allclose(net[2], -leg, rtol=1e-12)       # exit only
    # total cost over the 2-day hold is one round-trip, not two
    total_cost = (g0 + g1) - (net[0] + net[1] + net[2])
    np.testing.assert_allclose(total_cost, 2.0 * leg, rtol=1e-12)


def test_net_vetoes_illiquid_fill():
    sig, close, low, atr = _win_series()
    adv = np.array([5.0e6, 5.0e6, 5.0e6])    # thin: $5M ADV
    vol = np.array([0.45, 0.45, 0.45])
    one_way = hydrodynamic_slippage_bps(1.0 * CAP, 0.45, 5.0e6, C, SCALER)
    assert one_way > CEIL  # precondition: this fill should be blocked
    net = simulate_t1_returns_net(
        sig, close, low, atr, adv, vol, ATR_MULT, MAX_RISK, CAP, C, SCALER, CEIL
    )
    assert net[0] == 0.0  # vetoed -> no position, no return


def test_net_stop_out_charged_entry_then_flattens():
    sig = np.array([1, 0, 0], dtype=np.int64)
    close = np.array([100.0, 97.0, 97.0])
    low = np.array([100.0, 97.0, 97.0])      # bar1 low 97 <= stop 98 -> stop-out
    atr = np.array([1.0, 1.0, 1.0])
    adv = np.array([2.0e8, 2.0e8, 2.0e8])
    vol = np.array([0.30, 0.30, 0.30])
    gross = simulate_t1_returns(sig, close, low, atr, ATR_MULT, MAX_RISK)[0]
    net = simulate_t1_returns_net(
        sig, close, low, atr, adv, vol, ATR_MULT, MAX_RISK, CAP, C, SCALER, CEIL
    )
    assert gross == -0.02  # -risk_distance * size_fraction(1.0)
    one_way = hydrodynamic_slippage_bps(1.0 * CAP, 0.30, 2.0e8, C, SCALER)
    leg = one_way / 10_000.0
    # entry turnover charged at bar 0; the stop-out flattens the book, so bar 1
    # sees prev_pos == 0 (no spurious exit turnover on the already-exited name).
    np.testing.assert_allclose(net[0], gross - leg, rtol=1e-12)
    assert net[1] == 0.0
    assert net[0] < gross  # cost deepens the loss


def test_zero_cost_reduces_to_gross():
    # constant 0 => zero slippage => net path must equal gross exactly.
    sig, close, low, atr = _win_series()
    adv = np.array([1.0e9, 1.0e9, 1.0e9])
    vol = np.array([0.2, 0.2, 0.2])
    gross = simulate_t1_returns(sig, close, low, atr, ATR_MULT, MAX_RISK)
    net = simulate_t1_returns_net(
        sig, close, low, atr, adv, vol, ATR_MULT, MAX_RISK, CAP, 0.0, SCALER, CEIL
    )
    np.testing.assert_array_equal(net, gross)


def test_blockwise_net_matches_per_block_and_isolates():
    rng = np.random.default_rng(0)
    n = 40
    sig = (rng.random(n) > 0.5).astype(np.int64)
    close = 100.0 + np.cumsum(rng.normal(0, 1, n))
    low = close - np.abs(rng.normal(0, 1, n))
    atr = np.full(n, 1.5)
    adv = np.full(n, 2.0e8)
    vol = np.full(n, 0.3)
    block_ids = np.array([0] * 20 + [1] * 20)
    out = simulate_t1_returns_blockwise_net(
        sig, close, low, atr, adv, vol, block_ids, ATR_MULT, MAX_RISK, CAP, C, SCALER, CEIL
    )
    # each block equals a standalone net sim of that block (no cross-block exit)
    for a, b in ((0, 20), (20, 40)):
        standalone = simulate_t1_returns_net(
            sig[a:b], close[a:b], low[a:b], atr[a:b], adv[a:b], vol[a:b],
            ATR_MULT, MAX_RISK, CAP, C, SCALER, CEIL
        )
        np.testing.assert_array_equal(out[a:b], standalone)


def test_default_config_leaves_grid_search_gross(monkeypatch):
    # The dispatch flag is off by default: grid_search must call the gross sim.
    from new_pipeline.config import get_config, reload_config

    reload_config()
    assert get_config().execution.backtest_slippage_enabled is False
    # sanity: gross blockwise is unchanged and still importable/callable
    sig, close, low, atr = _win_series()
    out = simulate_t1_returns_blockwise(
        sig, close, low, atr, np.zeros(3), ATR_MULT, MAX_RISK
    )
    assert out[0] == (103.0 - 100.0) / 100.0
