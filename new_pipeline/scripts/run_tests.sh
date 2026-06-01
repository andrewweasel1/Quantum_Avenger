#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."
pytest new_pipeline/tests
