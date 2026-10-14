"""Decoupled HTTP API over the ML engine (FastAPI).

A thin JSON/SSE layer that exposes the engine's config "knobs", triggers backtests
as isolated subprocesses, and serves the resulting artifacts — so a React front-end
(``/frontend``) can drive the pipeline without importing any Python. The quant logic
in ``tournament``/``evaluation``/``features`` is untouched; this package only reads
its config schema and parses its output artifacts.
"""
