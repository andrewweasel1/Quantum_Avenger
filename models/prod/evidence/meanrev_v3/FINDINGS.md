# Tighter entry thresholds: hypothesis refuted, cleanly

96 priced trials (3 scanners x 32 constructions), touch_cap sizing only,
entry z extended to [0.5, 1.0, 1.5, 2.5] prior-day ATRs. 45,858 trades —
3.5x v2's 12,998. **Not promoted: DSR 0.227**, regimes veto at 0.649/0.176.

## Sample was NOT the binding constraint — the edge was

The premise was that v2 failed on sample (0.19 trades/session), not on edge.
The data says the opposite, monotonically:

| entry z | trades | per session/trial | gross bps | net bps | win rate |
|---------|--------|-------------------|-----------|---------|----------|
| 0.5 | 32,088 | 2.80 | **-10.6** | -17.9 | 58.0% |
| 1.0 | 9,648 | 0.84 | -5.4 | -15.0 | 49.9% |
| 1.5 | 3,476 | 0.30 | +9.4 | -1.5 | 50.7% |
| 2.5 | 646 | 0.06 | **+33.5** | **+20.4** | 47.2% |

Session Sharpe tells the same story — every z0.5 trial is negative (best
-0.063), while z2.5 holds the best (+0.088):

| z | best | median | worst |
|---|------|--------|-------|
| 0.5 | -0.063 | -0.115 | -0.156 |
| 1.0 | +0.051 | -0.066 | -0.103 |
| 1.5 | +0.070 | +0.020 | -0.011 |
| 2.5 | +0.088 | +0.027 | -0.041 |

**Trading 50x more often destroyed the edge rather than measuring it better.**
The signal is a genuine rare-event phenomenon: only extreme dislocations
revert profitably enough to pay even an 11 bps round trip.

The z0.5 row is the instructive one — a **58% win rate with -10.6 bps gross**.
Many small wins, occasional large losses: the classic mean-reversion failure
mode, catching small bounces and getting run over by the moves that keep
going. A win rate is not an edge.

## Why the DSR fell while the champion stayed identical

The champion is bit-for-bit v2's: `attention|touch_cap|open|z2.5|marketable|half`,
session Sharpe 0.0633, gross 43.1 bps, 73 trades — a useful determinism check
across a config change.

Yet DSR dropped 0.528 -> 0.227 on FEWER trials (96 vs 144). That is the
deflation working correctly: adding a spread of poor trials widens the trial-
Sharpe variance, which raises the SR0 hurdle. Searching more costs more, even
when the winner is unchanged. 64 of 96 trials cleared the activity floor.

Timing-null margin unchanged at +0.159 — the extra sample did not restore it.
Under honest costs the entry rule still barely beats random entry timing.

## What this establishes

Mean reversion on small/mid caps carries a real, cost-survivable edge **only
at rare extremes** (~0.06 trades/session/trial at z2.5, +20.4 bps net). The
binding constraint is the EVENT RATE, and it cannot be relaxed by lowering the
threshold — that trades a different, worse population.

The remaining lever is therefore more of the rare event, not a looser
definition of it: a wider universe (beyond 2,535 extended-cap names), a longer
history (beyond 24 months), or admitting more names per session at z2.5 rather
than the top-10 scanner cut. All three raise event count while holding the
signal definition fixed — the opposite of what this run tried.
