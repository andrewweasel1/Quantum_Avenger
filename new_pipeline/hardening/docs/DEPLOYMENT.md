# Deployment Guide

## 1. Build & test
```
make lint coverage          # ruff + tests + >=85% coverage gate
make docker                 # build app / dashboard / mcp images
```

## 2. Push images
```
docker tag quantum-avenger-app   <registry>/quantum-avenger-app:<tag>
docker push <registry>/quantum-avenger-app:<tag>     # repeat for dashboard, mcp
```

## 3. Configure
- Non-secret config: `k8s/configmap.yaml` (`QA_ENV=production`, worker counts).
- Secrets (Alpaca / Ollama): create a Kubernetes `Secret` and mount it with
  `envFrom.secretRef`, using the `QA_` env-var override convention
  (e.g. `QA_FUSION__OLLAMA_ENDPOINT`, `QA_ALPACA__API_KEY`). **Never commit secrets.**

## 4. Deploy (Kubernetes)
```
kubectl apply -f new_pipeline/hardening/k8s/configmap.yaml
kubectl apply -f new_pipeline/hardening/k8s/deployment.yaml
kubectl apply -f new_pipeline/hardening/k8s/service.yaml
```
Update the `image:` fields to your registry tags first. The trainer/feature
workloads target a GPU node pool (`device='cuda'`); the dashboard and MCP run
CPU-only.

## 5. Observe
Point Prometheus at `observability/prometheus.yml` and load `alert_rules.yml`.

## Follow-ons
Terraform for cloud infra, an ingress + HorizontalPodAutoscaler, and a chaos /
load-test suite are the remaining production extensions.
