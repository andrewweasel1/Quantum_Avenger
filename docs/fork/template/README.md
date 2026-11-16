# Quantum Intraday

Intraday equity trading research on Alpaca paper trading: minute bars,
measured quotes, and a promotion gauntlet that has to be passed before
anything trades.

**Status: research. No strategy is promoted and nothing is trading.**

## Start here

1. `claude.md` — the ruleset and charter.
2. `docs/fork/INTRADAY_HANDOVER.md` — what was already tried, with numbers.
3. `docs/intraday_learned_model_plan.md` — the plan of record.
4. `docs/fork/MANIFEST.md` — what is in this repository and why.

## Layout

| Path | What it is |
|---|---|
| `new_pipeline/intraday/` | Vault loaders, cost model, simulator, scanner |
| `new_pipeline/evaluation/` | The promotion gauntlet. **Byte-pinned; do not edit.** |
| `data/minute_archives/` | Minute-bar vault, 2021-09..2026-08, as monthly tars |
| `data/quote_vault/` | Measured NBBO half-spread and touch depth, by month |
| `evidence/` | Every prior intraday run: returns matrix, ledger, findings |

## Working

```
make install        # dependencies
make test           # unit + integration suite
make coverage       # the CI gate
bash new_pipeline/scripts/restore_minute_vault.sh <scratch> [START_YM] [END_YM]
export QA_INTRADAY__VAULT_DIR=<scratch>/minute_vault
```

Credentials are environment variables only (`QA_ALPACA__API_KEY`,
`QA_ALPACA__SECRET_KEY`) and must belong to the dedicated intraday paper
account.
