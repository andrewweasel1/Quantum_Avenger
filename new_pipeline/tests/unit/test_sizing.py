from new_pipeline.data.sizing import (
    MAX_BLOCK_BYTES,
    MIN_BLOCK_BYTES,
    dynamic_block_bytes,
    dynamic_row_group_size,
)

_GB = 1024**3


def test_block_bytes_clamped_to_max():
    assert dynamic_block_bytes(0.05, available_bytes=10 * _GB) == MAX_BLOCK_BYTES


def test_block_bytes_clamped_to_min():
    assert dynamic_block_bytes(0.05, available_bytes=100 * 1024**2) == MIN_BLOCK_BYTES


def test_block_bytes_within_range():
    block = dynamic_block_bytes(0.05, available_bytes=2 * _GB)
    assert block == int(2 * _GB * 0.05)
    assert MIN_BLOCK_BYTES <= block <= MAX_BLOCK_BYTES


def test_row_group_size_bounds():
    rows = dynamic_row_group_size(avg_row_bytes=512, available_bytes=2 * _GB)
    assert 1000 <= rows <= 500_000


def test_row_group_size_uses_psutil_by_default():
    assert dynamic_row_group_size() >= 1000
