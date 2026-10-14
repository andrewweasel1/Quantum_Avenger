# Spread-floor calibration against real NBBO quotes (2026-08-03)

`intraday.spread_floor_bps` was the largest term in the intraday cost model
and was never measured — ~80% of ORB trades paid within a few bps of it, so
the rejection verdicts rested partly on a guess. This replaces the guess.

**Method.** 400 fill events sampled (seed 0) from the orb_v2 champion ledger
(`cheap_gap|k15|or_low|none`), entries and exits alike, each priced against
the SIP quote stream in the 60 s window at the fill minute
(`scripts/calibrate_spread.py`). 400/400 events returned quotes.

## Result 1 — the floor was ~6x too conservative

Quoted half-spread (bps, one side, cost vs mid):

| p10 | p25 | p50 | p75 | p90 | p95 | mean |
|-----|-----|-----|-----|-----|-----|------|
| 0.7 | 1.4 | **2.4** | 5.1 | 10.2 | 18.7 | 4.6 |

**93.5% of fills sat below the configured 15.0 bps floor.** These are
depth-selected small/mid caps, so tight quotes are not surprising in
hindsight — but the model was charging ~30 bps round trip where the quoted
market implies ~5.

Floor lowered **15.0 -> 5.0 bps** (~p75): deliberately on the pessimistic
side of the measurement, with Corwin-Schultz still binding above it for
genuinely wide names.

## Result 2 — but our orders are bigger than the touch

Depth ratio (order notional / displayed notional at the touch):

- median **3.47**, p90 **28.2**
- **59% of fills exceeded displayed size** — they would walk the book

So the quoted half-spread is a *lower bound* on realized cost at our size.
A $5k order consuming ~3.5x the touch crosses several price levels; on a
1-cent tick at $20 that alone is ~7 bps, materially more than the
hydrodynamic impact term returns at these notionals (~1.5 bps). **The impact
term is probably under-modeled for size-vs-depth**, and that is now the
weakest part of the intraday cost stack.

Not fixed here, deliberately: recalibrating impact needs realized fills to
fit against, not more assumptions. When a strategy earns paper deployment,
compare its actual fill prices to the decision-time mid and fit the impact
term to that residual.

## What this does NOT change

The ORB verdict. Both runs fail at **zero** trading cost — best gross session
Sharpe across all 60 orb_v2 trials was +0.024 (a max over 60, so biased high).
A cheaper cost model cannot rescue a strategy with no directional edge; see
`FINDINGS.md`. The calibration matters for every FUTURE intraday strategy,
which will now be judged against a measured spread rather than a 6x-inflated
assumption.
