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
| **P1** Feature‑level signals ◐ | Frac‑diff ✅, vol estimators ✅, micro subset ✅ — as columns (info bars deferred: need tick data) | `features/fracdiff.py`, `features/vol_estimators.py`, `features/microstructure.py`, `features/extended.py` | `build_training_frame` after `compile_features`; consumed by causal selector + CPCV/DSR | §A,§D,§E,§F / 2 |
| **P2** Alpha eval ✅ | Per‑signal IC, ICIR, t‑stat, breadth, hit‑rate, decay diagnostics | `evaluation/alpha_eval.py` | universe‑wide in `run_offline_pipeline` → `alpha_eval.json` | §H / 1 |
| **P3** Meta‑labeling ✅ | Secondary model: act‑on / size the triple‑barrier primary | `tournament/meta_labeling.py` | after the candidate in the sector loop; OOS verdict in the manifest | §G / 3 |
| **P4** Combination ✅ | Multi‑sleeve book on a denoised covariance + multiple‑strategy guard | `portfolio/` pkg, `evaluation/reality_check.py` | reality check over the trials in promotion; sector book in `run_offline_pipeline` | §F,§H,§J / 5,6 |
| **P5** New families ◐ | Stat‑arb sleeve ✅; fundamentals & options factors (pending data) | `tournament/stat_arb.py`, `adapters/fundamentals_*`, `adapters/options_*` | stat‑arb → portfolio layer; new adapters behind ABC+fake | §B,§C,§D / 4 |

**P0 — Enabler (the keystone). ✅ Shipped.** `add_cross_sectional_factors(frame)` (`features/factors.py`) does `group_by("date")` then sector‑neutralizes + cross‑sectionally z‑scores across the universe; called in `build_training_frame`, names appended to `FEATURE_COLS`/`feature_cols` behind `features.factor_set` (default `[]` ⇒ off, so the suite stays bit‑stable). Factor set: `mom_12_1`, `reversal_21`, `low_vol`, `seasonality` (causal Heston‑Sadka same‑month), output columns `xf_*`. Adds the per‑date axis without disturbing per‑ticker features. Tested in `tests/unit/test_factors.py` + `tests/golden/test_factor_golden.py` (factors module 100% covered) and end‑to‑end in `tests/integration/test_offline_pipeline.py`. **Verified:** on the offline run the causal Granger + purged‑CPCV‑MDA screen *retained* `xf_low_vol` and `xf_mom_12_1` — the factors flow through and survive the gauntlet, exactly the consume‑and‑deflate goal.

**P1 — Feature‑level signals (fastest alpha). ◐ Shipped (price/volume families).** Three per‑ticker families behind `features.extended_features` (default empty ⇒ off), orchestrated by `features/extended.py::add_extended_features` per ticker (no cross‑symbol bleed) in `build_training_frame`, names appended to `feature_cols`: **`fracdiff.py`** (López de Prado fixed‑width fractional differentiation — binomial weights truncated at `fracdiff_threshold`; min‑`d` stationary‑with‑memory); **`vol_estimators.py`** (Parkinson, Garman‑Klass, Rogers‑Satchell, Yang‑Zhang range vols, annualized); **`microstructure.py`** (Roll measure, Corwin‑Schultz spread, Kyle‑λ proxy). Auto‑consumed by `causal_selection.py` + the CPCV/DSR stack. **Verified:** fracdiff turns a log‑price ADF of −1.35 (non‑stationary) into −3.42 (stationary, below −2.86) at 55 lags of retained memory; the causal screen *selected* `parkinson_vol` on the offline run; all four modules 100% covered (`tests/unit/test_extended_features.py` + `tests/golden/test_extended_golden.py` + the build‑hook assertion in `tests/integration/test_offline_pipeline.py`). **Deferred:** information bars (dollar/volume/imbalance) need intraday/tick data the daily OHLCV source lacks — a tick‑data milestone; GARCH vol (iterative MLE) is a noted follow‑up to the closed‑form range estimators.

**P2 — Alpha evaluation (the "finding" lens). ✅ Shipped.** `evaluation/alpha_eval.py` scores each signal's cross‑sectional **rank‑IC** (per‑date Spearman vs. forward return, across names), **ICIR** = mean(IC)/std(IC), t‑stat (= ICIR·√n), breadth, hit‑rate, and horizon **decay** (`information_coefficient`, `evaluate_signals`, `ic_decay`, `alpha_eval_report`). Computed **universe‑wide** (not per‑sector — our sectors are too thin for a meaningful cross‑section) in `run_offline_pipeline`, written to `alpha_eval.json` and returned in the run summary, gated by `evaluation.alpha_eval_enabled` (default on; read‑only — never gates promotion, so the deviation from "via `promotion.py`" is deliberate). Thin/zero‑dispersion dates degrade to a graceful all‑zero report. Tested in `tests/unit/test_alpha_eval.py` + `tests/golden/test_alpha_eval_golden.py` (module 100% covered) and end‑to‑end in `tests/integration/test_offline_pipeline.py`. **Verified:** on the factor‑enabled offline run the IC report and decay cover `xf_reversal_21`/`xf_low_vol`; a perfect factor scores IC 1.0, pure noise ≈ 0.

**P3 — Meta‑labeling. ✅ Shipped.** `tournament/meta_labeling.py` scores a secondary model on the **fired** primary signal: the per-sector booster's `P(win) > confidence_threshold` is the primary side; a meta model trained only on the fired training bars predicts whether each fired bet is a true win, and acting only when the primary fires **and** meta `P(win) > meta_threshold` raises precision (`primary_signal`, `precision_recall_f1`, `meta_filtered_signal`, `evaluate_meta_labeling`, `run_meta_labeling`). The director (`_meta_labeling`/`_meta_fit_fn`) trains a primary on the train split, derives signals, trains the meta model with the same uniqueness weights (subset to fired bars), and records an OOS primary-vs-meta `MetaVerdict` (precision/recall/F1 + `improved`) in the candidate manifest — gated by `tournament.enable_meta_labeling` (default off), `meta_threshold`, `meta_criterion` (f1|precision). Read-only: it records the verdict, never gates sector promotion; deploying the meta booster is deferred to the live-execution wiring. Single-class fired sets / thin splits skip gracefully (None). Tested in `tests/unit/test_meta_labeling.py` + `tests/golden/test_meta_labeling_golden.py` (module 100% covered) + `tests/integration/test_meta_labeling_director.py`. **Verified:** on a noisy mixed-outcome split the director produces a well-formed verdict; on the clean synthetic offline data the primary fires only on certain winners (single-class) so meta correctly skips.

**P4 — Combination + portfolio layer. ✅ Shipped.** Two pieces. (1) `evaluation/reality_check.py` — **White's Reality Check** + **Hansen's SPA** (shared stationary block bootstrap over the common time index, reusing `hmm_gauntlet.stationary_bootstrap_indices`): a multiple‑*strategy* p‑value for "the best of the searched trials beats the benchmark", wired into `_evaluate_and_promote` over the per‑sector `returns_matrix` (the aligned trial set) and recorded in the promotion registry as a ride‑along diagnostic, behind `evaluation.reality_check_enabled` (default off — bootstrap cost). (2) `portfolio/` package — `denoise_covariance` (RMT/Marchenko‑Pastur, dep‑free) + `ledoit_wolf_covariance` (sklearn) clean the covariance; `hrp_weights` (Hierarchical Risk Parity: correlation‑distance clustering → quasi‑diagonalization → recursive bisection) / `inverse_variance_weights` / equal‑weight allocate; `combine_returns` builds the book. `run_offline_pipeline` combines the per‑sector champion streams into `portfolio.json` (behind `portfolio.enabled`, default on). **Verified:** a genuinely skilled best‑of‑20 strategy scores RC p≈0.003 vs ≈0.7 for noise; RMT denoising cuts an N≈T condition number ~6×; HRP weights sum to 1 with lower‑vol sleeves weighted up; modules 100% covered (`tests/unit/test_reality_check.py`, `test_portfolio.py` + golden + `tests/integration/test_offline_pipeline.py`). **Alignment caveat:** the per‑sector champion streams are only approximately contemporaneous, so the cross‑sector book truncates to a common length — a best‑effort diagnostic; exact calendar alignment lands with date‑indexed sleeves (P5). NCO and IC‑weighting are noted follow‑ups (HRP + inverse‑variance shipped).

**P5 — Second family + data‑gated signals. ◐ Stat‑arb shipped.** `tournament/stat_arb.py` is a market‑neutral cointegration family: `adf_tstat` (self‑contained augmented Dickey‑Fuller, no statsmodels), `engle_granger` (OLS hedge ratio → ADF on the residual spread → `CointegrationResult`), `ou_half_life` (AR(1) decay), `mean_reversion_returns` (causal rolling‑z‑score entry/exit, position from t‑1 earns Δspread at t), `find_cointegrated_pairs`. `run_offline_pipeline._run_stat_arb` pivots the close panel, finds within‑sector cointegrated pairs, trades each spread, and combines the **date‑indexed** sleeves into a stat‑arb book via the P4 portfolio layer (exact HRP — no truncation), writing `stat_arb.json`, behind `stat_arb.enabled` (default off — new family). **Verified:** recovers a hedge ratio of 2.0 (±0.1) on a synthetic cointegrated pair (ADF ≈ −4.6, half‑life ≈ 6, strategy Sharpe ≈ 1.8), rejects independent random walks, and `_run_stat_arb` finds the planted within‑sector pairs and combines a book; module 100% covered (`tests/unit/test_stat_arb.py` + golden + `tests/integration/test_stat_arb_pipeline.py`). **Pending (data‑gated):** value/quality + options factors once `adapters/fundamentals_*` / `adapters/options_*` land (mock‑tested + coverage‑omitted like the existing live adapters); Johansen multivariate baskets are a noted follow‑up to the Engle‑Granger pairs.

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
