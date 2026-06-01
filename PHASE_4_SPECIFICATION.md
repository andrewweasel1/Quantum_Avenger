# Phase 4: Statistical Evaluation & Model Promotion - Detailed Specification

**Duration**: 2 weeks  
**Target Date**: Complete by mid-July (after Phase 3)  
**Success Criteria**: DSR computation validated; HMM synthetic tests passing; promotion gates working; 85%+ test coverage

---

## 1. Phase 4 Architecture Overview

### 1.1 System Context (Integration with Phases 1-3)

```
┌────────────────────────────────────────────────────────────┐
│  PHASES 1-3 (Complete): Infrastructure, Features, Training│
├────────────────────────────────────────────────────────────┤
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PHASE 4: STATISTICAL EVALUATION & MODEL PROMOTION  │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │                                                      │  │
│  │  LAYER 1: CANDIDATE REGISTRY LOADING                │  │
│  │  ├─ Read {sector}_candidate.json models             │  │
│  │  ├─ Read {sector}_candidate_features.json           │  │
│  │  ├─ Load returns_matrix_{sector}.parquet (OOS rets) │  │
│  │  └─ Load benchmark_{sector}.parquet (bench rets)    │  │
│  │                                                      │  │
│  │  LAYER 2: DEFLATED SHARPE RATIO (DSR)              │  │
│  │  ├─ Bailey & Lopez de Prado framework               │  │
│  │  ├─ Adjust for skewness, kurtosis                   │  │
│  │  ├─ Control for multiple testing bias               │  │
│  │  ├─ Compute DSR percentile (0-1)                    │  │
│  │  └─ Threshold: DSR ≥ 0.95 (99.5th percentile)      │  │
│  │                                                      │  │
│  │  LAYER 3: SYNTHETIC GENERALIZATION VALIDATION       │  │
│  │  ├─ Fit 3-state GaussianHMM to benchmark returns   │  │
│  │  ├─ Extract regime parameters (means, transitions)  │  │
│  │  ├─ Generate synthetic returns (Monte Carlo)        │  │
│  │  ├─ Bootstrap features (destroy temporal order)     │  │
│  │  ├─ Infer on synthetic → calculate Sharpe          │  │
│  │  └─ Verify synthetic_sr > 0 (true alpha, not luck) │  │
│  │                                                      │  │
│  │  LAYER 4: PROMOTION DECISION LOGIC                  │  │
│  │  ├─ If DSR ≥ 0.95 AND synthetic_sr > 0:            │  │
│  │  │   ├─ PROMOTE: candidate → champion              │  │
│  │  │   ├─ Generate HTML tearsheet                     │  │
│  │  │   └─ Register in champion registry               │  │
│  │  └─ Else: REJECT (log reason, cleanup)              │  │
│  │                                                      │  │
│  │  LAYER 5: AUDIT TRAIL & REPORTING                  │  │
│  │  ├─ Log DSR computation details                     │  │
│  │  ├─ Log HMM regime parameters                       │  │
│  │  ├─ Generate HTML tearsheets (quantstats)           │  │
│  │  ├─ Track promotion history per sector              │  │
│  │  └─ Alert on model promotion events                 │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│         Uses Phase 1: Config, Logger, Exceptions           │
│         Uses Phase 2: Feature outputs, Shield Agent        │
│         Uses Phase 3: Candidate models, returns matrices   │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

```
/new_pipeline/evaluation/        # ✨ NEW: Evaluation module
├── __init__.py
├── dsr.py                       # ✨ NEW: Deflated Sharpe Ratio
├── hmm_validator.py             # ✨ NEW: HMM synthetic validation
├── promotion.py                 # ✨ NEW: Promotion logic
├── tearsheet.py                 # ✨ NEW: HTML report generation
└── tests/
    ├── test_dsr.py
    ├── test_hmm_validator.py
    ├── test_promotion.py
    └── benchmarks/
        ├── bench_dsr_computation.py
        └── bench_hmm_generation.py
```

---

## 2. Deflated Sharpe Ratio (DSR) Computation

### 2.1 Theory: Bailey & Lopez de Prado Framework

**Problem**: Standard Sharpe ratio is biased upward under multiple testing hypothesis.

**Solution**: Deflate Sharpe by accounting for:
1. Non-Normal returns (skewness, kurtosis)
2. Number of trials (multiple testing bias)
3. Strategy history length

### 2.2 Module: `evaluation/dsr.py`

**File: `evaluation/dsr.py`**

#### 2.2.1 DSR Computation Function

**Function: `compute_deflated_sharpe_ratio()`**

```python
from scipy.stats import norm
import numpy as np

def compute_deflated_sharpe_ratio(
    trial_matrix: pd.DataFrame,
    champion_returns: pd.Series,
    verbose: bool = True
) -> float:
    """Compute Deflated Sharpe Ratio (DSR) for statistical validation.
    
    Args:
        trial_matrix: DataFrame where each column is out-of-sample returns 
                     from one backtest trial (hyperparameter combo).
                     Shape: (n_observations, n_trials)
        champion_returns: Series of OOS returns for the champion model 
                         (best hyperparameter combo).
        verbose: Print computation steps.
    
    Returns:
        DSR percentile (0-1):
        - DSR < 0.5: Model worse than random (likely overfit)
        - 0.5 ≤ DSR < 0.95: Statistically insignificant
        - DSR ≥ 0.95: Genuine alpha signal (99.5th percentile)
    
    Formula (High-Level):
        1. Compute champion Sharpe ratio: SR_champ = mean(ret) / std(ret)
        2. Extract non-Normal moments: skew, kurtosis
        3. Compute trial variances: var_trials = var(SR per trial)
        4. Compute expected max Sharpe under null (random):
           SR_expected = sqrt(var_trials) × exp(euler_mascheroni) / sqrt(n)
        5. Deflate champion Sharpe:
           denom = sqrt(1 - skew×SR_champ + (kurtosis-1)/4 × SR_champ²)
           DSR_stat = (SR_champ - SR_expected) × sqrt(T-1) / denom
        6. Return: P(Z ≤ DSR_stat) via normal CDF
    
    Mathematical Details:
        - bailey_lopez_de_prado_2013 (https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253)
        - euler_mascheroni ≈ 0.5772156649 (natural constant)
        - Non-Normal adjustment accounts for skewness/kurtosis bias
        - Multiple testing bias penalizes having too many trials
    """
    
    logger = get_logger(__name__)
    
    # ─────────────────────────────────────────────────────────────
    # STEP 1: Compute Champion Sharpe Ratio
    # ─────────────────────────────────────────────────────────────
    
    champ_returns = champion_returns.dropna()
    champ_mean = np.mean(champ_returns)
    champ_std = np.std(champ_returns, ddof=1)  # Sample std
    
    if champ_std == 0:
        logger.warning("Champion returns have zero std; DSR undefined")
        return 0.0
    
    sr_champ = champ_mean / champ_std
    
    if verbose:
        print(f"Champion Sharpe Ratio: {sr_champ:.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 2: Extract Non-Normal Moments
    # ─────────────────────────────────────────────────────────────
    
    skewness = scipy.stats.skew(champ_returns)
    kurtosis = scipy.stats.kurtosis(champ_returns)  # Excess kurtosis
    
    if verbose:
        print(f"Skewness: {skewness:.4f}, Excess Kurtosis: {kurtosis:.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 3: Compute Trial Sharpe Ratios & Variance
    # ─────────────────────────────────────────────────────────────
    
    trial_srs = []
    for col in trial_matrix.columns:
        trial_ret = trial_matrix[col].dropna()
        if len(trial_ret) > 1:
            trial_mean = np.mean(trial_ret)
            trial_std = np.std(trial_ret, ddof=1)
            if trial_std > 0:
                trial_sr = trial_mean / trial_std
                trial_srs.append(trial_sr)
    
    trial_srs = np.array(trial_srs)
    var_trials = np.var(trial_srs, ddof=1)
    n_trials = len(trial_srs)
    
    if verbose:
        print(f"Number of trials: {n_trials}")
        print(f"Trial Sharpe variance: {var_trials:.6f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 4: Compute Expected Max Sharpe Under Null (H0: random)
    # ─────────────────────────────────────────────────────────────
    
    euler_mascheroni = 0.5772156649
    T = len(champ_returns)
    
    # Expected max Sharpe formula
    sr_expected = np.sqrt(var_trials) * (
        (1 - euler_mascheroni) / np.sqrt(np.pi) +
        euler_mascheroni * np.log(n_trials) / np.sqrt(2 * np.pi)
    ) / np.sqrt(n_trials)
    
    if verbose:
        print(f"Expected max Sharpe (H0): {sr_expected:.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 5: Deflate Champion Sharpe (Account for Non-Normality)
    # ─────────────────────────────────────────────────────────────
    
    # Non-Normal adjustment factor
    denom = np.sqrt(
        1.0 - skewness * sr_champ + 
        (kurtosis - 1.0) / 4.0 * sr_champ ** 2
    )
    
    # Deflated Sharpe statistic
    dsr_stat = (sr_champ - sr_expected) * np.sqrt(T - 1) / denom
    
    if verbose:
        print(f"Deflated Sharpe statistic: {dsr_stat:.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 6: Convert to Percentile
    # ─────────────────────────────────────────────────────────────
    
    dsr_percentile = norm.cdf(dsr_stat)
    
    if verbose:
        print(f"Deflated Sharpe Ratio (percentile): {dsr_percentile:.4f}")
    
    return dsr_percentile
```

#### 2.2.2 DSR Interpretation & Thresholds

**Function: `interpret_dsr()`**

```python
def interpret_dsr(dsr: float) -> Dict[str, str]:
    """Interpret DSR value and provide recommendation.
    
    Args:
        dsr: DSR percentile (0-1).
    
    Returns:
        Dict with interpretation:
        {
            'percentile': float,
            'interpretation': str,
            'recommendation': str,
            'color': str (green/yellow/red)
        }
    
    Thresholds:
        - DSR < 0.5: Red (likely overfit)
        - 0.5 ≤ DSR < 0.95: Yellow (insufficient evidence)
        - DSR ≥ 0.95: Green (genuine alpha)
    """
    if dsr >= 0.95:
        return {
            'percentile': dsr,
            'interpretation': 'Genuine Alpha Signal',
            'recommendation': 'PROMOTE to production',
            'color': 'green',
            'reason': 'DSR ≥ 0.95 (99.5th percentile)'
        }
    elif dsr >= 0.50:
        return {
            'percentile': dsr,
            'interpretation': 'Statistically Insignificant',
            'recommendation': 'REJECT, need more tuning',
            'color': 'yellow',
            'reason': f'DSR = {dsr:.3f} (below threshold)'
        }
    else:
        return {
            'percentile': dsr,
            'interpretation': 'Likely Overfit',
            'recommendation': 'REJECT, model is curve-fitted',
            'color': 'red',
            'reason': f'DSR = {dsr:.3f} (worse than random)'
        }
```

#### 2.2.3 DSR with Confidence Intervals

**Function: `compute_dsr_confidence_interval()`**

```python
def compute_dsr_confidence_interval(
    trial_matrix: pd.DataFrame,
    champion_returns: pd.Series,
    n_bootstrap: int = 1000,
    ci: float = 0.95
) -> Tuple[float, float, float]:
    """Compute DSR with bootstrap confidence interval.
    
    Args:
        trial_matrix: Trial returns matrix.
        champion_returns: Champion returns series.
        n_bootstrap: Number of bootstrap iterations.
        ci: Confidence interval (e.g., 0.95 for 95%).
    
    Returns:
        (dsr_mean, dsr_lower, dsr_upper):
        - dsr_mean: Point estimate
        - dsr_lower: Lower bound
        - dsr_upper: Upper bound
    
    Notes:
        - Bootstrap resamples with replacement
        - Provides uncertainty quantification
        - Wider CI → less confidence in estimate
    """
    dsr_boots = []
    
    for _ in range(n_bootstrap):
        # Resample champion returns
        champ_boot = np.random.choice(
            champion_returns.dropna(),
            size=len(champion_returns),
            replace=True
        )
        
        # Resample trial matrix columns
        trial_boot = pd.DataFrame()
        for col in trial_matrix.columns:
            trial_col = trial_matrix[col].dropna()
            trial_boot[col] = np.random.choice(
                trial_col,
                size=len(trial_col),
                replace=True
            )
        
        # Compute DSR on bootstrap sample
        dsr_boot = compute_deflated_sharpe_ratio(
            trial_boot,
            pd.Series(champ_boot),
            verbose=False
        )
        
        dsr_boots.append(dsr_boot)
    
    dsr_boots = np.array(dsr_boots)
    dsr_mean = np.mean(dsr_boots)
    
    alpha = 1 - ci
    dsr_lower = np.percentile(dsr_boots, alpha / 2 * 100)
    dsr_upper = np.percentile(dsr_boots, (1 - alpha / 2) * 100)
    
    return dsr_mean, dsr_lower, dsr_upper
```

---

## 3. HMM Synthetic Generalization Validator

### 3.1 Theory: Testing Out-of-Distribution Generalization

**Problem**: DSR tests if champion beats random. But does it generalize to new market regimes?

**Solution**: Use Hidden Markov Model (HMM) to:
1. Extract market regime parameters from benchmark returns
2. Generate synthetic returns (novel distribution)
3. Apply champion model to synthetic data
4. Verify model performance > 0 (true alpha, not luck)

### 3.2 Module: `evaluation/hmm_validator.py`

**File: `evaluation/hmm_validator.py`**

#### 3.2.1 HMM Synthetic Validation

**Function: `run_hmm_synthetic_gauntlet()`**

```python
from hmmlearn.gaussian_hmm import GaussianHMM
import numpy as np

def run_hmm_synthetic_gauntlet(
    sector: str,
    champion_model_path: str,
    features_path: str,
    benchmark_returns: pd.Series,
    synthetic_returns: pd.Series = None,
    n_states: int = 3,
    n_synthetic: int = None,
    verbose: bool = True
) -> Dict[str, float]:
    """Validate champion model on HMM-generated synthetic returns.
    
    Args:
        sector: Sector name (for logging).
        champion_model_path: Path to champion XGBoost model JSON.
        features_path: Path to feature manifest JSON.
        benchmark_returns: Historical benchmark returns (used to fit HMM).
        synthetic_returns: If provided, use these instead of generating.
        n_states: Number of HMM states (typically 3 for low/normal/high vol).
        n_synthetic: Length of synthetic series (default = len(benchmark)).
        verbose: Print steps.
    
    Returns:
        {
            'synthetic_sharpe': float (model performance on synthetic),
            'synthetic_returns': np.ndarray,
            'hmm_means': List[float],
            'hmm_stds': List[float],
            'hmm_transitions': np.ndarray,
            'validation_passed': bool (synthetic_sr > 0)
        }
    
    Flow:
        1. Fit HMM to benchmark returns
        2. Generate synthetic returns via HMM sampling
        3. Create synthetic features (bootstrap historical)
        4. Load champion model
        5. Generate signals on synthetic features
        6. Calculate Sharpe ratio on synthetic returns
        7. Verify synthetic_sr > 0
    
    Rationale:
        - HMM preserves market regime dynamics (not iid random)
        - Synthetic returns never seen by training algorithm
        - If model works on synthetic → true alpha
        - If synthetic_sr ≤ 0 → model was just overfitting to historical noise
    """
    
    logger = get_logger(__name__)
    logger.info(f"Running HMM synthetic gauntlet for {sector}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 1: Fit HMM to Benchmark Returns
    # ─────────────────────────────────────────────────────────────
    
    bench_returns = benchmark_returns.dropna()
    X = bench_returns.values.reshape(-1, 1)
    
    hmm = GaussianHMM(n_components=n_states, covariance_type='full', n_iter=1000)
    hmm.fit(X)
    
    if verbose:
        print(f"HMM fitted with {n_states} states")
        print(f"  Means: {hmm.means_.flatten()}")
        print(f"  Transition matrix:\n{hmm.transmat_}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 2: Generate Synthetic Returns (Monte Carlo)
    # ─────────────────────────────────────────────────────────────
    
    if synthetic_returns is None:
        n_synthetic = n_synthetic or len(bench_returns)
        synthetic_returns, _ = hmm.sample(n_samples=n_synthetic)
        synthetic_returns = synthetic_returns.flatten()
    else:
        synthetic_returns = synthetic_returns.values
    
    if verbose:
        print(f"Generated {len(synthetic_returns)} synthetic returns")
        print(f"  Mean: {np.mean(synthetic_returns):.6f}")
        print(f"  Std: {np.std(synthetic_returns):.6f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 3: Bootstrap Historical Features (Destroy Temporal Order)
    # ─────────────────────────────────────────────────────────────
    
    # This is critical: we want to preserve feature distributions
    # but destroy any temporal correlation with synthetic returns
    
    # Placeholder: in actual implementation, load historical feature data
    # For now, assume synthetic features created by resampling
    
    # ─────────────────────────────────────────────────────────────
    # STEP 4: Load Champion Model & Generate Signals
    # ─────────────────────────────────────────────────────────────
    
    booster = xgb.Booster()
    booster.load_model(champion_model_path)
    
    # Load feature list
    with open(features_path, 'r') as f:
        feature_manifest = json.load(f)
    features = feature_manifest['features']
    
    # Create synthetic feature DataFrame (simplified)
    n_features = len(features)
    synthetic_features = np.random.randn(len(synthetic_returns), n_features)
    synthetic_df = pd.DataFrame(synthetic_features, columns=features)
    
    # Generate signals
    dmatrix = xgb.DMatrix(synthetic_df)
    synthetic_signals = booster.predict(dmatrix)
    synthetic_signals = (synthetic_signals > 0.5).astype(int)
    
    if verbose:
        print(f"Generated {np.sum(synthetic_signals)} signals on {len(synthetic_returns)} returns")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 5: Calculate Sharpe Ratio on Synthetic
    # ─────────────────────────────────────────────────────────────
    
    # Strategy returns = signal × synthetic returns
    strategy_returns = synthetic_signals * synthetic_returns
    
    mean_strat = np.mean(strategy_returns)
    std_strat = np.std(strategy_returns, ddof=1)
    
    synthetic_sharpe = (mean_strat / std_strat) * np.sqrt(252) if std_strat > 0 else 0.0
    
    if verbose:
        print(f"Synthetic Strategy Sharpe: {synthetic_sharpe:.4f}")
    
    # ─────────────────────────────────────────────────────────────
    # STEP 6: Validation
    # ─────────────────────────────────────────────────────────────
    
    validation_passed = synthetic_sharpe > 0.0
    
    logger.info(f"Validation {'PASSED' if validation_passed else 'FAILED'}: SR={synthetic_sharpe:.4f}")
    
    return {
        'synthetic_sharpe': synthetic_sharpe,
        'synthetic_returns': synthetic_returns,
        'hmm_means': hmm.means_.flatten().tolist(),
        'hmm_stds': np.sqrt(hmm.covars_.flatten()).tolist(),
        'hmm_transitions': hmm.transmat_.tolist(),
        'validation_passed': validation_passed
    }
```

---

## 4. Model Promotion Logic

### 4.1 Module: `evaluation/promotion.py`

**File: `evaluation/promotion.py`**

#### 4.1.1 Promotion Decision Engine

**Function: `assess_sector_for_promotion()`**

```python
def assess_sector_for_promotion(
    sector: str,
    dsr: float,
    hmm_result: Dict,
    config: AppConfig
) -> Dict[str, Any]:
    """Make promotion/rejection decision for a sector.
    
    Args:
        sector: Sector name.
        dsr: Deflated Sharpe Ratio (0-1 percentile).
        hmm_result: Output from run_hmm_synthetic_gauntlet().
        config: AppConfig with promotion thresholds.
    
    Returns:
        {
            'sector': str,
            'decision': str ('PROMOTE', 'REJECT'),
            'dsr': float,
            'synthetic_sharpe': float,
            'reasons': List[str],
            'champion_path': str (if promoted),
            'rejection_reason': str (if rejected)
        }
    
    Decision Logic:
        Gate 1: DSR ≥ 0.95?
        ├─ NO → REJECT ('DSR below threshold')
        └─ YES ↓
        
        Gate 2: Synthetic Sharpe > 0?
        ├─ NO → REJECT ('No generalization')
        └─ YES ↓
        
        Gate 3: All gates passed?
        └─ YES → PROMOTE
    """
    
    logger = get_logger(__name__)
    
    dsr_threshold = config.evaluation.dsr_promotion_threshold  # typically 0.95
    synthetic_sr_threshold = config.evaluation.synthetic_sr_threshold  # typically 0.0
    
    reasons = []
    decision = 'PROMOTE'
    
    # ─────────────────────────────────────────────────────────────
    # GATE 1: DSR Threshold
    # ─────────────────────────────────────────────────────────────
    
    if dsr < dsr_threshold:
        decision = 'REJECT'
        reasons.append(f"DSR {dsr:.3f} < threshold {dsr_threshold}")
    else:
        reasons.append(f"✓ DSR {dsr:.3f} ≥ threshold {dsr_threshold}")
    
    # ─────────────────────────────────────────────────────────────
    # GATE 2: Synthetic Sharpe Validation
    # ─────────────────────────────────────────────────────────────
    
    synthetic_sr = hmm_result['synthetic_sharpe']
    
    if synthetic_sr <= synthetic_sr_threshold:
        decision = 'REJECT'
        reasons.append(f"Synthetic SR {synthetic_sr:.3f} ≤ threshold {synthetic_sr_threshold}")
    else:
        reasons.append(f"✓ Synthetic SR {synthetic_sr:.3f} > threshold {synthetic_sr_threshold}")
    
    # ─────────────────────────────────────────────────────────────
    # DECISION OUTPUT
    # ─────────────────────────────────────────────────────────────
    
    result = {
        'sector': sector,
        'decision': decision,
        'dsr': dsr,
        'synthetic_sharpe': synthetic_sr,
        'reasons': reasons,
        'timestamp': pd.Timestamp.now()
    }
    
    if decision == 'PROMOTE':
        # Move candidate → champion
        candidate_path = f"{config.models.candidate_models_dir}/{sector}_candidate.json"
        champion_path = f"{config.models.prod_models_dir}/{sector}_champion.json"
        
        shutil.copy(candidate_path, champion_path)
        logger.info(f"[{sector}] PROMOTED: {candidate_path} → {champion_path}")
        
        result['champion_path'] = champion_path
    else:
        result['rejection_reason'] = '; '.join(reasons)
        logger.warning(f"[{sector}] REJECTED: {result['rejection_reason']}")
    
    return result
```

#### 4.1.2 Promotion Registry & Audit Trail

**Class: `PromotionRegistry`**

```python
class PromotionRegistry:
    """Track model promotions and maintain audit trail.
    
    Methods:
        record_promotion: Log a promotion event.
        get_promotion_history: Retrieve history for sector.
        get_active_champions: List currently live models.
    """
    
    def __init__(self, registry_path: str):
        """Initialize registry.
        
        Args:
            registry_path: Path to registry file (JSON).
        """
        self.registry_path = registry_path
        self.logger = get_logger(__name__)
        
        # Load existing registry or create new
        if os.path.exists(registry_path):
            with open(registry_path, 'r') as f:
                self.registry = json.load(f)
        else:
            self.registry = {'promotions': [], 'active_champions': {}}
    
    def record_promotion(self, promotion_record: Dict) -> None:
        """Record a promotion/rejection event.
        
        Args:
            promotion_record: Dict with sector, decision, dsr, etc.
        """
        self.registry['promotions'].append(promotion_record)
        
        if promotion_record['decision'] == 'PROMOTE':
            self.registry['active_champions'][promotion_record['sector']] = {
                'champion_path': promotion_record['champion_path'],
                'promoted_at': promotion_record['timestamp'].isoformat(),
                'dsr': promotion_record['dsr'],
                'synthetic_sharpe': promotion_record['synthetic_sharpe']
            }
        
        self._save()
        self.logger.info(f"Recorded: {promotion_record['decision']} for {promotion_record['sector']}")
    
    def _save(self) -> None:
        """Persist registry to disk."""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        with open(self.registry_path, 'w') as f:
            json.dump(self.registry, f, indent=2, default=str)
    
    def get_active_champions(self) -> Dict[str, Dict]:
        """Return currently active champion models."""
        return self.registry.get('active_champions', {})
```

---

## 5. HTML Tearsheet Generation

### 5.1 Module: `evaluation/tearsheet.py`

**File: `evaluation/tearsheet.py`**

#### 5.1.1 Tearsheet Generation

**Function: `generate_html_tearsheet()`**

```python
import quantstats as qs
from jinja2 import Template

def generate_html_tearsheet(
    sector: str,
    strategy_returns: pd.Series,
    benchmark_returns: pd.Series,
    dsr: float,
    hmm_result: Dict,
    output_path: str
) -> str:
    """Generate comprehensive HTML performance tearsheet.
    
    Args:
        sector: Sector name.
        strategy_returns: Strategy returns series.
        benchmark_returns: Benchmark returns series.
        dsr: Deflated Sharpe Ratio.
        hmm_result: HMM validation results.
        output_path: Where to save HTML file.
    
    Returns:
        Path to generated HTML file.
    
    Contents:
        1. Summary metrics (Sharpe, max drawdown, win rate)
        2. Equity curve comparison (strategy vs benchmark)
        3. Monthly/annual returns heatmap
        4. Drawdown timeline
        5. DSR computation details
        6. HMM regime analysis
        7. Rolling Sharpe ratio
        8. Return distribution histogram
    """
    
    logger = get_logger(__name__)
    
    # Generate quantstats report
    stats_html = qs.stats.html(
        strategy_returns,
        benchmark_returns,
        title=f"Quantum Avenger - {sector} Model Tearsheet"
    )
    
    # Extract key metrics
    metrics = {
        'sector': sector,
        'strategy_sharpe': qs.stats.sharpe(strategy_returns) * np.sqrt(252),
        'benchmark_sharpe': qs.stats.sharpe(benchmark_returns) * np.sqrt(252),
        'strategy_sortino': qs.stats.sortino(strategy_returns),
        'max_drawdown': qs.stats.max_drawdown(strategy_returns),
        'cagr': qs.stats.cagr(strategy_returns),
        'win_rate': np.sum(strategy_returns > 0) / len(strategy_returns[strategy_returns != 0]),
        'dsr': dsr,
        'synthetic_sharpe': hmm_result['synthetic_sharpe'],
        'validation_passed': hmm_result['validation_passed']
    }
    
    # Custom template
    template_str = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ sector }} Model Tearsheet</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .summary { background: #f0f0f0; padding: 10px; margin: 10px 0; }
            .metric { display: inline-block; margin: 10px; }
            .pass { color: green; font-weight: bold; }
            .fail { color: red; font-weight: bold; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
        </style>
    </head>
    <body>
        <h1>{{ sector }} Model Performance Tearsheet</h1>
        
        <div class="summary">
            <h2>Summary Metrics</h2>
            <table>
                <tr>
                    <th>Metric</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Strategy Sharpe (Annual)</td>
                    <td>{{ "%.3f" % metrics.strategy_sharpe }}</td>
                </tr>
                <tr>
                    <td>Benchmark Sharpe (Annual)</td>
                    <td>{{ "%.3f" % metrics.benchmark_sharpe }}</td>
                </tr>
                <tr>
                    <td>Max Drawdown</td>
                    <td>{{ "%.2f" % (metrics.max_drawdown * 100) }}%</td>
                </tr>
                <tr>
                    <td>CAGR</td>
                    <td>{{ "%.2f" % (metrics.cagr * 100) }}%</td>
                </tr>
                <tr>
                    <td>Win Rate</td>
                    <td>{{ "%.1f" % (metrics.win_rate * 100) }}%</td>
                </tr>
            </table>
        </div>
        
        <div class="summary">
            <h2>Statistical Validation</h2>
            <table>
                <tr>
                    <td>Deflated Sharpe Ratio (DSR)</td>
                    <td class="{{ 'pass' if metrics.dsr >= 0.95 else 'fail' }}">
                        {{ "%.4f" % metrics.dsr }}
                    </td>
                </tr>
                <tr>
                    <td>Synthetic Sharpe (HMM Test)</td>
                    <td class="{{ 'pass' if metrics.synthetic_sharpe > 0 else 'fail' }}">
                        {{ "%.4f" % metrics.synthetic_sharpe }}
                    </td>
                </tr>
                <tr>
                    <td>Validation Status</td>
                    <td class="{{ 'pass' if metrics.validation_passed else 'fail' }}">
                        {{ "PASSED" if metrics.validation_passed else "FAILED" }}
                    </td>
                </tr>
            </table>
        </div>
        
        <h2>Quantstats Report</h2>
        {{ stats_html|safe }}
    </body>
    </html>
    """
    
    template = Template(template_str)
    html_content = template.render(metrics=metrics, stats_html=stats_html)
    
    # Save to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    logger.info(f"Generated tearsheet: {output_path}")
    
    return output_path
```

---

## 6. Full Evaluation Pipeline

### 6.1 Module: `evaluation/evaluator.py` (Orchestrator)

**Class: `QuantitativeEvaluator`**

```python
class QuantitativeEvaluator:
    """Orchestrates full evaluation pipeline for all sectors.
    
    Methods:
        evaluate_all_sectors: Run evaluation for all candidates.
        evaluate_single_sector: Evaluate one sector.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
        self.registry = PromotionRegistry(
            f"{config.models.registry_path}/promotion_registry.json"
        )
    
    def evaluate_single_sector(self, sector: str) -> Dict:
        """Evaluate one sector and make promotion decision.
        
        Args:
            sector: Sector name.
        
        Returns:
            Dict with evaluation results and decision.
        
        Flow:
            1. Load candidate model + features
            2. Load returns matrix (from Phase 3)
            3. Compute DSR
            4. Run HMM synthetic gauntlet
            5. Make promotion decision
            6. Generate tearsheet
            7. Log to registry
        """
        self.logger.info(f"Evaluating {sector}")
        
        try:
            # Load candidate
            candidate_model_path = f"{self.config.models.candidate_models_dir}/{sector}_candidate.json"
            features_path = f"{self.config.models.candidate_models_dir}/{sector}_candidate_features.json"
            
            # Load returns
            returns_path = f"{self.config.tournament.results_dir}/returns_matrix_{sector}.parquet"
            benchmark_path = f"{self.config.tournament.results_dir}/benchmark_{sector}.parquet"
            
            returns_matrix = pd.read_parquet(returns_path)
            benchmark_returns = pd.read_parquet(benchmark_path).squeeze()
            champion_returns = returns_matrix.iloc[:, 0]  # Best combo
            
            # Compute DSR
            dsr = compute_deflated_sharpe_ratio(
                returns_matrix,
                champion_returns,
                verbose=True
            )
            
            # Run HMM validation
            hmm_result = run_hmm_synthetic_gauntlet(
                sector,
                candidate_model_path,
                features_path,
                benchmark_returns,
                verbose=True
            )
            
            # Make promotion decision
            promotion_result = assess_sector_for_promotion(
                sector,
                dsr,
                hmm_result,
                self.config
            )
            
            # Generate tearsheet
            tearsheet_path = f"{self.config.models.reports_dir}/{sector}_tearsheet.html"
            generate_html_tearsheet(
                sector,
                champion_returns,
                benchmark_returns,
                dsr,
                hmm_result,
                tearsheet_path
            )
            
            promotion_result['tearsheet_path'] = tearsheet_path
            
            # Record in registry
            self.registry.record_promotion(promotion_result)
            
            return promotion_result
            
        except Exception as e:
            self.logger.error(f"Evaluation failed for {sector}: {e}", exc_info=True)
            return {
                'sector': sector,
                'decision': 'ERROR',
                'error': str(e)
            }
    
    def evaluate_all_sectors(self) -> Dict[str, Dict]:
        """Evaluate all candidate models.
        
        Returns:
            Dict mapping sector → evaluation result.
        """
        results = {}
        
        # Get all candidate sectors
        candidate_dir = self.config.models.candidate_models_dir
        candidates = glob.glob(f"{candidate_dir}/*_candidate.json")
        sectors = [
            os.path.basename(p).replace('_candidate.json', '')
            for p in candidates
        ]
        
        for sector in sectors:
            result = self.evaluate_single_sector(sector)
            results[sector] = result
        
        # Summary report
        promoted = [s for s, r in results.items() if r.get('decision') == 'PROMOTE']
        rejected = [s for s, r in results.items() if r.get('decision') == 'REJECT']
        
        self.logger.info(f"Evaluation complete:")
        self.logger.info(f"  Promoted: {len(promoted)} ({', '.join(promoted)})")
        self.logger.info(f"  Rejected: {len(rejected)} ({', '.join(rejected)})")
        
        return results
```

---

## 7. Implementation Checklist - Phase 4

### Week 1: DSR & HMM Implementation

- [ ] **Day 1-2**: DSR computation
  - [ ] Implement `compute_deflated_sharpe_ratio()`
  - [ ] Implement `compute_dsr_confidence_interval()`
  - [ ] Unit tests: `test_dsr.py`
  - [ ] Verify against reference implementations

- [ ] **Day 2-3**: DSR validation
  - [ ] Test on synthetic data (known distributions)
  - [ ] Verify DSR ≥ 0.95 for alpha signal
  - [ ] Test DSR < 0.5 for overfit case

- [ ] **Day 3-4**: HMM synthetic validation
  - [ ] Implement `run_hmm_synthetic_gauntlet()`
  - [ ] Test HMM fitting to returns
  - [ ] Validate synthetic returns match regime stats

- [ ] **Day 4-5**: HMM integration
  - [ ] Test feature bootstrapping
  - [ ] Test model inference on synthetic
  - [ ] Unit tests: `test_hmm_validator.py`

### Week 2: Promotion & Reporting

- [ ] **Day 6-7**: Promotion logic
  - [ ] Implement `assess_sector_for_promotion()`
  - [ ] Implement `PromotionRegistry` class
  - [ ] Unit tests: `test_promotion.py`

- [ ] **Day 7-8**: Tearsheet generation
  - [ ] Implement `generate_html_tearsheet()`
  - [ ] Integrate quantstats
  - [ ] Generate sample tearsheet

- [ ] **Day 8-9**: Full evaluator
  - [ ] Implement `QuantitativeEvaluator` class
  - [ ] End-to-end evaluation (candidate → promotion/rejection)
  - [ ] Integration tests: `test_evaluator.py`

- [ ] **Day 9-10**: Benchmarking & optimization
  - [ ] Benchmark DSR computation
  - [ ] Benchmark HMM generation
  - [ ] Profile bottlenecks
  - [ ] All tests passing, 85%+ coverage

---

## 8. Success Criteria & Acceptance Tests

### 8.1 Functional Acceptance

| Criterion | Test | Expected |
|-----------|------|----------|
| DSR computation | `test_dsr_computation()` | ✓ Matches reference |
| DSR ≥ 0.95 detected | `test_dsr_promotion_threshold()` | ✓ Alpha signal identified |
| HMM fitting | `test_hmm_fitting()` | ✓ Regimes extracted |
| Synthetic generation | `test_synthetic_returns()` | ✓ New distribution, not identical |
| Model inference | `test_inference_on_synthetic()` | ✓ Predicts correctly |
| Promotion decision | `test_promotion_logic()` | ✓ Promotes if DSR+HMM pass |
| Rejection decision | `test_rejection_logic()` | ✓ Rejects if gates fail |
| Registry tracking | `test_promotion_registry()` | ✓ History persisted |

### 8.2 Performance Targets

| Component | Target |
|-----------|--------|
| DSR computation | < 10 seconds |
| HMM fitting | < 5 seconds |
| Synthetic generation | < 2 seconds |
| HTML tearsheet | < 5 seconds |
| Full evaluation (sector) | < 30 seconds |

### 8.3 Code Quality

| Criterion | Target |
|-----------|--------|
| Test coverage (evaluation/) | ≥ 85% |
| Type hints | 100% (mypy clean) |
| Linting errors | 0 |

---

## 9. Integration with Phases 1-3 & Handoff to Phase 5

### 9.1 Phase Dependencies

- **Phase 1**: Config (promotion thresholds), logging, exceptions
- **Phase 2**: Feature outputs used in HMM validation
- **Phase 3**: Candidate models, returns matrices

### 9.2 Handoff to Phase 5 (Live Execution)

- Champion models → loaded by live trader
- Promotion registry → tracks which models are live
- Feature manifests → used for real-time inference

---

## 10. Deliverables Summary - Phase 4

### Codebase
- [ ] `/new_pipeline/evaluation/dsr.py` (300+ lines)
- [ ] `/new_pipeline/evaluation/hmm_validator.py` (250+ lines)
- [ ] `/new_pipeline/evaluation/promotion.py` (200+ lines)
- [ ] `/new_pipeline/evaluation/tearsheet.py` (250+ lines)
- [ ] `/new_pipeline/evaluation/evaluator.py` (300+ lines)
- [ ] 100+ unit tests + benchmarks

### Performance
- [ ] DSR correctly identifies alpha vs luck
- [ ] HMM validates generalization
- [ ] Promotion gates enforce quality
- [ ] Full evaluation < 30 sec/sector

### Documentation
- [ ] DSR methodology & interpretation
- [ ] HMM synthetic validation rationale
- [ ] Promotion decision logic
- [ ] Tearsheet interpretation guide

---

**Next**: After Phase 4 completion, proceed to [Phase 5: Live Execution & Orchestration](PHASE_5_SPECIFICATION.md) (to be created).

**Previous Phases**:
- [Phase 1: Core Pipeline Infrastructure](PHASE_1_SPECIFICATION.md)
- [Phase 2: Vectorized Quant Engine & Shields](PHASE_2_SPECIFICATION.md)
- [Phase 3: Tournament Backtesting & Model Selection](PHASE_3_SPECIFICATION.md)
