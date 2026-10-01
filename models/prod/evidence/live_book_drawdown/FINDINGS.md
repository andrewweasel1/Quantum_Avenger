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

---

# Follow-up: the turnover cause is confirmed, but it does NOT explain the drawdown

## Step 1 could not be run as written

The champion's run directory holds only the 12 sector boosters and their
manifests. There is **no `oos_proba` artifact, no returns matrix, no
reconstructed paths** — the backtest's per-name scores were never persisted, so
there is no record of what it believed about any individual name, only the
aggregate diagnostics. The plan file's Phase 1 (persist per-fold OOS
probabilities) existed to make exactly this check possible and was never built.

Substitute, and a sharper test: rebuild the **live** score panel under the
champion's own mechanics and simulate its rebalance. That isolates cause
instead of comparing two things that differ in several ways at once.

## The live scoring path is the turnover driver — confirmed

Live panel: 197,313 rows, 236 sessions, 1,800 tickers, 5-day smoothing and
within-(date, sector) z-scores exactly as the champion specifies.

| | turnover/day | vs backtest |
|---|---|---|
| backtest `avg_daily_turnover` | 0.0406 | — |
| **simulated on LIVE scores** | **0.0785** | **1.9x** |
| observed live, ex incident | 0.0913 | 2.2x |
| observed live, all days | 0.1273 | 3.1x |

Simulating the identical mechanics on live scores reproduces **0.0785 of the
0.0913 observed** — roughly **86% of the excess turnover is the scores
themselves**, not execution, universe churn or position drift. The residual
~0.013/day is everything else.

Live score day-over-day rank autocorrelation is **0.9595** (median 0.9696).
That sounds high, and it is still not high enough: a hard 20% quantile cliff
rotates a large share of a 284-name leg every 5 days at that persistence. The
train/serve approximation is confirmed as the mechanism.

## Re-pricing the champion at live turnover

Backing the backtest's daily moments out of the manifest (gross SR 1.307, net
SR 1.010, cost 10 bps at turnover 0.0406): **gross +1.783 bps/day, sd 21.65
bps/day**.

Net Sharpe re-priced at live turnover, holding gross and sd at backtest values:

| turnover | 10 bps | 20 bps | 30 bps | |
|---|---|---|---|---|
| 0.0406 | **1.01** | 0.71 | 0.41 | backtest |
| 0.0785 | 0.73 | 0.16 | -0.42 | live scores |
| 0.0913 | 0.64 | **-0.03** | -0.70 | live ex-incident |
| 0.1273 | 0.37 | -0.56 | -1.49 | live all days |

Breakeven cost, which scales inversely with turnover: **54.3 bps at backtest
turnover becomes 28.1 / 24.1 / 17.3 bps** at the three live rates. Measured
half-spreads on this universe are 8-11 bps, so 16-22 bps round trip — i.e. the
book is near or past breakeven, and at live turnover with realistic spreads
the promoted net Sharpe of 1.01 re-prices to roughly **zero**.

## But costs are NOT the drawdown — correcting my earlier framing

The previous note said the book "may be at or past its cost breakeven", and let
that stand too close to an explanation of the -3.44%. The arithmetic does not
support that, and the distinction matters:

| | bps/day |
|---|---|
| backtest gross mean | +1.78 |
| backtest cost | -0.41 |
| **live observed mean** | **-11.06** |
| gross-to-live shortfall | **12.84** |

| extra cost vs backtest, at live turnover | bps/day | share of shortfall |
|---|---|---|
| 10 bps | 0.51 | 3.9% |
| 20 bps | 1.42 | 11.1% |
| 30 bps | 2.33 | 18.2% |

Explaining the whole shortfall through costs would need **141 bps per unit
turnover** — an order of magnitude beyond any plausible spread on these names.
So turnover re-prices the strategy's *expected* Sharpe materially, but it
accounts for only ~4-18% of what actually happened.

The rest is gross underperformance plus excess volatility: **live sd is 47.1
bps/day against 21.65 modelled — 2.2x**. A book running at twice its modelled
volatility and a negative gross mean is not a cost problem.

## What this establishes

1. **Confirmed:** the live scoring path drives ~86% of the excess turnover, via
   the documented train/serve approximation. Measured, not inferred.
2. **Confirmed:** at live turnover the champion's net Sharpe re-prices from
   1.01 to 0.64 (spec cost) or ~0.00 (measured spreads). The promotion rested
   on a turnover assumption live trading does not reproduce.
3. **Refuted (my own earlier framing):** costs do not explain the drawdown.
   They are 4-18% of it.
4. **Still inside noise:** t = -1.39 on 35 sessions. The drawdown itself
   remains unremarkable for a net-Sharpe-1.01 book and refutes nothing.
5. **New and unexplained:** live volatility is 2.2x modelled. That is the
   largest single discrepancy in the whole comparison and nothing here accounts
   for it.

## Next

The honest next step is **not** a turnover remedy. It is to explain the 2.2x
volatility gap, because a book at twice its modelled risk invalidates every
Sharpe figure above — including the re-pricing table. Candidates, cheapest
first: the eight sessions at a third of intended breadth (fewer names, more
idiosyncratic variance); the ~7% net exposure interacting with the size split;
and whether `sd` backed out of two manifest Sharpes is even the right
comparison, since it is a derived quantity rather than a recorded one.

Only after that is the re-pricing worth acting on — and acting on it means
re-running the gauntlet with honest turnover, not patching the live book.
