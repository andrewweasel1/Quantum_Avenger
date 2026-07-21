"""Offline end-to-end pipeline orchestration (Phase 3 glue).

Assembles the full chain with no network: synthetic market data -> vectorized
features -> sector join + friction labels -> per-sector tournament -> Deflated
Sharpe + HMM promotion. The legacy multi-phase ``main`` flow, rebuilt offline.
"""

import itertools
import json
import logging
from dataclasses import replace
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl

from new_pipeline.adapters import FakeMarketDataSource, StaticUniverseProvider
from new_pipeline.config import get_config
from new_pipeline.core.exceptions import MarketDataError
from new_pipeline.data.fundamentals import attach_fundamentals
from new_pipeline.data.short_volume import attach_short_volume
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
from new_pipeline.features.event_time import (
    FILING_EVENT_COLS,
    NEWS_EVENT_COLS,
    add_filing_event_features,
    add_news_burst,
)
from new_pipeline.features.extended import add_extended_features, extended_feature_names
from new_pipeline.features.factors import (
    FUNDAMENTAL_FACTORS,
    add_cross_sectional_factors,
    factor_feature_names,
)
from new_pipeline.features.labels import add_labels
from new_pipeline.features.markov_regime import MARKOV_FEATURE_NAMES, add_markov_regime_features
from new_pipeline.features.polars_engine import compile_features
from new_pipeline.features.short_flow import SHORT_FLOW_COLS, add_short_flow_features
from new_pipeline.portfolio.combination import combine_returns
from new_pipeline.tournament.accounting import collapse_to_daily
from new_pipeline.tournament.director import run_sector_tournament
from new_pipeline.tournament.johansen import johansen_basket
from new_pipeline.tournament.simulator import sharpe_ratio
from new_pipeline.tournament.stat_arb import adf_tstat, engle_granger, mean_reversion_returns
from new_pipeline.tournament.trainer import load_booster, predict_proba

_logger = logging.getLogger(__name__)

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
    fundamentals_source=None,
    short_volume_source=None,
    membership=None,
) -> pl.DataFrame:
    """Synthetic OHLCV -> features -> sector join + target_label, one frame.

    When ``news_source`` + ``sentiment_engine`` + ``anonymizer`` are supplied, a
    real causally-aligned ``sentiment_score`` is joined in before the (optional)
    sentiment-fused micro-HMM features.

    ``membership`` (a list of ``UniverseMember`` with real start/end dates)
    point-in-time masks each ticker's rows to its index-membership windows —
    see :func:`apply_membership_mask`. ``None`` keeps every row (fixtures with
    placeholder dates, direct callers).
    """
    source = source or FakeMarketDataSource()
    cfg = cfg or get_config()
    rows = []
    empty_symbols = 0
    for symbol in symbols:
        try:
            bars = source.history(symbol, start, end)
        except Exception as exc:  # one bad ticker must not kill a 500-name ingest
            _logger.warning("skipping %s: history fetch failed (%s)", symbol, exc)
            continue
        if not bars:
            # Providers return empty (not an error) outside their coverage — e.g.
            # Alpaca's IEX feed has no daily bars before mid-2020 (SIP does).
            _logger.warning("skipping %s: history returned no bars", symbol)
            empty_symbols += 1
            continue
        rows.extend(
            {
                "date": bar.day, "ticker": symbol, "open": bar.open, "high": bar.high,
                "low": bar.low, "close": bar.close, "volume": bar.volume,
            }
            for bar in bars
        )
    if symbols and not rows:
        # An all-empty fetch is a data-plane failure, not a valid (vacuously
        # "done", zero-sector) backtest — fail loudly with the likely cause.
        raise MarketDataError(
            f"no market data for any of the {len(symbols)} symbols in "
            f"{start}..{end} ({empty_symbols} returned empty). If this is a "
            "live Alpaca run, check alpaca.data_feed coverage for the period "
            "(the default 'iex' feed has no daily bars before mid-2020; "
            "'sip' carries full history)."
        )
    features = compile_features(pl.DataFrame(rows))
    if cfg.features.extended_features:
        features = add_extended_features(
            features, cfg.features.extended_features,
            fracdiff_d=cfg.features.fracdiff_d, fracdiff_threshold=cfg.features.fracdiff_threshold,
            vol_window=cfg.features.vol_window, micro_window=cfg.features.micro_window,
            garch_fit_window=cfg.features.garch_fit_window,
        )
    labeled = add_labels(
        features,
        cfg.features.label_horizon,
        cfg.features.label_cost_bps,
        cfg.features.label_pt_mult,
        cfg.features.label_sl_mult,
        cfg.features.label_method,
    )
    # Next-day close-to-close return per ticker: the REALIZATION leg for the
    # cross-sectional long-short sleeve (rank on info at t, earn t -> t+1).
    # Computed on full per-ticker history BEFORE the PIT mask so an index-exit
    # day still books its real forced-exit return. Forward-looking by design —
    # it must never appear in FEATURE_COLS or any selectable feature set.
    labeled = labeled.with_columns(
        (pl.col("close").shift(-1).over("ticker") / pl.col("close") - 1.0).alias("next_ret")
    )
    if short_volume_source is not None and cfg.features.short_flow_features:
        # Fast per-ticker daily short-flow signals; joined + transformed on full
        # per-ticker history (pre-PIT-mask) so the trailing z-score warms up.
        labeled = attach_short_volume(labeled, short_volume_source)
        labeled = add_short_flow_features(labeled)
    if news_source is not None and sentiment_engine is not None and anonymizer is not None:
        labeled = _attach_sentiment(
            labeled, symbols, news_source, sentiment_engine, anonymizer, start, end,
            attach_counts=cfg.features.event_features,
        )
        if cfg.features.event_features:
            # Trailing burst z over full per-ticker history (pre-PIT-mask,
            # like every other per-ticker window feature).
            labeled = add_news_burst(labeled)
    if cfg.fusion.enabled and cfg.fusion.markov_features:
        labeled = add_markov_regime_features(labeled)
    sector_df = pl.DataFrame(
        {"ticker": list(sectors), "sector": [sectors[t] for t in sectors]}
    )
    joined = labeled.join(sector_df, on="ticker", how="left")
    if membership is not None:
        # PIT mask BEFORE the cross-sectional factors: per-ticker features and
        # labels keep their full-history warmup above, but cross-sectional
        # ranks/z-scores must only ever see actual index members per date.
        joined = apply_membership_mask(joined, membership)
    # Exogenous market basis for the regime gate, pinned at the RAW layer:
    # equal-weight mean next_ret over PIT-ACTIVE names, recorded as a per-date
    # constant so every consumer (gate, diagnostics, offline forensics) reads
    # ONE canonical definition that survives any downstream row filtering.
    # The HMM partition is knife-edge-sensitive to basis composition (audit on
    # run 083aa78a529f: two defensible constructions moved the calm state from
    # 933 to 251 days), so the definition must be single and explicit.
    # Realization data like next_ret — never a feature.
    market = (
        joined.drop_nulls(["next_ret"])
        .group_by("date")
        .agg(pl.col("next_ret").mean().alias("market_next_ret"))
    )
    joined = joined.join(market, on="date", how="left")
    if cfg.features.factor_set:
        if fundamentals_source is not None and any(
            factor in FUNDAMENTAL_FACTORS for factor in cfg.features.factor_set
        ):
            joined = attach_fundamentals(  # point-in-time
                joined, fundamentals_source, keep_as_of=cfg.features.event_features
            )
            covered = joined.filter(pl.col("book_value_per_share").is_not_null())
            _logger.info(
                "fundamentals coverage: %.1f%% of rows, %d/%d tickers",
                100.0 * covered.height / max(joined.height, 1),
                covered["ticker"].n_unique(),
                joined["ticker"].n_unique(),
            )
            if cfg.features.event_features:
                # Filing clock/drift consume the kept as_of. Post-mask by
                # necessity (the attach is post-mask); membership gaps merely
                # truncate the drift window for re-entering names.
                joined = add_filing_event_features(joined)
        joined = add_cross_sectional_factors(
            joined, cfg.features.factor_set,
            sector_neutral=cfg.features.factor_sector_neutral,
            # "neutral": missing-fundamentals rows keep average exposure instead
            # of being dropped — dropping them would silently reintroduce the
            # survivorship the PIT universe removed.
            null_policy=cfg.features.factor_null_policy,
        )
    return joined


def apply_membership_mask(frame: pl.DataFrame, members) -> pl.DataFrame:
    """Keep only rows inside a ticker's index-membership window(s).

    ``members`` is a list of ``UniverseMember`` (ticker, start_date, end_date;
    end-exclusive, ``None`` = still a member; a ticker can carry several
    disjoint intervals — exits and re-entries). Rows for tickers with no
    interval at all are dropped: with a point-in-time fixture, "not in the
    membership file" means "never an index member in the window" — keeping
    such rows would reintroduce the survivorship the fixture exists to remove.
    """
    windows = pl.DataFrame({
        "ticker": [m.ticker for m in members],
        "_m_start": [m.start_date for m in members],
        "_m_end": [m.end_date for m in members],
    })
    if windows.is_empty():
        return frame.clear()
    windows = windows.with_columns(
        pl.col("_m_start").cast(pl.Date), pl.col("_m_end").cast(pl.Date)
    )
    # Many-to-many on ticker (one row per interval); intervals are disjoint, so
    # a (ticker, date) row survives through at most one of them.
    return (
        frame.join(windows, on="ticker", how="inner")
        .filter(
            (pl.col("date") >= pl.col("_m_start"))
            & (pl.col("_m_end").is_null() | (pl.col("date") < pl.col("_m_end")))
        )
        .drop("_m_start", "_m_end")
    )


def _event_feature_names(cfg) -> list[str]:
    """Event-time feature names the pipeline will actually materialize.

    Mirrors the build_training_frame gates exactly: the filing pair needs the
    fundamentals attach (fundamental factors requested), the news burst needs
    the fusion news path. Registering a name whose column never materializes
    would crash the tournament, so both sites must share this single rule."""
    if not cfg.features.event_features:
        return []
    names: list[str] = []
    if cfg.features.factor_set and any(
        factor in FUNDAMENTAL_FACTORS for factor in cfg.features.factor_set
    ):
        names += FILING_EVENT_COLS
    if cfg.fusion.enabled:
        names += NEWS_EVENT_COLS
    return names


def _attach_sentiment(
    labeled, symbols, news_source, sentiment_engine, anonymizer, start, end,
    attach_counts=False,
) -> pl.DataFrame:
    """Overwrite the neutral ``sentiment_score`` with a real, causally-aligned
    daily score joined per (ticker, date); no-news days keep the neutral 0.0.

    One RANGE fetch per symbol — never a per-(symbol, day) loop, which against a
    live provider like GDELT would mean hundreds of thousands of HTTP calls for
    an index-scale universe. A failing symbol is skipped, not fatal.

    ``attach_counts`` additionally joins the builder's per-(ticker, date)
    ``news_count`` (0.0 on no-news days) for the event-time burst feature;
    the column is guaranteed present on every return path when requested."""
    from new_pipeline.data.sentiment_feature_builder import SentimentFeatureBuilder

    def _zero_counts(frame):
        return (
            frame.with_columns(pl.lit(0.0).alias("news_count")) if attach_counts else frame
        )

    builder = SentimentFeatureBuilder(anonymizer=anonymizer, engine=sentiment_engine)
    records = []
    for symbol in symbols:
        try:
            items = news_source.fetch(symbol, start, end)
        except Exception as exc:
            _logger.warning("skipping news for %s: fetch failed (%s)", symbol, exc)
            continue
        records.extend(
            {"timestamp": item.timestamp, "text": item.headline, "ticker": item.symbol}
            for item in items
        )
    if not records:
        return _zero_counts(labeled)
    daily = builder.build_daily_sentiment(pd.DataFrame(records))
    if daily.empty:
        return _zero_counts(labeled)
    columns = ["date", "ticker", "sentiment"] + (["news_count"] if attach_counts else [])
    daily_pl = pl.from_pandas(daily[columns]).with_columns(pl.col("date").cast(pl.Date))
    out = (
        labeled.join(daily_pl, on=["date", "ticker"], how="left")
        .with_columns(pl.coalesce(["sentiment", "sentiment_score"]).alias("sentiment_score"))
        .drop("sentiment")
    )
    if attach_counts:
        out = out.with_columns(pl.col("news_count").cast(pl.Float64).fill_null(0.0))
    return out


def run_offline_pipeline(
    output_dir, start=date(2021, 1, 1), end=date(2022, 12, 31), max_symbols=None, source=None
) -> dict:
    cfg = get_config()
    universe = StaticUniverseProvider(
        Path(cfg.data.universe_path) if cfg.data.universe_path else None
    )
    sectors = universe.sectors()
    symbols = list(sectors)[: max_symbols] if max_symbols else list(sectors)
    news_source = sentiment_engine = anonymizer = None
    if cfg.fusion.enabled:
        from new_pipeline.adapters.factory import build_adapters, build_news_source

        bundle = build_adapters(cfg)
        news_source = build_news_source(cfg, universe)  # PIT fixture offline
        sentiment_engine, anonymizer = bundle.sentiment_engine, bundle.anonymizer
        source = source or bundle.market_data
    elif source is None:
        from new_pipeline.adapters.factory import LIVE_MODES, build_adapters

        # A live run_mode backtests on real bars even without the fusion stack —
        # e.g. the dashboard launching a run with a {"system": {"run_mode":
        # "paper"}} override pulls Alpaca history instead of the fake source.
        if (cfg.system.run_mode or "offline").lower() in LIVE_MODES:
            source = build_adapters(cfg).market_data
    fundamentals_source = None
    if cfg.features.factor_set and any(f in FUNDAMENTAL_FACTORS for f in cfg.features.factor_set):
        from new_pipeline.adapters.factory import build_fundamentals_source

        fundamentals_source = build_fundamentals_source(cfg, universe)
    short_volume_source = None
    if cfg.features.short_flow_features and cfg.short_volume.vault_path:
        from new_pipeline.adapters.short_volume_static import StaticShortVolumeSource

        short_volume_source = StaticShortVolumeSource(cfg.short_volume.vault_path)
    frame = build_training_frame(
        symbols, sectors, start, end, source, cfg,
        news_source=news_source, sentiment_engine=sentiment_engine, anonymizer=anonymizer,
        fundamentals_source=fundamentals_source, short_volume_source=short_volume_source,
        # PIT masking: with a dated fixture (sp500_pit.csv or membership.csv)
        # a ticker only contributes rows while an actual index member.
        membership=universe.members(),
    )
    feature_cols = list(FEATURE_COLS)
    if cfg.fusion.enabled:
        # Raw daily sentiment as a direct model feature (the causal screen judges
        # it); the sentiment-fused HMM regime probabilities ride the (costly,
        # config-gated) markov layer.
        feature_cols += ["sentiment_score"]
        if cfg.fusion.markov_features:
            feature_cols += list(MARKOV_FEATURE_NAMES)
    if cfg.features.factor_set:
        feature_cols += factor_feature_names(cfg.features.factor_set)
    if cfg.features.extended_features:
        feature_cols += extended_feature_names(cfg.features.extended_features)
    feature_cols += _event_feature_names(cfg)  # [] unless features.event_features
    if cfg.features.short_flow_features and short_volume_source is not None:
        feature_cols += SHORT_FLOW_COLS
    results = run_sector_tournament(frame, feature_cols, output_dir)
    gauntlet_results = results
    summary = {"sectors": list(results)}
    if cfg.long_short.enabled:
        from new_pipeline.tournament.long_short import LONG_SHORT_KEY, run_universe_long_short

        # The universe L/S book rides the SAME gauntlet as the sector champions
        # (one extra registry key); the sector-only ``results`` still feeds the
        # portfolio book and summary["sectors"] so their meaning is unchanged.
        ls_entry = run_universe_long_short(results, output_dir, cfg)
        if ls_entry is not None:
            gauntlet_results = {**results, LONG_SHORT_KEY: ls_entry}
            summary["long_short"] = ls_entry["diagnostics"]
    promotions = _evaluate_and_promote(frame, gauntlet_results, output_dir, cfg)
    summary["promotions"] = promotions
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


def _johansen_sleeve(panel, tickers, sector, cfg):
    """Fit a Johansen cointegrating basket of the sector's tickers IN-SAMPLE, then trade
    its OOS spread under the fixed in-sample vector. Returns (dates, oos_returns, entry),
    or None when the basket is too thin or not cointegrated in-sample (ADF on the spread)."""
    aligned = panel.select(["date", *tickers]).drop_nulls()
    split = int(aligned.height * cfg.stat_arb.insample_frac)
    if split < cfg.stat_arb.min_obs or aligned.height - split < cfg.stat_arb.zscore_window + 5:
        return None
    prices = aligned.select(tickers).to_numpy()
    vector = johansen_basket(prices[:split], cfg.stat_arb.adf_lags)
    tstat = adf_tstat(prices[:split] @ vector, cfg.stat_arb.adf_lags)
    if tstat >= cfg.stat_arb.adf_threshold:  # in-sample basket spread not stationary
        return None
    oos_returns = mean_reversion_returns(
        prices[split:] @ vector,  # fixed in-sample vector applied out-of-sample
        cfg.stat_arb.entry_z, cfg.stat_arb.exit_z, cfg.stat_arb.zscore_window,
    )
    entry = {
        "name": f"basket__{sector}", "basket": list(tickers),
        "sector": sector, "adf_tstat": float(tstat),
    }
    return aligned[split:].select("date"), oos_returns, entry


def _run_stat_arb(frame: pl.DataFrame, output_dir, cfg) -> dict | None:
    """Select within-sector cointegrated pairs (Engle-Granger) — and, when
    ``use_johansen``, a multivariate Johansen basket per sector — fit each IN-SAMPLE,
    trade the spread OUT-OF-SAMPLE (causal mean reversion), validate each sleeve by a
    Deflated Sharpe, and combine the validated date-aligned OOS sleeves into a stat-arb
    book via the portfolio layer -> stat_arb.json. None when nothing cointegrates."""
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

    def _add_sleeve(dates, oos_returns, entry):  # one date-indexed OOS sleeve (pair or basket)
        entry["sharpe"] = float(sharpe_ratio(oos_returns))
        sleeves.append(dates.with_columns(pl.Series(entry["name"], oos_returns)))
        sleeve_returns.append(oos_returns)
        pairs_report.append(entry)

    for sector, tickers in sector_tickers.items():
        for y_name, x_name in itertools.combinations(tickers, 2):
            aligned = panel.select(["date", y_name, x_name]).drop_nulls()  # per-pair overlap
            split = int(aligned.height * cfg.stat_arb.insample_frac)
            oos_len = aligned.height - split
            if split < cfg.stat_arb.min_obs or oos_len < cfg.stat_arb.zscore_window + 5:
                continue  # need enough to fit in-sample AND to trade out-of-sample
            n_candidates += 1  # a pair actually tested for cointegration (the search space)
            y, x = aligned[y_name].to_numpy(), aligned[x_name].to_numpy()
            # Select the pair + fit the hedge ratio IN-SAMPLE only (no look-ahead),
            result, _ = engle_granger(
                y[:split], x[:split], cfg.stat_arb.adf_lags, cfg.stat_arb.adf_threshold
            )
            if not result.cointegrated:
                continue
            # then trade the OOS spread under that fixed in-sample hedge ratio.
            oos_spread = y[split:] - (result.intercept + result.hedge_ratio * x[split:])
            _add_sleeve(
                aligned[split:].select("date"),
                mean_reversion_returns(
                    oos_spread, cfg.stat_arb.entry_z, cfg.stat_arb.exit_z,
                    cfg.stat_arb.zscore_window,
                ),
                {
                    "name": f"{y_name}__{x_name}", "y": y_name, "x": x_name, "sector": sector,
                    "hedge_ratio": result.hedge_ratio, "adf_tstat": result.adf_tstat,
                    "half_life": result.half_life,
                },
            )
        # Johansen multivariate basket of the whole sector (>= min_basket tickers).
        if cfg.stat_arb.use_johansen and len(tickers) >= cfg.stat_arb.min_basket:
            n_candidates += 1
            basket = _johansen_sleeve(panel, tickers, sector, cfg)
            if basket is not None:
                _add_sleeve(*basket)
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
    panel_returns = book_df.select([sleeve["name"] for sleeve in pairs_report]).to_numpy()
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
        # equal-weight sector daily return on the shared calendar-time collapse
        day, series = collapse_to_daily(dates, champion)
        daily[sector] = pl.DataFrame({"date": day, sector: series})
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


def _market_return_by_date(frame: pl.DataFrame) -> dict:
    """{date: equal-weight mean next_ret} — the EXOGENOUS regime-decode basis.

    Prefers the ``market_next_ret`` column pinned by ``build_training_frame``
    at the raw PIT layer (per-date constant, immune to downstream row drops);
    falls back to the mean over the frame's surviving rows for legacy frames.
    ``next_ret`` shares the champion series' timing convention (decision at t,
    realized t -> t+1), so market state and book return describe the same day."""
    if "market_next_ret" in frame.columns:
        daily = (
            frame.select("date", "market_next_ret").drop_nulls()
            .unique(subset=["date"]).sort("date")
        )
        return dict(
            zip(daily["date"].to_list(), daily["market_next_ret"].to_list(), strict=True)
        )
    if "next_ret" not in frame.columns:
        return {}
    daily = (
        frame.drop_nulls("next_ret").group_by("date")
        .agg(pl.col("next_ret").mean().alias("mkt")).sort("date")
    )
    return dict(zip(daily["date"].to_list(), daily["mkt"].to_list(), strict=True))


def _evaluate_and_promote(frame: pl.DataFrame, results: dict, output_dir, cfg) -> dict:
    registry = PromotionRegistry(Path(output_dir) / "promotion_registry.json")
    decisions: dict[str, bool] = {}
    market_by_date = _market_return_by_date(frame)
    for sector, result in results.items():
        trials = result["trial_sharpes"]
        if not trials:
            continue
        best = int(np.argmax(trials))
        pooled_matrix = pl.read_parquet(result["candidate_path"].replace(
            "_candidate.json", "_returns_matrix.parquet"
        )).to_numpy()
        pooled_champion = pooled_matrix[:, best]
        paths = _load_champion_paths(result["candidate_path"])
        dates = _load_sample_dates(result["candidate_path"])
        market_returns = None
        days = None
        if dates is not None and len(dates) == pooled_matrix.shape[0]:
            # Calendar-time axis: every gate statistic below runs on equal-weight
            # per-date returns (one shared collapse keeps trial columns aligned),
            # so n_obs / sqrt(252) / "years" mean what the formulas assume.
            days, eval_matrix = collapse_to_daily(dates, pooled_matrix)
            if paths is not None and paths.shape[1] == len(dates):
                paths = collapse_to_daily(dates, paths.T)[1].T
            if market_by_date:
                market_returns = np.array(
                    [market_by_date.get(d, 0.0) for d in days], dtype=np.float64
                )
        else:  # legacy artifacts without sample dates: pooled behavior unchanged
            _logger.warning("%s: no sample dates; evaluating on pooled samples", sector)
            eval_matrix = pooled_matrix
        champion_returns = eval_matrix[:, best]

        dsr = _deflated_sharpe(champion_returns, trials, eval_matrix, cfg)
        path_pass_fraction, path_dsr_median = _path_dsr_stats(paths, trials, eval_matrix, cfg)
        if result.get("kind") == "long_short":
            # A book-level candidate has no per-name booster to bootstrap (its
            # candidate.json is a manifest); its synthetic-gauntlet statistic is
            # the within-date permutation-null margin computed by the sleeve —
            # the same gate (`<= synthetic_sr_min` rejects) applies verbatim.
            synthetic_sr = float(result["synthetic_margin"])
        else:
            # The synthetic HMM gauntlet block-bootstraps the per-sample FEATURE
            # matrix, so its champion series stays row-aligned with samples (pooled).
            synthetic_sr = _synthetic_sharpe(frame, sector, result, pooled_champion, cfg)
        # Overfitting/selection diagnostics over the full (n_obs x n_trials) matrix.
        champion_sharpe = sharpe_ratio(champion_returns)
        pbo = probability_of_backtest_overfitting(eval_matrix, cfg.evaluation.pbo_partitions)
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
                eval_matrix,
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
            # Realized OOS trades behind the champion series: an entry threshold
            # that never fires yields an all-zero series whose DSR/PSR/PBO are
            # 0.0 by construction — name that explicitly instead of "low DSR".
            # Counted on the POOLED samples: a daily mean blurs distinct trades.
            n_trades=int(np.count_nonzero(pooled_champion)),
            n_obs=int(champion_returns.size),
            path_pass_fraction=path_pass_fraction,
            path_fraction_threshold=cfg.evaluation.cpcv_path_min_fraction,
            path_dsr_median=path_dsr_median,
            path_gate_enabled=cfg.evaluation.cpcv_path_gate_enabled,
            reality_check_pvalue=reality_check_p,
            reality_check_gate_enabled=cfg.evaluation.reality_check_gate_enabled,
            reality_check_threshold=cfg.evaluation.reality_check_threshold,
        )
        verdict = None
        if cfg.evaluation.regime_breakdown_enabled or (
            cfg.evaluation.regime_gate_enabled and decision.promoted
        ):
            verdict = _regime_verdict(
                champion_returns, trials, eval_matrix, cfg, market_returns=market_returns
            )
        if cfg.evaluation.regime_breakdown_enabled and verdict is not None:
            causal = (
                # mirror the TRADABLE decoder's spec (long_short.causal_window_days)
                # so the cross-check describes the instrument a policy would use
                _causal_breakdown(
                    champion_returns, days, market_by_date,
                    span=getattr(cfg.long_short, "causal_window_days", 252) or None,
                )
                if (market_by_date and days is not None)
                else None
            )
            decision = replace(
                decision, regime_breakdown=_regime_breakdown(verdict, cfg, causal=causal)
            )
        if cfg.evaluation.regime_gate_enabled and decision.promoted:
            if not verdict.promoted:
                # Distinguish "a regime failed its DSR" from "nothing was
                # testable" (all regimes thin, or the HMM failed to fit).
                reason = (
                    "failed per-regime DSR"
                    if verdict.per_regime
                    else "regime gate: no testable regime"
                )
                decision = replace(decision, promoted=False, reason=reason)
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


def _load_sample_dates(candidate_path):
    """Per-sample dates row-aligned with the persisted returns matrix (None if absent)."""
    dates_file = Path(candidate_path.replace("_candidate.json", "_sample_dates.parquet"))
    if not dates_file.exists():
        return None
    return pl.read_parquet(dates_file)["date"]


def _per_period_trials(trial_sharpes) -> np.ndarray:
    """De-annualize trial Sharpes for deflation statistics.

    ``grid_search``/``long_short`` store ANNUALIZED trial Sharpes (via
    ``sharpe_ratio``, x sqrt(252)) — the right unit for reporting. Every
    deflation statistic, however, runs on the per-period (daily) axis:
    ``deflated_sharpe_report`` benchmarks the champion's per-period Sharpe
    against ``expected_max_sharpe(var(trial_sharpes), N)``. Feeding annualized
    numbers inflates that benchmark by sqrt(252) (~16x) — which silently made
    the per-regime gate unclearable (implied hurdles of 2.4-4.7 ANNUALIZED
    Sharpe per regime slice; run 57e4507c774f rejected slices with OOS
    annualized Sharpe 2.7 at DSR 0.005). Convert at this boundary only, so
    manifests/diagnostics keep their human-readable annualized values.
    """
    return np.asarray(trial_sharpes, dtype=np.float64) / np.sqrt(252.0)


def _path_dsr_stats(paths, trials, returns_matrix, cfg):
    """Per-path Deflated Sharpe over the phi CPCV paths: (pass_fraction, median).

    Each path is the champion strategy resampled, so it is deflated by the same
    (effective) trial count and cross-trial variance as the mean-path DSR; the
    pass fraction is the share of paths individually clearing the threshold.
    """
    if paths is None or paths.shape[0] == 0:
        return None, None
    trials_pp = _per_period_trials(trials)
    if cfg.evaluation.use_effective_trials:
        n_eff = effective_number_of_trials(returns_matrix.T)
        path_dsrs = np.array(
            [deflated_sharpe_report(path, n_eff, trial_sharpes=trials_pp).dsr for path in paths]
        )
    else:
        path_dsrs = np.array([compute_deflated_sharpe_ratio(path, trials_pp) for path in paths])
    pass_fraction = float(np.mean(path_dsrs >= cfg.evaluation.dsr_promotion_threshold))
    return pass_fraction, float(np.median(path_dsrs))


def _deflated_sharpe(champion_returns, trials, returns_matrix, cfg) -> float:
    """Deflated Sharpe for the champion. With ``use_effective_trials`` the trial
    count is the correlation-adjusted N_eff (correlated grid configs otherwise
    over-deflate the DSR); the per-trial Sharpes still supply the variance
    (de-annualized — see :func:`_per_period_trials`).
    ``returns_matrix`` is the (n_obs x n_trials) numpy evaluation matrix."""
    trials_pp = _per_period_trials(trials)
    if cfg.evaluation.use_effective_trials:
        n_eff = effective_number_of_trials(returns_matrix.T)
        return deflated_sharpe_report(champion_returns, n_eff, trial_sharpes=trials_pp).dsr
    return compute_deflated_sharpe_ratio(champion_returns, trials_pp)


def _causal_breakdown(champion_returns, days, market_by_date, span=None) -> dict:
    """Leak-free cross-check of the HMM verdict: the champion's per-state
    economics under the causal expanding-percentile vol decoder (deterministic,
    no fit, no look-ahead). Pure observability — the HMM stays the judge; when
    both decoders agree on WHERE the book is weak, the finding is
    methodology-robust (the audit's calm-state result was exactly this)."""
    from new_pipeline.tournament.regime_state import causal_states_from_series

    all_days = sorted(market_by_date)
    states = causal_states_from_series(
        all_days, [market_by_date[d] for d in all_days], span=span
    )
    seq = np.array([states.get(d, 0) for d in days])
    returns = np.asarray(champion_returns, dtype=np.float64)
    out = {}
    for state in sorted(set(seq.tolist())):
        seg = returns[seq == state]
        out[int(state)] = {
            "sr_annual": round(float(sharpe_ratio(seg)), 3) if seg.size > 1 else None,
            "n_days": int(seg.size),
            "share": round(float(seg.size / max(len(days), 1)), 3),
        }
    return out


def _regime_breakdown(verdict, cfg, causal=None) -> dict:
    """What the per-regime gate saw: per-state DSR/Sharpe/day-count (pass/fail
    against the bar the gate ACTUALLY applied — T**K under the family-wise
    calibration), thin states skipped, and each state's share of days - so a
    rejection names WHICH regime killed the model. ``causal`` (optional) is the
    :func:`_causal_breakdown` cross-check, recorded alongside."""
    threshold = (
        verdict.effective_threshold
        if verdict.effective_threshold is not None
        else cfg.evaluation.dsr_promotion_threshold
    )
    states = verdict.states
    shares, runs = {}, {}
    if states is not None:
        seq = np.asarray(states)
        for s in np.unique(seq):
            mask = (seq == s).astype(int)
            shares[int(s)] = round(float(mask.mean()), 3)
            edges = np.flatnonzero(np.diff(np.concatenate([[0], mask, [0]])))
            lengths = edges.reshape(-1, 2)[:, 1] - edges.reshape(-1, 2)[:, 0]
            # decode-quality forensic: genuine regimes persist for weeks; a
            # sign-partition degeneracy shows 1-2 day mean runs.
            runs[int(s)] = round(float(lengths.mean()), 1) if lengths.size else 0.0
    return {
        "per_regime": {
            int(s): {
                "dsr": round(float(r.dsr), 4),
                "sr_annual": round(float(r.sr_annual), 3),
                "n_days": int(r.n_obs),
                "share": shares.get(int(s)),
                "mean_run_days": runs.get(int(s)),
                "passes": bool(r.dsr >= threshold),
            }
            for s, r in verdict.per_regime.items()
        },
        "skipped_thin": [int(s) for s in verdict.skipped_regimes],
        "threshold": round(float(threshold), 6),
        **({"causal_states": causal} if causal is not None else {}),
    }


def _regime_verdict(
    champion_returns, trials, returns_matrix, cfg, market_returns=None
) -> RegimeVerdict:
    """Per-regime DSR gate: the HMM decodes EXOGENOUS market states (equal-
    weight universe return + its rolling vol) and the champion's OOS returns
    must clear the DSR threshold within every testable state.

    The decode basis matters: regimes are states of the WORLD, not partitions
    of the strategy's P&L. Decoding the champion's own returns (the legacy
    behavior, kept as fallback when no market series is available) degenerates
    on smooth diversified books into a sign partition — 1-2 day "regimes" of
    up-days vs down-days that veto any profitable series by construction
    (recorded instance: Liquid-1500 run 2b71aeff8089, mean state runs 1.8/2.4
    days, sign fractions 0.99/0.11).

    Deflation inputs mirror the full-sample gate exactly: the SAME effective
    trial count (N_eff under ``use_effective_trials``, raw count otherwise) and
    the SAME per-period trial-Sharpe variance. The pre-correction gate passed
    the raw count with ANNUALIZED trial Sharpes, an inconsistent and
    unclearable benchmark (see ``_per_period_trials``)."""
    basis = champion_returns if market_returns is None else market_returns
    if market_returns is None:
        _logger.warning(
            "regime gate: no market series available; decoding on the champion's "
            "own returns (legacy fallback — degenerate on smooth books)"
        )
    volatility = pd.Series(basis).rolling(10).std().bfill().fillna(0.0).to_numpy()
    evaluator = QuantitativeEvaluator(
        min_dsr_threshold=cfg.evaluation.dsr_promotion_threshold,
        n_components=cfg.evaluation.hmm_states,
        min_regime_obs=cfg.evaluation.min_regime_obs,
        thin_policy=ThinRegimePolicy(cfg.evaluation.thin_regime_policy),
        family_wise=cfg.evaluation.regime_family_wise,
    )
    n_trials = (
        effective_number_of_trials(returns_matrix.T)
        if cfg.evaluation.use_effective_trials
        else len(trials)
    )
    return evaluator.evaluate_model_robustness(
        champion_returns, volatility, n_trials,
        trial_sharpes=_per_period_trials(trials), decode_returns=basis,
    )
