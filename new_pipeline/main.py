import argparse
from pathlib import Path

from new_pipeline.config import get_config, reload_config
from new_pipeline.core.logging import configure_logging
from new_pipeline.data.vaults import VaultManager
from new_pipeline.monitoring.health import HealthCheck


def run_show_config() -> None:
    config = get_config()
    print(config.model_dump_json(indent=2))


def run_init_vaults() -> None:
    manager = VaultManager()
    raw, processed = manager.ensure_vaults()
    print(f"Raw vault: {raw}")
    print(f"Processed vault: {processed}")


def run_health() -> None:
    print(HealthCheck().status())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Quantum Avenger Phase 1 CLI")
    parser.add_argument("command", choices=["show-config", "init-vaults", "health"], help="CLI command to execute")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    configure_logging()

    if args.command == "show-config":
        run_show_config()
    elif args.command == "init-vaults":
        run_init_vaults()
    elif args.command == "health":
        run_health()
