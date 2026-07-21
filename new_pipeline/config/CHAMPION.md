# Frozen champion spec — run 36a3e7abc9cb (2026-07-21)

`champion_run_body.json` is the canonical official-run body: POST it verbatim
to `/api/runs`. It reproduces the census-window Liquid-1500 Universe Long
Short candidate (`ls_calmband|combo3`): net Sharpe 1.017, every full-sample
gate green (DSR 0.998, PBO 0.27, CPCV path pass 1.00, Reality Check p 0.006,
permutation margin +1.98, 50 bps borrow + slippage paid), family-wise regime
gate 0.8570 vs the 0.857375 bar — a 0.0004 miss, pending forward data.

The spec is FROZEN: re-run it unchanged as new data accrues and let the
registry decide. Any field change makes a new experiment, not the champion.

Machine-local field: `news.vault_dir` — point `SET_ME` at a GDELT news vault
built by `scripts/ingest_news_vault` (S&P names; sentiment IC ~0, kept for
spec fidelity). Book-construction values are also the library defaults in
`defaults.yaml`; execution-context switches (run_mode, enabled flags, feeds)
live only here and in test overrides, keeping the offline suite hermetic.
