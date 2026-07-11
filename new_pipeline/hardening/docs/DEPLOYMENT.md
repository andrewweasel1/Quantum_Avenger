# Deployment Guide

> Status: the engine (`app`) and MCP tool-inventory images are buildable
> templates. The web dashboard (React SPA + FastAPI — `/frontend` +
> `new_pipeline/api/`) is **not containerized yet**; run it per
> `frontend/README.md` (uvicorn serves the API and the built SPA). Its image,
> service, and ingress land with the deployment phase.

## 1. Build & test
```
make lint coverage          # ruff + tests + >=85% coverage gate
make docker                 # build app / mcp images
```

## 2. Push images
```
docker tag quantum-avenger-app   <registry>/quantum-avenger-app:<tag>
docker push <registry>/quantum-avenger-app:<tag>     # repeat for mcp
```

## 3. Configure
- Non-secret config: `k8s/configmap.yaml` (`QA_ENV=production`, worker counts).
- Secrets (Alpaca / Ollama / the dashboard API token): create a Kubernetes
  `Secret` and mount it with `envFrom.secretRef`, using the `QA_` env-var
  override convention (e.g. `QA_FUSION__OLLAMA_ENDPOINT`, `QA_ALPACA__API_KEY`,
  `QA_API_TOKEN` when `dashboard.auth_enabled` is on). **Never commit secrets.**

## 4. Deploy (Kubernetes)
```
kubectl apply -f new_pipeline/hardening/k8s/configmap.yaml
kubectl apply -f new_pipeline/hardening/k8s/deployment.yaml
kubectl apply -f new_pipeline/hardening/k8s/hpa.yaml
kubectl apply -f new_pipeline/hardening/k8s/networkpolicy.yaml
```
Update the `image:` fields to your registry tags first. The trainer/feature
workloads target a GPU node pool (`device='cuda'`); MCP runs CPU-only.

## 5. Observe
Point Prometheus at `observability/prometheus.yml` and load `alert_rules.yml`.
NOTE: the `quantum_avenger_*` metrics those configs reference are not emitted
yet — collection is wired in the observability phase.

## Follow-ons
The dashboard (API + SPA) image/service/ingress, metric emission + `/metrics`,
Terraform for cloud infra, and a fuller chaos / load-test suite are the
remaining production extensions.
