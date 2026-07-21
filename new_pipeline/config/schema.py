from pydantic import BaseModel, Field


class DataConfig(BaseModel):
    raw_vault_dir: str
    processed_vault_dir: str
    parquet_blocksize: str
    row_group_size: int
    validation_mode: str
    # Path to a universe membership CSV (ticker,gics_sector,start_date,end_date).
    # Empty -> the packaged 41-name fixture; e.g. new_pipeline/data/universe/sp500.csv.
    universe_path: str = ""


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
    # Cross-sectional alpha factors (offense roadmap P0). Empty => off (pipeline
    # bit-stable); names from features.factors.SUPPORTED_FACTORS.
    factor_set: list[str] = Field(default_factory=list)
    factor_sector_neutral: bool = True  # sector-demean before cross-sectional z-score
    # Missing FUNDAMENTAL factor inputs: "neutral" fills xf_ z-scores with 0.0 so
    # PIT departed names survive drop_nulls; "drop" propagates nulls (legacy).
    factor_null_policy: str = "neutral"
    # Extended per-ticker feature families (offense roadmap P1). Empty => off.
    # Available: fracdiff, vol_estimators, microstructure, garch, overnight,
    # residual, flow (features.extended.SUPPORTED_FAMILIES).
    extended_features: list[str] = Field(default_factory=list)
    # Event-time family (filing clock/drift + news burst). Each subset only
    # materializes when its source is active: filing features need fundamental
    # factors in factor_set; the news burst needs fusion.enabled.
    event_features: bool = False
    # Short-flow family (FINRA daily short-volume): short_ratio + trailing
    # z-score + change. Needs short_volume.vault_path set. Default off.
    short_flow_features: bool = False
    fracdiff_d: float = 0.4  # fractional-differencing order
    fracdiff_threshold: float = 1e-3  # weight-truncation threshold (sets the window width)
    vol_window: int = 20  # range vol-estimator rolling window
    micro_window: int = 20  # microstructure rolling window
    garch_fit_window: int = 252  # in-sample window for the GARCH(1,1) MLE fit


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
    # Charge dynamic hydrodynamic slippage (features.slippage) on the gauntlet's
    # simulated t+1 returns: round-trip cost per fill + a veto above
    # features.max_slippage_bps. Default off keeps the suite/goldens bit-stable;
    # honest net-of-cost validation runs turn it on. account_capital sets the
    # order notional that drives the participation-rate impact.
    backtest_slippage_enabled: bool = False


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
    # "finbert" (neural; needs torch + HF egress) | "vader" (lexicon; no downloads).
    sentiment_backend: str = "finbert"
    # Rolling sentiment-fused HMM regime features (markov_prob_persist_*).
    # ~8s/ticker at 4y daily — disable for index-scale universes; the raw
    # sentiment_score feature still feeds the model either way.
    markov_features: bool = True
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
    penalty_fp: float = 1.0  # symmetric default; see defaults.yaml for the recalibration note
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
    # Meta-labeling (offense roadmap P3): a secondary model on the fired primary
    # signal; records an OOS primary-vs-meta verdict. Default off (diagnostic).
    enable_meta_labeling: bool = False
    meta_threshold: float = 0.5  # meta P(win) cutoff to act on a fired primary signal
    meta_criterion: str = "f1"  # | "precision" — what "improved" means for the verdict
    sectors: list[str] = Field(default_factory=list)


class EvaluationConfig(BaseModel):
    dsr_promotion_threshold: float = 0.95
    hmm_states: int = 3
    synthetic_sr_min: float = 0.0
    registry_path: str = "./models/prod/promotion_registry.json"
    psr_benchmark_sr: float = 0.0
    pbo_threshold: float = 0.5
    pbo_partitions: int = 10
    mt_method: str = "bhy"
    enforce_minbtl: bool = False
    # Sentiment-fusion (offline core): correlation-adjusted deflation + per-regime DSR.
    use_effective_trials: bool = True
    regime_gate_enabled: bool = True  # see defaults.yaml for the calendar-axis note
    # Record the per-decoded-regime DSR/Sharpe/day-share breakdown on EVERY
    # champion registry row (pure observability; one HMM fit per champion).
    regime_breakdown_enabled: bool = True
    min_regime_obs: int = 60
    thin_regime_policy: str = "skip"
    # Family-wise per-state bar: with K testable states each must clear
    # DSR >= dsr_promotion_threshold**K (0.95^3 ~= 0.857) AND have a positive
    # Sharpe. K conjunctive 0.95-tests are jointly ~0.95^K — far stricter than
    # the full-sample gate the per-state rule mirrors; T**K preserves that
    # joint severity while positivity still vetoes regime-concentrated books.
    # False = legacy flat threshold per state.
    regime_family_wise: bool = True
    # CPCV backtest-path DSR gate: require >= cpcv_path_min_fraction of the phi
    # reconstructed paths to clear dsr_promotion_threshold individually.
    cpcv_path_gate_enabled: bool = True
    cpcv_path_min_fraction: float = 0.5
    gauntlet_block_size: int = 10  # stationary-bootstrap avg block len for the HMM gauntlet
    # Per-signal alpha evaluation (offense roadmap P2): universe-wide IC/ICIR
    # diagnostics written to alpha_eval.json. Read-only — never gates promotion.
    alpha_eval_enabled: bool = True
    alpha_eval_min_names: int = 5  # min cross-sectional breadth for a usable IC date
    # White's Reality Check across the grid-search trials (offense roadmap P4 §J):
    # a multiple-testing p-value recorded per sector. Default off (bootstrap cost).
    reality_check_enabled: bool = False
    reality_check_bootstrap: int = 500
    reality_check_block: int = 10  # stationary-bootstrap avg block length
    reality_check_gate_enabled: bool = False  # gate promotion on the RC p-value (opt-in)
    reality_check_threshold: float = 0.05  # reject when the best-trial RC p-value exceeds this


class PortfolioConfig(BaseModel):
    """Cross-sleeve combination layer (offense roadmap P4)."""

    enabled: bool = True
    method: str = "hrp"  # hrp | inverse_variance | equal
    cov_method: str = "rmt"  # rmt | ledoit_wolf | sample
    min_obs: int = 20  # min common stream length to combine sleeves


class LongShortConfig(BaseModel):
    """Universe-wide cross-sectional long-short rank sleeve (breadth strategy).

    Ranks names daily by the model's bagged OOS probability, holds top-vs-bottom
    quantile dollar-neutral, books next-day returns net of turnover costs, and
    rides the full promotion gauntlet under one "Universe Long Short" key."""

    enabled: bool = False  # new sleeve; default off keeps the suite/runtime stable
    quantile: float = 0.2  # fraction of scored names per leg
    cost_bps: float = 10.0  # transaction cost per unit turnover (one-way, incl. slippage)
    min_names_per_day: int = 20  # below this breadth the book holds nothing that day
    sector_neutral: bool = True  # z-score scores within (date, sector) before ranking
    # Turnover levers (the alpha-arc diagnostics: 35%/day churn at 10 bps ate a
    # +1.54 gross Sharpe). Re-rank every N trading days, holding in between
    # (forced exits still charged), and/or smooth scores with a trailing
    # per-ticker mean before ranking. 1/1 = the original daily book.
    rebalance_days: int = 1
    score_smoothing_days: int = 1
    # No-trade band: hold a name until its rank leaves the widened exit band
    # (top/bottom quantile*(1+band)); new names enter only from the tight core.
    # Cuts turnover without the gross decay of a slower cadence. 0 = off.
    rebalance_band: float = 0.0
    # Vol-targeted de-risking (never levers up): scale rebalance weights by
    # min(1, target / trailing annualized vol of the UNIT book). 0 = off.
    vol_target_annual: float = 0.0
    vol_lookback_days: int = 20
    # Evaluation-window floor (ISO date). The book only trades dates >=
    # eval_start so the series under test IS the strategy the universe fixture
    # defines — e.g. the Liquid-1500 census floor 2018-09-01; earlier dates
    # evaluate its narrower pre-census ancestor instead (audited on run
    # 083aa78a529f: ancestor SR -0.165 over 420d vs 0.981 census-era).
    # None = full window.
    eval_start: str | None = None
    # Structure-variant trial expansion (audit follow-up: the single-name
    # short leg runs SR -1.20 in the causal calm state, the long leg +1.53).
    # Each grid combo is built under FOUR constructions — baseline L/S,
    # short-leg-gated L/S (single-name shorts off in the causal calm state,
    # residual beta hedged with the panel's equal-weight market), hedged
    # long-only, and hedged long-only with dispersion sizing — all in one
    # returns matrix so DSR deflation prices the selection.
    structure_variants: bool = False
    # Stock-loan fee (bps/yr) accrued daily on actual single-name short
    # exposure — the audit's unmodeled-cost item. 0 keeps legacy books exact.
    short_borrow_bps: float = 0.0
    # Cost (bps) per unit |change in index-hedge notional| in hedged variants.
    hedge_cost_bps: float = 2.0
    # Regime-conditional options (independently flaggable; share one causal
    # expanding-percentile market-vol state decoder, 0 = calmest state):
    # gate scales exposure per state; experts pick the best-in-state combo.
    regime_gate_enabled: bool = False
    regime_experts_enabled: bool = False
    regime_exposures: list[float] = Field(default_factory=lambda: [1.0, 1.0, 0.0])
    null_iterations: int = 20  # within-date permutation null (synthetic-gauntlet slot)
    null_quantile: float = 0.95  # champion must beat this quantile of the null


class StatArbConfig(BaseModel):
    """Cointegration / OU mean-reversion strategy family (offense roadmap P5)."""

    enabled: bool = False  # new family; default off keeps the suite/runtime stable
    adf_threshold: float = -2.86  # ADF 5% critical value — spread stationary below it
    adf_lags: int = 1
    insample_frac: float = 0.6  # fraction used to select pairs + fit the hedge (rest is OOS)
    entry_z: float = 2.0
    exit_z: float = 0.5
    zscore_window: int = 20
    min_obs: int = 60
    max_pairs_per_sector: int = 3
    use_johansen: bool = False  # also trade a Johansen multivariate basket per sector
    min_basket: int = 3  # min sector tickers for a Johansen basket


class MCPConfig(BaseModel):
    transport: str = "stdio"


class RAGConfig(BaseModel):
    embedder: str = "hashing"  # "hashing" (offline default) | "sentence_transformer"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k: int = 5
    chunk_size: int = 512
    chunk_overlap: int = 100
    evidence_enabled: bool = False  # wire retrieve() into the trade graph's evidence node


class NewsConfig(BaseModel):
    """Point-in-time news feed: offline fixture + live providers (GDELT/EDGAR)."""

    providers: list[str] = Field(default_factory=lambda: ["gdelt"])  # live composite order
    fixture_path: str = ""  # offline StaticNewsSource; "" -> packaged data/news/headlines.csv
    vault_dir: str = "./data/raw/news"
    limit: int = 20
    gdelt_endpoint: str = "https://api.gdeltproject.org/api/v2/doc/doc"
    edgar_forms: list[str] = Field(default_factory=lambda: ["8-K", "10-Q", "10-K"])
    edgar_identity: str = ""  # SEC requires a "Name email" User-Agent identity


class FundamentalsConfig(BaseModel):
    """Point-in-time fundamentals for value/quality cross-sectional factors."""

    fixture_path: str = ""  # offline StaticFundamentalsSource; "" -> deterministic fake
    edgar_identity: str = ""  # SEC "Name email" User-Agent for the live EDGAR source


class ShortVolumeConfig(BaseModel):
    """FINRA Reg SHO daily short-volume vault for the short-flow feature family."""

    vault_path: str = ""  # StaticShortVolumeSource CSV; "" -> feature family off


class DashboardConfig(BaseModel):
    veto_ledger_path: str = "./data/ledger/veto_ledger.parquet"
    trade_log_path: str = "./data/ledger/trade_log.parquet"
    refresh_seconds: int = 5
    max_drawdown_alert: float = 0.15
    min_sharpe_alert: float = 0.0
    max_veto_rate_alert: float = 0.5
    auth_enabled: bool = False
    alert_channels: list[str] = []  # push delivery: "console" and/or "webhook"; [] = off
    alert_webhook_url: str = ""


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
    # "iex" (free real-time; historical daily bars only from ~mid-2020) or
    # "sip" (full history on free keys — only *real-time* SIP needs a paid plan).
    # Backtests reaching before mid-2020 must use "sip".
    data_feed: str = "iex"


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
    portfolio: PortfolioConfig = Field(default_factory=PortfolioConfig)
    stat_arb: StatArbConfig = Field(default_factory=StatArbConfig)
    long_short: LongShortConfig = Field(default_factory=LongShortConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    news: NewsConfig = Field(default_factory=NewsConfig)
    fundamentals: FundamentalsConfig = Field(default_factory=FundamentalsConfig)
    short_volume: ShortVolumeConfig = Field(default_factory=ShortVolumeConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    alpaca: AlpacaConfig = Field(default_factory=AlpacaConfig)
