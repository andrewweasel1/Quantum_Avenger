# Chaos & Load Scenarios (Phase 7)

Resilience checks for the deployed system. `load_test.py` is the offline perf
smoke; the scenarios below target the live cluster (run against staging).

## Load
- `PYTHONPATH=. python new_pipeline/hardening/chaos/load_test.py --iters 200000` — hot-path throughput baseline.
- k6 / locust against the dashboard `/` and the MCP server under sustained RPS.

## Chaos (observe alerts + recovery)
| Scenario | Inject | Expected |
|----------|--------|----------|
| Dependency down | Block egress to Ollama / Alpaca | Circuit breaker opens, half-opens after `recovery_timeout`, no crash |
| Pod eviction | `kubectl delete pod` | Deployment reschedules; readiness/liveness probes gate traffic |
| Network partition | Drop traffic to a service | Retries with backoff; `HighExecutionLatency` alert fires |
| Disk pressure | Fill the ledger volume | Writes fail gracefully; alert fires; append-only ledgers stay intact |

## Recovery
Follow `docs/RECOVERY.md` — rollback, restore the promotion registry, re-promote from candidates.
