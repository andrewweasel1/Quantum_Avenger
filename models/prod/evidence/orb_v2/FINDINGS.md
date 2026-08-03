# Intraday ORB: why it failed (runs orb_v1, orb_v2)

Two official runs, 78 priced trials, 262k simulated trades. Both rejected.
This note records the *mechanism*, so no future experiment re-derives it.

## It is not churn

The champion trial (`cheap_gap|k15|or_low|none`) trades:

- **6.4 positions per session**, 204 distinct names over 477 sessions
- **exactly one round trip per (session, name)** — max 1, mean 1.0, by construction
- **median hold 283 minutes** (~4.7 hours); p10 30 min, p90 365 min

This is a low-frequency, nearly all-day-hold book, not a scalper. There is no
intra-session churn to remove.

## Cost per trade is ordinary, and mostly our own floor

Round-trip cost, champion trial: median **35 bps**, p10 31, p90 57.

- **80% of trades sit within ~5 bps of the 30 bps round-trip floor** we impose
  (`spread_floor_bps: 15` per side). Only 7.5% exceed 60 bps.
- The Corwin-Schultz spread estimate binds above the floor for a minority of
  names; the hydrodynamic impact term is small at $5k notional.
- The cost-aware scanner (`cheap_gap`) already cut cost/trade 55% vs v1
  ($44.30 -> $19.80), exactly as the signal diagnostic predicted.

So cost is not exotic — it is roughly twice an assumption we chose. Whether
15 bps/side is right for depth-selected small caps is untested; the honest
upgrade is measuring real NBBO spreads at entry timestamps (Alpaca's
`StockQuotesRequest`). Worth doing for FUTURE strategies — it cannot rescue
this one (see below).

## The moves are big enough; the direction is a coin flip

- median |gross move| over the hold: **65 bps** vs 35 bps cost — the price
  travels far enough to pay the spread nearly twice over.
- mean gross: **+0.8 bps/trade**. Win rate 30%, median gross -13.5 bps,
  mean ~0: the classic positive-skew breakout shape with no expectancy.

**Zero-cost counterfactual** — gross session Sharpe of the best of all 60
trials: **+0.024** (annualized +0.39), and that is a max over 60 trials, so
the unbiased figure is lower still. *Even with trading costs set to zero,
the strategy has no edge.* No cost-model refinement, scanner weighting, or
concentration changes that.

## Conclusion

Opening-range breakouts on small/mid caps carry no directional information
at minutes-to-hours scale in this universe. Costs are a secondary, ordinary
drag. The scanner search worked — it improved cost, gross, and win rate
monotonically — and still could not manufacture an edge that isn't there.

Reusable from this work: the minute vault, the causal signal menu +
`signal_ic` diagnostic (answers "what should the scanner look at" without
spending trials), and the priced (selection x construction) trial machinery.
