locals {
  proxmox_api_token = "${var.proxmox_api_token_id}=${var.proxmox_api_token_secret}"
}

provider "proxmox" {
  endpoint  = var.proxmox_endpoint
  api_token = local.proxmox_api_token
  insecure  = var.proxmox_insecure
}
