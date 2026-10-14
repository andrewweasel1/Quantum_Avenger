# Intraday mean reversion v1 — rejected, plus a harness bug worth more

48 priced trials (3 scanners x 16 constructions), 478 sessions, 4,438 trades.
Verdict: not promoted, DSR 0.768 vs the 0.95 bar.

## The reported champion was an artifact — and that is the real finding

The run crowned `tradable|vwap|z2.5|marketable|half` at session Sharpe +0.073
(+1.16 annualized), with both regimes positive (+1.41 / +1.12 annualized).
That trial made **3 trades** and was active on **0.6% of sessions**. A Sharpe
computed on 475 exact-zero sessions and 3 wins measures "three wins, no
losses", not an edge.

Champion selection is an argmax over trials, so it systematically favours the
THINNEST trial — fewer trades allow a more extreme Sharpe. The zero-trade
gate only fires at exactly zero, so nothing caught it.

**Filtering to trials that genuinely traded (>=50 trades AND >=10% of sessions
active) leaves 16 of 48, and every one is negative:**

| best qualifying | median | worst |
|---|---|---|
| -0.15 annualized | ~ -1.0 | -2.79 annualized |

So mean reversion v1 fails, cleanly, once the strategy is required to trade.
Fixed in the harness: an activity floor now gates champion eligibility, and a
run with no qualifying trial is vetoed by that reason instead of crowning an
artifact (a gate ADDED, nothing softened).

## The passive-fill thesis worked mechanically, and adverse selection ate it

Pooled across all trials:

| entry style | trades | gross bps | cost bps | net bps | win rate |
|---|---|---|---|---|---|
| marketable | 2,412 | **+15.3** | 54.4 | -39.1 | 41.9% |
| passive | 2,026 | **+2.3** | **27.3** | -25.0 | 44.4% |

Resting inside the spread did exactly what it was designed to do — **cost
halved, 54.4 -> 27.3 bps** — and the fill rate held up at 84% of the
marketable-equivalent signals. But **gross edge collapsed from +15.3 to +2.3
bps**: the trades a resting bid actually gets filled on are the worse ones.
That is adverse selection showing up precisely where theory says it should,
and it is the honest price of the cost saving. Passive still nets better
(-25.0 vs -39.1 bps) — both lose.

Cost is not near zero for passive because only the reversion TARGET exit is
passive. Exit mix: 2,943 forced closes, 791 stops, 704 targets — i.e. **66% of
trades never reverted within the session** and were flattened at the close,
crossing the spread.

## Structural read

A 1.5-2.5 prior-day-ATR stretch below the anchor is a rare intraday event:
0.19 trades/session at the wide end, and the wide-z trials are exactly the
ones too thin to evaluate. The z-threshold and the intraday horizon are
mismatched — but a smaller z is a NEW pre-registered trial set, not a tweak
to this one.

Open, untested: whether a tighter z (0.5-1.0) trades often enough to measure
while keeping a positive gross edge. The marketable +15.3 bps gross is the
one encouraging number in this run; it is currently swamped by a 54 bps
round-trip cost that the recalibrated 5 bps floor does not explain — worth
checking whether impact (known under-modeled vs displayed depth) or the
Corwin-Schultz estimate dominates that 54.
