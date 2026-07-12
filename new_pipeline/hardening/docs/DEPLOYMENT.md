# Deployment Guide

The stack ships as three CPU images — **api** (FastAPI + the built React SPA,
the dashboard), **app** (engine/CLI), **mcp** (tool inventory) — plus an
optional **gpu** trainer image (template; needs a CUDA host). CI builds the
three CPU images on every PR and smoke-tests the api container's health
endpoint and SPA.

## 1. Build & test
```
make lint coverage          # ruff + tests + >=85% coverage gate
make docker                 # build api / app / mcp images
```

## 2. Run locally (compose)
```
cd new_pipeline/hardening/docker
QA_DASHBOARD__AUTH_ENABLED=true QA_API_TOKEN=<secret> docker compose up --build
```
- Dashboard: http://localhost:8000 (provision the token once via `#token=<secret>`)
- Prometheus: http://localhost:9090 (scrapes the api's `/metrics`; when auth is
  on, add an `authorization: {type: Bearer, credentials: <QA_API_TOKEN>}` block
  to `observability/prometheus.yml`)
- Run artifacts + ledgers persist in the `qa-data` volume.

## 3. Push images
```
docker tag quantum-avenger-api <registry>/quantum-avenger-api:<tag>
docker push <registry>/quantum-avenger-api:<tag>      # repeat for app, mcp
```

## 4. Configure (Kubernetes)
- Non-secret config: `k8s/configmap.yaml` (`QA_ENV=production`, worker counts).
- Secrets: populate `quantum-avenger-secrets` (see `k8s/secrets.yaml` — a
  TEMPLATE with placeholders) via a secrets manager, Sealed Secrets, or
  `kubectl create secret`. Keys: `QA_ALPACA__API_KEY`, `QA_ALPACA__SECRET_KEY`,
  `QA_FUSION__OLLAMA_ENDPOINT`, `QA_API_TOKEN`. **Never commit secrets.**

## 5. Deploy (Kubernetes)
```
kubectl apply -f new_pipeline/hardening/k8s/configmap.yaml
kubectl apply -f new_pipeline/hardening/k8s/api.yaml          # dashboard (auth forced on)
kubectl apply -f new_pipeline/hardening/k8s/deployment.yaml   # app / mcp
kubectl apply -f new_pipeline/hardening/k8s/hpa.yaml
kubectl apply -f new_pipeline/hardening/k8s/networkpolicy.yaml
```
Update `image:` fields to your registry tags first. The api Service is
ClusterIP — front it with your ingress controller + TLS. Swap the api pod's
`emptyDir` volumes for PVCs to persist runs/ledgers. GPU training targets a
CUDA node pool via `Dockerfile.gpu` (template) + `tournament.device=cuda`.

## 6. Observe
Prometheus scrapes `api:8000/metrics` (`observability/prometheus.yml`);
`alert_rules.yml` fires on veto-rate / drawdown / DSR / negative-Sharpe
breaches and `grafana_dashboard.json` renders the same series. These metrics
are live (wired through the orchestrator/runner/API), not aspirational.

## 7. GPU reconciliation
`.github/workflows/nightly-gpu.yml` runs the `@pytest.mark.gpu` kernel-parity
suite — manual (`workflow_dispatch`) until a self-hosted GPU runner with labels
`[self-hosted, gpu]` is registered; add a `schedule:` block then.
