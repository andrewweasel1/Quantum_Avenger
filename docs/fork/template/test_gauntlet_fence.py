"""The promotion gauntlet is pinned: its code by SHA-256, its thresholds by value.

Every verdict under ``evidence/`` was produced by this code under these
settings. Change either and the old rejections stop being comparable to
anything a new strategy is scored against — and a session asked to find a
profitable model, holding an editable copy of its own judge, has one very
cheap path to success.

A change here is sometimes right. It is never incidental: it needs the owner's
explicit sign-off, after which the pins are regenerated in the same reviewed
commit (commands in docs/fork/MANIFEST.md, "Changing the gauntlet").
"""

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
CODE_PINS = ROOT / "docs" / "fork" / "GAUNTLET.sha256"
CONFIG_PIN = ROOT / "docs" / "fork" / "GAUNTLET_CONFIG.json"
REMEDY = ("If this change is intended, it needs the owner's explicit sign-off; "
          "then regenerate the pins as described in docs/fork/MANIFEST.md.")


def _code_pins() -> dict[str, str]:
    pins = {}
    for line in CODE_PINS.read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, path = line.split(maxsplit=1)
        pins[path.strip().lstrip("*")] = digest
    return pins


def test_gauntlet_code_is_byte_identical_to_its_pins():
    pins = _code_pins()
    assert pins, "the code manifest must pin something"
    changed = sorted(
        path for path, digest in pins.items()
        if not (ROOT / path).exists()
        or hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest)
    assert not changed, f"gauntlet code changed or missing: {changed}. {REMEDY}"


def test_no_unpinned_module_has_joined_the_gauntlet():
    """A new file in evaluation/ is a change to the judge too: code that scores
    a strategy must not be able to arrive without the same sign-off."""
    present = {p.relative_to(ROOT).as_posix()
               for p in (ROOT / "new_pipeline" / "evaluation").glob("*.py")}
    unpinned = sorted(present - set(_code_pins()))
    assert not unpinned, f"unpinned gauntlet modules: {unpinned}. {REMEDY}"


def test_gauntlet_thresholds_match_their_pin():
    """Read in a scrubbed subprocess, so neither the suite's own config overlay
    nor a QA_* variable in a developer's shell can make a softened default
    look pinned. ``registry_path`` is storage, not a threshold, and is free."""
    env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": str(ROOT)}
    code = ("import json; from new_pipeline.config import get_config; "
            "print(json.dumps(get_config().evaluation.model_dump(), sort_keys=True))")
    done = subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env,
                          capture_output=True, text=True, timeout=120, check=False)
    assert done.returncode == 0, done.stderr[-2000:]
    live = json.loads(done.stdout)
    pinned = json.loads(CONFIG_PIN.read_text())
    live.pop("registry_path", None)
    pinned.pop("registry_path", None)
    drift = {key: {"pinned": pinned.get(key), "now": live.get(key)}
             for key in sorted(set(pinned) | set(live))
             if pinned.get(key) != live.get(key)}
    assert not drift, f"gauntlet thresholds drifted from their pin: {drift}. {REMEDY}"
