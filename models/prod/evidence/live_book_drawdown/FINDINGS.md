# Live book drawdown: not the market, not the tilt — turnover is 2-3x modelled

Window 2026-07-25..2026-09-28, 35 paired sessions, 4,487 fills.
Equity 98,280 -> 94,897 = **-3.44%** (-3.83% compounding the daily series).

## The drawdown is idiosyncratic, not exposure

| regression of daily book return on | beta | t | R2 |
|---|---|---|---|
| IWM (small-cap proxy for the universe) | +0.048 | 0.53 | 0.008 |
| SPY | +0.171 | 1.55 | 0.068 |
| both | SPY +0.353 / IWM -0.177 | 1.89 / -1.21 | 0.108 |

The window had a sharp size split — **SPY +3.97%, IWM -3.88%, MDY -3.67%** —
so a net-long small/mid tilt was the obvious suspect. It is not the cause:
betas are small and insignificant and R2 is 0.008-0.108. At the observed ~7%
net exposure the tilt accounts for roughly -0.27%, under a tenth of the loss.

Book: -11.06 bps/day, sd 47.1 bps, **Sharpe -3.72 annualized**.

## Turnover is running 2-3x what the promoted spec assumed

| | turnover/day | vs modelled |
|---|---|---|
| backtest `avg_daily_turnover` | 0.0406 | — |
| **live, all days** | **0.1273** | **3.1x** |
| live, excluding the Sep 14/15 universe incident | 0.0913 | **2.2x** |

Where it comes from (turnover in the 0.5*sum|dw| convention):

| day kind | days | orders | notional | turnover |
|---|---|---|---|---|
| rebalance | 6 | 3,496 | $602,833 | 3.105 |
| incident (Sep 14/15) | 2 | 827 | $244,672 | 1.260 |
| hold-day drift | 6 | 164 | $17,930 | 0.092 |

**Hold-day drift is negligible** (0.092 total, ~1.5 bps/day of turnover) — it was
my prior suspect and it is not the problem. The cost is concentrated in the
rebalances themselves: **0.517 per rebalance against the backtest's 0.203 per
5-day cycle**, i.e. live rebalances rotate ~2.5x more of the book.

## Why that matters more than the drawdown itself

`breakeven_cost_bps` was **54.3** in the backtest — but that number was computed
at 0.0406 turnover. Breakeven scales inversely with turnover:

> at live turnover, breakeven is **17.3 bps**

and the intraday programme measured half-spreads on this very universe at
**8-11 bps, i.e. 16-22 bps round trip**. So the book is sitting at or past its
cost breakeven on measured spreads alone. The promoted net Sharpe of 1.01
(gross 1.31) assumed a turnover live trading is not reproducing.

Cost drag at the live rate:

| assumed cost | drag | share of the -11.06 bps/day |
|---|---|---|
| 10 bps (the spec's `cost_bps`) | 1.27 bps/day, 3.2%/yr | 12% |
| 20 bps | 2.55 bps/day, 6.4%/yr | 23% |
| 30 bps | 3.82 bps/day, 9.6%/yr | 35% |

## Most likely root cause, and it is already disclosed

`paper_trade_book`'s own docstring says it: "the gauntlet's book is built from
OUT-OF-SAMPLE bagged probabilities that only exist inside a backtest; live, each
name is scored by its sector's deployed candidate booster (the standard
train/serve approximation — documented, not hidden)."

Bagged OOS probabilities are an average over folds and are therefore smoother
across days than a single deployed booster's score. Smoother scores rotate the
top/bottom quantile less. That is exactly the shape of the discrepancy: same
rebalance cadence, same quantile, ~2.5x the rotation. The approximation was
documented but its turnover consequence was never measured — this is that
measurement.

Note also `rebalance_band` is absent from `best_params`, so the live book runs
with no rank hysteresis (band 0.0). The hysteresis machinery exists precisely
to cut turnover; the promoted champion does not use it.

## What is and is not established

**Established (measurement, not inference):** live turnover is 2.2-3.1x the
modelled rate; hold-day drift is not the driver; breakeven at live turnover is
17.3 bps against 16-22 bps measured round-trip spreads.

**NOT established:** that the strategy is broken. 35 sessions at -11.06 bps/day
with sd 47.1 gives **t = -1.39** — comfortably inside noise. A -3.4% drawdown
is unremarkable for a book whose backtested net Sharpe is 1.01. Nothing here
refutes the champion.

**Partly self-inflicted:** the expired-universe incident contributed 1.260 of
the 4.457 total turnover (28%) across two days, for a book that spent eight
sessions at a third of its intended breadth.

## Next tests, cheapest first

1. **Measure score persistence directly** — day-over-day rank correlation of
   live deployed-booster scores vs the backtest's bagged OOS probabilities. If
   live autocorrelation is materially lower, the train/serve gap is confirmed
   as the turnover driver. Read-only, no trading.
2. **Re-price the champion at live turnover.** Re-run the L/S sleeve's cost
   haircut with turnover 0.0913-0.1273 instead of 0.0406 and see whether net
   Sharpe survives its own gauntlet. If it does not, the promotion rested on an
   unmet assumption and the honest response is to re-run the gauntlet, not to
   keep trading it.
3. **Only then** consider remedies (rank hysteresis, wider quantile, slower
   cadence) — each is a spec change that must clear the gauntlet, not a patch.
