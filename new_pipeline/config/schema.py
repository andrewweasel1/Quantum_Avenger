from pydantic import BaseModel, Field


class DataConfig(BaseModel):
    raw_vault_dir: str
    processed_vault_dir: str
    parquet_blocksize: str
    row_group_size: int
    validation_mode: str


class FeatureConfig(BaseModel):
    cache_enabled: bool
    gpu_enabled: bool
    batch_size: int
    metadata_dir: str
    slippage_constant: float = 0.5
    regime_percentile: float = 0.8
    bps_scaler: float = 10000.0
    max_slippage_bps: float = 50.0
    crash_window: int = 60
    label_horizon: int = 1
    label_cost_bps: float = 10.0
    label_method: str = "triple_barrier"  # "triple_barrier" | "friction"
    label_pt_mult: float = 2.0  # profit-take barrier in ATR units
    label_sl_mult: float = 2.0  # stop-loss barrier in ATR units (mirrors execution stop)


class ModelConfig(BaseModel):
    prod_models_dir: str
    candidate_models_dir: str
    model_version: str


class ExecutionConfig(BaseModel):
    max_risk_per_trade: float
    atr_stop_multiplier: float
    confidence_threshold: float
    max_adv_coverage: float = 0.25
    ledger_dir: str = "./data/ledger"
    max_retries: int = 3
    tif: str = "day"
    account_capital: float = 100_000.0


class LoggingConfig(BaseModel):
    level: str
    format: str
    log_file: str
    max_bytes: int
    json_logs: bool = False
    trace_enabled: bool = True


class FusionConfig(BaseModel):
    enabled: bool
    ollama_endpoint: str
    llm_model_name: str
    sentiment_timeout: float
    semaphore_limit: int
    verdict_model: str = "qwen-3"
    sentiment_model: str = "ProsusAI/finbert"  # FinBERT weights (live sentiment engine)
    spacy_model: str = "en_core_web_lg"  # spaCy NER model (live anonymizer)
    mask_for_scorer: bool = False  # FinBERT trained WITH names; mask only for the LLM


class GPUConfig(BaseModel):
    cuda_enabled: bool = False
    device: str = "cpu"
    fallback_to_cpu: bool = True


class TournamentConfig(BaseModel):
    n_groups: int = 6
    test_groups: int = 2
    purge_days: int = 5
    embargo_days: int = 5
    embargo_pct: float = 0.0  # fractional embargo: ceil(pct * n_samples) positions
    penalty_fp: float = 5.0
    penalty_fn: float = 1.0
    num_boost_round: int = 100
    early_stopping_rounds: int = 25
    cache_host_ratio: float = 0.75
    tree_method: str = "hist"
    device: str = "cpu"
    max_workers: int = 1
    cfs_distance_threshold: float = 0.5
    cfs_min_importance: float = 0.0
    feature_selection_method: str = "causal"  # | "clustered_permutation"
    causal_alpha: float = 0.10  # BHY-adjusted p-value keep threshold (Granger screen)
    causal_granger_lags: int = 3  # Granger AR / feature lag order
    sample_weighting: str = "uniqueness"  # | "none" — LdP uniqueness weights for overlapping labels
    sectors: list[str] = Field(default_factory=list)


class EvaluationConfig(BaseModel):
    dsr_promotion_threshold: float = 0.95
    hmm_states: int = 3
    hmm_n_iter: int = 100
    synthetic_sr_min: float = 0.0
    registry_path: str = "./models/prod/promotion_registry.json"
    psr_benchmark_sr: float = 0.0
    pbo_threshold: float = 0.5
    pbo_partitions: int = 10
    mt_method: str = "bhy"
    enforce_minbtl: bool = False
    # Sentiment-fusion (offline core): correlation-adjusted deflation + per-regime DSR.
    use_effective_trials: bool = True
    regime_gate_enabled: bool = False
    min_regime_obs: int = 60
    thin_regime_policy: str = "skip"
    # CPCV backtest-path DSR gate: require >= cpcv_path_min_fraction of the phi
    # reconstructed paths to clear dsr_promotion_threshold individually.
    cpcv_path_gate_enabled: bool = True
    cpcv_path_min_fraction: float = 0.5


class MCPConfig(BaseModel):
    transport: str = "stdio"


class RAGConfig(BaseModel):
    embedder: str = "hashing"
    top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 100


class NewsConfig(BaseModel):
    """Point-in-time news feed: offline fixture + live providers (GDELT/EDGAR)."""

    providers: list[str] = Field(default_factory=lambda: ["gdelt"])  # live composite order
    fixture_path: str = ""  # offline StaticNewsSource; "" -> packaged data/news/headlines.csv
    vault_dir: str = "./data/raw/news"
    limit: int = 20
    gdelt_endpoint: str = "https://api.gdeltproject.org/api/v2/doc/doc"
    edgar_forms: list[str] = Field(default_factory=lambda: ["8-K", "10-Q", "10-K"])
    edgar_identity: str = ""  # SEC requires a "Name email" User-Agent identity


class DashboardConfig(BaseModel):
    veto_ledger_path: str = "./data/ledger/veto_ledger.parquet"
    trade_log_path: str = "./data/ledger/trade_log.parquet"
    refresh_seconds: int = 5
    max_drawdown_alert: float = 0.15
    min_sharpe_alert: float = 0.0
    max_veto_rate_alert: float = 0.5
    auth_enabled: bool = False


class SystemConfig(BaseModel):
    run_mode: str
    dask_enabled: bool
    num_workers: int
    memory_limit: str


class AlpacaConfig(BaseModel):
    """Live Alpaca credentials/settings. Keys come from QA_ALPACA__* env vars and
    are never committed; dev/test/backtest run on fakes and ignore these."""

    api_key: str = ""
    secret_key: str = ""
    paper: bool = True
    data_feed: str = "iex"  # free feed; "sip" needs a paid subscription


class AppConfig(BaseModel):
    data: DataConfig
    features: FeatureConfig
    models: ModelConfig
    execution: ExecutionConfig
    logging: LoggingConfig
    fusion: FusionConfig
    system: SystemConfig
    gpu: GPUConfig = Field(default_factory=GPUConfig)
    tournament: TournamentConfig = Field(default_factory=TournamentConfig)
    evaluation: EvaluationConfig = Field(default_factory=EvaluationConfig)
    mcp: MCPConfig = Field(default_factory=MCPConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    news: NewsConfig = Field(default_factory=NewsConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    alpaca: AlpacaConfig = Field(default_factory=AlpacaConfig)
