# Mean reversion v2 on the corrected cost model — rejected, but net-positive

144 priced trials (3 scanners x 3 sizing models x 16 constructions), 478
sessions, 12,998 trades. Measured-spread coverage **92.3%** of name-days
(43,158 quote-vault cells); Corwin-Schultz fell back on the remaining 7.7%.

**Verdict: not promoted.** DSR 0.528 against the 144-trial deflated bar;
both testable regimes veto (0.833 and 0.324 vs the 0.9025 family-wise bar).

## The corrected costs flipped the SIGN, not the verdict

v1 charged 54.4 bps round trip against +15.3 bps of marketable gross, and
every adequately-active trial was negative. With measured spreads and
depth-aware impact:

| sizing | trades | avg notional | spread bps | impact bps | gross bps | **net bps** | net $ |
|---|---|---|---|---|---|---|---|
| touch_cap | 4,122 | $2,062 | 11.3 | **0.0** | 13.2 | **+1.9** | **+$23,746** |
| volume_part | 4,438 | $4,629 | 11.7 | **0.0** | 9.3 | -2.3 | +$4,272 |
| uncapped | 4,438 | $4,630 | 11.7 | **56.6** | 9.3 | -58.7 | -$113,555 |

This is the **first net-positive intraday result** in the programme. Three
things did it, and they separate cleanly:

1. **Measured spread**: 11.3-11.7 bps round trip, versus the ~54 bps
   Corwin-Schultz was charging. The estimator was the whole cost story.
2. **Impact is real and enormous when you ignore depth**: `uncapped` pays
   **56.6 bps** of book-walking — it alone destroys the strategy, and the old
   bar-volume term charged ~2 bps for the same behaviour. The v1 model was
   wrong in BOTH directions at once: fictional spread, invisible impact.
3. **Sizing is the lever**: capping inside the displayed touch eliminates
   impact entirely and turns -58.7 bps into +1.9 bps on the same signal.

Note `touch_cap` is not as starved as the partial-vault reading suggested:
median position $662, mean $2,062 (the depth distribution is bimodal — a thin
median with a deep tail). It deployed $8.5M of cumulative notional across 478
sessions, versus $20.5M for the uncapped models.

## Why it still fails

- **Edge is tiny.** +1.9 bps/trade net on ~13 bps gross. Session Sharpe
  0.063 (~1.0 annualized) for the best trial — real, but not 144-trial-DSR
  real.
- **The timing null collapsed**: margin +0.159, down from v1's +1.52. Under
  honest costs the strategy barely beats entering at random minutes, which is
  the sharpest available statement that the *entry timing* carries little.
- **Regime 1 is weak**: DSR 0.324, +0.52 annualized — the edge is concentrated
  in one regime, exactly what the family-wise gate exists to catch.
- **Halves disagree**: +0.009 then +0.089.
- 48 of 144 trials cleared the activity floor; the champion is one of them
  (73 trades), so this is not a thin-trial artifact like v1's.

## What is now established

- The intraday cost model is calibrated against measurement rather than a
  range estimator, and it prices depth. Every future intraday verdict rests
  on the corrected model.
- Execution style dominates this strategy class: the SAME signal is +$23.7k
  or -$113.6k depending only on how the order is sized against displayed
  liquidity.
- Mean reversion carries a small, real, cost-survivable edge — and not enough
  of one to clear an honest deflated bar at this trial count.

Open and untested: a tighter entry z (0.5-1.0) to lift trade counts, and
whether concentrating on the deep-touch tail (where `touch_cap` can size
meaningfully) improves the edge rather than just the capacity.
