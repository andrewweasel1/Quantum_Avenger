"""Dynamic, RAM-aware Parquet sizing (claude.md mandate).

Picks a Parquet block size and row-group size from available physical RAM
(psutil) — 64-256 MiB blocks — so large vaults stream without OOM instead of a
hardcoded constant. ``available_bytes`` is injectable for deterministic tests.
"""

import psutil

MIN_BLOCK_BYTES = 64 * 1024 * 1024
MAX_BLOCK_BYTES = 256 * 1024 * 1024


def dynamic_block_bytes(fraction: float = 0.05, available_bytes: int | None = None) -> int:
    if available_bytes is None:
        available_bytes = psutil.virtual_memory().available
    target = int(available_bytes * fraction)
    return max(MIN_BLOCK_BYTES, min(MAX_BLOCK_BYTES, target))


def dynamic_row_group_size(
    avg_row_bytes: int = 512,
    fraction: float = 0.05,
    max_rows: int = 500_000,
    available_bytes: int | None = None,
) -> int:
    block = dynamic_block_bytes(fraction, available_bytes)
    rows = block // max(1, avg_row_bytes)
    return max(1000, min(max_rows, rows))
