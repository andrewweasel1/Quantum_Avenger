"""Derive control-panel "knob" metadata from the Pydantic config schema.

The React control panel renders itself from this metadata, so it never hard-codes the
~200 config fields. Field name / type / default come from Pydantic introspection
(always in sync with the schema); descriptions, enum options, and slider ranges for
the *tunable* knobs come from the curated ``KNOB_META`` map below (the schema uses
inline ``#`` comments rather than ``Field(description=...)``, so they aren't
introspectable). Fields without curated metadata still render from their type.
"""

import typing

from pydantic_core import PydanticUndefined

from new_pipeline.config.schema import AppConfig

# Curated metadata for the tunable knobs: option lists for the str-enums and
# list-multiselects (the schema stores them as plain str/list), slider ranges, and
# human descriptions. Groups flagged ``primary`` lead the control panel.
KNOB_META: dict = {
    "features": {
        "label": "Features & Signals", "primary": True,
        "fields": {
            "factor_set": {
                "description": "Cross-sectional alpha factors (default off).",
                "control": "multiselect",
                "options": ["mom_12_1", "reversal_21", "low_vol", "seasonality",
                            "book_to_market", "earnings_yield", "roe"],
            },
            "extended_features": {
                "description": "Per-ticker feature families (default off).",
                "control": "multiselect",
                "options": ["fracdiff", "vol_estimators", "microstructure", "garch"],
            },
            "factor_sector_neutral": {"description": "Sector-demean before the z-score."},
            "fracdiff_d": {"description": "Fractional-differencing order.",
                           "min": 0.0, "max": 1.0, "step": 0.05},
            "fracdiff_threshold": {"description": "Frac-diff weight-truncation threshold.",
                                   "min": 1e-4, "max": 1e-2, "step": 1e-4},
            "vol_window": {"description": "Range vol-estimator window.", "min": 5, "max": 60},
            "micro_window": {"description": "Microstructure window.", "min": 5, "max": 60},
            "garch_fit_window": {"description": "GARCH(1,1) MLE fit window.",
                                 "min": 60, "max": 504},
            "label_horizon": {"description": "Label look-ahead (bars).", "min": 1, "max": 20},
            "label_method": {"description": "Target label method.",
                             "control": "select", "options": ["triple_barrier", "friction"]},
        },
    },
    "tournament": {
        "label": "Tournament & Model", "primary": True,
        "fields": {
            "num_boost_round": {"description": "XGBoost boosting rounds.", "min": 10, "max": 500},
            "n_groups": {"description": "CPCV groups.", "min": 4, "max": 10},
            "test_groups": {"description": "CPCV test groups.", "min": 1, "max": 4},
            "purge_days": {"description": "CPCV purge window.", "min": 0, "max": 20},
            "embargo_days": {"description": "CPCV embargo window.", "min": 0, "max": 20},
            "penalty_fp": {"description": "False-positive loss weight.", "min": 1.0, "max": 10.0,
                           "step": 0.5},
            "penalty_fn": {"description": "False-negative loss weight.", "min": 1.0, "max": 10.0,
                           "step": 0.5},
            "feature_selection_method": {"description": "Feature selection.", "control": "select",
                                         "options": ["causal", "clustered_permutation"]},
            "causal_alpha": {"description": "Granger BHY keep threshold.", "min": 0.01, "max": 0.5,
                             "step": 0.01},
            "sample_weighting": {"description": "Overlapping-label weighting.", "control": "select",
                                 "options": ["uniqueness", "none"]},
            "enable_meta_labeling": {"description": "Secondary act/size model."},
            "meta_threshold": {"description": "Meta P(win) cutoff.", "min": 0.3, "max": 0.8,
                               "step": 0.05},
            "meta_criterion": {"description": "Meta improvement metric.", "control": "select",
                               "options": ["f1", "precision"]},
            "max_workers": {"description": "Parallel sectors.", "min": 1, "max": 8},
        },
    },
    "evaluation": {
        "label": "Significance Gates", "primary": True,
        "fields": {
            "dsr_promotion_threshold": {"description": "Deflated-Sharpe promotion gate.",
                                        "min": 0.5, "max": 0.99, "step": 0.01},
            "pbo_threshold": {"description": "Max Probability of Backtest Overfitting.",
                              "min": 0.1, "max": 0.9, "step": 0.05},
            "use_effective_trials": {"description": "Correlation-adjusted deflation."},
            "cpcv_path_gate_enabled": {"description": "CPCV path-distribution DSR gate."},
            "cpcv_path_min_fraction": {"description": "Min fraction of paths clearing DSR.",
                                       "min": 0.1, "max": 1.0, "step": 0.05},
            "regime_gate_enabled": {"description": "Per-regime DSR gate."},
            "alpha_eval_enabled": {"description": "Per-signal IC/ICIR diagnostics."},
            "reality_check_enabled": {"description": "White's Reality Check (diagnostic)."},
            "reality_check_gate_enabled": {"description": "Gate on the RC p-value."},
            "reality_check_threshold": {"description": "RC p-value reject threshold.",
                                        "min": 0.01, "max": 0.2, "step": 0.01},
        },
    },
    "portfolio": {
        "label": "Portfolio Combination", "primary": True,
        "fields": {
            "enabled": {"description": "Combine sectors into a book."},
            "method": {"description": "Allocation method.", "control": "select",
                       "options": ["hrp", "nco", "inverse_variance", "ic_weighted", "equal"]},
            "cov_method": {"description": "Covariance cleaning.", "control": "select",
                           "options": ["rmt", "ledoit_wolf", "sample"]},
            "min_obs": {"description": "Min stream length to combine.", "min": 5, "max": 60},
        },
    },
    "stat_arb": {
        "label": "Statistical Arbitrage", "primary": True,
        "fields": {
            "enabled": {"description": "Cointegration / OU mean-reversion family."},
            "adf_threshold": {"description": "ADF stationarity cutoff.", "min": -4.0, "max": -2.0,
                              "step": 0.1},
            "insample_frac": {"description": "In-sample fit fraction (rest OOS).",
                              "min": 0.3, "max": 0.8, "step": 0.05},
            "entry_z": {"description": "Z-score entry.", "min": 1.0, "max": 3.0, "step": 0.25},
            "exit_z": {"description": "Z-score exit.", "min": 0.0, "max": 1.5, "step": 0.25},
            "use_johansen": {"description": "Johansen multivariate baskets."},
            "max_pairs_per_sector": {"description": "Max pairs per sector.", "min": 1, "max": 6},
        },
    },
    "execution": {
        "label": "Risk & Execution", "primary": True,
        "fields": {
            "max_risk_per_trade": {"description": "Max risk per trade (fraction).",
                                   "min": 0.005, "max": 0.05, "step": 0.005},
            "atr_stop_multiplier": {"description": "ATR stop multiple.", "min": 1.0, "max": 4.0,
                                    "step": 0.5},
            "confidence_threshold": {"description": "Signal probability cutoff.",
                                     "min": 0.5, "max": 0.9, "step": 0.05},
            "account_capital": {"description": "Capital base for sizing.",
                                "min": 10000, "max": 1000000, "step": 10000},
        },
    },
}


def _type_name(annotation) -> str:
    """Map a Pydantic field annotation to a control hint: bool/int/float/str/list."""
    if annotation is bool:
        return "bool"
    if annotation is int:
        return "int"
    if annotation is float:
        return "float"
    if annotation is str:
        return "str"
    if typing.get_origin(annotation) in (list, typing.List):  # noqa: UP006
        return "list"
    return "str"


def _default_value(field):
    """JSON-safe static default, or ``None`` for required fields (whose effective
    value comes from ``defaults.yaml`` and is served live by ``GET /api/config``)."""
    if field.default_factory is not None:
        try:
            return field.default_factory()
        except TypeError:  # pragma: no cover - factory needing validated data
            return None
    if field.default is PydanticUndefined:
        return None
    return field.default


def _control(type_name: str, meta: dict) -> str:
    if "control" in meta:
        return meta["control"]
    if type_name == "bool":
        return "switch"
    if type_name == "list":
        return "multiselect"
    if type_name in ("int", "float") and "min" in meta and "max" in meta:
        return "slider"
    if type_name in ("int", "float"):
        return "number"
    return "text"


def config_schema() -> dict:
    """Group/field metadata for the control panel, derived from ``AppConfig``."""
    groups = []
    for group_key, group_field in AppConfig.model_fields.items():
        sub_model = group_field.annotation
        if not (isinstance(sub_model, type) and hasattr(sub_model, "model_fields")):
            continue
        group_meta = KNOB_META.get(group_key, {})
        fields_meta = group_meta.get("fields", {})
        fields = []
        for field_name, field in sub_model.model_fields.items():
            type_name = _type_name(field.annotation)
            meta = fields_meta.get(field_name, {})
            fields.append({
                "name": field_name,
                "type": type_name,
                "default": _default_value(field),
                "control": _control(type_name, meta),
                "description": meta.get("description", ""),
                "options": meta.get("options"),
                "min": meta.get("min"),
                "max": meta.get("max"),
                "step": meta.get("step"),
                "tunable": field_name in fields_meta,
            })
        groups.append({
            "key": group_key,
            "label": group_meta.get("label", group_key.replace("_", " ").title()),
            "primary": group_meta.get("primary", False),
            "fields": fields,
        })
    groups.sort(key=lambda g: (not g["primary"], g["key"]))
    return {"groups": groups}
