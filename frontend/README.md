# Quantum Avenger — Web Dashboard

A modern, decoupled React front-end for the Quantum Avenger ML quant engine. The
UI talks to a thin **FastAPI** layer (`new_pipeline/api/`) over JSON/SSE — no Python
is imported in the browser, and the quant engine (`tournament`/`evaluation`/
`features`) is untouched.

> This React app fully replaces the old Streamlit dashboard. The Streamlit UI has
> been removed; its pure data + alert layer (`new_pipeline/monitoring/dashboard/`:
> `realtime.py` / `views.py` / `alerts.py` / `notifications.py`) is reused as-is by
> the FastAPI monitor router, so nothing in the quant engine changed.

## Stack

- **Vite** + **React 18** + **TypeScript**
- **Tailwind CSS** + **shadcn/ui** primitives (Radix-based), dark-mode first
- **Recharts** for equity curves / veto breakdowns
- **TanStack Query** for data fetching, polling, and cache

## Pages

| Page | What it shows |
|------|---------------|
| **Overview** | Live KPI cards (P&L, Sharpe, drawdown, veto rate, win rate, profit factor), the equity curve, vetoes-by-gate, and threshold alerts — read from the veto ledger + trade log via `/api/monitor/*`. |
| **Analytics** | Per-run model performance: promotion table with gate badges (DSR / PBO / PSR / haircut / CPCV path-pass), per-sector equity + drawdown, the CPCV path-distribution fan, meta-labeling precision/recall, the IC/ICIR signal table, the portfolio donut, and the stat-arb pairs table — parsed from `/api/runs/{id}/results`. |
| **Live Monitor** | Four tabs — the executed trade log, per-decision veto analysis (by-gate + decision ledger), live risk exposure, and the model registry (champions + promotion history). |
| **Engine Control** | The whole control panel renders itself from `/api/config/schema` — sliders / switches / selects / multiselects / number inputs per knob, seeded with the live config. Launch an isolated backtest, watch it run, and see the champion's equity + metrics when it finishes. |

## Develop

The dev server proxies `/api` to the FastAPI backend, so run both:

```bash
# 1. Backend (from the repo root)
pip install -r new_pipeline/requirements-api.txt
uvicorn new_pipeline.api.app:app --reload --port 8000

# 2. Frontend (from frontend/)
npm install
npm run dev          # http://localhost:5173  (proxies /api -> :8000)
```

## Build & serve (production)

```bash
npm run build        # type-checks (tsc) then emits dist/
python -m new_pipeline.api.app   # FastAPI serves the API *and* dist/ as an SPA
```

When `frontend/dist/` exists, `new_pipeline/api/app.py` mounts it at `/`, so a
single `uvicorn` process serves the whole app on one origin.

## Layout

```
src/
  lib/api.ts          typed client + response types (the backend contract)
  hooks/useApi.ts     TanStack Query hooks (monitor polling, run lifecycle)
  components/ui/       shadcn primitives (card, button, slider, switch, select, …)
  components/          KpiCard, EquityChart, VetoBarChart, AlertsList, KnobControl, AppShell
  pages/              Overview, AnalyticsPage, LiveMonitorPage, ControlPanelPage
```

The control panel never hard-codes config fields: `KnobControl` dispatches on the
`control` hint the backend derives from the Pydantic schema (`config/schema.py`),
so new knobs appear automatically.
