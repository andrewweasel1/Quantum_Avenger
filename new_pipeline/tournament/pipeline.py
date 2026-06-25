"""Offline end-to-end pipeline orchestration (Phase 3 glue).

Assembles the full chain with no network: synthetic market data -> vectorized
features -> sector join + friction labels -> per-sector tournament -> Deflated
Sharpe + HMM promotion. The legacy multi-phase ``main`` flow, rebuilt offline.
"""

import itertools
import json
from dataclasses import replace
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl

from new_pipeline.adapters import FakeMarketDataSource, StaticUniverseProvider
from new_pipeline.config import get_config
from new_pipeline.evaluation.alpha_eval import alpha_eval_report
from new_pipeline.evaluation.dsr import (
    compute_deflated_sharpe_ratio,
    deflated_sharpe_report,
    effective_number_of_trials,
    probabilistic_sharpe_ratio,
)
from new_pipeline.evaluation.haircut import haircut_sharpe_ratio
from new_pipeline.evaluation.hmm_gauntlet import run_hmm_synthetic_gauntlet
from new_pipeline.evaluation.minbtl import backtest_length_is_sufficient
from new_pipeline.evaluation.pbo import probability_of_backtest_overfitting
from new_pipeline.evaluation.promotion import PromotionRegistry, assess_promotion
from new_pipeline.evaluation.reality_check import whites_reality_check
from new_pipeline.evaluation.regime_dsr import (
    QuantitativeEvaluator,
    RegimeVerdict,
    ThinRegimePolicy,
)
from new_pipeline.features.extended import add_extended_features, extended_feature_names
from new_pipeline.features.factors import add_cross_sectional_factors, factor_feature_names
from new_pipeline.features.labels import add_labels
from new_pipeline.features.markov_regime import MARKOV_FEATURE_NAMES, add_markov_regime_features
from new_pipeline.features.polars_engine import compile_features
from new_pipeline.portfolio.combination import combine_returns
from new_pipeline.tournament.director import run_sector_tournament
from new_pipeline.tournament.simulator import sharpe_ratio
from new_pipeline.tournament.stat_arb import engle_granger, mean_reversion_returns
from new_pipeline.tournament.trainer import load_booster, predict_proba

FEATURE_COLS = [
    "returns", "atr", "adv_20", "volatility", "spread_pct", "roll_spread",
    "amihud", "ncskew", "duvol",
]


def build_training_frame(
    symbols,
    sectors,
    start,
    end,
    source=None,
    cfg=None,
    news_source=None,
    sentiment_engine=None,
    anonymizer=None,
) -> pl.DataFrame:
    """Synthetic OHLCV -> features -> sector join + target_label, one frame.

    When ``news_source`` + ``sentiment_engine`` + ``anonymizer`` are supplied, a
    real causally-aligned ``sentiment_score`` is joined in before the (optional)
    sentiment-fused micro-HMM features.
    """
    source = source or FakeMarketDataSource()
    cfg = cfg or get_config()
    rows = [
        {
            "date": bar.day, "ticker": symbol, "open": bar.open, "high": bar.high,
            "low": bar.low, "close": bar.close, "volume": bar.volume,
        }
        for symbol in symbols
        for bar in source.history(symbol, start, end)
    ]
    features = compile_features(pl.DataFrame(rows))
    if cfg.features.extended_features:
        features = add_extended_features(
            features, cfg.features.extended_features,
            fracdiff_d=cfg.features.fracdiff_d, fracdiff_threshold=cfg.features.fracdiff_threshold,
            vol_window=cfg.features.vol_window, micro_window=cfg.features.micro_window,
        )
    labeled = add_labels(
        features,
        cfg.features.label_horizon,
        cfg.features.label_cost_bps,
        cfg.features.label_pt_mult,
        cfg.features.label_sl_mult,
        cfg.features.label_method,
    )
    if news_source is not None and sentiment_engine is not None and anonymizer is not None:
        labeled = _attach_sentiment(labeled, symbols, news_source, sentiment_engine, anonymizer)
    if cfg.fusion.enabled:
        labeled = add_markov_regime_features(labeled)
    sector_df = pl.DataFrame(
        {"ticker": list(sectors), "sector": [sectors[t] for t in sectors]}
    )
    joined = labeled.join(sector_df, on="ticker", how="left")
    if cfg.features.factor_set:
        joined = add_cross_sectional_factors(
            joined, cfg.features.factor_set, sector_neutral=cfg.features.factor_sector_neutral
        )
    return joined


def _attach_sentiment(labeled, symbols, news_source, sentiment_engine, anonymizer) -> pl.DataFrame:
    """Overwrite the neutral ``sentiment_score`` with a real, causally-aligned
    daily score joined per (ticker, date); no-news days keep the neutral 0.0."""
    from new_pipeline.data.sentiment_feature_builder import SentimentFeatureBuilder

    builder = SentimentFeatureBuilder(anonymizer=anonymizer, engine=sentiment_engine)
    dates = labeled.select("date").unique().to_series().to_list()
    records = [
        {"timestamp": item.timestamp, "text": item.headline, "ticker": item.symbol}
        for symbol in symbols
        for day in dates
        for item in news_source.headlines(symbol, day)
    ]
    if not records:
        return labeled
    daily = builder.build_daily_sentiment(pd.DataFrame(records))
    if daily.empty:
        return labeled
    daily_pl = pl.from_pandas(daily[["date", "ticker", "sentiment"]]).with_columns(
        pl.col("date").cast(pl.Date)
    )
    return (
        labeled.join(daily_pl, on=["date", "ticker"], how="left")
        .with_columns(pl.coalesce(["sentiment", "sentiment_score"]).alias("sentiment_score"))
        .drop("sentiment")
    )


def run_offline_pipeline(
    output_dir, start=date(2021, 1, 1), end=date(2022, 12, 31), max_symbols=None, source=None
) -> dict:
    cfg = get_config()
    universe = StaticUniverseProvider()
    sectors = universe.sectors()
    symbols = list(sectors)[: max_symbols] if max_symbols else list(sectors)
    news_source = sentiment_engine = anonymizer = None
    if cfg.fusion.enabled:
        from new_pipeline.adapters.factory import build_adapters, build_news_source

        bundle = build_adapters(cfg)
        news_source = build_news_source(cfg, universe)  # PIT fixture offline
        sentiment_engine, anonymizer = bundle.sentiment_engine, bundle.anonymizer
        source = source or bundle.market_data
    frame = build_training_frame(
        symbols, sectors, start, end, source, cfg,
        news_source=news_source, sentiment_engine=sentiment_engine, anonymizer=anonymizer,
    )
    feature_cols = list(FEATURE_COLS)
    if cfg.fusion.enabled:
        feature_cols += list(MARKOV_FEATURE_NAMES)
    if cfg.features.factor_set:
        feature_cols += factor_feature_names(cfg.features.factor_set)
    if cfg.features.extended_features:
        feature_cols += extended_feature_names(cfg.features.extended_features)
    results = run_sector_tournament(frame, feature_cols, output_dir)
    promotions = _evaluate_and_promote(frame, results, output_dir, cfg)
    summary = {"sectors": list(results), "promotions": promotions}
    if cfg.evaluation.alpha_eval_enabled:
        summary["alpha_eval"] = _write_alpha_eval(frame, feature_cols, cfg, output_dir)
    if cfg.portfolio.enabled:
        book = _combine_book(results, output_dir, cfg)
        if book is not None:
            summary["portfolio"] = book
    if cfg.stat_arb.enabled:
        stat_arb = _run_stat_arb(frame, output_dir, cfg)
        if stat_arb is not None:
            summary["stat_arb"] = stat_arb
    return summary


def _run_stat_arb(frame: pl.DataFrame, output_dir, cfg) -> dict | None:
    """Select within-sector cointegrated pairs and fit each hedge ratio IN-SAMPLE,
    trade the spread OUT-OF-SAMPLE (causal mean reversion), and combine the
    date-aligned OOS sleeves into a stat-arb book via the portfolio layer ->
    stat_arb.json. Returns None when no pair cointegrates in-sample."""
    if "ticker" not in frame.columns or "sector" not in frame.columns:
        return None
    # Pivot to a close panel WITHOUT a universe-wide drop_nulls: a single gappy /
    # late-listing ticker must not truncate every other pair's history. Each pair
    # aligns its own two legs below.
    panel = (
        frame.select(["date", "ticker", "close"])
        .pivot(on="ticker", index="date", values="close")
        .sort("date")
    )
    panel_tickers = [c for c in panel.columns if c != "date"]
    if panel.height < cfg.stat_arb.min_obs or len(panel_tickers) < 2:
        return None
    available = set(panel_tickers)
    sector_tickers: dict[str, list[str]] = {}
    for ticker, sector in frame.select("ticker", "sector").unique().iter_rows():
        if ticker in available:
            sector_tickers.setdefault(sector, []).append(ticker)

    n_candidates = 0
    pairs_report, sleeves, sleeve_returns = [], [], []
    for sector, tickers in sector_tickers.items():
        for y_name, x_name in itertools.combinations(tickers, 2):
            aligned = panel.select(["date", y_name, x_name]).drop_nulls()  # per-pair overlap
            split = int(aligned.height * cfg.stat_arb.insample_frac)
            oos_len = aligned.height - split
            if split < cfg.stat_arb.min_obs or oos_len < cfg.stat_arb.zscore_window + 5:
                continue  # need enough to fit in-sample AND to trade out-of-sample
            n_candidates += 1  # a pair actually tested for cointegration (the search space)
            y = aligned[y_name].to_numpy()
            x = aligned[x_name].to_numpy()
            # Select the pair + fit the hedge ratio IN-SAMPLE only (no look-ahead),
            result, _ = engle_granger(
                y[:split], x[:split], cfg.stat_arb.adf_lags, cfg.stat_arb.adf_threshold
            )
            if not result.cointegrated:
                continue
            # then trade the OOS spread under that fixed in-sample hedge ratio.
            oos_spread = y[split:] - (result.intercept + result.hedge_ratio * x[split:])
            oos_returns = mean_reversion_returns(
                oos_spread, cfg.stat_arb.entry_z, cfg.stat_arb.exit_z, cfg.stat_arb.zscore_window
            )
            sleeves.append(
                aligned[split:].select("date").with_columns(
                    pl.Series(f"{y_name}__{x_name}", oos_returns)
                )
            )
            sleeve_returns.append(oos_returns)
            pairs_report.append({
                "y": y_name, "x": x_name, "sector": sector,
                "hedge_ratio": result.hedge_ratio, "adf_tstat": result.adf_tstat,
                "half_life": result.half_life, "sharpe": float(sharpe_ratio(oos_returns)),
            })
    if not pairs_report:
        return None
    # Validate each sleeve: Deflated Sharpe of its OOS returns, deflated by the number
    # of pairs *searched* (multiple-testing). Only validated sleeves feed the book.
    for pair, returns in zip(pairs_report, sleeve_returns, strict=True):
        dsr = deflated_sharpe_report(returns, max(n_candidates, 1)).dsr
        pair["dsr"] = float(dsr)
        pair["validated"] = bool(dsr >= cfg.evaluation.dsr_promotion_threshold)
    report = {"pairs": pairs_report, "n_pairs": len(pairs_report), "n_candidates": n_candidates}

    # Date-align every sleeve onto one calendar (missing -> 0) for the family-level
    # reality check and the validated-sleeve book.
    book_df = sleeves[0]
    for sleeve in sleeves[1:]:
        book_df = book_df.join(sleeve, on="date", how="full", coalesce=True)
    book_df = book_df.sort("date").fill_null(0.0)
    panel_returns = book_df.select([f"{p['y']}__{p['x']}" for p in pairs_report]).to_numpy()
    # White's Reality Check over the searched pair sleeves (multiple-strategy guard).
    report["reality_check_pvalue"] = float(
        whites_reality_check(
            panel_returns,
            cfg.evaluation.reality_check_bootstrap,
            cfg.evaluation.reality_check_block,
        )
    )
    validated = [i for i, pair in enumerate(pairs_report) if pair["validated"]]
    report["n_validated"] = len(validated)
    if len(validated) >= 2:  # exact date-aligned HRP book of the validated sleeves
        _, book = combine_returns(
            panel_returns[:, validated],
            cfg.portfolio.method, cfg.portfolio.cov_method, cfg.portfolio.min_obs,
        )
        report["book_sharpe"] = float(sharpe_ratio(book))
    (Path(output_dir) / "stat_arb.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def _combine_book(results: dict, output_dir, cfg) -> dict | None:
    """Exact cross-sector book over the per-sector champions -> portfolio.json.

    Each champion's per-sample returns are aggregated to a **daily sector return**
    (mean across the sector's tickers per date), the sectors are date-aligned (outer
    join, missing -> 0), and combined on the real cross-sector covariance via the
    portfolio layer (HRP by default). Returns None when fewer than two sectors have
    the per-sample dates needed (or the aligned panel is too short)."""
    daily = {}
    for sector, result in results.items():
        trials = result["trial_sharpes"]
        if not trials:
            continue
        base = result["candidate_path"].replace("_candidate.json", "")
        dates_path = Path(base + "_sample_dates.parquet")
        if not dates_path.exists():
            continue
        champion = pl.read_parquet(base + "_returns_matrix.parquet")[
            :, int(np.argmax(trials))
        ].to_numpy()
        dates = pl.read_parquet(dates_path)["date"]
        daily[sector] = (
            pl.DataFrame({"date": dates, sector: champion})
            .group_by("date")
            .agg(pl.col(sector).mean())  # equal-weight sector daily return
            .sort("date")
        )
    if len(daily) < 2:
        return None
    sectors = list(daily)
    book_df = daily[sectors[0]]
    for sector in sectors[1:]:
        book_df = book_df.join(daily[sector], on="date", how="full", coalesce=True)
    book_df = book_df.sort("date").fill_null(0.0)
    if book_df.height < cfg.portfolio.min_obs:
        return None
    panel = book_df.select(sectors).to_numpy()
    weights, book = combine_returns(
        panel, cfg.portfolio.method, cfg.portfolio.cov_method, cfg.portfolio.min_obs
    )
    report = {
        "sectors": sectors,
        "weights": {s: float(w) for s, w in zip(sectors, weights, strict=True)},
        "method": cfg.portfolio.method,
        "cov_method": cfg.portfolio.cov_method,
        "book_sharpe": float(sharpe_ratio(book)),
        "sector_sharpe": {s: float(sharpe_ratio(book_df[s].to_numpy())) for s in sectors},
        "n_obs": int(book_df.height),
    }
    (Path(output_dir) / "portfolio.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def _write_alpha_eval(frame: pl.DataFrame, feature_cols, cfg, output_dir) -> dict:
    """Universe-wide per-signal IC/ICIR diagnostics -> alpha_eval.json (read-only;
    never gates promotion). Decay is reported for the cross-sectional factor subset."""
    factor_cols = factor_feature_names(cfg.features.factor_set) if cfg.features.factor_set else []
    report = alpha_eval_report(
        frame, feature_cols, factor_signals=factor_cols,
        min_names=cfg.evaluation.alpha_eval_min_names,
    )
    (Path(output_dir) / "alpha_eval.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def _evaluate_and_promote(frame: pl.DataFrame, results: dict, output_dir, cfg) -> dict:
    registry = PromotionRegistry(Path(output_dir) / "promotion_registry.json")
    decisions: dict[str, bool] = {}
    for sector, result in results.items():
        trials = result["trial_sharpes"]
        if not trials:
            continue
        best = int(np.argmax(trials))
        returns_matrix = pl.read_parquet(result["candidate_path"].replace(
            "_candidate.json", "_returns_matrix.parquet"
        ))
        champion_returns = returns_matrix[:, best].to_numpy()
        paths = _load_champion_paths(result["candidate_path"])

        dsr = _deflated_sharpe(champion_returns, trials, returns_matrix, cfg)
        path_pass_fraction, path_dsr_median = _path_dsr_stats(paths, trials, returns_matrix, cfg)
        synthetic_sr = _synthetic_sharpe(frame, sector, result, champion_returns, cfg)
        # Overfitting/selection diagnostics over the full (n_obs x n_trials) matrix.
        champion_sharpe = sharpe_ratio(champion_returns)
        pbo = probability_of_backtest_overfitting(
            returns_matrix.to_numpy(), cfg.evaluation.pbo_partitions
        )
        psr = probabilistic_sharpe_ratio(champion_returns, cfg.evaluation.psr_benchmark_sr)
        haircut = haircut_sharpe_ratio(
            champion_sharpe, champion_returns.size, len(trials), cfg.evaluation.mt_method,
        ).adjusted_sharpe
        minbtl_ok = None
        if cfg.evaluation.enforce_minbtl:
            minbtl_ok = backtest_length_is_sufficient(
                champion_returns.size, len(trials), champion_sharpe
            )
        reality_check_p = (
            whites_reality_check(
                returns_matrix.to_numpy(),
                cfg.evaluation.reality_check_bootstrap,
                cfg.evaluation.reality_check_block,
            )
            if cfg.evaluation.reality_check_enabled or cfg.evaluation.reality_check_gate_enabled
            else None
        )
        decision = assess_promotion(
            sector, dsr, synthetic_sr,
            cfg.evaluation.dsr_promotion_threshold, cfg.evaluation.synthetic_sr_min,
            pbo=pbo, pbo_threshold=cfg.evaluation.pbo_threshold,
            psr=psr, haircut_sharpe=haircut, minbtl_satisfied=minbtl_ok,
            path_pass_fraction=path_pass_fraction,
            path_fraction_threshold=cfg.evaluation.cpcv_path_min_fraction,
            path_dsr_median=path_dsr_median,
            path_gate_enabled=cfg.evaluation.cpcv_path_gate_enabled,
            reality_check_pvalue=reality_check_p,
            reality_check_gate_enabled=cfg.evaluation.reality_check_gate_enabled,
            reality_check_threshold=cfg.evaluation.reality_check_threshold,
        )
        if cfg.evaluation.regime_gate_enabled and decision.promoted:
            if not _regime_verdict(champion_returns, trials, cfg).promoted:
                decision = replace(decision, promoted=False, reason="failed per-regime DSR")
        model_path = result["candidate_path"] if decision.promoted else None
        registry.record(decision, model_path=model_path)
        decisions[sector] = decision.promoted
    return decisions


def _synthetic_sharpe(frame, sector, result, champion_returns, cfg) -> float:
    booster = load_booster(result["candidate_path"])
    features = (
        frame.filter(pl.col("sector") == sector)
        .with_columns(pl.col(result["selected_features"]).fill_nan(None))
        .drop_nulls(subset=result["selected_features"])
        .select(result["selected_features"])
        .to_numpy()
    )
    if features.shape[0] < 10:
        return 0.0
    return run_hmm_synthetic_gauntlet(
        champion_returns,
        features,
        lambda matrix: predict_proba(booster, matrix),
        n_iter=20,
        block_size=cfg.evaluation.gauntlet_block_size,
    )


def _load_champion_paths(candidate_path):
    """Load the champion's reconstructed CPCV backtest paths as a (phi, n) array."""
    paths_file = Path(candidate_path.replace("_candidate.json", "_paths.parquet"))
    if not paths_file.exists():
        return None
    return pl.read_parquet(paths_file).to_numpy().T  # columns are paths -> rows are paths


def _path_dsr_stats(paths, trials, returns_matrix, cfg):
    """Per-path Deflated Sharpe over the phi CPCV paths: (pass_fraction, median).

    Each path is the champion strategy resampled, so it is deflated by the same
    (effective) trial count and cross-trial variance as the mean-path DSR; the
    pass fraction is the share of paths individually clearing the threshold.
    """
    if paths is None or paths.shape[0] == 0:
        return None, None
    if cfg.evaluation.use_effective_trials:
        n_eff = effective_number_of_trials(returns_matrix.to_numpy().T)
        path_dsrs = np.array(
            [deflated_sharpe_report(path, n_eff, trial_sharpes=trials).dsr for path in paths]
        )
    else:
        path_dsrs = np.array([compute_deflated_sharpe_ratio(path, trials) for path in paths])
    pass_fraction = float(np.mean(path_dsrs >= cfg.evaluation.dsr_promotion_threshold))
    return pass_fraction, float(np.median(path_dsrs))


def _deflated_sharpe(champion_returns, trials, returns_matrix, cfg) -> float:
    """Deflated Sharpe for the champion. With ``use_effective_trials`` the trial
    count is the correlation-adjusted N_eff (correlated grid configs otherwise
    over-deflate the DSR); the per-trial Sharpes still supply the variance."""
    if cfg.evaluation.use_effective_trials:
        n_eff = effective_number_of_trials(returns_matrix.to_numpy().T)
        return deflated_sharpe_report(champion_returns, n_eff, trial_sharpes=trials).dsr
    return compute_deflated_sharpe_ratio(champion_returns, trials)


def _regime_verdict(champion_returns, trials, cfg) -> RegimeVerdict:
    """Per-regime DSR gate over the champion's OOS returns: volatility is the
    champion's own rolling std, regimes are decoded by a Gaussian HMM, and DSR
    must clear the threshold in every testable regime (thin regimes per policy)."""
    volatility = pd.Series(champion_returns).rolling(10).std().bfill().fillna(0.0).to_numpy()
    evaluator = QuantitativeEvaluator(
        min_dsr_threshold=cfg.evaluation.dsr_promotion_threshold,
        n_components=cfg.evaluation.hmm_states,
        min_regime_obs=cfg.evaluation.min_regime_obs,
        thin_policy=ThinRegimePolicy(cfg.evaluation.thin_regime_policy),
    )
    return evaluator.evaluate_model_robustness(
        champion_returns, volatility, len(trials), trial_sharpes=trials
    )
