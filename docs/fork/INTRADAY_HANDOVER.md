# Intraday handover: what was already tried, and what it cost to learn

You are starting an intraday trading system in a fresh repository, with the
daily long/short book deliberately left behind. This document exists for one
reason: **two strategy families have already been built, priced and rejected
here, and rediscovering that would cost weeks.** The numbers below are from
official gauntlet runs with measured costs, not impressions.

Read this before designing a scanner or a signal. Nothing in it tells you what
to build; it tells you four things not to spend your sample on.

Source evidence travels with the fork under `evidence/` (runs `orb_v1`,
`orb_v2`, `meanrev_v1..v7`), each with its returns matrix, trade ledger and
candidate manifest, so every figure here is re-derivable rather than asserted.

---

## 1. Opening-range breakout: no directional information

Two runs, 78 priced trials, 262k simulated trades. Both rejected.

The decisive number is the **zero-cost counterfactual**: with trading costs set
to **zero**, the gross session Sharpe of the best of 60 trials was **+0.024**
(annualized +0.39) — and that is a maximum over 60 trials, so the unbiased
figure is lower.

The shape was diagnosed, not guessed:

| quantity | value |
|---|---|
| median \|gross move\| over hold | 65 bps |
| round-trip cost | 35 bps median |
| mean gross | **+0.8 bps/trade** |
| win rate | 30% |
| median gross | −13.5 bps |

The price travels far enough to pay the spread nearly twice over. The moves are
big enough; the *direction* is a coin flip — a positive-skew breakout with no
expectancy. Costs were a secondary, ordinary drag.

**Do not re-attempt ORB expecting cost work to rescue it.** Cost refinement,
scanner weighting and concentration changes cannot alter a zero-cost Sharpe of
+0.024.

## 2. Intraday mean reversion: the edge was one window, not a small effect

Seven runs. The last one extended history 478 → **1,232 sessions**
(2021-09..2026-07), 140,082 trades, 94.4% measured-spread coverage.

This was designed as the decisive test of a specific prediction — that `t`
scales with √n, so more history would clear the bar. It refuted it:

| | 478 sessions | 1,232 sessions |
|---|---|---|
| session Sharpe | 0.0944 | **0.0575** |
| √n | 21.9 | 35.1 |
| **t** | **2.06** | **2.02** |
| SR annualized | 1.50 | 0.91 |
| 1st / 2nd half SR | +0.045 / +0.131 | **−0.038** / +0.083 |

Sample rose 2.58×, √n rose 1.61×, and **t did not move**, because the Sharpe
fell by almost exactly the offsetting factor. That is the signature of a
statistic measuring a window rather than an effect.

Where the money was:

| period | sessions | session SR | total return |
|---|---|---|---|
| 2021-09..2024-08 (unseen) | 754 | **−0.0202** | **−0.07%** |
| 2024-09..2026-07 (dev window) | 478 | +0.0938 | +5.61% |

And inside the dev window, one partial year carries everything: **2026 — 145
sessions, 87 trades — is 103% of the programme's lifetime profit**, at 124.4
net bps and a 64.4% win rate against 9–33 bps and 43–50% in every other year.
Five of six years are flat or negative.

**Median trade: −$0.14. The top 10 trades of 551 are 70% of all profit; the
top 3 are 29%.**

A strategy whose median trade loses money and whose result is ten fills is not
a small edge awaiting more sample.

## 3. Consensus scanning is dead, and the mechanism is known

Five scanners × 32 constructions = 160 trials. Two consensus designs were
built. Both lost to the single best solo scanner (`attention`).

| scanner | mean session SR | outright wins | net bps |
|---|---|---|---|
| **attention** | **−0.0284** | **17/32** | **43.1** |
| union_v2 | −0.0402 | 2/32 | 33.4 |
| union (v1) | −0.0578 | 0/32 | 25.5 |

The second design fixed a real defect in the first and beat it on 30/32
constructions — and still lost to `attention` on 28/32. Net edge turned out to
be almost a linear function of how much of `attention`'s book a scanner
*retains* (60.7% → 25.5 bps; 71.6% → 33.4; 100% → 43.1).

The ledger shows why: of `attention`'s 275 events, `union_v2` dropped 78 for
failing unanimity, and those 78 were worth **42.9 net bps — indistinguishable
from the 43.1 average of the book they were removed from.** Unanimity across
weightings is not a quality signal on top of a single good ranking; it removes
good names at the same rate as a random cut, so the best achievable consensus
rule is the degenerate one that discards nothing.

**Do not rebuild a consensus/union/voting scanner.** Build one good ranker.

## 4. Effect size binds, not trial count

This is the most load-bearing item here, and the easiest to get backwards.

Going from 32 trials to 2,000 raises the required annualized Sharpe only
**1.61 → 2.11**. Multiplicity is cheap. What kills candidates is effect size.

Concretely, on the final mean-reversion run:

| gate | value | verdict |
|---|---|---|
| observed t-stat | 2.019 | — |
| Harvey-Liu haircut, 32 trials | **0.0000** (100% discount) | fails |
| Harvey-Liu haircut, 776 trials | **0.0000** (100% discount) | fails |
| White's Reality Check p | **0.6248** | fails (needs < 0.05) |

A t of 2.02 does not survive BHY adjustment for even a 32-way search, so
cross-run multiplicity never became binding. **Searching more carefully will
not help; searching at all is not the constraint.** Reality Check is the
blunter statement: p = 0.6248 says the best of 32 columns is entirely
consistent with none of them beating zero.

The practical consequence: do not optimize for "fewer trials so the haircut is
kinder". Spend trials freely on honest exploration and reject on effect size.

---

## The gauntlet is not yours to edit

`new_pipeline/evaluation/` travels **unmodified**, and changing a gate, a
threshold or a null is out of scope for this project. This is the single rule
in this document that is not advice.

The reason is structural, not ceremonial. Every verdict above was produced by
this code; soften a gate and the rejections stop being comparable to anything,
including each other. And a fresh session told to "build a profitable intraday
model", holding an editable copy of its own judge and no memory of why each
gate exists, has one very cheap path to success. It would not look like
cheating — it would look like reasonable engineering by someone who did not
know the history.

Two gates were missing from the intraday evaluator for most of its life
(`haircut_sharpe` was hardcoded `None`; `whites_reality_check` was never
called), so intraday registry rows carried null where the daily stack carried
values. They are wired now. **Both reject the final mean-reversion run
independently of the sample-size work** — which is the argument for wiring
gates before a result, not after.

If a gate genuinely looks wrong, the honest move is to write down the argument
and the counter-evidence, not to change the number.

## Daily-horizon assumptions NOT to inherit

The framework comes from a daily long/short book. These parts encode its
horizon and will mislead at intraday scale:

- **PIT universe** (`liquid1500_pit.csv`) — monthly, **end-exclusive**
  membership intervals, built for daily rebalancing. The intraday stack
  deliberately bypasses it via `segment_symbols`. Do not reach for it.
- `score_smoothing_days`, `rebalance_days`, `vol_lookback_days`, the 252-day
  momentum/seasonality warmup — all daily-bar constructs.
- HMM regime tagging on **daily** returns. The regime concept may transfer; the
  series it is fitted on does not.
- `claude.md`'s promotion threshold of DSR > 0.95 is stated for the daily
  stack. The intraday gauntlet adds a family-wise per-regime bar (T^K: 0.9025
  for K=2, 0.857375 for K=3). Write the fork's own `claude.md`.

## What is genuinely reusable

From the rejection notes, stated there rather than claimed here:

- **The minute vault** (63 archives, 4.2 GB, 2021-09..2026-08) and the
  **measured quote vault** (60 monthly cells, 94.4% name-day coverage). Months
  of ingest. This is data, not assumptions — it carries no horizon bias.
- **Measured NBBO spreads.** The old `spread_floor_bps: 15`/side guess was
  **~6× too conservative**: real quoted half-spread is p50 **2.4 bps**, mean
  4.6 (400 sampled fills, 400/400 returned quotes). Use the measured vault.
- `touch_cap` sizing, depth-aware impact, the priced (selection × construction)
  trial machinery, and the **`signal_ic` diagnostic** — which answers "what
  should the scanner look at" *without spending trials*. Start there.
- The ingest hardening: candidate symbols must be intersected with census
  tickers, or CUSIP/CVR junk (`0029900E0`, `004CVR049`) 400s the bars endpoint
  and the retry/bisect path stalls the run (31.3 s → 0.7 s per batch once
  fixed).

## Operational constraints that must carry over

- **Dedicated Alpaca keys.** The intraday runner requires
  `QA_ALPACA_INTRADAY__*` and refuses keys identical to the daily book's. The
  daily book's keys should be **absent** from this environment, so touching
  that account is structurally impossible rather than merely guarded.
- Credentials live only in environment variables, never in files or commits;
  secret-scan the staged diff before every commit.
- Paper only: hard-refuse any key that is not a `PK…` paper key, and always
  construct the broker with `paper=True`.

## The honest summary

Intraday ORB and intraday mean reversion on small/mid caps have both been
tested to the limit of available minute data and found to carry no persistent
edge. The infrastructure built around them — vaults, measured costs, trial
machinery, the gauntlet — is sound and worth keeping.

That means a new intraday project is not resuming a promising line. It is
starting a genuinely new one, and the four results above are the map of where
the ground has already been dug.
