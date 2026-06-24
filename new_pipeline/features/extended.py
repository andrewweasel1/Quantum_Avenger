"""Extended per-ticker feature families (offense roadmap P1).

Orchestrates the optional P1 signal families — fractional differentiation, range-based
volatility estimators, and microstructure proxies — over a multi-ticker frame,
grouping per ticker so rolling windows never bleed across symbols (mirrors
``polars_engine.compile_features``). Each family is opt-in via ``features.extended_features``
(default empty ⇒ off, pipeline bit-stable) and its columns are appended to the
tournament's feature set, riding the existing causal-selection + CPCV/DSR stack.

Information bars (dollar/volume/imbalance) are intentionally *not* here — they need
intraday/tick data the daily OHLCV source does not provide; deferred to a tick-data
milestone. See ``docs/OFFENSE_ROADMAP.md`` (P1).
"""

import polars as pl

from new_pipeline.core.exceptions import SchemaValidationError
from new_pipeline.features.fracdiff import FRACDIFF_FEATURE_NAMES, add_fracdiff
from new_pipeline.features.microstructure import MICRO_FEATURE_NAMES, add_microstructure
from new_pipeline.features.vol_estimators import VOL_FEATURE_NAMES, add_vol_estimators

SUPPORTED_FAMILIES = ("fracdiff", "vol_estimators", "microstructure")
_FAMILY_FEATURE_NAMES = {
    "fracdiff": FRACDIFF_FEATURE_NAMES,
    "vol_estimators": VOL_FEATURE_NAMES,
    "microstructure": MICRO_FEATURE_NAMES,
}


def extended_feature_names(families) -> list[str]:
    """Output column names contributed by the requested families (order-preserving)."""
    names: list[str] = []
    for family in families:
        names.extend(_FAMILY_FEATURE_NAMES[family])
    return names


def add_extended_features(
    frame: pl.DataFrame, families, fracdiff_d=0.4, fracdiff_threshold=1e-3,
    vol_window=20, micro_window=20,
) -> pl.DataFrame:
    """Append the requested P1 family columns, computed per ticker. No-op when
    ``families`` is empty."""
    if not families:
        return frame
    unknown = [family for family in families if family not in SUPPORTED_FAMILIES]
    if unknown:
        raise SchemaValidationError(f"Unknown extended feature family(ies): {unknown}")
    groups = []
    for _, group in frame.sort(["ticker", "date"]).group_by("ticker", maintain_order=True):
        if "fracdiff" in families:
            group = add_fracdiff(group, fracdiff_d, fracdiff_threshold)
        if "vol_estimators" in families:
            group = add_vol_estimators(group, vol_window)
        if "microstructure" in families:
            group = add_microstructure(group, micro_window)
        groups.append(group)
    return pl.concat(groups) if groups else frame
