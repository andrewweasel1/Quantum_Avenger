"""Parse a run's output artifacts into chart-ready JSON for the dashboards.

Reuses the engine's own accessors — ``tearsheet.summary_metrics`` and
``simulator.sharpe_ratio`` — so the API reports exactly what the engine computes.
The per-sector champion is recovered as the highest-Sharpe column of the persisted
``returns_matrix`` (the champion index isn't written to disk).
"""

import json
from pathlib import Path

import numpy as np
import polars as pl

from new_pipeline.evaluation.tearsheet import summary_metrics
from new_pipeline.tournament.accounting import collapse_to_daily
from new_pipeline.tournament.simulator import sharpe_ratio

_MAX_PATHS = 12  # cap CPCV path lines sent to the UI


def _read_json(path: Path):
    return json.loads(path.read_text()) if path.exists() else None


def _equity(returns: np.ndarray) -> list[float]:
    return np.cumprod(1.0 + returns).tolist()


def _load_daily_dates(output: Path, slug: str, n_rows: int):
    """The per-sample dates aligned with this sector's matrix, or None (legacy
    artifacts, or a length mismatch) — the caller then keeps pooled behavior."""
    dates_path = output / f"{slug}_sample_dates.parquet"
    if not dates_path.exists():
        return None
    dates = pl.read_parquet(dates_path)["date"]
    return dates if len(dates) == n_rows else None


def _sector_performance(output: Path) -> list[dict]:
    sectors = []
    for matrix_path in sorted(output.glob("*_returns_matrix.parquet")):
        slug = matrix_path.name.replace("_returns_matrix.parquet", "")
        matrix = pl.read_parquet(matrix_path).to_numpy()  # (n_obs, n_trials)
        if matrix.size == 0:
            continue
        # Calendar-time view when sample dates are present: charts/metrics on the
        # equal-weight daily series, matching the axis the promotion gates use.
        dates = _load_daily_dates(output, slug, matrix.shape[0])
        if dates is not None:
            matrix = collapse_to_daily(dates, matrix)[1]
        champion_idx = int(np.argmax([sharpe_ratio(matrix[:, j]) for j in range(matrix.shape[1])]))
        champion = matrix[:, champion_idx]
        entry = {
            "sector": slug.replace("_", " ").title(),
            "slug": slug,
            "equity": _equity(champion),
            "metrics": summary_metrics(champion),
            "n_trials": int(matrix.shape[1]),
        }
        paths_path = output / f"{slug}_paths.parquet"
        if paths_path.exists():
            paths = pl.read_parquet(paths_path).to_numpy()
            if dates is not None and paths.shape[0] == len(dates):
                paths = collapse_to_daily(dates, paths)[1]
            entry["paths"] = [_equity(paths[:, j]) for j in range(min(paths.shape[1], _MAX_PATHS))]
        features = _read_json(output / f"{slug}_candidate_features.json") or {}
        meta = (features.get("metadata") or {}).get("meta_labeling")
        if meta:
            entry["meta_labeling"] = meta
        sectors.append(entry)
    return sectors


def parse_results(run_dir: Path | str) -> dict:
    """Aggregate a run's artifacts: per-sector equity/metrics/CPCV-paths/confusion,
    the promotion table, alpha-eval IC/ICIR, the portfolio book, and stat-arb pairs."""
    run_dir = Path(run_dir)
    output = run_dir / "output"
    registry = _read_json(output / "promotion_registry.json") or {
        "promotions": [], "active_champions": {}
    }
    return {
        "run_id": run_dir.name,
        "summary": _read_json(run_dir / "summary.json") or {},
        "promotions": registry.get("promotions", []),
        "active_champions": registry.get("active_champions", {}),
        "alpha_eval": _read_json(output / "alpha_eval.json"),
        "portfolio": _read_json(output / "portfolio.json"),
        "stat_arb": _read_json(output / "stat_arb.json"),
        "sectors": _sector_performance(output) if output.exists() else [],
    }
