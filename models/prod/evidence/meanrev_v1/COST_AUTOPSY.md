# Why the mean-reversion cost was 54 bps (meanrev_v1 cost autopsy)

The champion paid a **54.4 bps round trip** while the configured spread floor
is 5 bps/side. This decomposes it. Headline: **the Corwin-Schultz spread
estimator produced ~90% of that cost, and it is roughly 4x the real quoted
spread on the same names and days.**

## The two terms, measured

Cost per leg = `max(Corwin-Schultz/2, floor) + hydrodynamic impact`.

Corwin-Schultz FULL-spread estimate over the 185 traded names (90,352
name-days):

| p10 | p25 | p50 | p75 | p90 | mean |
|-----|-----|-----|-----|-----|------|
| 20.0 | 29.0 | **42.4** | 65.8 | 110.9 | 57.2 |

Implied half-spread charged to a marketable leg: **median 21.2 bps**.

Real NBBO half-spread at 400 actual fill timestamps on these same trades
(SIP quotes, 400/400 returned):

| p10 | p25 | p50 | p75 | p90 | mean |
|-----|-----|-----|-----|-----|------|
| 1.5 | 2.7 | **5.1** | 11.0 | 19.9 | 9.1 |

**Corwin-Schultz overstates the spread by ~4x (21.2 vs 5.1 bps at the
median).** CS assumes the daily high/low come from continuous trading under
GBM; overnight gaps and high volatility-to-spread ratios inflate it, and
gap-selected small caps are precisely its worst case.

## Impact is a rounding error in the model — and shouldn't be

The passive-vs-marketable split isolates the terms cleanly, because a passive
entry pays no spread:

| style | round-trip cost | CS estimate on the same names |
|---|---|---|
| marketable | 54.4 bps | 56.3 |
| passive | 27.3 bps | 58.3 |

The 27.1 bps difference is exactly the entry half-spread. Everything else —
the hydrodynamic impact term — is only a few bps.

That is backwards. Measured at the same fills, **our orders are a median
6.77x the displayed size at the touch, and 64% exceed it**. Orders that size
walk several price levels; the true impact is plausibly 10-20 bps/side, not
2-4. The model charges a fictional spread and almost no impact, when reality
is a modest spread and substantial book-walking.

## Correction to the earlier floor calibration

Lowering `spread_floor_bps` 15 -> 5 was reported as a meaningful cost-model
improvement. It was **cosmetic**: CS/2 exceeds the 5 bps floor on **97.5%**
of traded name-days, so the floor almost never binds. The estimator, not the
floor, sets the cost.

## What this does and does not change

- **ORB verdict: unchanged.** It failed at ZERO cost (best gross session
  Sharpe +0.024 across 60 trials). Cost was never its problem.
- **Mean reversion: the verdict is now in question.** Marketable gross was
  **+15.3 bps/trade**. Against the charged 54.4 it nets -39. Against a
  realistic 10-18 bps round-trip spread plus honest book-walking impact, the
  net is near zero to slightly positive — inside the noise, not clearly dead.
  meanrev_v1's rejection stands as recorded (all 16 adequately-active trials
  negative), but it was judged under a cost model that mispriced the dominant
  term by 4x, so it does not settle the family.

## The fix this implies

1. Replace CS with a MEASURED spread: build a per-(name, month) quoted-spread
   vault from sampled SIP quotes, mirroring the minute-vault pattern.
2. Make impact depth-aware — participation against QUOTED SIZE at the touch,
   not one minute bar's volume — so book-walking is priced where it happens.
3. Add a participation cap tied to displayed depth (our 6.77x median is a
   sizing decision, not a market fact; smaller orders cut impact bps directly
   while gross bps is size-invariant).

Ledger rows now carry `spread_bps`, `impact_bps` and `cs_spread_bps` per
trade, so no future post-mortem needs this archaeology.
