# Quantum Avenger — Quantitative Methods Reference

> **Source of truth for the math.** Two parts. **Part I — the implemented rigor stack (defense):** how we *validate* a strategy so it can't be a fluke; every method is in `new_pipeline/` and pinned in `new_pipeline/tests/golden/`. **Part II — the alpha & quant toolbox (offense + candidate library):** the universe of signal‑generating and portfolio methods we can "precipitate out" into the project to raise the probability of finding alpha; each entry is tagged **[implemented]** or **[candidate]** with an integration point. For architecture/status see `ARCHITECTURE_ROADMAP.md`; candidates are tracked in `IMPLEMENTATION_STATUS.md §8`.

**Why two parts.** Part I is the *defensive* stack — the leakage‑hygiene + multiple‑testing machinery every signal must survive. Part II began as a candidate menu when the offensive surface was ~11 microstructure features; the **top‑priority families have since shipped** (cross‑sectional factors incl. value/quality on PIT fundamentals, frac‑diff/vol‑estimator/microstructure/GARCH features, meta‑labeling, stat‑arb, the HRP/NCO portfolio layer, IC/ICIR eval, reality‑check guards) — tags below mark each entry `[implemented: file]` or `[candidate]`. **Every remaining candidate must pass the Part I gauntlet before promotion** (see "Precipitating a method" below).

---

# PART I — Implemented rigor stack (defense)

The sections follow the data's path: label → cross‑validate → weight → select → train → simulate → test significance → test overfitting → promote.

## 1. Labeling & target construction — `features/labels.py`

**Triple‑barrier (López de Prado), default.** For each entry bar `t` (entered at `close[t]`) three barriers race over the next `horizon` bars:

- upper / profit‑take `close[t] + pt_mult·atr[t]` (touched when `high ≥` it),
- lower / stop‑loss `close[t] − sl_mult·atr[t]` (touched when `low ≤` it),
- vertical / time at `t + horizon`.

The label is the **first‑touched** outcome: `1` if profit‑take first, `0` if stop first; at the vertical barrier `1` iff the close‑to‑close return clears `cost_bps` else `0`. Same‑bar ties resolve **conservatively to the stop**. `sl_mult` defaults to the execution `atr_stop_multiplier`, so the *label and the simulated trade share the same stop* — the model trains on outcomes the backtester can realize.

The labeller also emits **`fwd_ret`** (realized entry→first‑touch return) and **`label_t1_offset`** (bars to first touch = the per‑sample **event span** `t1`). `t1` is the keystone of the rest of the stack: overlapping label windows make samples non‑IID, and the span is what CPCV purges on (§2) and what uniqueness weights down (§3). The final `horizon` rows have no vertical window → NaN (dropped). **Friction‑aware fallback:** `1` iff the `horizon`‑bar forward return beats `cost_bps` — used when intrabar high/low/ATR are absent.

## 2. Cross‑validation hygiene — Combinatorial Purged CV — `tournament/cpcv.py`

A time‑ordered index is split into `n_groups` contiguous blocks; every `C(n_groups, test_groups)` combination is a test set (defaults 6/2 → **15 folds**).

- **Purge (span‑based, getTrainTimes).** With per‑sample event‑ends `t1`, a train row `i` with span `[i, t1[i]]` is dropped if it **overlaps any test block's span** — tying the purge to the *real* label horizon, not a fixed margin. `absolute_t1(offset, n, block_ids)` clamps each span to its **ticker run** (`block_end_index`), so in the ticker‑concatenated per‑sector matrix a span never crosses into another ticker. A fixed `purge` count is kept as a floor.
- **Embargo.** Train rows just after a test block are dropped (serial‑correlation leakage); window `= max(embargo, ceil(embargo_pct·n))`.
- **Combinatorial backtest paths.** The combinations reconstruct **φ = C(n_groups−1, test_groups−1)** full‑length OOS paths (`assemble_paths`): each group is tested in exactly φ combinations, so stitching one test segment per group across combinations yields φ independent paths. Their distribution (not just the averaged path) feeds the promotion gate (§10).

## 3. Sample‑uniqueness weighting — `tournament/sample_weights.py`

Overlapping triple‑barrier labels are **non‑IID**, so unweighted training over‑counts redundant observations and inflates the apparent sample size.

- **Concurrency** `c[b] = #{i : i ≤ b ≤ t1[i]}` — labels live at bar `b` (O(n) difference‑array).
- **Average uniqueness** `u[i] = mean_{b∈[i,t1[i]]} 1/c[b]`.
- **Training weights** = `u` normalized to mean 1, fed to the XGBoost `DMatrix`. Non‑overlapping labels (`t1 == arange`) give unit weights — the unweighted baseline exactly.
- **Sequential bootstrap** — draw probability ∝ a candidate's uniqueness given the already‑drawn set (López de Prado), for bagged / meta‑labelled resampling.

## 4. Feature selection & engineering — `tournament/causal_selection.py`, `features/`

**Causal feature selection (default)** — a two‑stage hybrid replacing purely correlational pruning:

- **Stage A — Granger directional screen** (`granger_pvalue`/`granger_screen`): an F‑test of each feature `→ fwd_ret` controlling for the target's own lags. `fwd_ret` over the horizon is serially overlapping, so the test is **overlap‑deflated** to `n_eff = rows/horizon` (reduces to the standard test at horizon 1). Dependent feature p‑values are **Benjamini–Yekutieli FDR‑corrected** (reuses `evaluation.haircut.multiple_testing_adjust`); survivors clear `causal_alpha`.
- **Stage B — purged‑CPCV MDA** (`purged_cpcv_mda`): Ward‑cluster the survivors, keep per cluster the feature with the highest **mean‑decrease‑accuracy averaged across the purged CPCV folds** (vs single‑split permutation). Per‑(fold,feature) seeding ⇒ thread‑stable.

Granger gives direction/causality; MDA gives robust, nonlinear, leakage‑purged importance. Empty‑screen / MDA‑prunes‑all fall back to the Granger survivors (never readmitting screened‑out decoys); a `CPCVSplitError` falls back to the correlational selector.

**Features** (`features/polars_engine.py`, `gpu_kernels.py`): arithmetic returns, **Wilder ATR**, 20‑day ADV, **annualized volatility** (rolling std × √252), 80th‑percentile **volatility‑regime** flag, high‑low **spread** + rolling mean, **Amihud illiquidity** (|ret|/(close·volume)), crash‑risk **NCSKEW / DUVOL**. CUDA kernels with NumPy CPU fallback. *(This per‑ticker core is widened by the shipped Part II families: cross‑sectional `xf_*` factors (`features/factors.py`) and the extended frac‑diff / range‑vol / microstructure / GARCH families (`features/extended.py`), both config‑gated.)*

## 5. Model objective — asymmetric financial loss — `tournament/objectives.py`

In trading a **false positive** (a buy that loses capital) costs more than a **false negative** (a missed trade). The logistic grad/hess are scaled by a per‑class penalty `Penalty(FP) = 5·Penalty(FN)`:

```
weight = where(label==0, penalty_fp=5, penalty_fn=1)
grad   = (p − y)·weight ;  hess = p(1−p)·weight
```

Because a *custom* objective bypasses XGBoost's built‑in weighting, the objective **also multiplies grad/hess by the `DMatrix` sample weights** (§3), so class asymmetry and label uniqueness compose. XGBoost ≥ 2.0, `tree_method='hist'`, `device='cuda'→cpu` fallback.

## 6. Backtest simulation — `tournament/simulator.py`, `features/shields.py`, `slippage.py`

**t+1, block‑wise.** Enter at `close[i]` on signal, place an ATR stop, realize on the **next** bar (stop‑out → negative risk distance; else close‑to‑close), scaled by the risk‑based size. The sim runs **independently per contiguous block** (`simulate_t1_returns_blockwise`) so a trade's exit never borrows a non‑adjacent bar across a CPCV group *or* ticker boundary — the OOS return at every group/ticker end is correctly `0`.

**Kelly sizing** (`calculate_kelly_position_size`): `size = floor(capital·max_risk / (atr_mult·atr))`, capped by affordable shares — shared by backtest and the live Shield (the central invariant; never re‑implemented).

**Dynamic hydrodynamic slippage** (`hydrodynamic_slippage_bps`) — *never* a fixed bps assumption: `S = c·σ·√(Q/V)` (`c ≈ 0.5`), in bps, **2× in a high‑volatility regime**. Gate 4 of the five‑gate Shield veto: (1) stop validity → (2) Kelly size ≥ 1 share → (3) liquidity ≤ `max_adv_coverage`·ADV → (4) slippage ≤ `max_slippage_bps` → (5) portfolio reconciliation. An asymmetric `sentiment_volatility_gate` sits beside it.

## 7. Significance — Deflated & Probabilistic Sharpe — `evaluation/dsr.py`

`PSR = Φ((SR − SR*)·√(T−1) / √(1 − γ₃·SR + (γ₄−1)/4·SR²))` (skew γ₃, non‑excess kurtosis γ₄). The **DSR** sets `SR* =` the **expected maximum** Sharpe under `n_trials` skill‑less strategies, `E[maxSR] = σ_trials·((1−γ)·Z_{1−1/N} + γ·Z_{1−1/(Ne)})` (Euler–Mascheroni γ ≈ 0.5772) — correcting selection bias. **`N_eff = N/(1+(N−1)·r̄)`** corrects for correlated trials; **MinTRL** gives the track length needed for confidence. Promotion threshold **DSR ≥ 0.95**.

## 8. Regime robustness — `evaluation/regime_dsr.py`, `evaluation/hmm_gauntlet.py`

**Per‑regime DSR** — a Gaussian HMM decodes regimes over `[returns, volatility, (sentiment)]`; DSR must clear the threshold in every testable regime (thin‑regime skip/veto). **HMM synthetic gauntlet** — fit a 3‑state HMM, sample a synthetic path, run the model's signals on a **stationary block bootstrap** of features (preserves cross‑feature *and* temporal autocorrelation) and require positive Sharpe.

## 9. Overfitting / multiple‑testing — `evaluation/{pbo,cscv,haircut,minbtl}.py`

**PBO via CSCV** = `P(λ ≤ 0)` over symmetric IS/OOS splits (IS‑best trial's OOS rank logit) — probability the selection is no better than the OOS median. **Haircut Sharpe** (Harvey–Liu): SR → t → p → multiplicity‑inflated p (Bonferroni / Holm / **BHY**) → adjusted SR. **MinBTL**: minimum backtest length for the expected‑max Sharpe to be significant at the trial count.

## 10. Promotion gate — `evaluation/promotion.py`

Promote only if **all** clear: (1) DSR ≥ threshold (N_eff‑deflated); (2) synthetic Sharpe > min (gauntlet); (3) PBO ≤ threshold; (4) MinBTL satisfied (optional); (5) **CPCV path‑distribution DSR gate** — ≥ `cpcv_path_min_fraction` of the φ paths individually clear DSR; (6) per‑regime DSR (optional). Diagnostics recorded in the immutable `PromotionRegistry`.

---

# PART II — Alpha & quant toolbox (offense + candidate library)

The menu for widening the signal surface. **Status:** `[implemented]` (with its Part I §/file) or `[candidate]`. **Integration point** names where it would plug in. For the *architecture and phased sequencing* that ships these candidates — the three missing axes (cross‑sectional stage, IC/ICIR alpha eval, multi‑sleeve combination) and the P0→P5 plan — see **`OFFENSE_ROADMAP.md`**. Citations: López de Prado, *Advances in Financial ML* (AFML); Harvey–Liu; Bailey et al.

## A. Data representation & sampling *(foundational — better bars ⇒ better everything downstream)*

- **Information‑driven bars** `[candidate]` — sample by **activity, not the clock**: tick / volume / **dollar** bars, plus **imbalance** and **run** bars (AFML Ch.2). Dollar bars give the most stable counts; activity sampling makes bar returns closer to IID and partially de‑seasonalizes. *Integration:* a resampling stage upstream of `features/polars_engine.py` (new `features/bars.py`).
- **Fractional differentiation** `[implemented: features/fracdiff.py]` — `(1−B)^d` with fractional `d` via the binomial‑weight expansion (truncated at `fracdiff_threshold`); keeps maximal memory while achieving stationarity (AFML Ch.5). Behind `features.extended_features` (`fracdiff`); golden‑pinned incl. an ADF assertion (log‑price −1.35 → −3.42).

## B. Cross‑sectional alpha factors *(the shipped cross‑sectional stage — `features/factors.py` behind `features.factor_set`)*

Cross‑sectionally rank each factor across the universe per date, z‑score, and **sector‑demean** (`factor_sector_neutral`); the model consumes the `xf_*` columns.
- **Momentum** `[implemented: xf_mom_12_1]` — 12‑1 total return (skip the last month). **Residual/idiosyncratic momentum** `[candidate]` — momentum of CAPM/factor residuals (cleaner).
- **Short‑term reversal** `[implemented: xf_reversal_21]` — −1×(last‑month return). **Time‑series momentum/trend** `[candidate]` — sign of trailing return, asset‑by‑asset.
- **Value / Quality** `[implemented: xf_book_to_market, xf_earnings_yield, xf_roe]` on the **point‑in‑time fundamentals layer** (`adapters/` `FundamentalsSource` fake/static/EDGAR + `data/fundamentals.py` backward as‑of join). **Investment**, **Size**, accruals `[candidate]`.
- **Low‑volatility** `[implemented: xf_low_vol]`; full **Betting‑Against‑Beta** `[candidate]`.
- **Seasonality** `[implemented: xf_seasonality]` (turn‑of‑month); day‑of‑week / FOMC‑drift / earnings‑window variants `[candidate]`.

## C. Statistical arbitrage / mean reversion *(a second, market‑neutral strategy family)*

- **Cointegration** `[implemented: tournament/stat_arb.py + johansen.py]` — Engle‑Granger pairs (residual ADF) and **Johansen** multivariate baskets (reduced‑rank VECM eigenproblem), fit in‑sample, traded out‑of‑sample, DSR‑validated per sleeve with a family reality check; behind `stat_arb.enabled` / `stat_arb.use_johansen`.
- **Ornstein‑Uhlenbeck mean reversion** `[implemented: stat_arb.py::ou_half_life]` — **half‑life = ln2/θ** sets the holding horizon; causal ±zσ entry/exit on the spread.
- **PCA / eigenportfolio stat‑arb** `[candidate]` — Avellaneda‑Lee: residuals of returns on principal components mean‑revert.

## D. Volatility & options‑derived signals

- **Realized‑vol estimators** `[implemented: features/vol_estimators.py]` — **Parkinson / Garman‑Klass / Yang‑Zhang** range estimators behind `features.extended_features` (`vol_estimators`); **bipower variation** (jump‑robust) `[candidate]`.
- **Vol forecasting** `[implemented: features/garch.py]` — **GARCH(1,1)** conditional volatility (MLE fit on a warmup window, causal variance recursion, leak‑free post‑warmup); EGARCH / GJR (asymmetry) / **HAR‑RV** `[candidate]`.
- **Options‑implied** `[candidate]` *(needs an options chain feed)* — **variance risk premium** (RV vs IV), implied **skew** and **term structure**, **gamma exposure (GEX)**, put/call ratio, IV‑surface features. Strong, lightly‑arbitraged signals where data exists.

## E. Microstructure / order‑flow alpha *(we have Amihud only)*

- **Order‑flow imbalance (OFI, bar‑level proxy)** `[implemented: features/microstructure.py]`; true **trade signing** (Lee‑Ready / tick rule) `[candidate]` (needs tick data).
- **Kyle's λ (proxy)** `[implemented: features/microstructure.py]` — price‑impact slope `Δp = λ·signed_volume` from bar data.
- **VPIN** `[candidate]` — volume‑synchronized probability of informed trading (toxicity / adverse selection).
- **Roll effective spread** `[implemented: features/microstructure.py]`; **Hasbrouck information share**, **order‑book imbalance** `[candidate]`. **Amihud illiquidity** `[implemented: §4]`.
- *All shipped entries ride `features.extended_features` (`microstructure`); the candidates need tick/quote data (Alpaca trades feed).*

## F. Feature transforms & denoising

- **Entropy features** `[candidate]` — Shannon / sample entropy / Kontoyiannis on the return sign or quantized series (information content of price dynamics).
- **Structural‑break / bubble tests** `[candidate]` — CUSUM, Chu‑Stinchcombe, **SADF** (Phillips‑Shi‑Yu explosive‑root test) to flag regime shifts / bubbles (AFML Ch.17).
- **Long memory** `[candidate]` — Hurst exponent / DFA. **Spectral** — wavelet / Fourier features.
- **Covariance denoising** `[implemented: portfolio/covariance.py]` — **Random Matrix Theory / Marchenko‑Pastur** eigenvalue clipping (`cov_method="rmt"`, default) and **Ledoit‑Wolf shrinkage** (`"ledoit_wolf"`), feeding every §H optimizer; **detoning** `[candidate]`.
- **Dimensionality** `[candidate]` — PCA / ICA / autoencoder denoising of the feature block.

## G. Labeling & feature importance *(extend Part I §1, §4)*

- **Meta‑labeling** `[implemented: tournament/meta_labeling.py]` — a **secondary** model predicts whether to *act on* the primary triple‑barrier signal (AFML Ch.3); the director records an OOS primary‑vs‑meta precision/recall/F1 verdict behind `tournament.enable_meta_labeling`. *Pending:* persisting + deploying the meta booster to size live bets.
- **Trend‑scanning labels** `[candidate]` — label by the t‑stat of the best‑fit trend over look‑forward windows (continuous, regression‑friendly).
- **Importance** — MDA `[implemented: §4]`, clustered importance `[implemented: §4]`; add **MDI**, **SFI** (single‑feature) `[candidate]`.
- **Causal** — Granger `[implemented: §4]`; add **transfer entropy** (nonlinear directed info), **double/debiased ML**, **DAG/PC‑algorithm** discovery `[candidate]` (the selector already switches on `feature_selection_method`).

## H. Signal combination & portfolio construction *(the shipped `portfolio/` layer)*

- **Alpha evaluation** `[implemented: evaluation/alpha_eval.py]` — universe‑wide rank‑**IC**, **ICIR = mean(IC)/std(IC)**, t‑stat, breadth, hit‑rate, and horizon decay per signal → `alpha_eval.json` (read‑only diagnostics; golden‑pinned). Turnover analysis `[candidate]`.
- **Combination** `[implemented: portfolio/combination.py]` — **IC/Sharpe‑weighted** ensembles alongside the optimizers; **factor orthogonalization** (Gram‑Schmidt / symmetric) and ML stacking `[candidate]`.
- **Optimization** `[implemented: portfolio/hrp.py, nco.py]` — **Hierarchical Risk Parity** (default) and **Nested Clustered Optimization** (AFML Ch.16), plus inverse‑variance and equal weights, on the §F denoised covariance; exact date‑aligned cross‑sector + stat‑arb books. Mean‑variance / **Black‑Litterman** / risk parity `[candidate]`.

## I. Bet sizing & risk management *(extend §6)*

- **Bet sizing from probabilities** `[candidate]` — size ∝ `(p − 0.5)` mapped through the model's predicted probability (AFML Ch.10), averaged over concurrent bets. **Fractional Kelly** `[candidate]` (full Kelly `[implemented: §6]`).
- **Volatility targeting** `[candidate]` — scale exposure to a constant ex‑ante vol. **CVaR / expected‑shortfall** optimization and **drawdown control** (the "triple‑penance" max‑DD rule) `[candidate]`.
- **Optimal execution** `[candidate]` — Almgren‑Chriss / implementation shortfall (beyond the static slippage gate).
- **Risk metrics** — **Sortino** `[implemented: evaluation/tearsheet.py]` (annualized, downside deviation vs a 0 target, reported beside Sharpe in `summary_metrics`); Calmar, Omega, Ulcer, VaR/CVaR `[candidate]`.

## J. Data‑snooping guards *(complement §9 as the factor count grows)*

- **White's Reality Check** / **Hansen's SPA** `[implemented: evaluation/reality_check.py]` — stationary‑block‑bootstrap tests for "is the *best* of N strategies truly better than the benchmark?"; RC is recorded per sector and **gateable** (`reality_check_gate_enabled`), and runs as the family guard inside stat‑arb validation (SPA is a library‑only alternative). **StepM** `[candidate]`.
- **Strategy risk / probability of failure** `[candidate]` (AFML Ch.15); **bootstrap confidence intervals** on Sharpe; **autocorrelation‑adjusted Sharpe** (Lo) `[candidate]`.

---

## Precipitating a method into the project (discipline)

A new signal/tool is not "done" when it computes — it must survive the Part I gauntlet:
1. **Implement behind a config flag** (a feature in the engine, a label, a selector mode, a portfolio layer, or an eval gate), defaulting off.
2. **Golden‑test the formula** in `tests/golden/` (pin it to fixed numbers) + property tests.
3. **Run it through the full chain** — CPCV (span/ticker purge) → uniqueness‑weighted training → the DSR/PBO/haircut/MinBTL/per‑regime/**path‑distribution DSR** gates. A new factor that doesn't survive deflation is noise.
4. **Promote only on survival**; record diagnostics (IC/ICIR for factors) in the registry. Flip the default once validated.

## Prioritization (highest alpha‑per‑effort for our architecture)

**Status: all six shipped** (details + pendings in `IMPLEMENTATION_STATUS.md`, "Alpha research roadmap"):

1. **Cross‑sectional factor library (B) + IC/ICIR (H)** — ✅ `features/factors.py` + `evaluation/alpha_eval.py` (incl. value/quality on PIT fundamentals).
2. **Fractional differentiation (A)** — ✅ `features/fracdiff.py`; *information bars remain a candidate* (need tick data).
3. **Meta‑labeling (G)** — ✅ `tournament/meta_labeling.py` (OOS verdict; live meta‑sizing pending).
4. **Stat‑arb: cointegration / OU (C)** — ✅ `tournament/stat_arb.py` + `johansen.py`.
5. **Portfolio layer: HRP/NCO + denoising (H, F)** — ✅ `portfolio/`.
6. **White's Reality Check / SPA (J)** — ✅ `evaluation/reality_check.py` (RC gateable).

The highest‑value *remaining* candidates: information bars, options‑implied signals (needs a chain feed), VPIN/trade‑signing (needs tick data), transfer‑entropy causal screen, bet sizing from probabilities, and drawdown‑control rules.

---

## Configuration knobs (rigor‑relevant)

`features.{label_method, label_horizon, label_cost_bps, label_pt_mult, label_sl_mult}` · `tournament.{n_groups, test_groups, purge_days, embargo_days, embargo_pct, penalty_fp, penalty_fn, feature_selection_method, causal_alpha, causal_granger_lags, sample_weighting}` · `evaluation.{dsr_promotion_threshold, use_effective_trials, psr_benchmark_sr, pbo_threshold, pbo_partitions, mt_method, enforce_minbtl, regime_gate_enabled, min_regime_obs, thin_regime_policy, cpcv_path_gate_enabled, cpcv_path_min_fraction, gauntlet_block_size}`.

## Verification

Part I `tests/golden/` pins ATR/vol/Amihud/slippage, Kelly + the 5‑gate Shield, DSR/PSR/MinTRL/haircut, CPCV folds, Granger/MDA, concurrency/uniqueness/sequential‑bootstrap, and the gauntlet to fixed literals; unit suites add property tests (block‑bootstrap autocorrelation, span‑purge no‑overlap, no cross‑group/ticker t+1). Run `python -m pytest new_pipeline/tests/golden -q`, or the full suite with `--cov-fail-under=85`. Part II candidates each arrive with their own golden + gate tests per "Precipitating a method."
