# Quantum Avenger — Quantitative Methods Reference

> **Source of truth for the math.** Two parts. **Part I — the implemented rigor stack (defense):** how we *validate* a strategy so it can't be a fluke; every method is in `new_pipeline/` and pinned in `new_pipeline/tests/golden/`. **Part II — the alpha & quant toolbox (offense + candidate library):** the universe of signal‑generating and portfolio methods we can "precipitate out" into the project to raise the probability of finding alpha; each entry is tagged **[implemented]** or **[candidate]** with an integration point. For architecture/status see `ARCHITECTURE_ROADMAP.md`; candidates are tracked in `IMPLEMENTATION_STATUS.md §8`.

**Why two parts.** The edge today is *defensive* — a deep leakage‑hygiene + multiple‑testing stack (Part I). But our *offensive* surface is thin: ~11 microstructure/technical features feeding one XGBoost classifier per sector. Most alpha lives in signal families we don't yet compute. Part II is the menu; **every candidate must pass the Part I gauntlet before promotion** (see "Precipitating a method" below).

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

**Features** (`features/polars_engine.py`, `gpu_kernels.py`): arithmetic returns, **Wilder ATR**, 20‑day ADV, **annualized volatility** (rolling std × √252), 80th‑percentile **volatility‑regime** flag, high‑low **spread** + rolling mean, **Amihud illiquidity** (|ret|/(close·volume)), crash‑risk **NCSKEW / DUVOL**. CUDA kernels with NumPy CPU fallback. *(This 11‑signal set is the current alpha surface — Part II is how we widen it.)*

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

The menu for widening the signal surface. **Status:** `[implemented]` (with its Part I §/file) or `[candidate]`. **Integration point** names where it would plug in. Citations: López de Prado, *Advances in Financial ML* (AFML); Harvey–Liu; Bailey et al.

## A. Data representation & sampling *(foundational — better bars ⇒ better everything downstream)*

- **Information‑driven bars** `[candidate]` — sample by **activity, not the clock**: tick / volume / **dollar** bars, plus **imbalance** and **run** bars (AFML Ch.2). Dollar bars give the most stable counts; activity sampling makes bar returns closer to IID and partially de‑seasonalizes. *Integration:* a resampling stage upstream of `features/polars_engine.py` (new `features/bars.py`).
- **Fractional differentiation** `[candidate]` — `(1−B)^d` with fractional `d` via the binomial‑weight expansion; pick the minimum `d` that passes ADF. Raw prices are non‑stationary; returns are stationary but **memory‑less** — frac‑diff keeps maximal memory while achieving stationarity, yielding more predictive features (AFML Ch.5). *Integration:* a transform in the feature engine; emit `fracdiff_close` etc.

## B. Cross‑sectional alpha factors *(biggest gap — we compute none today; most equity alpha lives here)*

Cross‑sectionally rank each factor across the universe per date, z‑score, and **neutralize** to sector/beta; the model or a combiner consumes the ranks.
- **Momentum** `[candidate]` — 12‑1 total return (skip the last month). **Residual/idiosyncratic momentum** — momentum of CAPM/factor residuals (cleaner).
- **Short‑term reversal** `[candidate]` — −1×(last‑month return). **Time‑series momentum/trend** — sign of trailing return, asset‑by‑asset.
- **Value** `[candidate]` (B/M, E/P, FCF yield), **Quality/Profitability** (gross profitability, ROE, accruals), **Investment**, **Size**, **Low‑volatility / Betting‑Against‑Beta** (BAB).
- **Seasonality** `[candidate]` — turn‑of‑month, day‑of‑week, month, FOMC‑drift, earnings‑window effects.
- *Integration:* a cross‑sectional factor module (`features/factors.py`) joined per (date, ticker); requires a fundamentals adapter for value/quality (news/EDGAR partials exist).

## C. Statistical arbitrage / mean reversion *(a second, market‑neutral strategy family)*

- **Cointegration** `[candidate]` — Engle‑Granger (residual ADF) / **Johansen** (multivariate) to find stationary spreads; trade deviations. *Integration:* a `stat_arb` strategy alongside the directional XGBoost.
- **Ornstein‑Uhlenbeck mean reversion** `[candidate]` — fit `dx = θ(μ−x)dt + σdW`; **half‑life = ln2/θ** sets holding horizon; enter at ±zσ. 
- **PCA / eigenportfolio stat‑arb** `[candidate]` — Avellaneda‑Lee: residuals of returns on principal components mean‑revert.

## D. Volatility & options‑derived signals

- **Realized‑vol estimators** `[partial]` — we have rolling‑std vol; add **Parkinson / Garman‑Klass / Yang‑Zhang** (use OHLC, far more efficient) and **bipower variation** (jump‑robust). *Integration:* `features/polars_engine.py`.
- **Vol forecasting** `[candidate]` — GARCH / EGARCH / GJR‑GARCH (asymmetry) / **HAR‑RV** (long‑memory realized vol).
- **Options‑implied** `[candidate]` *(needs an options chain feed)* — **variance risk premium** (RV vs IV), implied **skew** and **term structure**, **gamma exposure (GEX)**, put/call ratio, IV‑surface features. Strong, lightly‑arbitraged signals where data exists.

## E. Microstructure / order‑flow alpha *(we have Amihud only)*

- **Order‑flow imbalance (OFI)** `[candidate]`, **trade signing** (Lee‑Ready / tick rule) `[candidate]`.
- **Kyle's λ** `[candidate]` — price‑impact slope `Δp = λ·signed_volume` (informed‑trading intensity).
- **VPIN** `[candidate]` — volume‑synchronized probability of informed trading (toxicity / adverse selection).
- **Roll effective spread**, **Hasbrouck information share**, **order‑book imbalance** `[candidate]`. **Amihud illiquidity** `[implemented: §4]`.
- *Integration:* features in the engine; some need tick/quote data (Alpaca trades feed).

## F. Feature transforms & denoising

- **Entropy features** `[candidate]` — Shannon / sample entropy / Kontoyiannis on the return sign or quantized series (information content of price dynamics).
- **Structural‑break / bubble tests** `[candidate]` — CUSUM, Chu‑Stinchcombe, **SADF** (Phillips‑Shi‑Yu explosive‑root test) to flag regime shifts / bubbles (AFML Ch.17).
- **Long memory** `[candidate]` — Hurst exponent / DFA. **Spectral** — wavelet / Fourier features.
- **Covariance denoising** `[candidate]` — **Random Matrix Theory / Marchenko‑Pastur** eigenvalue clipping + **detoning**; **Ledoit‑Wolf shrinkage** — clean covariance before any optimizer (AFML Ch.2; feeds §H).
- **Dimensionality** `[candidate]` — PCA / ICA / autoencoder denoising of the feature block.

## G. Labeling & feature importance *(extend Part I §1, §4)*

- **Meta‑labeling** `[candidate]` — a **secondary** model predicts whether to *act on* (and how big to size) the primary triple‑barrier signal; decouples *side* from *size*, lifts precision/F1 and cuts false positives (AFML Ch.3). Highest‑ROI extension of what we already have. *Integration:* a second classifier in `tournament/` consuming the primary's output + features.
- **Trend‑scanning labels** `[candidate]` — label by the t‑stat of the best‑fit trend over look‑forward windows (continuous, regression‑friendly).
- **Importance** — MDA `[implemented: §4]`, clustered importance `[implemented: §4]`; add **MDI**, **SFI** (single‑feature) `[candidate]`.
- **Causal** — Granger `[implemented: §4]`; add **transfer entropy** (nonlinear directed info), **double/debiased ML**, **DAG/PC‑algorithm** discovery `[candidate]` (the selector already switches on `feature_selection_method`).

## H. Signal combination & portfolio construction *(we have none — we promote one model per sector)*

- **Alpha evaluation** `[candidate]` — **Information Coefficient** (rank corr of signal vs forward return), **ICIR = mean(IC)/std(IC)**, factor decay/turnover, breadth; **Fundamental Law: IR ≈ IC·√breadth**. The right lens for ranking/sizing many signals.
- **Combination** `[candidate]` — IC‑/risk‑weighted ensembles, **factor orthogonalization** (Gram‑Schmidt / symmetric), ML stacking of alpha sleeves.
- **Optimization** `[candidate]` — mean‑variance, **Black‑Litterman**, risk parity, and **Hierarchical Risk Parity / Nested Clustered Optimization** (AFML Ch.16 — robust to the ill‑conditioned covariance that breaks Markowitz), on a denoised covariance (§F). *Integration:* a new `portfolio/` layer combining per‑sector/-factor signals into target weights.

## I. Bet sizing & risk management *(extend §6)*

- **Bet sizing from probabilities** `[candidate]` — size ∝ `(p − 0.5)` mapped through the model's predicted probability (AFML Ch.10), averaged over concurrent bets. **Fractional Kelly** `[candidate]` (full Kelly `[implemented: §6]`).
- **Volatility targeting** `[candidate]` — scale exposure to a constant ex‑ante vol. **CVaR / expected‑shortfall** optimization and **drawdown control** (the "triple‑penance" max‑DD rule) `[candidate]`.
- **Optimal execution** `[candidate]` — Almgren‑Chriss / implementation shortfall (beyond the static slippage gate).
- **Risk metrics** `[candidate]` — Sortino, Calmar, Omega, Ulcer, VaR/CVaR alongside Sharpe.

## J. Data‑snooping guards *(complement §9 as the factor count grows)*

- **White's Reality Check** / **Hansen's SPA** / **StepM** `[candidate]` — bootstrap tests for "is the *best* of N strategies truly better than the benchmark?" — the multiple‑strategy analogue to our per‑strategy DSR/PBO.
- **Strategy risk / probability of failure** `[candidate]` (AFML Ch.15); **bootstrap confidence intervals** on Sharpe; **autocorrelation‑adjusted Sharpe** (Lo) `[candidate]`.

---

## Precipitating a method into the project (discipline)

A new signal/tool is not "done" when it computes — it must survive the Part I gauntlet:
1. **Implement behind a config flag** (a feature in the engine, a label, a selector mode, a portfolio layer, or an eval gate), defaulting off.
2. **Golden‑test the formula** in `tests/golden/` (pin it to fixed numbers) + property tests.
3. **Run it through the full chain** — CPCV (span/ticker purge) → uniqueness‑weighted training → the DSR/PBO/haircut/MinBTL/per‑regime/**path‑distribution DSR** gates. A new factor that doesn't survive deflation is noise.
4. **Promote only on survival**; record diagnostics (IC/ICIR for factors) in the registry. Flip the default once validated.

## Prioritization (highest alpha‑per‑effort for our architecture)

1. **Cross‑sectional factor library (B) + IC/ICIR (H)** — our surface is microstructure‑only; this is where equity alpha concentrates.
2. **Information bars + fractional differentiation (A)** — foundational data/feature quality, fits the leakage ethos.
3. **Meta‑labeling (G)** — direct, high‑ROI extension of the triple‑barrier we already emit.
4. **Stat‑arb: cointegration / OU (C)** — a market‑neutral second strategy family.
5. **Portfolio layer: HRP/NCO + RMT/Ledoit‑Wolf denoising (H, F)** — we currently combine nothing across sectors/signals.
6. **White's Reality Check / SPA (J)** — needed once many factors are searched.

These six are tracked with acceptance criteria in `IMPLEMENTATION_STATUS.md §8`.

---

## Configuration knobs (rigor‑relevant)

`features.{label_method, label_horizon, label_cost_bps, label_pt_mult, label_sl_mult}` · `tournament.{n_groups, test_groups, purge_days, embargo_days, embargo_pct, penalty_fp, penalty_fn, feature_selection_method, causal_alpha, causal_granger_lags, sample_weighting}` · `evaluation.{dsr_promotion_threshold, use_effective_trials, psr_benchmark_sr, pbo_threshold, pbo_partitions, mt_method, enforce_minbtl, regime_gate_enabled, min_regime_obs, thin_regime_policy, cpcv_path_gate_enabled, cpcv_path_min_fraction, gauntlet_block_size}`.

## Verification

Part I `tests/golden/` pins ATR/vol/Amihud/slippage, Kelly + the 5‑gate Shield, DSR/PSR/MinTRL/haircut, CPCV folds, Granger/MDA, concurrency/uniqueness/sequential‑bootstrap, and the gauntlet to fixed literals; unit suites add property tests (block‑bootstrap autocorrelation, span‑purge no‑overlap, no cross‑group/ticker t+1). Run `python -m pytest new_pipeline/tests/golden -q`, or the full suite with `--cov-fail-under=85`. Part II candidates each arrive with their own golden + gate tests per "Precipitating a method."
