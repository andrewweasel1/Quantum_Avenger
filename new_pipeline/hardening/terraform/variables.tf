variable "region" {
  type        = string
  description = "Cloud region to deploy into."
}

variable "cluster_name" {
  type    = string
  default = "quantum-avenger"
}

variable "node_count" {
  type        = number
  default     = 3
  description = "CPU node pool size (dashboard, MCP, app)."
}

variable "gpu_node_count" {
  type        = number
  default     = 1
  description = "GPU nodes for the trainer / feature service."
}
