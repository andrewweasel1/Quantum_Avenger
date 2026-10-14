# union_v2: the diagnosis was right, the fix worked, the conclusion is unchanged

Five scanners priced together — `attention`, `tradable`, `cheap_gap`, `union`
(v1) and `union_v2` — x 32 constructions = 160 trials, 284,656 trades. One
variable vs v5: the tiebreak below the consensus tier.

- v1 filled remaining slots by BLENDED score (the mean of all three members'
  views), which averages in the weaker rankers.
- v2 fills them from `attention`'s own ranking, so the weak scanners can ADD a
  name via unanimity but can never displace an `attention` pick with one of
  their own.

**union_v2 beat union on 30/32 constructions and still lost to `attention`.**
Not promoted; champion unchanged and bit-identical for the third run running.

## The fix is real and large

| scanner | mean session SR | best | outright wins | beats attention | net bps @ z2.5 |
|---|---|---|---|---|---|
| **attention** | **-0.0284** | **+0.0944** | **17/32** | — | **43.1** |
| union_v2 | -0.0402 | +0.0756 | 2/32 | 4/32 | 33.4 |
| cheap_gap | -0.0415 | +0.0601 | 7/32 | 11/32 | 17.7 |
| tradable | -0.0566 | +0.0757 | 6/32 | 6/32 | 24.9 |
| union (v1) | -0.0578 | +0.0706 | 0/32 | 2/32 | 25.5 |

`union_v2 > union` on **30/32**; net bps 25.5 -> 33.4. The v5 diagnosis — that
the blended tiebreak was demoting `attention`'s best idiosyncratic picks — is
confirmed by fixing exactly that and recovering ~45% of the gap.

It is still not enough. `union_v2 > best-of-others` on 2/32, and it beats
`attention` on 4/32.

## Why: consensus carries no information about WHICH attention picks are good

Net edge is almost a linear function of how much of `attention`'s book a
scanner retains:

| scanner | keeps of attention's book | net bps |
|---|---|---|
| union (v1) | 60.7% | 25.5 |
| union_v2 | 71.6% | 33.4 |
| attention | 100% | 43.1 |

The mechanism is visible directly in the ledger. Of `attention`'s 275 z2.5
events, `union_v2` dropped 78 for failing unanimity. Those 78 were worth
**42.9 net bps — indistinguishable from the 43.1 average of the book they were
removed from.**

That is the whole finding. The consensus filter is not identifying bad names;
it removes good ones at the same rate as any random cut of the same size.
Unanimity across weightings is not a quality signal ON TOP OF `attention`'s own
ranking, so every name it discards costs proportionally, and the best
achievable consensus rule is the degenerate one that discards nothing —
`attention` itself.

`union_v2` did reach 13 events no other scanner touched (names all three
scanners rate top-100 but none rates top-50). Their mean was +44.0 net bps but
-$238 in dollars: 13 events is far too thin to read, and the sign disagreement
between the per-trade and dollar-weighted views is itself a warning not to.

## Trade economics (z2.5, `open|marketable|anchor`)

| scanner | trades | sessions | gross bps | net bps | win rate | net $ |
|---|---|---|---|---|---|---|
| **attention** | 275 | 151 | 61.2 | **43.1** | 52.7% | **$5,534** |
| union_v2 | 251 | 140 | 51.9 | 33.4 | 52.2% | $4,370 |
| union | 228 | 122 | 43.4 | 25.5 | 50.9% | $3,256 |
| tradable | 222 | 126 | 44.7 | 24.9 | 49.1% | $2,099 |
| cheap_gap | 197 | 102 | 32.1 | 17.7 | 48.2% | $2,340 |

## The no-op that nearly shipped

`union_v2` requires consensus drawn from a WIDER window than the budget it
spends. Measured on the real cross-section before the run (signal ranks only,
no return data):

| pool_n | consensus core | outside attention's top-50 | v2 names new vs attention |
|---|---|---|---|
| 50 (1x) | 10.2 | **0.0** | **0.0** |
| **100 (2x)** | 39.3 | 18.4 | 14.4 |
| 150 (3x) | 82.7 | 52.4 | 18.4 |

At 1x the overlap is **exactly zero**: unanimity within each member's top-50 is
by construction a subset of `attention`'s top-50, so filling the remainder from
`attention` returns `attention`'s list reordered. A run configured that way
would have produced a bit-identical no-op while appearing in the manifest as a
fifth scanner. At 3x the consensus core (82.7) exceeds the budget, so the
"fill from attention" half of the rule never executes at all.

2x is therefore the only multiplier that implements the specified rule, chosen
structurally rather than by performance. The degeneracy is pinned by
`test_union_v2_at_pool_equal_to_budget_degenerates_to_the_primary`.

## Deflation: three runs, no cost

| run | trials | trial-SR std | DSR |
|---|---|---|---|
| v4 | 96 | 0.0870 | 0.5363 |
| v5 | 128 | 0.0868 | 0.5415 |
| v6 | 160 | — | 0.5493 |

67% more trials across two runs moved the DSR *up* slightly. Every scanner
added was a near-duplicate of trials already in the family, so effective
multiplicity barely rose. Compare v3, where a genuinely new axis (entry z)
moved DSR 0.528 -> 0.227. **A search direction that costs no deflation is not
a new search direction** — the machinery has now said this twice.

## What this settles

1. **Consensus scanning is finished.** Two designs, one a direct fix of the
   other's diagnosed flaw, both beaten by a member. The trajectory is
   monotone toward `attention` and its limit IS `attention`.
2. **`scanner_variants` stays `["attention"]`.** Unchanged from v5; v6 tested
   the alternative and confirmed it.
3. **Event rate is still the binding constraint and still unreachable by
   re-ranking.** Three runs have now varied how names are ordered within a
   fixed budget; none moved the champion. Coverage is set by `scanner_top_n`
   and by history length.

The remaining honest lever is unchanged: 478 -> ~1,200 sessions multiplies t by
1.58, giving t ~ 3.26 at the current Sharpe, which clears. It costs vault
ingest and touches no signal definition.
