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


class GPUConfig(BaseModel):
    cuda_enabled: bool = False
    device: str = "cpu"
    fallback_to_cpu: bool = True


class TournamentConfig(BaseModel):
    n_groups: int = 6
    test_groups: int = 2
    purge_days: int = 5
    embargo_days: int = 5
    penalty_fp: float = 5.0
    penalty_fn: float = 1.0
    num_boost_round: int = 100
    early_stopping_rounds: int = 25
    cache_host_ratio: float = 0.75
    tree_method: str = "hist"
    device: str = "cpu"
    cfs_distance_threshold: float = 0.5
    cfs_min_importance: float = 0.0
    sectors: list[str] = Field(default_factory=list)


class EvaluationConfig(BaseModel):
    dsr_promotion_threshold: float = 0.95
    hmm_states: int = 3
    hmm_n_iter: int = 100
    synthetic_sr_min: float = 0.0
    registry_path: str = "./models/prod/promotion_registry.json"


class MCPConfig(BaseModel):
    transport: str = "stdio"


class RAGConfig(BaseModel):
    embedder: str = "hashing"
    top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 100


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
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
