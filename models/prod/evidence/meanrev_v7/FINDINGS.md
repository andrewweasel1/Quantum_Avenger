# The sample-size lever, spent: the edge was one period, not a small effect

One variable vs v6: history extended 478 -> 1,232 sessions (2021-09-01..
2026-07-31), scanner collapsed to `attention` alone per v6. 32 trials,
140,082 trades, measured-spread coverage **94.4%** of name-days (up from
92.3%) on a quote vault backfilled to 60 months.

**Not promoted, and this run ends the strategy family.** The extension was
designed to test one assumption, and refuted it.

## The prediction, and why it failed

v4 recorded: "t scales with sqrt(n_obs). Extending history from 478 to ~1,200
sessions multiplies t by 1.58: at the CURRENT Sharpe that is t ~ 3.26, which
clears." The clause doing the work was *at the current Sharpe*.

| | v6 (478 sessions) | v7 (1,232 sessions) |
|---|---|---|
| session Sharpe | 0.0944 | **0.0575** |
| sqrt(n) | 21.9 | 35.1 |
| **t** | **2.06** | **2.02** |
| SR annualized | 1.50 | 0.91 |
| gross bps/trade | 61.2 | 37.2 |
| win rate | 52.7% | 48.8% |
| DSR | 0.5493 | 0.4349 |
| timing-null margin | 0.189 | 0.131 |
| PBO | 0.238 | 0.000 |
| 1st / 2nd half SR | +0.045 / +0.131 | **-0.038** / +0.083 |

Sample rose 2.58x, sqrt(n) rose 1.61x, and **t did not move** (2.06 -> 2.02)
because the Sharpe fell by almost exactly the offsetting factor (0.0944 ->
0.0575 is a ratio of 1.64 against sqrt's 1.61). That is the signature of a
statistic that was measuring a window, not an effect.

## The backfilled three years returned nothing

| period | sessions | session SR | ann SR | t | total return |
|---|---|---|---|---|---|
| FULL | 1,232 | 0.0575 | 0.91 | 2.02 | +5.54% |
| **2021-09..2024-08** | **754** | **-0.0202** | **-0.32** | **-0.55** | **-0.07%** |
| 2024-09..2026-07 | 478 | +0.0938 | 1.49 | 2.05 | +5.61% |

Every dollar came from the window the strategy was developed on. The 754
sessions it had never seen produced a flat line.

## And within that window, one year carries everything

| year | sessions | session SR | trades | net bps | win rate | net $ |
|---|---|---|---|---|---|---|
| 2021 | 85 | 0.0019 | 51 | 32.5 | 43.1% | $1 |
| 2022 | 251 | 0.0161 | 85 | 32.4 | 44.7% | $22 |
| 2023 | 250 | **-0.1234** | 88 | **-65.0** | 43.2% | -$145 |
| 2024 | 252 | 0.0098 | 100 | 9.2 | 50.0% | $19 |
| 2025 | 249 | **-0.0295** | 140 | 9.4 | 46.4% | -$200 |
| **2026** | **145** | **0.1818** | **87** | **124.4** | **64.4%** | **$5,730** |

2026 — 145 partial-year sessions, 87 trades — is 103% of the programme's
lifetime profit. Its 124.4 net bps and 64.4% win rate resemble no other year
in the sample (9-33 bps, 43-50% win). Five of six years are flat or negative.

**Median trade: -$0.14. The top 10 trades of 551 are 70% of all profit; the
top 3 are 29%.** A strategy whose median trade loses money and whose result is
ten fills is not a small edge that needs more sample. It is a handful of
outcomes.

## The regime gate, with three testable states

More sessions made all three HMM states testable (each clearing the 60-obs
floor), so k=3 and the family-wise bar fell from 0.9025 to 0.857375:

| regime | DSR | bar | SR annualized | T |
|---|---|---|---|---|
| 0 | 0.848 | 0.857 | +1.50 | 342 |
| 1 | 0.388 | 0.857 | +0.84 | 536 |
| 2 | 0.463 | 0.857 | +0.89 | 354 |

All three positive for the first time — and all three fail. Regime 0 misses by
**0.009**, which is a fail. The bar moved only because a third state became
testable, never to fit a result, and a 0.009 shortfall is not "essentially
passing". Given the yearly table, regime 0's DSR is in any case reading the
2026 window rather than a regime property.

PBO fell to 0.000, which is worth stating precisely: the trials are not
overfit *to each other*. They are all resting on the same 145 sessions.
A clean PBO does not rescue a result concentrated in one period.

## What is now established, and what it costs

1. **Intraday mean reversion on small/mid caps has no demonstrated persistent
   edge.** Six years, 1,232 sessions, measured costs, and five of six years
   flat-to-negative.
2. **Every prior intraday verdict was reading the same window.** v2's "first
   net-positive result", v3's z-monotonicity, v4's "both regimes positive",
   v5/v6's scanner comparisons — all were computed on samples containing 2026.
   The rankings between scanners may still hold; the *level* they were ranked
   at does not.
3. **The sample-size lever is spent.** It was the last honest one that touched
   no signal definition, and it resolved against the strategy. There is no
   version of "more data" left to try: the vault now runs to the limit of
   what Alpaca serves at minute resolution for this universe.

The correct action is to stop developing this family, not to search for a
variant that rescues 2026. Any further axis tried now would be selected
against a known-good period, which is the definition of the overfitting this
gauntlet exists to prevent.

## What the run does NOT say

- It does not say the cost model is wrong; measured-spread coverage improved
  to 94.4% and cost share of gross was stable (7.0% -> 7.1%).
- It does not say the execution work was wasted. touch_cap sizing, depth-aware
  impact and measured spreads are correct infrastructure and would be needed
  by any intraday strategy.
- It does not say 2026 was fake. It says 87 trades in one partial year cannot
  distinguish a real regime-specific edge from luck, and the other 464 trades
  across five years say the base rate is roughly zero.
