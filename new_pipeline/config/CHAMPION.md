# Frozen champion spec — runs a4889768320e + fc80f05205b3 (re-frozen 2026-07-23)

`champion_run_body.json` is the canonical official-run body: POST it verbatim
to `/api/runs`. It is the census-window Liquid-1500 Universe Long Short book
with per-date causal market-state features (`features.market_state_features`),
the first spec ever to clear the FULL gauntlet — and it did so in two
consecutive independent runs:

| run           | calm s0 DSR | s1     | s2     | net SR | verdict              |
|---------------|-------------|--------|--------|--------|----------------------|
| a4889768320e  | 0.8672      | 0.9733 | 0.9617 | 0.998  | promoted, true alpha |
| fc80f05205b3  | 0.8577      | 0.9751 | 0.9645 | 1.000  | promoted, true alpha |

Family-wise per-regime bar 0.857375 (0.95^3); full-sample gates in both runs:
DSR ~0.998, PBO 0.004, CPCV path pass 1.00, Reality Check p 0.004, permutation
margin +1.9, 10 bps + slippage + 50 bps borrow paid. The previous frozen spec
(run 36a3e7abc9cb, no market-state features) missed the calm state at 0.8570.

Mechanism, replicated exactly in both runs: the causal screen selects
`mkt_vol_pctl_252`/`mkt_trend_pctl_252` only in the extended-cap books
(small-cap both, mid-cap trend, GICS sectors none); their cross-sectional IC
is degenerate by construction (per-date constants) — the value is interaction
context inside the trees. Label horizon stays 21d: the 5d-label experiment
(run 27bfe9f35cb0) selected reversal features 13/13 but the book collapsed
(net 0.22, calm-state SR -3.9 ann) — the slow construction is the edge's home.

Construction: `ls_calmband` (top/bottom 20%, 5d rebalance + smoothing, 0.5
band, calm 1.5/10d, 5% vol target). Its sibling `ls_calmboth` traded argmax
places with it across the two runs within refetch noise (±0.01 net); the
frozen construction is retained — a flip on noise is not a spec change.

The spec is FROZEN as of 2026-07-23 (forward clock restarted): re-run it
unchanged as new data accrues and let the registry decide. Any field change
makes a new experiment, not the champion.

Machine-local field: `news.vault_dir` — point `SET_ME` at a GDELT news vault
built by `scripts/ingest_news_vault` (sentiment IC ~0, kept for spec
fidelity). Book-construction values and the market-state flag are also the
library defaults in `defaults.yaml`; execution-context switches (run_mode,
enabled flags, feeds) live only here and in test overrides.
