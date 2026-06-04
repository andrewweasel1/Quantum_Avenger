# Recovery Playbook

## Resilience built in
- **Circuit breaker** (`core/circuit_breaker.py`) around flaky externals (LLM,
  broker, market data) — fails fast, half-opens after the recovery window.
- **Retries with backoff** (`utils/retry.py`) for transient blips.
- **Shield Agent veto** — no trade ever bypasses the deterministic risk gates.

## Common incidents
| Symptom | Action |
|---------|--------|
| Bad deploy | `kubectl rollout undo deployment/<name>` |
| External dependency down | breaker opens automatically; verify endpoint, then it half-opens |
| HighDrawdown / HighVetoRate alert | inspect the veto ledger + dashboard; halt new entries if breaching risk limits |
| Champion misbehaving | revert `active_champions` in the promotion registry to the prior model_path |

## State & backups
- **Promotion registry** (`models/prod/promotion_registry.json`) — append-only;
  back up before each promotion run.
- **Veto ledger / trade log** (Parquet) — append-only audit trail; snapshot regularly.
- Models are immutable artifacts keyed by version; re-promote from candidates if lost.

## Smoke test after recovery
```
python -m new_pipeline.scripts.check_health
make coverage
```
