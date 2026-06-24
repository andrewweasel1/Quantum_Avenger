# Quantum Avenger — Offense & Signal‑Integration Roadmap

> **How we widen the signal surface and combine many alphas — without loosening a single defense.** Build‑forward companion to `IMPLEMENTATION_STATUS.md` (esp. **§8 Alpha research roadmap**) and `quantitative_math.md` **Part II** (the A–J toolbox). Where §8 lists the prioritized candidates, this doc is the *architecture and sequencing* that turns them into shipped code.

**Thesis.** Our *defenses* are deep — span/ticker‑purged CPCV, uniqueness weighting, DSR/PSR/N_eff, PBO/CSCV, haircut, MinBTL, path‑distribution DSR, per‑regime gating, an immutable promotion registry. Our *offense* is thin: `build_training_frame` (`tournament/pipeline.py:47`) makes **per‑(ticker, date)** rows → `compile_features` (per‑ticker) → `FEATURE_COLS` (`tournament/pipeline.py:41`, 9–11 columns) → **one XGBoost per sector** (`tournament/director.py::run_sector_tournament`). More edge comes from *more and better signals* and from *combining* them — caught by the same gauntlet, so more searching automatically earns more deflation.

---

## The three structural gaps

| Gap | Today | Consequence |
|---|---|---|
| **No cross‑sectional axis** | Features are computed per ticker over time; nothing ranks *across* names on a date (grep: no `group_by("date")` / neutralization stage). | Most equity alpha — momentum, reversal, value, low‑vol — is *cross‑sectional* and simply can't be expressed. |
| **No per‑signal alpha measurement** | Signals are dumped into one tree; we never score a signal's standalone predictive content. | We can't *find* edge — only hope the model finds it. No IC/ICIR, no decay, no breadth. |
| **No combination / portfolio layer** | We promote isolated per‑sector models; sleeves are never combined. | No diversification across strategy families; no denoised‑covariance weighting; no multiple‑*strategy* snooping control. |

> The cross‑sectional axis also subsumes the deferred **cross‑sectional leakage** item (`IMPLEMENTATION_STATUS.md §7`): once rows are grouped per date, the same machinery hosts a cross‑sectional purge.

---

## The integration architecture

Add three axes; keep the rigor invariant.

1. **Cross‑sectional stage** — a per‑date, across‑universe rank / z‑score / sector‑(and beta‑)neutralization step the per‑ticker engine lacks. *Enables the entire factor family.*
2. **Alpha evaluation (IC/ICIR)** — measure each signal's rank‑Information‑Coefficient, **ICIR = mean(IC)/std(IC)**, decay, and breadth, so edge is *found and ranked*, not assumed.
3. **Multi‑sleeve combination** — treat each validated strategy family as a "sleeve" emitting a signal/return stream; combine into one book on a **denoised covariance** (Ledoit‑Wolf + RMT/Marchenko‑Pastur) via IC‑weighting → **HRP/NCO**.

**The invariant — every signal rides the existing stack:**
```
config flag (default-off) → golden test → CPCV span/ticker purge → uniqueness-weighted train
   → DSR / PBO / haircut / path-DSR / per-regime gate → promotion registry
```
A signal family that does not survive deflation is **dropped, not shipped**. As the signal/trial count grows, `effective_number_of_trials` rises and DSR/PBO/haircut tighten automatically; White's RC/SPA (P4) adds the multiple‑*strategy* guard.

---

## Signal taxonomy & data gating

What is buildable **now** (data surface = OHLCV + causal sentiment) vs. what needs a new adapter behind the existing `adapters/base.py` ABC + fake seam.

| Family (quant_math §) | Buildable now? | Needs |
|---|---|---|
| Information bars, fractional differentiation (§A) | ✅ price/volume | — |
| Cross‑sectional **momentum / reversal / TS‑momentum / low‑vol·BAB / seasonality** (§B) | ✅ price/volume | — |
| Realized‑vol estimators (Parkinson/Garman‑Klass/Yang‑Zhang) + GARCH (§D/§E) | ✅ OHLC | — |
| Microstructure: OFI, Roll spread, Kyle‑λ proxy, Amihud (§D) | ◐ subset from OHLCV | tick/L2 for full VPIN |
| Stat‑arb cointegration / OU (§C) | ✅ price | — |
| **Value / quality** factors (§B) | ✗ | fundamentals adapter (EDGAR) |
| Options: VRP, skew, gamma‑exposure (§D) | ✗ | options chain feed |

→ **Price‑first.** P0–P3 ship on data we already have; fundamentals/options factors (P5) land behind new adapters mirroring the Alpaca/FinBERT lazy‑import + coverage‑omit pattern (`IMPLEMENTATION_STATUS.md §3`).

---

## Phased build

Each phase = its own commit series; **config‑gated, default‑off** so the 333‑test suite stays bit‑stable until each family is flipped on after it clears the gauntlet.

| Phase | Adds | New modules | Plugs in at | quant_math / §8 |
|---|---|---|---|---|
| **P0** Enabler ✅ | Cross‑sectional per‑date stage + signal contract | `features/factors.py` | `build_training_frame` after `compile_features`; append to `FEATURE_COLS` | §B,§H / 1 |
| **P1** Feature‑level signals | Info bars, frac‑diff, price factors, vol estimators, micro subset — as columns | `features/bars.py`, `features/fracdiff.py`, `features/vol_estimators.py`, `features/microstructure.py` | `compile_features` / upstream resampler; consumed by causal selector + CPCV/DSR | §A,§B,§D,§E,§F / 1,2 |
| **P2** Alpha eval | Per‑signal IC, ICIR, decay, breadth as promotion diagnostics | `evaluation/alpha_eval.py` | called in `director` / `pipeline`; recorded via `promotion.py` | §H / 1 |
| **P3** Meta‑labeling | Secondary model: act‑on / size the triple‑barrier primary | `tournament/meta_labeling.py` | after primary in the sector loop; same CPCV/uniqueness | §G / 3 |
| **P4** Combination | Multi‑sleeve book on denoised covariance + multiple‑strategy guard | `portfolio/` pkg, `evaluation/reality_check.py` | new layer over sleeve outputs; book is itself DSR/PBO‑gated | §F,§H,§J / 5,6 |
| **P5** New families | Stat‑arb sleeve; fundamentals & options factors | `tournament/stat_arb.py`, `adapters/fundamentals_*`, `adapters/options_*` | stat‑arb → portfolio layer; new adapters behind ABC+fake | §B,§C,§D / 4 |

**P0 — Enabler (the keystone). ✅ Shipped.** `add_cross_sectional_factors(frame)` (`features/factors.py`) does `group_by("date")` then sector‑neutralizes + cross‑sectionally z‑scores across the universe; called in `build_training_frame`, names appended to `FEATURE_COLS`/`feature_cols` behind `features.factor_set` (default `[]` ⇒ off, so the suite stays bit‑stable). Factor set: `mom_12_1`, `reversal_21`, `low_vol`, `seasonality` (causal Heston‑Sadka same‑month), output columns `xf_*`. Adds the per‑date axis without disturbing per‑ticker features. Tested in `tests/unit/test_factors.py` + `tests/golden/test_factor_golden.py` (factors module 100% covered) and end‑to‑end in `tests/integration/test_offline_pipeline.py`. **Verified:** on the offline run the causal Granger + purged‑CPCV‑MDA screen *retained* `xf_low_vol` and `xf_mom_12_1` — the factors flow through and survive the gauntlet, exactly the consume‑and‑deflate goal.

**P1 — Feature‑level signals (fastest alpha).** Each family behind its own flag, golden‑tested, then auto‑consumed by `causal_selection.py` (which prunes the widened set) and the CPCV/DSR stack (which deflates the added trials). Lowest‑friction integration — widens the model's search space immediately. **Done when:** each family is golden‑pinned, frac‑diff passes an ADF stationarity assertion, and any promotion survives the gauntlet with the flag on.

**P2 — Alpha evaluation (the "finding" lens).** Score each signal's rank‑IC vs. forward return, ICIR, decay, breadth; record per‑signal IC/ICIR as promotion diagnostics so edge is *measured*. **Done when:** IC/ICIR are computed in the director run and golden‑pinned for the P0 factor set.

**P3 — Meta‑labeling.** Secondary model on the primary signal (side → size); rides the same CPCV/uniqueness/gates (the sequential‑bootstrap utility for bagged meta‑models already exists — `IMPLEMENTATION_STATUS.md §7`). **Done when:** OOS precision/F1 beat the primary alone under CPCV.

**P4 — Combination + portfolio layer.** Each family emits a signal/return stream; combine via IC‑weighting → HRP/NCO on a denoised covariance. The combined book is DSR/PBO‑gated; `reality_check.py` adds **White's Reality Check / Hansen SPA** for the multiple‑strategy search. **Done when:** the combined book's DSR ≥ the best single sleeve at lower drawdown, and a noise‑only N‑strategy universe is correctly rejected.

**P5 — Second family + data‑gated signals.** Cointegration (Johansen/Engle‑Granger) + OU half‑life as a market‑neutral sleeve into the portfolio layer; value/quality + options factors once adapters land. **Done when:** a cointegrated basket clears the gate stack and feeds the book; new adapters are mock‑tested + coverage‑omitted like the existing live adapters.

---

## Cross‑cutting — reuse, don't duplicate

- **Selection & weighting:** `tournament/causal_selection.py` (prunes the widened feature set + over‑fit guard), `tournament/sample_weights.py` (uniqueness), `tournament/cpcv.py` (φ paths).
- **Gates & registry:** the full `evaluation/` stack (`dsr.py`, `pbo.py`, `cscv.py`, `haircut.py`, `minbtl.py`, `regime_dsr.py`, `hmm_gauntlet.py`) + `promotion.py` (now also records IC/ICIR + new diagnostics).
- **Backtest & loop:** `tournament/simulator.py`, the per‑sector `director`, `StaticUniverseProvider` (cross‑sectional universe), and the adapter+fake seam for new data feeds.
- **Config surface (all default‑off):** `features.{factor_set, enable_fracdiff, bar_type}`, `tournament.enable_meta_labeling`, `evaluation.enable_reality_check`, a `portfolio.*` block.

---

## Sequencing & first increment

Order follows `§8` priority — biggest alpha‑per‑effort first:

**P0 + P1 factor library + P2 IC/ICIR** → **P3 meta‑labeling** → **P4 combination + reality‑check** → **P5 stat‑arb + data‑gated families.**

**First concrete increment (P0):** `features/factors.py` + the `build_training_frame` cross‑sectional stage + `FEATURE_COLS` wiring + a momentum / short‑term‑reversal / low‑vol / seasonality set behind `features.factor_set`, golden‑tested, run through `python new_pipeline/main.py pipeline` to confirm the causal selector and DSR gates consume and deflate the new columns.

---

## Verification & definition of done (offense)

Per phase: new modules golden‑tested in `tests/golden/`; the offline pipeline stays green with the family flag **on**; each family must clear **CPCV + DSR/PBO/haircut/path‑DSR + per‑regime** before promotion; `ruff` clean; `--cov-fail-under=85`; default‑off keeps the suite bit‑stable until each flip.

**Offense is "done"** when: a cross‑sectional factor library and ≥1 alternative strategy family (stat‑arb) each clear the gauntlet and feed a **combined book** whose deflated Sharpe beats the best single sleeve at lower drawdown — with White's RC/SPA guarding the enlarged search — and every defense above still holds, because each new signal entered through the identical config‑flag → golden‑test → CPCV → DSR → promotion path.
