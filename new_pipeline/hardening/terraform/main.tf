# Quantum Avenger — cloud infrastructure skeleton (Phase 7).
#
# Cloud-specific provider, managed-Kubernetes, and object-storage resources are
# intentionally left as a skeleton; fill in for your target cloud (AWS EKS /
# GCP GKE / Azure AKS). Keep model artifacts + parquet ledgers in object
# storage, and Alpaca/Ollama credentials in a managed secrets store — never in
# tfvars committed to git.
terraform {
  required_version = ">= 1.5"
}

locals {
  tags = {
    project = "quantum-avenger"
    managed = "terraform"
  }
}

# Resources to fill in per cloud:
# - Managed Kubernetes cluster (var.cluster_name) with a CPU node pool
#   (var.node_count) and a GPU node pool (var.gpu_node_count) for training.
# - Object-storage bucket for model artifacts + parquet ledgers (tagged local.tags).
# - Managed secrets store wired to the quantum-avenger-secrets Kubernetes Secret.
