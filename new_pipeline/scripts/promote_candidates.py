"""Manually promote gauntlet candidates into the paper-trading registry.

The gauntlet's registry is the honest record: rows say what the gates decided
and are never rewritten. Deployment is a HUMAN decision layered on top — this
tool copies a run's candidate artifacts into a durable models directory and
appends an explicitly-marked ``MANUAL OVERRIDE`` promotion row to the TARGET
registry (default ``./models/prod/promotion_registry.json``), which is what
``run_trading_session`` and the paper book executor read. The source run's own
registry is never touched, so the audit trail stays truthful: gate verdict and
deployment decision are two different facts, recorded separately.

    # one candidate (the champion book)
    python -m new_pipeline.scripts.promote_candidates \
        --run-dir <run>/output --key "Universe Long Short"

    # every sector champion (the 13 per-sector boosters; excludes the book)
    python -m new_pipeline.scripts.promote_candidates \
        --run-dir <run>/output --all-sectors
"""

import argparse
import json
import shutil
from pathlib import Path

from new_pipeline.evaluation.promotion import PromotionDecision, PromotionRegistry
from new_pipeline.tournament.long_short import LONG_SHORT_KEY

_DECISION_FIELDS = (
    "dsr", "synthetic_sharpe", "pbo", "psr", "haircut_sharpe",
    "cpcv_path_pass_fraction", "cpcv_path_dsr_median", "reality_check_pvalue",
    "n_trades", "n_obs", "regime_breakdown",
)


def _latest_rows(run_registry: Path) -> dict:
    """{sector: last registry row} — one gauntlet appends one row per key."""
    data = json.loads(run_registry.read_text(encoding="utf-8"))
    rows: dict[str, dict] = {}
    for row in data.get("promotions", []):
        rows[row["sector"]] = row
    return rows


def _slug(key: str) -> str:
    return key.lower().replace(" ", "_")


def _copy_artifacts(run_dir: Path, key: str, dest: Path) -> Path:
    """Copy the candidate + its sidecars out of the (ephemeral) run dir into a
    durable models directory; returns the copied candidate path."""
    slug = _slug(key)
    dest.mkdir(parents=True, exist_ok=True)
    candidate = run_dir / f"{slug}_candidate.json"
    if not candidate.exists():
        raise FileNotFoundError(f"no candidate artifact for {key!r}: {candidate}")
    copied = dest / candidate.name
    shutil.copy2(candidate, copied)
    for sidecar in run_dir.glob(f"{slug}_*"):
        if sidecar != candidate and sidecar.is_file():
            shutil.copy2(sidecar, dest / sidecar.name)
    return copied


def manual_promote(run_dir, keys=None, all_sectors=False,
                   registry_path="./models/prod/promotion_registry.json",
                   dest_root="./models/prod/manual") -> list[dict]:
    """Promote ``keys`` (or every sector champion) from ``run_dir`` into the
    target registry with an explicit MANUAL OVERRIDE marker. Returns the
    appended registry entries."""
    run_dir = Path(run_dir)
    rows = _latest_rows(run_dir / "promotion_registry.json")
    if all_sectors:
        keys = [k for k in rows if k != LONG_SHORT_KEY]
    if not keys:
        raise ValueError("nothing to promote: pass keys or all_sectors=True")
    missing = [k for k in keys if k not in rows]
    if missing:
        raise KeyError(f"keys not in run registry: {missing}")

    registry = PromotionRegistry(registry_path)
    dest = Path(dest_root) / run_dir.parent.name
    entries = []
    for key in keys:
        row = rows[key]
        copied = _copy_artifacts(run_dir, key, dest)
        decision = PromotionDecision(
            sector=key,
            promoted=True,
            reason=f"MANUAL OVERRIDE ({row.get('reason', 'gate verdict unavailable')})",
            **{f: row.get(f) for f in _DECISION_FIELDS},
        )
        entries.append(registry.record(decision, model_path=str(copied)))
    return entries


def main() -> None:  # pragma: no cover - argparse shell around tested core
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run-dir", required=True,
                        help="a run's output/ directory (registry + artifacts)")
    parser.add_argument("--key", action="append", default=None,
                        help="registry key to promote (repeatable), e.g. "
                             "'Universe Long Short' or 'Information Technology'")
    parser.add_argument("--all-sectors", action="store_true",
                        help="promote every sector champion (excludes the book)")
    parser.add_argument("--registry", default="./models/prod/promotion_registry.json")
    parser.add_argument("--dest", default="./models/prod/manual")
    args = parser.parse_args()
    entries = manual_promote(args.run_dir, keys=args.key, all_sectors=args.all_sectors,
                             registry_path=args.registry, dest_root=args.dest)
    for entry in entries:
        print(f"promoted {entry['sector']!r} -> {entry['model_path']}")


if __name__ == "__main__":  # pragma: no cover
    main()
