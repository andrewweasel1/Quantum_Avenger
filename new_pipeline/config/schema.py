from pydantic import BaseModel


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


class ModelConfig(BaseModel):
    prod_models_dir: str
    candidate_models_dir: str
    model_version: str


class ExecutionConfig(BaseModel):
    max_risk_per_trade: float
    atr_stop_multiplier: float
    confidence_threshold: float


class LoggingConfig(BaseModel):
    level: str
    format: str
    log_file: str
    max_bytes: int


class FusionConfig(BaseModel):
    enabled: bool
    ollama_endpoint: str
    llm_model_name: str
    sentiment_timeout: float
    semaphore_limit: int


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
