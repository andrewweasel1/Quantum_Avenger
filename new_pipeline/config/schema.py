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
    # Per-date causal market-state features (trend/vol percentile ranks,
    # rolling-252) broadcast to every name: interaction context for the trees,
    # judged by the causal screen like any feature. Default off (bit-stable).
    market_state_features: bool = False
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
    rebalance_days: int = 5
    score_smoothing_days: int = 5
    # No-trade band: hold a name until its rank leaves the widened exit band
    # (top/bottom quantile*(1+band)); new names enter only from the tight core.
    # Cuts turnover without the gross decay of a slower cadence. 0 = off.
    rebalance_band: float = 0.5
    # Vol-targeted de-risking (never levers up): scale rebalance weights by
    # min(1, target / trailing annualized vol of the UNIT book). 0 = off.
    vol_target_annual: float = 0.05
    vol_lookback_days: int = 20
    # Evaluation-window floor (ISO date). The book only trades dates >=
    # eval_start so the series under test IS the strategy the universe fixture
    # defines — e.g. the Liquid-1500 census floor 2018-09-01; earlier dates
    # evaluate its narrower pre-census ancestor instead (audited on run
    # 083aa78a529f: ancestor SR -0.165 over 420d vs 0.981 census-era).
    # None = full window.
    eval_start: str | None = "2018-09-01"
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
    short_borrow_bps: float = 50.0
    # Cost (bps) per unit |change in index-hedge notional| in hedged variants.
    hedge_cost_bps: float = 2.0
    # Calm-state COST policy factorial (audit Q1: turnover is state-invariant
    # while calm-state gross sits at the cost line, so the flat cost consumes
    # >100% of calm-state gross). Builds each grid combo as control +
    # calm-band-only + calm-cadence-only + both, in ONE returns matrix so DSR
    # deflation prices the selection. States: leak-free causal vol decoder.
    calm_cost_variants: bool = True
    # Exit-band width used ONLY in causal calm states (baseline band stays
    # rebalance_band elsewhere): k_exit = n*quantile*(1 + calm_rebalance_band).
    calm_rebalance_band: float = 1.5
    # Minimum days between re-ranks while calm (rounds up to the
    # rebalance_days grid; forced exits still charged on skipped days).
    calm_rebalance_days: int = 10
    # Causal vol-decoder percentile window in trading days (0 = legacy
    # expanding). Rolling 252 keeps calm-state prevalence stationary across
    # vol eras — the expanding window's 2016-17 anchor shrank "calm" to ~9%
    # of census-window days vs the evaluation HMM's ~46% (the mismatch that
    # neutered the calm-cost policy in run 711bdbd6845a). Evidence-informed,
    # pre-registered; not a scan surface.
    causal_window_days: int = 252
    # Mixture-of-experts column: per date, apply the calm-policy construction
    # with the best in-state Sharpe over an EXPANDING strictly-prior window
    # (fallback: untreated control). One extra trial column per combo; requires
    # calm_cost_variants (it learns over those four constructions).
    moe_variants: bool = False
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


class IntradayConfig(BaseModel):
    """Minute-bar intraday stack (small/mid-cap ORB v1). Sibling to the daily
    tournament: separate vault, universe filters, and its own promotion key;
    nothing here alters the frozen daily champion's behavior."""

    vault_dir: str = "./data/minute_vault"  # per (symbol, month) parquet tree
    bar_minutes: int = 1
    history_months: int = 24
    # Static base: liquid1500 extended-cap segments + liquidity floors
    # (computed causally from daily bars at run time).
    universe_segments: list[str] = Field(
        default_factory=lambda: ["Small Cap Extended", "Mid Cap Extended"])
    min_adv_dollars: float = 5_000_000.0  # 20d median dollar volume floor
    min_price: float = 3.0
    # Daily scanner overlay: causal-at-open ranking, top_n admitted to ORB.
    # 10 concentrates on the best-ranked names (v1 ran 60 and found gross edge
    # ~0 with cost varying 5x across the pick set — selection is the lever).
    # 50, up from 10: meanrev_v3 established that the binding constraint is the
    # EVENT RATE of extreme dislocations (~0.06 trades/session/trial at z2.5),
    # and that it cannot be relaxed by lowering the threshold. Admitting more
    # names per session raises event count while holding the signal definition
    # fixed — the honest direction. Deeper ranks are less tradable, but
    # touch_cap sizing self-corrects by giving thin names smaller positions.
    scanner_top_n: int = 50
    # Scanner weightings to PRICE as trials (intraday.scanner.VARIANTS). Every
    # entry multiplies the trial family the deflation must pay for.
    # Collapsed to "attention" alone by meanrev_v5, which priced all three
    # survivors plus a consensus "union" of them (128 trials, one construction
    # axis at a time): attention won 19/32 constructions outright and netted
    # 43.1 bps at z2.5 against 24.9 (tradable), 25.5 (union) and 17.7
    # (cheap_gap). Nothing beat it on any construction, so carrying the others
    # bought a 4x trial family and no champion. Re-add an entry only with
    # evidence, never to widen a search.
    scanner_variants: list[str] = Field(default_factory=lambda: ["attention"])
    # Trials searched in EARLIER runs whose outcomes fixed this run's spec.
    # A run's DSR/haircut deflate only that run's own trials, but the champion
    # is the product of a search spanning runs — touch_cap was chosen in v3,
    # z2.5 in v3's sweep, top-50 in v4, the attention scanner in v5/v6. v7
    # priced 32 trials against 776 actually searched across the programme.
    # Set this explicitly per run and record it; 0 means "this run is the whole
    # search", which is true only of a genuinely first look at an axis.
    prior_trials_searched: int = 0
    # ORB trial family (deflation-priced together; every axis value is a trial).
    range_minutes: list[int] = Field(default_factory=lambda: [5, 15, 30])
    stop_styles: list[str] = Field(default_factory=lambda: ["or_low", "or_mid"])
    target_r_multiples: list[float] = Field(default_factory=lambda: [2.0, 0.0])  # 0 -> no target
    entry_buffer_bps: float = 5.0
    # Risk: fixed-fractional per trade against the stop distance.
    risk_bps: float = 25.0            # of equity, per trade
    max_position_pct: float = 5.0     # of equity, per name
    max_concurrent: int = 15
    flatten_buffer_min: int = 5       # exit N minutes before session close
    # Strategy family for an official intraday run: "orb" (opening range
    # breakout, rejected in runs orb_v1/orb_v2) | "meanrev" (anchor reversion).
    strategy: str = "meanrev"
    # Mean-reversion axes (intraday.meanrev). entry_styles is the decisive one:
    # "passive" rests a limit and fills only on a strict trade-through, so it
    # pays no spread but inherits adverse selection; "marketable" crosses.
    mr_anchors: list[str] = Field(default_factory=lambda: ["vwap", "open"])
    # Tighter thresholds added: 1.5-2.5 prior-day ATRs is a rare intraday
    # stretch (~0.19 trades/session), and sample size was the binding
    # constraint on the DSR, not the edge.
    mr_entry_z: list[float] = Field(default_factory=lambda: [0.5, 1.0, 1.5, 2.5])
    mr_entry_styles: list[str] = Field(default_factory=lambda: ["marketable", "passive"])
    mr_exit_targets: list[str] = Field(default_factory=lambda: ["anchor", "half"])
    # Activity floors. Champion selection is an argmax over trials, which
    # systematically favours the THINNEST trial: fewer trades means a more
    # extreme achievable Sharpe. meanrev_v1 crowned a 3-trade trial active on
    # 0.6% of sessions at +1.16 annualized, while every trial that actually
    # traded was negative. Trials below either floor are ineligible to be
    # champion (a strengthening of the gauntlet, never a softening).
    min_trades: int = 50
    min_active_session_frac: float = 0.10
    mr_passive_ttl_min: int = 5   # bars a resting entry limit stays live
    mr_stop_atr: float = 1.0      # stop distance in prior-day ATRs below entry
    # Costs: spread-dominated. Per-side charge = max(cs_spread/2, floor) + impact.
    # Measured, not assumed: 400 real fill events from the orb_v2 ledger priced
    # against SIP NBBO quotes at the fill minute gave a quoted half-spread of
    # median 2.4 bps / p75 5.1 / p90 10.2 (mean 4.6). The original 15.0 was ~6x
    # too conservative — 93.5% of fills sat below it. 5.0 (~p75) keeps the floor
    # on the pessimistic side of the measurement; the Corwin-Schultz estimate
    # still binds above it for genuinely wide names.
    # CAVEAT recorded with the calibration: our $5k orders ran a median 3.5x the
    # displayed size at the touch (59% exceeded it), so real fills walk the book
    # and the impact term — not this floor — must carry that cost. See
    # models/prod/evidence/orb_v2/SPREAD_CALIBRATION.md.
    spread_floor_bps: float = 5.0
    # MEASURED quote statistics replace Corwin-Schultz, which overstated the
    # spread ~4x on gap-selected small caps and set ~90% of every intraday
    # trading cost (evidence/meanrev_v1/COST_AUTOPSY.md).
    quote_vault_dir: str = "./data/quote_vault"
    # Position size may not exceed this multiple of the DISPLAYED touch
    # notional. meanrev_v1 ran a median 6.77x the touch, so most of its real
    # cost was book-walking the old bar-volume impact term never charged.
    max_touch_participation: float = 1.0
    # Sizing models, priced as a TRIAL AXIS because the measured touch is far
    # thinner than assumed (median $150 on traded names, not ~$700), which
    # makes the constraint strategy-defining rather than a mild guardrail:
    #   volume_part  work the order over a window, capped at a share of the
    #                flow — the standard desk practice; no book-walking, but
    #                the spread is paid on every slice.
    #   touch_cap    fit inside the instantaneous displayed touch. Honest for
    #                single-shot execution; positions collapse ~33x.
    #   uncapped     fire the full position at the touch and pay the whole
    #                book-walk. Deliberately pessimistic.
    # touch_cap only, as the standing spec: meanrev_v2 priced all three and it
    # was the sole net-positive model (+1.9bps/trade vs -2.3 volume_part and
    # -58.7 uncapped), because fitting inside displayed depth eliminates
    # book-walking entirely. The other two stay available for re-pricing.
    sizing_models: list[str] = Field(default_factory=lambda: ["touch_cap"])
    volume_participation_rate: float = 0.10  # share of window flow a worked order takes
    exec_window_min: int = 5                 # minutes an order is worked over
    # Fall back to Corwin-Schultz where a name-month has no measured cell;
    # runs record the measured-coverage share so a thin vault is visible.
    allow_cs_fallback: bool = True


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

    # repr=False keeps live credentials out of every rendered AppConfig: a
    # pytest assertion or exception traceback that touches the config used to
    # print the real key and secret in plaintext. Attribute access is
    # unchanged, so callers read cfg.alpaca.api_key exactly as before.
    api_key: str = Field(default="", repr=False)
    secret_key: str = Field(default="", repr=False)
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
    intraday: IntradayConfig = Field(default_factory=IntradayConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    alpaca: AlpacaConfig = Field(default_factory=AlpacaConfig)
