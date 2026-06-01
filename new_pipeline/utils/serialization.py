import json
from pathlib import Path
from typing import Any


def to_json(obj: Any, path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(obj, handle, indent=2)


def from_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
