from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def project_root() -> Path:
    return PROJECT_ROOT


def data_dir() -> Path:
    return PROJECT_ROOT / "data"


def logs_dir() -> Path:
    return PROJECT_ROOT / "logs"
