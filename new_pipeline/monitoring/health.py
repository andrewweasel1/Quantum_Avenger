"""Real health probes over the system's on-disk state.

Each check reports ``ok`` / ``absent`` / ``error: ...``. Absence is healthy —
vaults and ledgers legitimately don't exist before the first ingest/trade; only
*broken* state (config that won't load, a ledger that won't parse, a corrupt
promotion registry) degrades the overall status. ``scripts/check_health.py``
exits non-zero on ``degraded``, which is what the container liveness probe runs.
"""

import json
from pathlib import Path

import pyarrow.parquet as pq


class HealthCheck:
    def status(self, cfg=None) -> dict:
        if cfg is None:
            try:
                from new_pipeline.config import get_config

                cfg = get_config()
            except Exception as exc:  # config that won't load is itself the finding
                return {"status": "degraded", "checks": {"config": f"error: {exc}"}}

        checks = {
            "config": "ok",
            "raw_vault_dir": _check_dir(cfg.data.raw_vault_dir),
            "processed_vault_dir": _check_dir(cfg.data.processed_vault_dir),
            "veto_ledger": _check_parquet(cfg.dashboard.veto_ledger_path),
            "trade_log": _check_parquet(cfg.dashboard.trade_log_path),
            "promotion_registry": _check_registry(cfg.evaluation.registry_path),
        }
        degraded = any(value.startswith("error") for value in checks.values())
        return {"status": "degraded" if degraded else "healthy", "checks": checks}


def _check_dir(path) -> str:
    return "ok" if Path(path).is_dir() else "absent"


def _check_parquet(path) -> str:
    file = Path(path)
    if not file.exists():
        return "absent"
    try:
        pq.read_schema(file)
        return "ok"
    except Exception as exc:
        return f"error: {exc}"


def _check_registry(path) -> str:
    file = Path(path)
    if not file.exists():
        return "absent"
    try:
        data = json.loads(file.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "promotions" not in data:
            return "error: registry missing 'promotions' key"
        return "ok"
    except Exception as exc:
        return f"error: {exc}"
