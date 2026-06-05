"""Offline micro load / chaos harness (Phase 7).

Drives the hot deterministic paths (Shield veto gates, t+1 simulation) under a
fixed budget to give a throughput baseline — a CI-friendly perf smoke, not a
substitute for k6/locust against the live services.

Run:  PYTHONPATH=. python new_pipeline/hardening/chaos/load_test.py --iters 100000
"""

import argparse
import time

import numpy as np
from new_pipeline.features.shields import evaluate_risk_veto_gates
from new_pipeline.tournament.simulator import simulate_t1_returns


def bench_shield(iters: int) -> float:
    start = time.perf_counter()
    for _ in range(iters):
        evaluate_risk_veto_gates(100.0, 1.0, 2.0, 100000.0, 0.02, 0.0, 5e6, 5e6, 0.02)
    return iters / (time.perf_counter() - start)


def bench_simulator(n: int) -> float:
    rng = np.random.default_rng(0)
    close = 100.0 + np.cumsum(rng.normal(0, 1, n))
    signals = rng.integers(0, 2, n).astype(np.int64)
    start = time.perf_counter()
    simulate_t1_returns(signals, close, close - 1.0, np.ones(n), 2.0, 0.02)
    return n / (time.perf_counter() - start)


def main() -> None:
    parser = argparse.ArgumentParser(description="Quantum Avenger load/chaos harness")
    parser.add_argument("--iters", type=int, default=100_000)
    args = parser.parse_args()
    print(f"shield:    {bench_shield(args.iters):,.0f} evals/sec")
    print(f"simulator: {bench_simulator(args.iters):,.0f} bars/sec")


if __name__ == "__main__":
    main()
