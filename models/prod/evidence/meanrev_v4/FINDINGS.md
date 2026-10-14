# Scanner top-50: the event-rate lever works

One variable vs v3: `scanner_top_n` 10 -> 50. 96 priced trials, 169,048 trades
(v3: 45,858). **Not promoted — DSR 0.536 vs the 0.95 bar — but every metric
improved, and for the reason predicted.**

## More names bought events without buying worse trades

| entry z | trades v3 -> v4 | per session/trial | gross bps v3 -> v4 | net bps v3 -> v4 |
|---------|-----------------|-------------------|--------------------|------------------|
| 0.5 | 32,088 -> 113,504 | 2.80 -> 9.89 | -10.6 -> -8.1 | -17.9 -> -16.3 |
| 1.0 | 9,648 -> 38,838 | 0.84 -> 3.39 | -5.4 -> +1.5 | -15.0 -> -8.7 |
| 1.5 | 3,476 -> 13,962 | 0.30 -> 1.22 | +9.4 -> +10.3 | -1.5 -> -1.3 |
| **2.5** | **646 -> 2,744** | **0.06 -> 0.24** | **+33.5 -> +30.9** | **+20.4 -> +18.5** |

The z2.5 event count scaled **4.2x** on a 5x name expansion, and per-trade edge
degraded only ~8% (+33.5 -> +30.9 gross). The deeper scanner ranks are less
tradable, but touch_cap sizing absorbs that automatically — median position
falls from $871 at z0.5 to $421 at z2.5, sizing each name to its own displayed
depth rather than a fixed notional.

The z-monotonicity from v3 survives intact: edge still rises with the
threshold, at every level.

## Champion, and why the numbers moved

`attention|touch_cap|open|z2.5|marketable|anchor`

| | v3 | v4 |
|---|---|---|
| session Sharpe | 0.0633 | **0.0944** (~1.50 annualized) |
| trades | 73 | **275** |
| gross bps/trade | 43.1 | 61.2 |
| cost share of gross | 3.9% | 7.0% |
| DSR (96 trials) | 0.227 | **0.536** |
| regime 0 / 1 DSR | 0.649 / 0.176 | **0.684 / 0.496** |
| regime Sharpes (ann.) | +1.73 / +0.52 | **+1.76 / +1.46** |
| timing-null margin | +0.159 | +0.189 |
| PBO | 0.139 | 0.238 |
| eligible trials | 64/96 | 84/96 |

**Both regimes are positive for the first time** (+1.76 / +1.46), and regime 1 —
the weak one that vetoed every previous run at 0.176 — nearly tripled to 0.496.
Session Sharpe rose 49% because more concurrent names diversify each session's
return, not because per-trade edge improved.

## The concurrency cap is now binding — at the levels that don't matter

`max_concurrent` = 15, and 11.7% of (trial, session) cells sit exactly at it.
That truncation is concentrated at z0.5 (9.89 events/session/trial, so the tail
routinely exceeds 15). At z2.5 the rate is 0.24/session — the cap never binds
on the configuration that carries the edge. Left at 15 and disclosed rather
than tuned.

## What it would take to clear the bar

The champion's session Sharpe of 0.0944 over 478 sessions gives t ~ 2.06.
Clearing a 96-trial deflated bar needs roughly t > 3.

Two independent routes, and the arithmetic favours the second:

1. **More names.** Session Sharpe rose 0.063 -> 0.094 going 10 -> 50. A further
   widening (top-100+) plausibly reaches ~0.11-0.12 through diversification —
   helpful, not decisive on its own.
2. **More sessions.** t scales with sqrt(n_obs) directly. Extending history
   from 478 to ~1,200 sessions (5 years) multiplies t by 1.58: at the CURRENT
   Sharpe that is t ~ 3.26, which clears. This is now the highest-value lever,
   and it costs vault ingest rather than any change to the strategy.

Combining both is the obvious play, and neither touches the signal definition —
which is what makes them honest extensions rather than a search for a better
number.
