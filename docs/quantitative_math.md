# Quantum Avenger — Quantitative Methods Reference

> **Source of truth.** This is the math/rigor reference for the implemented pipeline. For architecture + status see `ARCHITECTURE_ROADMAP.md`; for remaining work see `IMPLEMENTATION_STATUS.md`. Every method below is implemented in `new_pipeline/` and **pinned to fixed numbers** in `new_pipeline/tests/golden/`, so a refactor that changes the math fails CI.

The pipeline's edge is not a single model — it is a stack of **leakage‑hygiene and multiple‑testing defenses** layered so a strategy must survive all of them before a dollar is risked. The sections follow the data's path: label → cross‑validate → weight → select → train → simulate → test significance → test overfitting → promote.

---

## 1. Labeling & target construction — `features/labels.py`

**Triple‑barrier (López de Prado), default.** For each entry bar `t` (entered at `close[t]`) three barriers race over the next `horizon` bars:

- upper / profit‑take `close[t] + pt_mult·atr[t]` (touched when `high ≥` it),
- lower / stop‑loss `close[t] − sl_mult·atr[t]` (touched when `low ≤` it),
- vertical / time at `t + horizon`.

The label is the **first‑touched** outcome: `1` if profit‑take first, `0` if stop first; at the vertical barrier `1` iff the close‑to‑close return clears `cost_bps` else `0`. Same‑bar ties resolve **conservatively to the stop**. `sl_mult` defaults to the execution `atr_stop_multiplier`, so the *label and the simulated trade share the same stop* — the model trains on outcomes the backtester can realize.

The labeller also emits **`fwd_ret`** (realized entry→first‑touch return) and **`label_t1_offset`** (bars to first touch = the per‑sample **event span** `t1`). `t1` is the keystone of the rest of the stack: overlapping label windows make samples non‑IID, and the span is what CPCV purges on (§2) and what uniqueness weights down (§3). The final `horizon` rows have no vertical window → NaN (dropped). **Friction‑aware fallback:** `1` iff the `horizon`‑bar forward return beats `cost_bps` — used when intrabar high/low/ATR are absent.

---

## 2. Cross‑validation hygiene — Combinatorial Purged CV — `tournament/cpcv.py`

A time‑ordered index is split into `n_groups` contiguous blocks; every `C(n_groups, test_groups)` combination is a test set (defaults 6/2 → **15 folds**).

- **Purge (span‑based, getTrainTimes).** With per‑sample event‑ends `t1`, a train row `i` with span `[i, t1[i]]` is dropped if it **overlaps any test block's span** — tying the purge to the *real* label horizon, not a fixed margin. `absolute_t1(offset, n, block_ids)` clamps each span to its **ticker run** (`block_end_index`), so in the ticker‑concatenated per‑sector matrix a span never crosses into another ticker. A fixed `purge` count is kept as a floor.
- **Embargo.** Train rows just after a test block are dropped (serial‑correlation leakage); window `= max(embargo, ceil(embargo_pct·n))`.
- **Combinatorial backtest paths.** The combinations reconstruct **φ = C(n_groups−1, test_groups−1)** full‑length OOS paths (`assemble_paths`): each group is tested in exactly φ combinations, so stitching one test segment per group across combinations yields φ independent paths. Their distribution (not just the averaged path) feeds the promotion gate (§10).

---

## 3. Sample‑uniqueness weighting — `tournament/sample_weights.py`

Overlapping triple‑barrier labels are **non‑IID**, so unweighted training over‑counts redundant observations and inflates the apparent sample size.

- **Concurrency** `c[b] = #{i : i ≤ b ≤ t1[i]}` — labels live at bar `b` (O(n) difference‑array).
- **Average uniqueness** `u[i] = mean_{b∈[i,t1[i]]} 1/c[b]`.
- **Training weights** = `u` normalized to mean 1, fed to the XGBoost `DMatrix`. Non‑overlapping labels (`t1 == arange`) give unit weights — the unweighted baseline exactly.
- **Sequential bootstrap** — draw probability ∝ a candidate's uniqueness given the already‑drawn set (López de Prado), for bagged / meta‑labelled resampling.

---

## 4. Feature selection & engineering — `tournament/causal_selection.py`, `features/`

**Causal feature selection (default)** — a two‑stage hybrid replacing purely correlational pruning:

- **Stage A — Granger directional screen** (`granger_pvalue`/`granger_screen`): an F‑test of each feature `→ fwd_ret` controlling for the target's own lags. `fwd_ret` over the horizon is serially overlapping, so the test is **overlap‑deflated** to `n_eff = rows/horizon` (reduces to the standard test at horizon 1). Dependent feature p‑values are **Benjamini–Yekutieli FDR‑corrected** (reuses `evaluation.haircut.multiple_testing_adjust`); survivors clear `causal_alpha`.
- **Stage B — purged‑CPCV MDA** (`purged_cpcv_mda`): Ward‑cluster the survivors, keep per cluster the feature with the highest **mean‑decrease‑accuracy averaged across the purged CPCV folds** (vs single‑split permutation). Per‑(fold,feature) seeding ⇒ thread‑stable.

Granger gives direction/causality; MDA gives robust, nonlinear, leakage‑purged importance. Empty‑screen / MDA‑prunes‑all fall back to the Granger survivors (never readmitting screened‑out decoys); a `CPCVSplitError` falls back to the correlational selector.

**Features** (`features/polars_engine.py`, `gpu_kernels.py`): arithmetic returns, **Wilder ATR**, 20‑day ADV, **annualized volatility** (rolling std × √252), 80th‑percentile **volatility‑regime** flag, high‑low **spread** + rolling mean, **Amihud illiquidity** (|ret|/(close·volume)), crash‑risk **NCSKEW / DUVOL**. CUDA kernels with NumPy CPU fallback.

---

## 5. Model objective — asymmetric financial loss — `tournament/objectives.py`

In trading a **false positive** (a buy that loses capital) costs more than a **false negative** (a missed trade). The logistic grad/hess are scaled by a per‑class penalty `Penalty(FP) = 5·Penalty(FN)`:

```
weight = where(label==0, penalty_fp=5, penalty_fn=1)
grad   = (p − y)·weight ;  hess = p(1−p)·weight
```

Because a *custom* objective bypasses XGBoost's built‑in weighting, the objective **also multiplies grad/hess by the `DMatrix` sample weights** (§3), so class asymmetry and label uniqueness compose. XGBoost ≥ 2.0, `tree_method='hist'`, `device='cuda'→cpu` fallback.

---

## 6. Backtest simulation — `tournament/simulator.py`, `features/shields.py`, `slippage.py`

**t+1, block‑wise.** Enter at `close[i]` on signal, place an ATR stop, realize on the **next** bar (stop‑out → negative risk distance; else close‑to‑close), scaled by the risk‑based size. The sim runs **independently per contiguous block** (`simulate_t1_returns_blockwise`) so a trade's exit never borrows a non‑adjacent bar across a CPCV group *or* ticker boundary — the OOS return at every group/ticker end is correctly `0`.

**Kelly sizing** (`calculate_kelly_position_size`): `size = floor(capital·max_risk / (atr_mult·atr))`, capped by affordable shares — shared by backtest and the live Shield (the central invariant; never re‑implemented).

**Dynamic hydrodynamic slippage** (`hydrodynamic_slippage_bps`) — *never* a fixed bps assumption: `S = c·σ·√(Q/V)` (`c ≈ 0.5`; `Q` order notional, `V` volume, `σ` volatility), in bps, **2× in a high‑volatility regime** (`adjust_slippage_by_regime`). It is gate 4 of the five‑gate Shield veto: (1) stop validity → (2) Kelly size ≥ 1 share → (3) liquidity ≤ `max_adv_coverage`·ADV → (4) slippage ≤ `max_slippage_bps` (default 50) → (5) portfolio reconciliation. An asymmetric `sentiment_volatility_gate` sits beside it.

---

## 7. Significance — Deflated & Probabilistic Sharpe — `evaluation/dsr.py`

Generic metrics (accuracy, raw Sharpe) are inadequate; promotion is gated on the **Deflated Sharpe Ratio**. The **PSR** is `P(true SR > benchmark)` adjusting for length + non‑normality:

`PSR = Φ((SR − SR*)·√(T−1) / √(1 − γ₃·SR + (γ₄−1)/4·SR²))` — skew γ₃, non‑excess kurtosis γ₄.

The **DSR** is PSR with `SR* =` the **expected maximum** Sharpe under `n_trials` skill‑less strategies, `E[maxSR] = σ_trials·((1−γ)·Z_{1−1/N} + γ·Z_{1−1/(Ne)})` (Euler–Mascheroni γ ≈ 0.5772) — correcting selection bias.

- **Effective trials** `N_eff = N / (1 + (N−1)·r̄)` from the mean pairwise correlation of trial OOS streams: correlated grid configs over‑deflate the raw count; `N_eff` corrects it.
- **MinTRL** — minimum track‑record length for PSR to reach a confidence. **`deflated_sharpe_report`** returns a rich `DSRResult` (DSR, PSR‑vs‑0, period/annual Sharpe, the deflation benchmark, n_obs, trials, skew, kurtosis, Lo‑2002 fallback‑variance flag). Promotion threshold: **DSR ≥ 0.95**.

---

## 8. Regime robustness — `evaluation/regime_dsr.py`, `evaluation/hmm_gauntlet.py`

**Per‑regime DSR.** A Gaussian HMM decodes regimes over `[returns, volatility, (sentiment)]`; DSR must clear the threshold in **every testable regime**, with a thin‑regime policy (skip / veto) for under‑sampled states.

**HMM synthetic gauntlet.** Fit a 3‑state `GaussianHMM`, sample a synthetic return path, run the model's signals on a **stationary block bootstrap** of feature rows (Politis–Romano — contiguous, geometrically‑sized blocks preserving *both* cross‑feature correlation *and* temporal autocorrelation; `avg_block=1` degenerates to IID), and require a positive Sharpe — a regime‑robustness gate, `gauntlet_block_size`‑tuned. (Volatility regime tagging: a rolling volatility flips to `high_vol` above the **80th percentile** of its history, shortening lookbacks toward recent action.)

---

## 9. Overfitting / multiple‑testing — `evaluation/{pbo,cscv,haircut,minbtl}.py`

- **PBO via CSCV** (`pbo.py`,`cscv.py`): over every combinatorially‑symmetric IS/OOS split take the IS‑best trial and its OOS rank logit `λ = ln(r/(1−r))`; **PBO = P(λ ≤ 0)** — the probability the selected config is no better than the OOS median. Plus performance‑degradation slope and probability of loss.
- **Haircut Sharpe** (`haircut.py`, Harvey–Liu): Sharpe → t‑stat → p‑value → **multiplicity‑inflated** p (`multiple_testing_adjust`: Bonferroni / Holm / **Benjamini–Yekutieli**) → adjusted t → discounted "haircut" Sharpe; plus the minimum profit hurdle. The BHY adjuster is reused by the Granger screen (§4).
- **MinBTL** (`minbtl.py`): minimum backtest length for the expected‑max Sharpe to be significant at the trial count; flags backtests too short to trust.

---

## 10. Promotion gate — `evaluation/promotion.py`

A candidate is promoted only if it clears **every** gate, the first failure naming the reason:

1. **DSR ≥ `dsr_promotion_threshold`** (default 0.95), deflated by `N_eff` and the trial‑Sharpe variance;
2. **synthetic Sharpe > min** (the HMM gauntlet, §8);
3. **PBO ≤ `pbo_threshold`** (§9);
4. **MinBTL satisfied** (optional);
5. **CPCV path‑distribution DSR gate** (default on): ≥ `cpcv_path_min_fraction` of the φ reconstructed paths (§2) must **individually** clear the DSR threshold — robustness beyond the single averaged path;
6. **per‑regime DSR** (optional, §8).

PSR, haircut Sharpe, PBO, the path pass‑fraction and median path DSR ride along as diagnostics in the append‑only, immutable `PromotionRegistry`.

---

## Configuration knobs (rigor‑relevant)

`features.{label_method, label_horizon, label_cost_bps, label_pt_mult, label_sl_mult}` · `tournament.{n_groups, test_groups, purge_days, embargo_days, embargo_pct, penalty_fp, penalty_fn, feature_selection_method, causal_alpha, causal_granger_lags, sample_weighting}` · `evaluation.{dsr_promotion_threshold, use_effective_trials, psr_benchmark_sr, pbo_threshold, pbo_partitions, mt_method, enforce_minbtl, regime_gate_enabled, min_regime_obs, thin_regime_policy, cpcv_path_gate_enabled, cpcv_path_min_fraction, gauntlet_block_size}`.

## Verification

`tests/golden/` pins ATR/vol/Amihud/slippage, Kelly + the 5‑gate Shield, DSR/PSR/MinTRL/haircut, CPCV folds, Granger/MDA, concurrency/uniqueness/sequential‑bootstrap, and the gauntlet output to fixed literals; unit suites add property tests (block‑bootstrap autocorrelation, span‑purge no‑overlap, no cross‑group/ticker t+1). Run `python -m pytest new_pipeline/tests/golden -q`, or the full suite with `--cov-fail-under=85`.
