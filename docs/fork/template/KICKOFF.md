# Kickoff: the first session

You are opening the intraday project. Everything you need is in this
repository; you have no access to the daily long/short project it was forked
from, and you do not need any.

The owner's charter, decided 2026-11-16, is in `claude.md`. In one line:
**research first, starting from the learned-model plan, and a "no" is a valid
deliverable.**

## Step 0 — orient and verify (do this before building anything)

1. Read, in order: `claude.md`, `docs/fork/INTRADAY_HANDOVER.md`,
   `docs/intraday_learned_model_plan.md`, `docs/fork/MANIFEST.md`.

2. **Check whose account you are holding.** This is the one hazard that no
   code in this repository can catch for you:

   ```
   python3 - <<'PY'
   import os
   from alpaca.trading.client import TradingClient
   k = os.environ.get("QA_ALPACA__API_KEY", "")
   assert k.startswith("PK"), "not a paper key — stop"
   c = TradingClient(k, os.environ["QA_ALPACA__SECRET_KEY"], paper=True)
   a = c.get_account()
   print("account", a.account_number, "| equity", a.equity,
         "| open positions", len(c.get_all_positions()))
   PY
   ```

   The dedicated intraday account is new: it should hold **no positions**.
   The daily book's account holds several hundred. If you see positions, or
   the keys are missing, **stop and tell the owner** — this session was opened
   in the wrong environment. Otherwise show the owner the account number once
   and ask them to confirm it is the intraday paper account.

3. Confirm the tree is sound: `make lint` and `make test` (the fence test
   proves the gauntlet is the one that produced every prior verdict).

4. Prove the pipeline runs end to end on real data. Restore two months of the
   vault and run the inherited book over one of them:

   ```
   bash new_pipeline/scripts/restore_minute_vault.sh <scratch> 202606 202607
   QA_INTRADAY__VAULT_DIR=<scratch>/minute_vault \
     python3 -m new_pipeline.intraday.run \
       --start 2026-07-01 --end 2026-07-31 --output-dir <scratch>/smoke
   ```

   The session hook exports `QA_DATA__UNIVERSE_PATH`; if the run refuses with
   "0 symbols", that variable is what is missing, and the message says so.
   Run it detached (it outlives a foreground call). The exact output this
   produced at fork time is recorded in `docs/fork/MANIFEST.md`; yours should
   match. It runs the REJECTED mean-reversion book — this is a plumbing check,
   not a result, and its verdict will be "not promoted".

5. Report to the owner what you found, including anything that did not match.

## Step 1 — the first milestone: the event-level IC check, alone

Plan §6: build Phase 1 plus a minimal feature set and run the event-level IC
check **before investing in anything else**. It is the cheapest falsifiable
read on whether any signal exists.

Order of work, and the order matters:

1. **Pre-register first.** Before computing a single label, commit a file
   that fixes: the candidate generators and their exact (loose) parameters,
   the label definition, the minimal feature list with each feature's as-of
   minute, the fold scheme, and the kill criteria from plan §5. Put it to the
   owner for sign-off with an option card. Nothing after this step may quietly
   change it.
2. Build the event panel `(session_date, ticker, decision_minute)` with
   net-of-cost labels produced by the EXISTING cost path.
3. Build the minimal causal features, each tested on a hand-built session.
4. Session-grouped CPCV; a test asserting no session is in both train and
   test of any fold.
5. Compute OOS rank-IC of the model score against the net outcome, by
   session, and report it against the pre-registered bar (t-stat over 3).

## What done looks like

A report that states the IC, its t-stat across sessions, the split at
2024-09-01, the number of axes searched and the resulting
`prior_trials_searched` (starting from 776), with the tearsheet image — and a
plain statement of whether the kill criterion fired. If it fired: stop, say
so, and propose what (if anything) is worth trying next. Do not tune.

## What not to do in this milestone

- Do not build a live trading loop, a paper session, or anything that can
  place an order.
- Do not edit `new_pipeline/evaluation/`, its pins, or a gate threshold.
- Do not revive opening-range breakout, rule-based mean reversion, or a
  consensus/union scanner. The handover explains why with numbers.
- Do not tighten a generator after seeing outcomes without counting it.

## Open questions the owner has NOT decided (ask with cards when they bite)

- **Universe.** The vault covers the Small Cap Extended and Mid Cap Extended
  segments only (2,634 symbols); there is no large-cap minute data. Staying
  there is the default. A large-cap or mixed approach needs new ingestion.
- **LLM fusion.** Out of scope until the owner asks for it.
- **Live runtime.** Deliberately undecided until something is promoted.
- **The static base is not point-in-time** (see the handover). Decide
  deliberately whether the learned model keeps that approximation.
