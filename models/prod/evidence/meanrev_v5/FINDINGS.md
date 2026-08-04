# Union scanner: rejected on its own terms, and the coverage premise was wrong

One variable vs v4: the `union` scanner priced ALONGSIDE the three weightings
it aggregates (4 scanners x 32 constructions = 128 trials, 225,420 trades).
Pricing it against its own members rather than alone was deliberate — a
union-only run would have cut the family to 32 trials and flattered the DSR
through a smaller search, not a better scanner.

**Verdict: not promoted, and the union is not the scanner to keep.** It won
0 of 32 constructions outright and never beat the best member on any of them.

## The paired result, construction by construction

Same construction, four scanners, so scanner quality is the only thing moving:

| scanner | mean session Sharpe | best | outright wins | union beats it |
|---|---|---|---|---|
| **attention** | **-0.0284** | **+0.0944** | **19/32** | 2/32 |
| cheap_gap | -0.0415 | +0.0601 | 7/32 | 7/32 |
| tradable | -0.0566 | +0.0757 | 6/32 | 17/32 |
| union | -0.0578 | +0.0706 | **0/32** | — |

Restricted to z2.5, the level that carries the whole edge:

| scanner | mean | best |
|---|---|---|
| attention | **+0.0406** | **+0.0944** |
| cheap_gap | +0.0116 | +0.0601 |
| tradable | +0.0046 | +0.0684 |
| union | -0.0078 | +0.0706 |

`union > best-of-members` on **0/32**. The champion is bit-for-bit v4's
(`attention|touch_cap|open|z2.5|marketable|anchor`, session Sharpe 0.0944,
275 trades, 61.2 gross bps) — a clean determinism check across a config change.

## Why it lost: consensus beat the AVERAGE scanner, not the BEST one

The v4 agreement table that motivated this — 1/2/3-scanner agreement netting
17.2 / 38.6 / 34.0 bps — pooled events across all three books. "Solo" there
lumps `attention`-only picks together with `tradable`-only and `cheap_gap`-only
ones. Split by book, at z2.5 on the champion construction:

| scanner | trades | sessions | gross bps | net bps | win rate | net $ |
|---|---|---|---|---|---|---|
| **attention** | 275 | 151 | 61.2 | **43.1** | 52.7% | **$5,534** |
| union | 228 | 122 | 43.4 | 25.5 | 50.9% | $3,256 |
| tradable | 222 | 126 | 44.7 | 24.9 | 49.1% | $2,099 |
| cheap_gap | 197 | 102 | 32.1 | 17.7 | 48.2% | $2,340 |

`attention` alone nets **43.1 bps — above the 2-scanner consensus bucket's
38.6**. The agreement effect was real but it was measuring "consensus beats a
randomly-chosen scanner," which is a much weaker claim than the one the union
was built on. Requiring agreement with two weaker rankers discards
`attention`'s best idiosyncratic picks and backfills with names those weaker
rankers liked: the union shares only 167 of `attention`'s 275 events (61%) while
taking 75-76% of `tradable`'s and `cheap_gap`'s books. It lands almost exactly
where those two do (25.5 vs 24.9 / 17.7 net bps) because that is mostly what it
is holding.

## The coverage premise was a unit error

The union was also justified on event count — 438 distinct z2.5 events across
the three scanners versus 275 for the best single one, with event rate the
binding constraint on every intraday verdict since v2. **That comparison was
between three 50-name scanners and one 50-name scanner.** It is three
scanners' worth of capacity, not a property of consensus ranking.

The union is a single scanner admitting `scanner_top_n` = 50 names per session.
It selects the top 50 of a pooled candidate set; it cannot exceed the budget
every member already spends. Measured across all constructions:

| scanner | distinct (day, ticker) events |
|---|---|
| attention | 8,685 |
| **union** | **8,331** |
| cheap_gap | 8,244 |
| tradable | 8,091 |

The union sits in the middle of its members and **below** `attention`. It
widened nothing. Zero of its 228 z2.5 events fall outside the members' pool —
it invents no names, it only re-ranks, and it re-ranks worse.

The unit test written alongside it (`test_union_widens_coverage_beyond_any_
single_scanner`) passed only because it gave the union `top_n=20` against the
members' 10. It encoded the same confusion instead of catching it, and has
been renamed and re-scoped to what it actually proves — that the union draws
from more than one member's list at equal-per-member budget.

## The deflation saw it independently

Trial-Sharpe dispersion barely moved on 33% more trials (std 0.0870 -> 0.0868;
DSR 0.536 -> 0.542, eligible trials 84/96 -> 112/128). Adding 32 union trials
cost essentially nothing in deflation because they are near-duplicates of
trials already in the family — the same fact the event-overlap table shows,
arriving through the multiplicity machinery rather than the ledger.

Compare v3, where adding a genuinely different axis (entry z) moved DSR
0.528 -> 0.227. A search direction that costs no deflation is not a new search
direction.

## What this settles

1. **Streamline to `attention` alone.** It wins 19/32 constructions, holds the
   champion, and nets 43.1 bps against 17.7-25.5 for everything else. Dropping
   to one scanner cuts the trial family 4x with no loss of the champion — the
   answer to "can we reduce three scanners to one" is yes, but the one is
   `attention`, not a blend.
2. **Consensus ranking is dead as a scanner design** on this evidence. Not
   "needs tuning" — it was beaten by a member on every construction.
3. **The binding constraint is still event rate**, and it is still not
   reachable by re-ranking. Coverage is set by `scanner_top_n` and by history
   length. Nothing about how names are ordered within a fixed budget changes
   how many events exist.

The union code stays in the tree (tested, one line to enable) and is priced as
a trial if ever re-run, but it is not part of the standing spec.

## Honest limits

- The union's design (members, agreement-first ordering) was fitted on v4's
  ledger over this same window, so this run is in-sample for the union. That
  cuts against the union, not for it: a rule fitted in-sample still lost.
- The 3-vs-2 agreement inversion (34.0 vs 38.6 bps) was already flagged as
  noise on 57 and 142 events. It should have been read as a warning that the
  agreement gradient was weak, rather than absorbed into a binary rule.
