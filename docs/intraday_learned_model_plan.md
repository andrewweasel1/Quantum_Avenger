# Plan: fold the intraday book into the full selection model

Status: proposed, not started. Written after meanrev_v7 refuted the rule-based
mean-reversion book (see `models/prod/evidence/meanrev_v7/FINDINGS.md`).

## 1. What "working" has to mean, numerically

`minimum_profit_hurdle` at 1,233 sessions, BHY, 5%:

| trials priced | min annualized SR | implied t | session SR |
|---|---|---|---|
| 32 | 1.605 | 3.55 | 0.1011 |
| 200 | 1.851 | 4.09 | 0.1166 |
| 776 | 2.008 | 4.44 | 0.1265 |
| 2,000 | 2.110 | 4.67 | 0.1329 |
| **v7 actual** | **0.913** | **2.02** | **0.0575** |

Two things follow, and they set the whole strategy of this plan:

1. **Multiplicity is cheap.** 32 -> 2,000 trials raises the bar only 31%
   (1.61 -> 2.11 annualized). A wide, honest search costs remarkably little.
2. **Effect size is everything.** We are at 0.91 and need ~1.9 — roughly 2x.
   No refinement of the existing book closes that. Only a materially
   different signal does.

So: search wide, but only over mechanisms that could plausibly double the
effect. Tuning thresholds on a 0.91 strategy is the futile direction, and
that is exactly what v3-v6 spent their budget on.

## 2. What this plan is, and is not

**Is:** replacing hand-specified scanners and entry rules with a learned model
that goes through the same machinery as the daily stack — causal feature
screen, CPCV, OOS probabilities, full gauntlet. Signals and scanner weights
become *discovered* rather than *assumed*.

**Is not:** a rescue of mean reversion. v7 established that the specific
phenomenon (rare-extreme reversion to VWAP/open) has no persistent edge — five
of six years flat or negative, the whole result in 145 sessions of 2026. A
learned model is a NEW bet that other intraday structure exists and the
rule-based form could not express it. If that bet is wrong, this plan should
fail fast and say so.

**Bonus:** a trained model makes the CPCV path gate applicable for the first
time, closing the last disclosed gap between the intraday and daily gauntlets.

## 3. Architecture

### Phase 1 — Event panel and net-of-cost labels

The row unit is a **candidate event**: `(session_date, ticker, decision_minute)`.
Not one row per bar (24M rows, mostly noise) and not one per session (throws
away timing).

Candidates come from a **pre-registered generator set**, deliberately broader
than v1-v7's single family so the model has real hypotheses to choose between:

- reversion: |price - anchor| > k*ATR (the v7 family, k deliberately LOOSE)
- breakout: range expansion past the opening range / prior-day high-low
- gap behaviour: continuation vs fade after an opening gap
- volume shock: bar volume >> typical-at-this-minute
- VWAP cross: first cross of session VWAP after N minutes

Loose triggers on purpose: the generator's job is recall, the model's job is
precision. Target ~20-60 candidates per session (~25k-75k rows over 1,233
sessions) — enough to train, small enough to simulate.

**Label** = net-of-cost outcome of the trade that would follow, produced by the
EXISTING `run_session` machinery (measured spread, depth-aware impact,
touch_cap sizing, calendar-aware flatten). Triple-barrier in intraday time:
target / stop / forced flatten. Labelling through the real cost model is
non-negotiable — a gross-return label teaches the model to trade expensive
names.

### Phase 2 — Features, causal at the DECISION MINUTE

Three blocks, all computable from information available at that minute:

- **Intraday state**: distance from session VWAP and open in prior-day-ATR
  units, realized vol so far, elapsed-session fraction, volume vs the typical
  profile *for that minute of day*, current spread vs the name's typical,
  a bar-level order-flow proxy (close position within the bar's range,
  volume-weighted).
- **Cross-sectional, within-date only**: percentile ranks of the above across
  that session's candidates. Within-date is what makes them non-leaking.
- **Daily context**: the ten existing `scanner.SIGNALS` — gap, RVOL, ADV,
  price, ATR%, range%, spread, 5d return, idiosyncratic gap — now entering as
  *features* rather than a hand-weighted score. **This is how the scanner gets
  learned.**

### Phase 3 — Selection and CPCV

- Causal Granger screen (`tournament/causal_selection.py`) on the event panel,
  BHY-adjusted, exactly as the daily stack.
- CPCV with **session-level grouping**: every event in a session goes to the
  same fold. Same-session events are strongly dependent; splitting them across
  train/test is the leak that would make this whole exercise a fiction.
- Purge and embargo in session time around each test fold.
- Uniqueness weights for concurrent/overlapping events (`sample_weighting`).
- XGBoost -> per-fold OOS probabilities, stitched into paths.

### Phase 4 — Book construction

The model's OOS probability of a profitable net trade **replaces both the
scanner and the entry rule**: rank each session's candidates by predicted net
edge, take the top-K subject to `max_concurrent`, size by `touch_cap`. There is
no weighting left to hand-pick — which is the direct answer to "find the
signals and scanners needed".

### Phase 5 — The full gauntlet, now complete

DSR with N_eff, PBO, PSR, haircut (with `prior_trials_searched` set honestly),
White's Reality Check, family-wise per-regime gate, timing null, activity
floor — **plus the CPCV path gate**, applicable for the first time.

## 4. Leakage hazards, ranked

These are where this plan most plausibly produces a beautiful, false result.

1. **Session-level fold grouping.** Without it, a model can memorize a
   session's character from its own events. Highest-risk item; pin with a test
   asserting no session appears in both train and test of any fold.
2. **Decision-minute causality.** A feature using session VWAP at 15:00 is not
   available to a 10:00 entry. Every feature needs an explicit as-of minute,
   tested on a hand-built session.
3. **Cross-sectional features computed on the full sample.** Must be
   within-date. The existing scanner does this correctly; the event panel must
   too.
4. **Label cost model drift.** The label and the backtest must use the *same*
   cost path, or the book will look better than anything tradeable.
5. **Candidate generator tuned on outcomes.** The generator is pre-registered
   and LOOSE; tightening it after seeing results is a hidden search axis and
   must be counted in `prior_trials_searched` if ever done.

## 5. Kill criteria, pre-registered

Stated before any result, so they cannot be renegotiated afterwards:

- **Event-level signal.** If OOS rank-IC of the model score against net outcome
  is not clearly > 0 (say a t-stat over 3 across sessions), stop. No book
  construction can manufacture edge the score does not have.
- **Effect size.** If the best OOS book lands below ~1.6 annualized on the full
  1,233 sessions, it cannot clear even a 32-trial haircut. Stop rather than
  search for a variant.
- **Time stability.** Pre-registered split at 2024-09-01. If performance is
  again concentrated in one sub-period — as it was in v7, where 2026 carried
  103% of lifetime profit — stop. This is the check v1-v6 never ran and it is
  the one that mattered.
- **Trial accounting.** Every axis searched gets counted into
  `prior_trials_searched`. The hurdle table shows this costs little; hiding it
  costs credibility.

## 6. Sequencing

Phases 1-2 are the real work (event panel, labels, causal features). Phase 3
mostly reuses existing machinery. Phase 4 is small. Phase 5 is already built.

Recommended: build Phase 1 + a minimal feature set, and run the **event-level
IC check alone** before investing in the rest. That is a cheap, early,
falsifiable read on whether any signal exists — and if it says no, the plan
stops there having cost days rather than weeks.
