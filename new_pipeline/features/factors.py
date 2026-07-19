"""Cross-sectional alpha factors — P0 of the offense roadmap.

``polars_engine.py`` computes per-ticker *time-series* features; this module adds
the missing **cross-sectional** axis: factors that rank a name against its peers
on the *same date*. Each factor is a per-(ticker, date) raw signal — oriented so
higher ⇒ higher expected return — optionally **sector-neutralized**, then
**cross-sectionally z-scored within each date**. Output columns are prefixed
``xf_`` and registered, so they flow through the causal selector + CPCV/DSR
gauntlet exactly like any other feature.

Default-off: :func:`add_cross_sectional_factors` is the identity unless a
non-empty ``factor_set`` is supplied (config ``features.factor_set``), so the
existing pipeline stays bit-stable until a family is explicitly enabled.

See ``docs/OFFENSE_ROADMAP.md`` (P0) and ``docs/quantitative_math.md`` Part II §B.
"""

import polars as pl

from new_pipeline.core.exceptions import SchemaValidationError
from new_pipeline.features.registry import FeatureMetadata, feature_registry

FACTOR_PREFIX = "xf_"

# Canonical lookback windows (trading days).
MOMENTUM_LOOKBACK = 252  # 12 months
MOMENTUM_SKIP = 21  # skip the most recent month (12-1 momentum)
REVERSAL_WINDOW = 21  # short-term (one-month) reversal

SUPPORTED_FACTORS = (
    "mom_12_1", "reversal_21", "low_vol", "seasonality",  # price-derived
    "book_to_market", "earnings_yield", "roe",  # fundamental (value / quality)
    # fundamental quality + growth (richer composite; each an orthogonal input
    # the model combines — raises COMBINED IC without a new data source):
    "roa", "gross_margin", "accruals", "fcf_yield", "revenue_growth", "earnings_growth",
)
# Factors needing point-in-time fundamentals joined onto the frame first.
FUNDAMENTAL_FACTORS = frozenset({
    "book_to_market", "earnings_yield", "roe",
    "roa", "gross_margin", "accruals", "fcf_yield", "revenue_growth", "earnings_growth",
})


def factor_feature_names(factor_set) -> list[str]:
    """Prefixed output column names for a requested ``factor_set`` (preserves order)."""
    return [f"{FACTOR_PREFIX}{name}" for name in factor_set]


def _raw_signal(name: str) -> pl.Expr:
    """Per-(ticker, date) raw factor signal, oriented higher ⇒ higher expected return.

    Uses ``.over("ticker")`` so rolling windows never bleed across symbols; the
    caller must pre-sort by (ticker, date).
    """
    close = pl.col("close")
    if name == "mom_12_1":
        # 12-1 momentum: trailing 12-month return, skipping the most recent month.
        return (close.shift(MOMENTUM_SKIP) / close.shift(MOMENTUM_LOOKBACK) - 1.0).over("ticker")
    if name == "reversal_21":
        # short-term reversal: negative of the trailing one-month return.
        return (-(close / close.shift(REVERSAL_WINDOW) - 1.0)).over("ticker")
    if name == "low_vol":
        # low-volatility anomaly: lower realized vol ⇒ higher risk-adjusted return.
        return -pl.col("volatility")
    if name == "seasonality":
        return _seasonality_raw()
    if name == "book_to_market":
        # value: high book value per dollar of price ⇒ cheap.
        return pl.col("book_value_per_share") / close
    if name == "earnings_yield":
        # value: earnings per dollar of price.
        return pl.col("earnings_per_share") / close
    if name == "roe":
        # quality: return on equity (higher ⇒ more profitable).
        return pl.col("return_on_equity")
    if name == "roa":
        # quality: return on assets (profitability per dollar of assets).
        return pl.col("return_on_assets")
    if name == "gross_margin":
        # quality: gross profit per dollar of revenue (pricing power / moat).
        return pl.col("gross_margin")
    if name == "accruals":
        # quality: LOW accruals ⇒ higher-quality (cash-backed) earnings, so the
        # signal is the negative (Sloan accrual anomaly).
        return -pl.col("accruals")
    if name == "fcf_yield":
        # value: operating cash flow per dollar of price.
        return pl.col("ocf_per_share") / close
    if name == "revenue_growth":
        # growth: year-over-year revenue growth.
        return pl.col("revenue_growth")
    if name == "earnings_growth":
        # growth: year-over-year EPS growth.
        return pl.col("earnings_growth")
    raise SchemaValidationError(f"Unknown cross-sectional factor: {name!r}")


def _seasonality_raw() -> pl.Expr:
    """Heston-Sadka same-calendar-month seasonality: the ticker's *causal* mean return
    in this month-of-year over strictly prior observations (needs multi-year history;
    null until at least one prior same-month observation exists)."""
    grp = ["ticker", "_xf_month"]
    ret = pl.col("returns")
    filled = ret.fill_null(0.0)
    valid = ret.is_not_null().cast(pl.Int64)
    prior_sum = filled.cum_sum().over(grp) - filled  # exclude the current observation
    prior_count = valid.cum_sum().over(grp) - valid
    return pl.when(prior_count > 0).then(prior_sum / prior_count).otherwise(None)


def _zscore(name: str) -> pl.Expr:
    """Cross-sectional z-score of a factor's sector-neutralized base, per date.

    Null where the raw signal is null (insufficient history ⇒ the row drops in the
    tournament); neutral 0.0 where a date has no cross-sectional dispersion (≤1
    name, or all-equal) so a degenerate date never injects NaN/inf.
    """
    raw = pl.col(f"_xf_raw_{name}")
    base = pl.col(f"_xf_base_{name}")
    std_d = base.std().over("date")
    z = (base - base.mean().over("date")) / std_d
    return (
        pl.when(raw.is_null())
        .then(pl.lit(None, dtype=pl.Float64))
        .when(std_d.is_null() | (std_d == 0.0))
        .then(pl.lit(0.0))
        .otherwise(z)
        .alias(f"{FACTOR_PREFIX}{name}")
    )


def add_cross_sectional_factors(
    frame: pl.DataFrame, factor_set, *, sector_neutral: bool = True, null_policy: str = "drop"
) -> pl.DataFrame:
    """Append cross-sectional ``xf_*`` factor columns for the requested ``factor_set``.

    No-op (identity) when ``factor_set`` is empty. Requires ``close`` and, depending
    on the factors, ``returns`` / ``volatility`` (all produced by ``compile_features``);
    ``sector_neutral`` additionally requires a ``sector`` column (else it is skipped).

    ``null_policy`` governs rows whose FUNDAMENTAL factor inputs are missing
    (no resolvable filings — e.g. departed names): ``"neutral"`` fills their
    ``xf_`` z-scores with 0.0 (exactly-average exposure) so the rows survive
    the tournament's ``drop_nulls`` — with a point-in-time universe, dropping
    them would silently reintroduce the survivorship the fixture removed.
    ``"drop"`` (the function default; config default is "neutral") preserves
    the legacy null-propagation. Price-factor warmup nulls always stay null.
    """
    if not factor_set:
        return frame
    unknown = [name for name in factor_set if name not in SUPPORTED_FACTORS]
    if unknown:
        raise SchemaValidationError(f"Unknown cross-sectional factor(s): {unknown}")
    _register(factor_set)
    neutral = sector_neutral and "sector" in frame.columns

    out = frame.sort(["ticker", "date"])
    if "seasonality" in factor_set:
        out = out.with_columns(pl.col("date").dt.month().alias("_xf_month"))

    out = out.with_columns(
        [_raw_signal(name).alias(f"_xf_raw_{name}") for name in factor_set]
    )
    out = out.with_columns(
        [
            (
                pl.col(f"_xf_raw_{name}")
                - pl.col(f"_xf_raw_{name}").mean().over(["date", "sector"])
                if neutral
                else pl.col(f"_xf_raw_{name}")
            ).alias(f"_xf_base_{name}")
            for name in factor_set
        ]
    )
    out = out.with_columns([_zscore(name) for name in factor_set])
    if null_policy == "neutral":
        fundamental = [n for n in factor_set if n in FUNDAMENTAL_FACTORS]
        if fundamental:
            out = out.with_columns(
                [pl.col(f"{FACTOR_PREFIX}{n}").fill_null(0.0) for n in fundamental]
            )

    scratch = [f"_xf_raw_{name}" for name in factor_set]
    scratch += [f"_xf_base_{name}" for name in factor_set]
    if "_xf_month" in out.columns:
        scratch.append("_xf_month")
    return out.drop(scratch)


def _factor_metadata() -> dict[str, FeatureMetadata]:
    return {
        "mom_12_1": FeatureMetadata(
            "xf_mom_12_1", "Cross-sectional 12-1 momentum (z-scored).", "price", "252d"
        ),
        "reversal_21": FeatureMetadata(
            "xf_reversal_21", "Cross-sectional short-term reversal (z-scored).", "price", "21d"
        ),
        "low_vol": FeatureMetadata(
            "xf_low_vol", "Cross-sectional low-volatility factor (z-scored).", "price", "20d"
        ),
        "seasonality": FeatureMetadata(
            "xf_seasonality",
            "Cross-sectional same-month seasonality (z-scored).",
            "price",
            "annual",
        ),
        "book_to_market": FeatureMetadata(
            "xf_book_to_market", "Cross-sectional book-to-market value (z-scored).",
            "fundamental", "quarterly",
        ),
        "earnings_yield": FeatureMetadata(
            "xf_earnings_yield", "Cross-sectional earnings yield (z-scored).",
            "fundamental", "quarterly",
        ),
        "roe": FeatureMetadata(
            "xf_roe", "Cross-sectional return-on-equity quality (z-scored).",
            "fundamental", "quarterly",
        ),
        "roa": FeatureMetadata(
            "xf_roa", "Cross-sectional return-on-assets quality (z-scored).",
            "fundamental", "quarterly",
        ),
        "gross_margin": FeatureMetadata(
            "xf_gross_margin", "Cross-sectional gross-margin quality (z-scored).",
            "fundamental", "quarterly",
        ),
        "accruals": FeatureMetadata(
            "xf_accruals", "Cross-sectional (negative) accruals quality (z-scored).",
            "fundamental", "quarterly",
        ),
        "fcf_yield": FeatureMetadata(
            "xf_fcf_yield", "Cross-sectional operating-cash-flow yield (z-scored).",
            "fundamental", "quarterly",
        ),
        "revenue_growth": FeatureMetadata(
            "xf_revenue_growth", "Cross-sectional YoY revenue growth (z-scored).",
            "fundamental", "annual",
        ),
        "earnings_growth": FeatureMetadata(
            "xf_earnings_growth", "Cross-sectional YoY EPS growth (z-scored).",
            "fundamental", "annual",
        ),
    }


def _register(factor_set) -> None:
    # persist=False: keep the tracked registry YAML stable during runs/tests.
    meta = _factor_metadata()
    for name in factor_set:
        column = f"{FACTOR_PREFIX}{name}"
        if feature_registry.get(column) is None:
            feature_registry.register(column, meta[name], persist=False)
