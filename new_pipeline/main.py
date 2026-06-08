import argparse
import json
from pathlib import Path

from new_pipeline.config import get_config
from new_pipeline.core.logging import configure_logging
from new_pipeline.data.vaults import VaultManager
from new_pipeline.monitoring.health import HealthCheck


def run_show_config() -> None:
    print(get_config().model_dump_json(indent=2))


def run_init_vaults() -> None:
    manager = VaultManager()
    raw, processed = manager.ensure_vaults()
    print(f"Raw vault: {raw}")
    print(f"Processed vault: {processed}")


def run_health() -> None:
    print(HealthCheck().status())


def run_pipeline() -> None:
    # Lazy import so the lightweight commands don't pull xgboost/hmmlearn.
    from new_pipeline.tournament.pipeline import run_offline_pipeline

    summary = run_offline_pipeline(get_config().models.candidate_models_dir)
    print(json.dumps(summary, indent=2))


def run_trade() -> None:
    """Drive promoted champions through the whole trade graph (training first if needed)."""
    from dataclasses import asdict

    from new_pipeline.evaluation.promotion import PromotionRegistry
    from new_pipeline.execution.runner import run_trading_session
    from new_pipeline.tournament.pipeline import run_offline_pipeline

    candidates = get_config().models.candidate_models_dir
    registry = PromotionRegistry(Path(candidates) / "promotion_registry.json")
    if not registry.active_champions():
        print("No champions yet — running the offline pipeline to produce them...")
        run_offline_pipeline(candidates)
    summary = run_trading_session(candidates)
    print(json.dumps(asdict(summary), indent=2))


_COMMANDS = {
    "show-config": run_show_config,
    "init-vaults": run_init_vaults,
    "health": run_health,
    "pipeline": run_pipeline,
    "trade": run_trade,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quantum Avenger CLI")
    parser.add_argument("command", choices=list(_COMMANDS), help="CLI command to execute")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    configure_logging()
    _COMMANDS[args.command]()
