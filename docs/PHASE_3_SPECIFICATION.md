# Phase 3: Tournament Backtesting & Model Selection - Detailed Specification

> **Implementation status: ✅ DONE (substantially evolved past spec).** CPCV, the XGBoost trainer, grid search and the per‑sector director are implemented in `new_pipeline/tournament/`. **The hygiene grew well past the fixed‑purge spec:** span‑based purge by the label event‑span `t1` (getTrainTimes), **ticker/block‑aware** span clamping, fractional embargo, and reconstruction of the **φ = C(N−1,k−1) combinatorial backtest paths**; plus **causal feature selection** (Granger screen + purged‑CPCV MDA, default) and **sample‑uniqueness weighting** — none of which were in the original spec. See `quantitative_math.md` §2–§5. *Original build spec; current state in `ARCHITECTURE_ROADMAP.md`.*

**Duration**: 2 weeks  
**Target Date**: Complete by end of June (after Phase 2)  
**Success Criteria**: CPCV backtests passing; XGBoost models trained; 85%+ out-of-sample test coverage; model promotion logic validated

---

## 1. Phase 3 Architecture Overview

### 1.1 System Context (Integration with Phases 1-2)

```
┌────────────────────────────────────────────────────────────┐
│  PHASE 1 (Complete): Config, Logging, Exceptions, Testing │
│  PHASE 2 (Complete): Polars Vectors, GPU Kernels, Shield  │
├────────────────────────────────────────────────────────────┤
│                           │                                 │
│                           ▼                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  PHASE 3: TOURNAMENT BACKTESTING & MODEL SELECTION  │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │                                                      │  │
│  │  LAYER 1: DATA PREPARATION                          │  │
│  │  ├─ Load PROCESSED_VAULT (Parquet)                  │  │
│  │  ├─ Sector filtering                                │  │
│  │  ├─ Dask lazy loading                               │  │
│  │  └─ Feature manifest preparation                    │  │
│  │                                                      │  │
│  │  LAYER 2: CPCV SPLIT GENERATION                     │  │
│  │  ├─ 6-group temporal splits                         │  │
│  │  ├─ C(6,2) = 15 test combinations                   │  │
│  │  ├─ Purge gap removal (look-ahead prevention)      │  │
│  │  ├─ Embargo window (data leakage prevention)        │  │
│  │  └─ Yields (train_df, test_df) tuples              │  │
│  │                                                      │  │
│  │  LAYER 3: PARQUET DATA ITERATOR                     │  │
│  │  ├─ Zero-copy PyArrow streaming                     │  │
│  │  ├─ Row-group iteration                             │  │
│  │  ├─ On-disk feature selection                       │  │
│  │  └─ Feeds directly to XGBoost                        │  │
│  │                                                      │  │
│  │  LAYER 4: XGBOOST TRAINING                          │  │
│  │  ├─ Asymmetric financial loss (FP = 5× FN)         │  │
│  │  ├─ ExtMemQuantileDMatrix (VRAM adaptive)           │  │
│  │  ├─ CUDA acceleration (tree_method='gpu_hist')      │  │
│  │  ├─ Hyperparameter grid search                      │  │
│  │  └─ Per-fold model saving                           │  │
│  │                                                      │  │
│  │  LAYER 5: RISK SIMULATION & RETURNS                 │  │
│  │  ├─ Shield Agent evaluation (Numba @njit)           │  │
│  │  ├─ Position sizing & ATR stops                     │  │
│  │  ├─ Out-of-sample returns calculation               │  │
│  │  ├─ Accumulates trial returns matrix                │  │
│  │  └─ Per-fold statistics                             │  │
│  │                                                      │  │
│  │  LAYER 6: MODEL SELECTION & REGISTRATION            │  │
│  │  ├─ Best hyperparams per sector                     │  │
│  │  ├─ Candidate model registry (JSON)                 │  │
│  │  ├─ Feature manifold metadata                       │  │
│  │  └─ Ready for Phase 4 evaluation                    │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                           │                                 │
│         Uses Phase 1: Config, Logger, Exceptions           │
│         Uses Phase 2: Feature outputs, Shield Agent        │
│                                                              │
└────────────────────────────────────────────────────────────┘
```

### 1.2 Module Map

```
/new_pipeline/models/
├── __init__.py
├── registry.py                # ✨ NEW: Model artifact storage
├── metadata.py                # ✨ NEW: Model metadata tracking
│
/new_pipeline/tournament/       # ✨ NEW: Tournament module
├── __init__.py
├── base.py                    # Tournament base classes
├── cpcv.py                    # ✨ NEW: CPCV split generation
├── data_iterator.py           # ✨ NEW: ParquetDataIter (zero-copy)
├── training.py                # ✨ NEW: XGBoost training loop
├── risk_simulator.py          # ✨ NEW: Backtest risk simulation
├── grid_search.py             # ✨ NEW: Hyperparameter tuning
├── director.py                # ✨ NEW: ModularTournamentDirector
└── tests/
    ├── test_cpcv.py
    ├── test_data_iterator.py
    ├── test_training.py
    ├── test_risk_simulator.py
    ├── test_grid_search.py
    ├── test_director.py
    └── benchmarks/
        ├── bench_xgboost_training.py
        ├── bench_cpcv_splits.py
        └── bench_risk_simulation.py
```

---

## 2. CPCV (Combinatorial Purged Cross-Validation)

### 2.1 Principle: Preventing Look-Ahead Bias

**Problem**: Standard K-fold CV on time-series data leaks information from future into training set.

**Solution**: CPCV applies temporal purging + embargo gaps to prevent look-ahead bias.

```
Time →

Historical Data:     [0........100........200........300.........400]
                     └─ Start ─────────────────────────────────── End ─┘

Grouping (6 groups):  [0|1|2|3|4|5]
                      └─ Each group ≈ 67 trading days ─┘

Combo 1 (Test=[0,1]):
                      Test: [0|1|·|·|·|·]
                      Purge: Gap before & after test
                      Train: [·|·|2|3|4|5] minus purge zones
                      
Combo 2 (Test=[0,2]):
                      Test: [0|·|2|·|·|·]
                      Purge: Gaps around both test groups
                      Train: [·|1|·|3|4|5] minus purge zones
                      
... (15 total combinations)
```

### 2.2 Module: `tournament/cpcv.py`

**File: `tournament/cpcv.py`**

#### 2.2.1 CPCV Split Generator Class

**Class: `CPCVSplitGenerator`**

```python
class CPCVSplitGenerator:
    """Generates Combinatorial Purged Cross-Validation splits.
    
    Attributes:
        df: DataFrame indexed by date.
        n_groups: Number of temporal groups (default 6).
        test_groups: Size of test set in each split (default 2).
        purge_gap: Gap before/after test set (days, default 5).
        embargo_gap: Additional embargo zone (days, default 5).
    
    Methods:
        generate_splits() → Generator[(train_df, test_df), ...]
        _split_into_groups() → List[indices]
        _apply_purge_embargo() → Purged indices
    """
    
    def __init__(
        self,
        df: pd.DataFrame,
        n_groups: int = 6,
        test_groups: int = 2,
        purge_days: int = 5,
        embargo_days: int = 5,
        config: AppConfig = None
    ):
        """Initialize CPCV generator.
        
        Args:
            df: Indexed by date (required for temporal logic).
            n_groups: Partition data into this many groups.
            test_groups: Size of holdout set C(n_groups, test_groups).
            purge_days: Remove this many days before/after test.
            embargo_days: Additional embargo window (prevents leakage).
            config: AppConfig for DEFAULT_* values.
        """
        if not isinstance(df.index, pd.DatetimeIndex):
            raise ValueError("DataFrame must be indexed by date")
        
        self.df = df.sort_index()
        self.n_groups = n_groups
        self.test_groups = test_groups
        self.purge_gap = pd.Timedelta(days=purge_days)
        self.embargo_gap = pd.Timedelta(days=embargo_days)
        self.logger = get_logger(__name__)
    
    def generate_splits(self) -> Generator[Tuple[pd.DataFrame, pd.DataFrame], None, None]:
        """Generate all CPCV splits.
        
        Yields:
            (train_df, test_df): Train/test DataFrames for each split.
        
        Notes:
            - All indices are date-based (temporal order preserved)
            - Training set is ALWAYS before test set
            - No data leakage between folds
        """
        # Split index into groups
        indices = self._split_into_groups()
        
        # Generate all C(n_groups, test_groups) combinations
        from itertools import combinations
        
        group_ids = list(range(self.n_groups))
        for test_combo in combinations(group_ids, self.test_groups):
            # Extract test indices
            test_indices = []
            for group_id in test_combo:
                test_indices.extend(indices[group_id])
            
            # Separate test set
            test_df = self.df.loc[test_indices]
            
            # Initialize train set (all data except test)
            train_df = self.df.drop(index=test_indices)
            
            # Apply purge & embargo gaps
            train_df = self._apply_purge_embargo(
                train_df, test_df, 
                self.purge_gap, self.embargo_gap
            )
            
            self.logger.debug(
                f"Generated CPCV split: "
                f"test_groups={test_combo}, "
                f"train_rows={len(train_df)}, "
                f"test_rows={len(test_df)}"
            )
            
            yield train_df, test_df
    
    def _split_into_groups(self) -> List[List[pd.Timestamp]]:
        """Split DataFrame index into n_groups temporal groups.
        
        Returns:
            List of index lists, one per group.
        
        Notes:
            - Each group contains roughly equal number of rows
            - Groups are contiguous in time (no shuffling)
        """
        n = len(self.df)
        group_size = n // self.n_groups
        
        indices = np.array_split(self.df.index, self.n_groups)
        
        return [list(idx) for idx in indices]
    
    def _apply_purge_embargo(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        purge_gap: pd.Timedelta,
        embargo_gap: pd.Timedelta
    ) -> pd.DataFrame:
        """Remove dates adjacent to test set from training.
        
        Args:
            train_df: Training set (before purging).
            test_df: Test set (determines removal zones).
            purge_gap: Distance in days to remove (look-ahead prevention).
            embargo_gap: Additional distance (data leakage prevention).
        
        Returns:
            Training set with purged dates removed.
        
        Logic:
            - test_min_date = earliest date in test set
            - test_max_date = latest date in test set
            - Remove train data where:
              * date >= (test_min_date - purge_gap - embargo_gap)
              * AND date <= (test_max_date + purge_gap + embargo_gap)
        
        Rationale:
            - Purge gap: prevents look-ahead (future prices leak into past features)
            - Embargo gap: prevents data snooping (prevents fitting on test-adjacent data)
        """
        test_min = test_df.index.min()
        test_max = test_df.index.max()
        
        # Define removal window
        removal_start = test_min - purge_gap - embargo_gap
        removal_end = test_max + purge_gap + embargo_gap
        
        # Keep only dates outside removal window
        mask = (train_df.index < removal_start) | (train_df.index > removal_end)
        purged_train = train_df.loc[mask]
        
        removed_count = len(train_df) - len(purged_train)
        self.logger.debug(
            f"Purged {removed_count} rows from training set "
            f"({removed_count/len(train_df)*100:.1f}%)"
        )
        
        return purged_train
```

#### 2.2.2 CPCV Statistics

**Function: `validate_cpcv_splits()`**

```python
def validate_cpcv_splits(
    train_test_pairs: List[Tuple[pd.DataFrame, pd.DataFrame]],
    verbose: bool = True
) -> Dict[str, float]:
    """Validate CPCV splits for temporal integrity.
    
    Args:
        train_test_pairs: List of (train_df, test_df) tuples from splits.
        verbose: Print summary statistics.
    
    Returns:
        Dict with validation metrics:
        {
            'avg_overlap_days': float,  # Should be 0
            'min_train_date_before_test': bool,
            'max_train_date_before_test': bool,
            'total_folds': int,
            'avg_train_rows': int,
            'avg_test_rows': int
        }
    
    Checks:
        1. No date overlap between train and test
        2. All training dates are before test dates
        3. Purge/embargo gaps present
    """
    stats = {
        'total_folds': len(train_test_pairs),
        'overlaps': 0,
        'train_after_test': 0,
        'train_sizes': [],
        'test_sizes': [],
        'test_date_diffs': []
    }
    
    for train_df, test_df in train_test_pairs:
        train_dates = train_df.index
        test_dates = test_df.index
        
        # Check for overlap
        overlap = train_dates.intersection(test_dates)
        if len(overlap) > 0:
            stats['overlaps'] += 1
        
        # Check temporal ordering
        if train_dates.max() > test_dates.min():
            stats['train_after_test'] += 1
        
        # Record sizes
        stats['train_sizes'].append(len(train_df))
        stats['test_sizes'].append(len(test_df))
        stats['test_date_diffs'].append((test_dates.max() - test_dates.min()).days)
    
    stats['avg_train_rows'] = np.mean(stats['train_sizes'])
    stats['avg_test_rows'] = np.mean(stats['test_sizes'])
    
    if verbose:
        print(f"CPCV Validation:")
        print(f"  Folds: {stats['total_folds']}")
        print(f"  Overlaps: {stats['overlaps']} (expected 0)")
        print(f"  Train after test: {stats['train_after_test']} (expected 0)")
        print(f"  Avg train rows: {stats['avg_train_rows']:.0f}")
        print(f"  Avg test rows: {stats['avg_test_rows']:.0f}")
    
    return stats
```

---

## 3. Out-of-Core Data Iterator for XGBoost

### 3.1 Module: `tournament/data_iterator.py`

**File: `tournament/data_iterator.py`**

#### 3.1.1 ParquetDataIter Class

**Class: `ParquetDataIter`**

```python
import pyarrow.parquet as pq
import xgboost as xgb
from typing import List

class ParquetDataIter(xgb.DataIter):
    """Zero-copy XGBoost data iterator for Parquet files.
    
    Design:
        - Reads Parquet row-groups sequentially
        - No full file load into memory
        - Direct feed to XGBoost DMatrix
        - Memory footprint = 1 row-group at a time
    
    Attributes:
        file_path: Path to Parquet file.
        features: List of feature column names.
        target_col: Target column name (label).
        pf: ParquetFile object (maintains row-group index).
        num_row_groups: Total row groups in file.
        it: Current row-group iterator index.
    
    Methods:
        __init__: Initialize iterator.
        reset: Rewind to start.
        next: Load next row-group into DMatrix.
    """
    
    def __init__(
        self,
        file_path: str,
        features: List[str],
        target_col: str,
        on_host: bool = True
    ):
        """Initialize ParquetDataIter.
        
        Args:
            file_path: Path to Parquet file.
            features: Feature column names.
            target_col: Target (label) column name.
            on_host: If True, keep data in host memory (CPU).
                     If False, can stream to GPU via XGBoost.
        
        Notes:
            - Requires Parquet file with explicit row-groups
            - PyArrow handles zero-copy column access
        """
        super().__init__(on_host=on_host)
        
        self.file_path = file_path
        self.features = features
        self.target_col = target_col
        
        # Open ParquetFile (doesn't load data)
        self.pf = pq.ParquetFile(file_path)
        self.num_row_groups = self.pf.num_row_groups
        self.it = 0
        
        logger = get_logger(__name__)
        logger.info(
            f"Initialized ParquetDataIter: "
            f"{self.num_row_groups} row-groups, "
            f"{len(features)} features"
        )
    
    def reset(self) -> None:
        """Rewind iterator to start.
        
        Notes:
            - Called by XGBoost for repeated cross-validation
            - No data reload (just reset counter)
        """
        self.it = 0
    
    def next(self, input_data: Callable) -> int:
        """Load next row-group and feed to XGBoost.
        
        Args:
            input_data: Callback function provided by XGBoost.
                       Called as: input_data(data=features_table, label=label_table)
        
        Returns:
            1: More data available (loaded this row-group)
            0: End of iteration (no more row-groups)
        
        Flow:
            1. Check if more row-groups exist
            2. If yes: read row-group from disk
            3. Extract features & label columns (PyArrow → Arrow Table)
            4. Pass to XGBoost via input_data callback
            5. Increment iterator
            6. Return 1
        
        Notes:
            - Zero-copy: PyArrow Table returned directly
            - XGBoost converts to DMatrix internally
            - Row-group stays in RAM only during XGBoost processing
        """
        if self.it == self.num_row_groups:
            return 0  # No more data
        
        # Read row-group from disk
        chunk_table = self.pf.read_row_group(
            self.it,
            columns=self.features + [self.target_col]
        )
        
        # Extract features and label
        features_table = chunk_table.select(self.features)
        label_table = chunk_table.select([self.target_col])
        
        # Feed to XGBoost
        input_data(data=features_table, label=label_table)
        
        self.it += 1
        return 1  # More data available
```

#### 3.1.2 Usage Pattern

```python
# Training setup
train_path = "data/train_fold_1.parquet"
features = ['atr', 'adv_20', 'volatility', 'sentiment_score', ...]
target = 'target_label'

# Create iterator (doesn't load data)
train_iter = ParquetDataIter(train_path, features, target)

# Feed to XGBoost (loads row-groups on-demand)
dtrain = xgb.ExtMemQuantileDMatrix(
    train_iter,
    cache_host_ratio=0.75  # 75% histogram cache in RAM
)

# Train (XGBoost calls iter.next() internally)
booster = xgb.train(params, dtrain, num_boost_round=100)
```

### 3.2 DMatrix Variants for Memory Management

**Class: `DMatrixSelector`**

```python
def create_dmatrix(
    data_source,  # ParquetDataIter or DataFrame
    label_source=None,
    cache_host_ratio: float = 0.75,
    use_sparse: bool = False,
    use_quantile: bool = True
) -> xgb.DMatrix:
    """Select appropriate DMatrix variant based on memory constraints.
    
    Args:
        data_source: ParquetDataIter or DataFrame.
        cache_host_ratio: Fraction of histogram cache in RAM (vs GPU).
        use_sparse: If True, use sparse matrix format (saves RAM).
        use_quantile: If True, use QuantileDMatrix (histogram-based).
    
    Returns:
        Appropriate DMatrix variant:
        - ExtMemQuantileDMatrix: Out-of-core + quantile + VRAM adaptive
        - QuantileDMatrix: In-memory + quantile (fast)
        - DMatrix: Standard (requires all data in RAM)
    
    Logic:
        1. If ParquetDataIter: use ExtMemQuantileDMatrix
        2. Else if in-memory size > 5GB: use QuantileDMatrix
        3. Else: use standard DMatrix
    """
    if isinstance(data_source, ParquetDataIter):
        return xgb.ExtMemQuantileDMatrix(
            data_source,
            cache_host_ratio=cache_host_ratio
        )
    elif isinstance(data_source, pd.DataFrame):
        data_size_gb = data_source.memory_usage(deep=True).sum() / 1e9
        if data_size_gb > 5.0:
            return xgb.QuantileDMatrix(data_source, label=label_source)
        else:
            return xgb.DMatrix(data_source, label=label_source)
    else:
        raise ValueError(f"Unsupported data source: {type(data_source)}")
```

---

## 4. XGBoost Training with Asymmetric Loss

### 4.1 Module: `tournament/training.py`

**File: `tournament/training.py`**

#### 4.1.1 Asymmetric Financial Loss Objective

**Function: `asymmetric_financial_loss()`**

```python
def asymmetric_financial_loss(
    preds: np.ndarray,
    dtrain: xgb.DMatrix,
    penalty_fp: float = 5.0,
    penalty_fn: float = 1.0
) -> Tuple[np.ndarray, np.ndarray]:
    """Custom objective: Penalize false positives 5x more than false negatives.
    
    Args:
        preds: Raw logit predictions from XGBoost.
        dtrain: DMatrix containing labels.
        penalty_fp: Multiplier for false positive gradient/hessian.
        penalty_fn: Multiplier for false negative gradient/hessian.
    
    Returns:
        (grad, hess): Gradients and Hessians for XGBoost to use in updates.
    
    Formula (Binary Cross-Entropy with Asymmetric Weights):
        - Convert logits to probabilities: p = 1 / (1 + exp(-preds))
        - Base BCE gradient: grad = p - y (where y ∈ {0, 1})
        - Base BCE hessian: hess = p * (1 - p)
        - **Asymmetric scaling**:
          * If y == 0 (negative, False Positive): grad *= penalty_fp, hess *= penalty_fp
          * If y == 1 (positive, False Negative): grad *= penalty_fn, hess *= penalty_fn
    
    Rationale:
        - False Positive (model predicts BUY, stock falls): Direct capital loss
        - False Negative (model predicts SKIP, stock rises): Opportunity cost
        - In trading, capital preservation > opportunity hunting
        - Penalty_fp = 5× prevents overconfident BUY signals
    
    Notes:
        - XGBoost uses grad & hess to guide tree splits
        - Higher penalty → more cautious on that class
        - Custom objectives allow domain-specific loss functions
    
    Example Scenario:
        Label = 0 (negative day), Prediction = 0.8 (model thinks it's positive)
        - Base grad = 0.8 - 0 = 0.8
        - Asymmetric grad = 0.8 × 5.0 = 4.0
        - Tree will penalize this prediction more heavily
        - Next tree will try harder to get negatives right
    """
    labels = dtrain.get_label()
    
    # Convert logits to probabilities
    preds_prob = 1.0 / (1.0 + np.exp(-preds))
    
    # Base gradient and hessian (BCE)
    grad = preds_prob - labels
    hess = preds_prob * (1.0 - preds_prob)
    
    # Apply asymmetric penalties
    # labels == 0 → False Positive penalty
    # labels == 1 → False Negative penalty
    grad = np.where(labels == 0, grad * penalty_fp, grad * penalty_fn)
    hess = np.where(labels == 0, hess * penalty_fp, hess * penalty_fn)
    
    return grad, hess
```

#### 4.1.2 XGBoost Training Pipeline

**Class: `XGBoostTrainer`**

```python
class XGBoostTrainer:
    """Orchestrates XGBoost model training with Asymmetric Loss.
    
    Methods:
        train_single_fold: Train one XGBoost model on a fold.
        train_grid_search: Hyperparameter grid search with CPCV.
        save_model: Serialize trained model + feature metadata.
    """
    
    def __init__(self, config: AppConfig):
        """Initialize trainer.
        
        Args:
            config: AppConfig with XGBoost parameters.
        """
        self.config = config
        self.logger = get_logger(__name__)
    
    def train_single_fold(
        self,
        train_df: pd.DataFrame,
        test_df: pd.DataFrame,
        features: List[str],
        target: str,
        params: Dict[str, Any],
        num_boost_round: int = 100
    ) -> Tuple[xgb.Booster, np.ndarray]:
        """Train single XGBoost model on one fold.
        
        Args:
            train_df: Training DataFrame (from CPCV).
            test_df: Test DataFrame (from CPCV).
            features: List of feature column names.
            target: Target column name.
            params: XGBoost hyperparameters:
                {
                    'max_depth': 3,
                    'learning_rate': 0.05,
                    'subsample': 0.8,
                    'colsample_bytree': 0.8,
                    'tree_method': 'gpu_hist',
                    'device': 'cuda',
                    'objective': 'binary:logistic'  # (or custom)
                }
            num_boost_round: Number of boosting rounds.
        
        Returns:
            (booster: Trained model, test_predictions: Probability predictions on test)
        
        Flow:
            1. Write train_df to temp Parquet (row-grouped)
            2. Create ParquetDataIter for zero-copy
            3. Create ExtMemQuantileDMatrix
            4. Train with custom objective (asymmetric_financial_loss)
            5. Infer on test set
            6. Return booster + predictions
        
        Notes:
            - Training data written with row-groups for iterator
            - Memory efficient: loaded row-group by row-group
            - GPU acceleration via tree_method='gpu_hist'
        """
        import tempfile
        
        self.logger.info(f"Training XGBoost: {len(train_df)} train rows, {len(test_df)} test rows")
        
        # Write training data to temporary Parquet
        temp_train_path = f"/tmp/xgb_train_{id(train_df)}.parquet"
        try:
            train_df.to_parquet(
                temp_train_path,
                engine='pyarrow',
                row_group_size=self.config.data.row_group_size
            )
            
            # Create data iterator
            train_iter = ParquetDataIter(temp_train_path, features, target)
            
            # Create DMatrix
            dtrain = xgb.ExtMemQuantileDMatrix(
                train_iter,
                cache_host_ratio=0.75
            )
            
            # Update params for asymmetric loss
            params['objective'] = asymmetric_financial_loss
            params['disable_default_eval_metric'] = 1
            
            # Train
            evals = [(dtrain, 'train')]
            booster = xgb.train(
                params,
                dtrain,
                num_boost_round=num_boost_round,
                evals=evals,
                verbose_eval=False
            )
            
            # Predict on test set
            dtest = xgb.DMatrix(test_df[features], label=test_df[target])
            test_preds = booster.predict(dtest)
            
            self.logger.info(f"Training complete: {num_boost_round} rounds")
            
            return booster, test_preds
            
        finally:
            # Cleanup
            if os.path.exists(temp_train_path):
                os.remove(temp_train_path)
    
    def save_model(
        self,
        booster: xgb.Booster,
        model_path: str,
        features: List[str],
        features_path: str,
        metadata: Dict[str, Any] = None
    ) -> None:
        """Save model and metadata to disk.
        
        Args:
            booster: Trained XGBoost model.
            model_path: Where to save model JSON.
            features: Feature column names.
            features_path: Where to save feature list.
            metadata: Additional metadata (sector, params, etc.).
        
        Outputs:
            - model.json: XGBoost model (can load with booster.load_model)
            - features.json: Feature list + metadata
        
        Notes:
            - JSON format allows inspection
            - Features list essential for inference (must match training)
        """
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        os.makedirs(os.path.dirname(features_path), exist_ok=True)
        
        # Save model
        booster.save_model(model_path)
        
        # Save features + metadata
        feature_manifest = {
            'features': features,
            'n_features': len(features),
            'metadata': metadata or {}
        }
        
        with open(features_path, 'w') as f:
            json.dump(feature_manifest, f, indent=2)
        
        self.logger.info(f"Saved model: {model_path}, features: {features_path}")
```

---

## 5. Risk Simulation & Backtest Returns

### 5.1 Module: `tournament/risk_simulator.py`

**File: `tournament/risk_simulator.py`**

#### 5.1.1 Risk Manager Simulation

**Function: `simulate_backtest_returns()`**

```python
from features.shields import evaluate_risk_veto_gates

def simulate_backtest_returns(
    test_df: pd.DataFrame,
    predictions: np.ndarray,
    confidence_threshold: float = 0.65,
    config: AppConfig = None
) -> np.ndarray:
    """Simulate backtest returns using Shield Agent risk gates.
    
    Args:
        test_df: Test set DataFrame (with OHLCV + features).
        predictions: Model predictions (probabilities).
        confidence_threshold: Threshold for generating signal (e.g., 0.65).
        config: AppConfig with risk parameters.
    
    Returns:
        Array of simulated returns per row.
    
    Flow (per row):
        1. If prediction > threshold: signal = 1 (BUY)
        2. Else: signal = 0 (SKIP)
        3. If signal == 1:
           a. Query Shield Agent with current row's risk metrics
           b. If approved: calculate position P&L
           c. If veto'd: return = 0 (no trade)
        4. If signal == 0: return = 0 (no trade)
    
    Formula (if signal & approved):
        - entry = close[t]
        - stop = entry - (atr_multiplier × atr[t])
        - risk_distance = entry - stop
        - size = (capital × max_risk) / risk_distance
        - If low[t+1] <= stop:
          * return = -risk_distance × size (hit stop)
        - Else:
          * return = (close[t+1] - entry) / entry × size (daily P&L)
    
    Notes:
        - Returns are forward-shifted (entry at t, exit at t+1)
        - No look-ahead bias (uses only t's data for signal)
        - Shield Agent prevents over-sizing
    """
    n = len(test_df)
    returns = np.zeros(n)
    veto_counts = {'stop_loss': 0, 'size': 0, 'liquidity': 0, 'slippage': 0}
    
    logger = get_logger(__name__)
    
    for i in range(n - 1):  # Can't trade last bar (no exit)
        pred = predictions[i]
        signal = 1 if pred > confidence_threshold else 0
        
        if signal == 0:
            returns[i] = 0.0
            continue
        
        # Extract current row features
        close = test_df['close'].iloc[i]
        atr = test_df['atr'].iloc[i]
        adv_20 = test_df['adv_20'].iloc[i]
        volume_today = test_df['volume'].iloc[i]
        volatility = test_df['volatility'].iloc[i]
        
        # Query Shield Agent
        approved, position_size = evaluate_risk_veto_gates(
            entry_price=close,
            atr=atr,
            atr_multiplier=config.execution.atr_stop_multiplier,
            account_capital=100000.0,  # Fixed capital for backtest
            max_risk_pct=config.execution.max_risk_per_trade,
            current_qty=0.0,  # Assume flat
            adv_20=adv_20,
            volume_today=volume_today,
            volatility=volatility
        )
        
        if not approved:
            returns[i] = 0.0
            veto_counts['size'] += 1
            continue
        
        # Calculate P&L
        entry = close
        stop_loss = entry - (config.execution.atr_stop_multiplier * atr)
        risk_per_share = entry - stop_loss
        
        # Next bar's prices
        low_next = test_df['low'].iloc[i + 1]
        close_next = test_df['close'].iloc[i + 1]
        
        # Check if hit stop
        if low_next <= stop_loss:
            # Hit stop loss
            returns[i] = -risk_per_share / entry * position_size
        else:
            # Normal exit at close
            pnl_per_share = (close_next - entry) / entry
            returns[i] = pnl_per_share * position_size
    
    logger.info(f"Backtest simulation complete: {np.sum(np.abs(returns) > 0):.0f} trades")
    
    return returns
```

#### 5.1.2 Fold Statistics

**Function: `calculate_fold_statistics()`**

```python
def calculate_fold_statistics(returns: np.ndarray) -> Dict[str, float]:
    """Calculate performance metrics for a single fold.
    
    Args:
        returns: Array of returns from backtest.
    
    Returns:
        Dict with metrics:
        {
            'total_return': float,
            'annual_return': float,
            'sharpe_ratio': float,
            'max_drawdown': float,
            'win_rate': float,
            'n_trades': int
        }
    """
    n_trades = np.sum(np.abs(returns) > 1e-6)
    cumulative = np.cumprod(1 + returns)
    
    if n_trades == 0:
        return {
            'total_return': 0.0,
            'annual_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'n_trades': 0
        }
    
    # Sharpe Ratio (assuming 252 trading days)
    mean_ret = np.mean(returns[returns != 0])
    std_ret = np.std(returns[returns != 0])
    sharpe = (mean_ret / std_ret) * np.sqrt(252) if std_ret > 0 else 0.0
    
    # Max Drawdown
    running_max = np.maximum.accumulate(cumulative)
    drawdown = (cumulative - running_max) / running_max
    max_dd = np.min(drawdown)
    
    # Win Rate
    winning_trades = np.sum(returns[returns != 0] > 0)
    win_rate = winning_trades / n_trades if n_trades > 0 else 0.0
    
    return {
        'total_return': cumulative[-1] - 1,
        'annual_return': cumulative[-1] ** (252 / len(returns)) - 1,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd,
        'win_rate': win_rate,
        'n_trades': int(n_trades)
    }
```

---

## 6. Hyperparameter Grid Search

### 6.1 Module: `tournament/grid_search.py`

**File: `tournament/grid_search.py`**

#### 6.1.1 Grid Search Over Sectors

**Class: `HyperparameterGridSearch`**

```python
class HyperparameterGridSearch:
    """Execute grid search over hyperparameters + CPCV folds.
    
    Methods:
        generate_parameter_grid: Create all param combinations.
        execute_grid_search: Run training for each combo.
        select_best_params: Choose params with highest OOS Sharpe.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
    
    def generate_parameter_grid(self) -> List[Dict[str, Any]]:
        """Generate all hyperparameter combinations.
        
        Returns:
            List of param dictionaries.
        
        Grid:
            - max_depth: [1, 2, 3]
            - learning_rate: [0.01, 0.05, 0.1]
            - subsample: [0.8]
            - colsample_bytree: [0.8]
            - Total combinations: 3 × 3 = 9
        
        Each combo includes:
            - tree_method: 'gpu_hist' (GPU acceleration)
            - device: 'cuda'
            - num_leaves: 2^max_depth
        """
        from itertools import product
        
        depth_range = [1, 2, 3]
        lr_range = [0.01, 0.05, 0.1]
        
        combos = []
        for depth, lr in product(depth_range, lr_range):
            combos.append({
                'max_depth': depth,
                'learning_rate': lr,
                'subsample': 0.8,
                'colsample_bytree': 0.8,
                'tree_method': 'gpu_hist',
                'device': 'cuda'
            })
        
        self.logger.info(f"Generated {len(combos)} parameter combinations")
        return combos
    
    def execute_grid_search(
        self,
        cpcv_splits: Generator,
        features: List[str],
        target: str,
        num_boost_round: int = 100
    ) -> pd.DataFrame:
        """Execute grid search across all param combos + CPCV folds.
        
        Args:
            cpcv_splits: Generator yielding (train_df, test_df) tuples.
            features: Feature column names.
            target: Target column name.
            num_boost_round: Boosting rounds per model.
        
        Returns:
            DataFrame with results:
            {
                'param_combo': int (which combo)
                'fold': int (which CPCV fold)
                'sharpe': float (OOS Sharpe on this fold)
                'max_drawdown': float
                'n_trades': int
                'avg_win_rate': float
            }
        
        Notes:
            - For each param combo: train on all folds
            - Accumulates returns across folds
            - Final Sharpe computed from all OOS returns
        """
        param_grid = self.generate_parameter_grid()
        
        all_results = []
        
        for param_idx, params in enumerate(param_grid):
            self.logger.info(f"Training combo {param_idx + 1}/{len(param_grid)}: {params}")
            
            trainer = XGBoostTrainer(self.config)
            fold_returns = []
            
            for fold_idx, (train_df, test_df) in enumerate(cpcv_splits):
                self.logger.debug(f"  Fold {fold_idx + 1}")
                
                booster, test_preds = trainer.train_single_fold(
                    train_df, test_df, features, target, params, num_boost_round
                )
                
                # Simulate returns on test fold
                fold_rets = simulate_backtest_returns(
                    test_df, test_preds, 
                    confidence_threshold=self.config.execution.confidence_threshold,
                    config=self.config
                )
                
                fold_returns.extend(fold_rets[fold_rets != 0])
            
            # Compute statistics
            if fold_returns:
                combo_stats = calculate_fold_statistics(np.array(fold_returns))
                combo_stats['param_combo'] = param_idx
                combo_stats['param_dict'] = str(params)
                all_results.append(combo_stats)
        
        results_df = pd.DataFrame(all_results)
        
        # Sort by Sharpe
        results_df = results_df.sort_values('sharpe_ratio', ascending=False)
        
        self.logger.info(f"Grid search complete. Best Sharpe: {results_df.iloc[0]['sharpe_ratio']:.3f}")
        
        return results_df
```

---

## 7. Tournament Director

### 7.1 Module: `tournament/director.py`

**File: `tournament/director.py`**

#### 7.1.1 Modular Tournament Director

**Class: `ModularTournamentDirector`**

```python
class ModularTournamentDirector:
    """Orchestrates full tournament for a sector.
    
    Methods:
        execute_gauntlet: Full tournament pipeline for sector.
        run_sector_tournament: Single sector tournament.
    """
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = get_logger(__name__)
    
    def run_sector_tournament(self, sector: str) -> Dict[str, Any]:
        """Run full tournament for one sector.
        
        Args:
            sector: Sector name (e.g., "Technology").
        
        Returns:
            {
                'sector': str,
                'best_params': Dict,
                'best_sharpe': float,
                'candidate_model_path': str,
                'features_path': str,
                'all_results': pd.DataFrame
            }
        
        Flow:
            1. Load processed vault for sector
            2. Generate CPCV splits
            3. Execute hyperparameter grid search
            4. Select best params (highest OOS Sharpe)
            5. Train final model on full data (using best params)
            6. Save to candidate registry
            7. Return metadata
        """
        self.logger.info(f"Starting tournament for {sector}")
        
        # Load data
        vault_path = f"{self.config.data.processed_vault_dir}/sector={sector}"
        df = pd.read_parquet(f"{vault_path}/*.parquet")
        df = df.sort_index()  # Ensure temporal order
        
        self.logger.info(f"Loaded {len(df)} rows for {sector}")
        
        # CPCV split generation
        cpcv_gen = CPCVSplitGenerator(
            df,
            n_groups=6,
            test_groups=2,
            purge_days=5,
            embargo_days=5,
            config=self.config
        )
        
        # Grid search
        grid_search = HyperparameterGridSearch(self.config)
        
        # Collect splits for grid search (convert generator to list)
        splits_list = list(cpcv_gen.generate_splits())
        
        results_df = grid_search.execute_grid_search(
            cpcv_splits=iter(splits_list),
            features=[c for c in df.columns if c not in self.config.data.metadata_cols],
            target='target_label',
            num_boost_round=100
        )
        
        # Select best params
        best_row = results_df.iloc[0]
        best_params = ast.literal_eval(best_row['param_dict'])
        
        self.logger.info(f"Best params for {sector}: {best_params}")
        self.logger.info(f"Best OOS Sharpe: {best_row['sharpe_ratio']:.3f}")
        
        # Train final model on all data
        trainer = XGBoostTrainer(self.config)
        booster, _ = trainer.train_single_fold(
            train_df=df,
            test_df=df.iloc[-100:],  # Dummy test (not used for eval)
            features=[c for c in df.columns if c not in self.config.data.metadata_cols],
            target='target_label',
            params=best_params,
            num_boost_round=100
        )
        
        # Save candidate model
        candidate_model_path = f"{self.config.models.candidate_models_dir}/{sector}_candidate.json"
        candidate_features_path = f"{self.config.models.candidate_models_dir}/{sector}_candidate_features.json"
        
        trainer.save_model(
            booster,
            candidate_model_path,
            features=[c for c in df.columns if c not in self.config.data.metadata_cols],
            features_path=candidate_features_path,
            metadata={'sector': sector, 'params': best_params}
        )
        
        return {
            'sector': sector,
            'best_params': best_params,
            'best_sharpe': float(best_row['sharpe_ratio']),
            'candidate_model_path': candidate_model_path,
            'features_path': candidate_features_path,
            'all_results': results_df
        }
    
    def execute_gauntlet(self) -> Dict[str, Dict]:
        """Execute tournament for all sectors.
        
        Returns:
            Dict mapping sector → tournament results.
        """
        sectors = ['Technology', 'Healthcare', 'Financials', ...]  # From universe
        
        results = {}
        for sector in sectors:
            try:
                sector_result = self.run_sector_tournament(sector)
                results[sector] = sector_result
            except Exception as e:
                self.logger.error(f"Tournament failed for {sector}: {e}", exc_info=True)
        
        self.logger.info(f"Tournament complete: {len(results)} sectors processed")
        
        return results
```

---

## 8. Implementation Checklist - Phase 3

### Week 1: CPCV & Data Iterator

- [ ] **Day 1-2**: CPCV implementation
  - [ ] Implement `CPCVSplitGenerator` class
  - [ ] Implement purge/embargo gap logic
  - [ ] Unit tests: `test_cpcv.py`
  - [ ] Validate splits (no overlap, proper temporal ordering)

- [ ] **Day 2-3**: ParquetDataIter
  - [ ] Implement `ParquetDataIter` class
  - [ ] Test zero-copy with mock Parquet files
  - [ ] Integration test: Iterator → XGBoost DMatrix
  - [ ] Unit tests: `test_data_iterator.py`

- [ ] **Day 3-4**: Risk simulator
  - [ ] Implement `simulate_backtest_returns()`
  - [ ] Implement fold statistics calculation
  - [ ] Unit tests: `test_risk_simulator.py`

- [ ] **Day 4-5**: XGBoost training
  - [ ] Implement `asymmetric_financial_loss()` objective
  - [ ] Implement `XGBoostTrainer` class
  - [ ] Test custom objective with mock data
  - [ ] Unit tests: `test_training.py`

### Week 2: Grid Search & Tournament Director

- [ ] **Day 6-7**: Grid search
  - [ ] Implement `HyperparameterGridSearch` class
  - [ ] Implement parameter grid generation
  - [ ] Unit tests: `test_grid_search.py`

- [ ] **Day 7-8**: Tournament director
  - [ ] Implement `ModularTournamentDirector` class
  - [ ] Implement sector-level tournament
  - [ ] Unit tests: `test_director.py`

- [ ] **Day 8-9**: Integration & benchmarking
  - [ ] End-to-end integration test (CPCV → training → results)
  - [ ] Performance benchmarking: training speed, memory usage
  - [ ] Verify no look-ahead bias in CPCV splits

- [ ] **Day 9-10**: Validation & optimization
  - [ ] Verify asymmetric loss penalizes FP correctly
  - [ ] Profile training bottlenecks
  - [ ] Optimize if needed (GPU utilization, memory)
  - [ ] Run all tests, verify 85%+ coverage

---

## 9. Success Criteria & Acceptance Tests

### 9.1 Functional Acceptance

| Criterion | Test | Expected |
|-----------|------|----------|
| CPCV no overlap | `test_validate_cpcv_splits()` | ✓ 0 overlaps |
| CPCV temporal order | `test_temporal_ordering()` | ✓ All train before test |
| ParquetDataIter loads | `test_parquet_iterator()` | ✓ Row-groups loaded sequentially |
| XGBoost trains | `test_xgboost_training()` | ✓ Model saves, predicts |
| Asymmetric loss works | `test_asymmetric_objective()` | ✓ FP penalized 5× |
| Backtest sim valid | `test_backtest_returns()` | ✓ No look-ahead, forward-shifted |
| Grid search completes | `test_grid_search_execution()` | ✓ All combos trained |
| Tournament director end-to-end | `test_full_tournament()` | ✓ Sector → candidate model |

### 9.2 Performance Targets

| Component | Metric | Target | Test |
|-----------|--------|--------|------|
| CPCV generation | Speed | 1000 splits/sec | `bench_cpcv_splits.py` |
| ParquetDataIter | Throughput | 100k rows/sec | `bench_data_iterator.py` |
| XGBoost training | Time per fold | < 60 sec | `bench_xgboost_training.py` |
| Risk simulation | Speed | 100k returns/sec | `bench_risk_simulation.py` |
| Full tournament | End-to-end | < 1 hour (sector) | Integration benchmark |

### 9.3 Code Quality

| Criterion | Target |
|-----------|--------|
| Test coverage (tournament/) | ≥ 85% |
| Type hints | 100% (mypy clean) |
| Linting errors | 0 |
| CPCV correctness | 0 overlaps, proper ordering |

---

## 10. Integration Points with Phases 1-2 & Handoff to Phase 4

### 10.1 Phase 1 Dependencies

- Config system: All hyperparams from `AppConfig`
- Logging: All operations logged
- Exception hierarchy: Use custom exceptions
- Testing: Pytest fixtures (config, data)

### 10.2 Phase 2 Dependencies

- Feature outputs: Read from Parquet (Phase 2 output)
- Shield Agent: Integrated into risk simulator
- Slippage model: Available for realistic position sizing

### 10.3 Handoff to Phase 4 (Evaluation)

- Candidate model registry → Phase 4 loads for DSR evaluation
- Feature manifests → Phase 4 needs for inference
- Returns matrices → Phase 4 uses for statistical tests

---

## 11. Deliverables Summary - Phase 3

### Codebase
- [ ] `/new_pipeline/tournament/cpcv.py` (300+ lines)
- [ ] `/new_pipeline/tournament/data_iterator.py` (200+ lines)
- [ ] `/new_pipeline/tournament/training.py` (400+ lines)
- [ ] `/new_pipeline/tournament/risk_simulator.py` (300+ lines)
- [ ] `/new_pipeline/tournament/grid_search.py` (300+ lines)
- [ ] `/new_pipeline/tournament/director.py` (400+ lines)
- [ ] `/new_pipeline/models/registry.py` (model storage)
- [ ] 100+ unit tests + benchmarks

### Performance
- [ ] CPCV prevents all look-ahead bias
- [ ] ParquetDataIter enables 10GB+ training
- [ ] XGBoost trains with asymmetric loss
- [ ] Tournament runs sector in < 1 hour
- [ ] Candidate models ready for evaluation

### Documentation
- [ ] CPCV methodology & validation
- [ ] ParquetDataIter usage guide
- [ ] Asymmetric loss rationale
- [ ] Grid search tuning guide

---

## 12. Quick Reference Commands

```bash
# Generate CPCV splits (validate)
python -c "
from tournament.cpcv import CPCVSplitGenerator, validate_cpcv_splits
import pandas as pd
df = pd.read_parquet('data/processed/sector=Technology')
gen = CPCVSplitGenerator(df)
splits = list(gen.generate_splits())
validate_cpcv_splits(splits, verbose=True)
"

# Test ParquetDataIter
pytest tests/unit/tournament/test_data_iterator.py -v

# Run grid search for sector
python -c "
from tournament.director import ModularTournamentDirector
from config import get_config
config = get_config()
director = ModularTournamentDirector(config)
results = director.run_sector_tournament('Technology')
print(f'Best Sharpe: {results[\"best_sharpe\"]:.3f}')
"

# Benchmark training
pytest tests/benchmarks/bench_xgboost_training.py -v --benchmark-only

# Run all Phase 3 tests
pytest tests/unit/tournament/ tests/integration/tournament/ --cov=tournament --cov-report=html
```

---

**Next**: After Phase 3 completion, proceed to [Phase 4: Statistical Evaluation & Model Promotion](PHASE_4_SPECIFICATION.md) (to be created).

**Previous Phases**:
- [Phase 1: Core Pipeline Infrastructure](PHASE_1_SPECIFICATION.md)
- [Phase 2: Vectorized Quant Engine & Shields](PHASE_2_SPECIFICATION.md)
