variable "proxmox_endpoint" {
  description = "Proxmox API endpoint, for example https://proxmox.example.local:8006/api2/json."
  type        = string
}

variable "proxmox_api_token_id" {
  description = "Proxmox API token ID in the form user@realm!token-name."
  type        = string
  sensitive   = true
}

variable "proxmox_api_token_secret" {
  description = "Proxmox API token secret."
  type        = string
  sensitive   = true
}

variable "proxmox_insecure" {
  description = "Allow insecure TLS for Proxmox API access. Prefer false with trusted certificates."
  type        = bool
  default     = true
}

variable "proxmox_node_name" {
  description = "Target Proxmox node name."
  type        = string
}

variable "vm_id" {
  description = "Unique VM ID to assign in Proxmox."
  type        = number
}

variable "vm_name" {
  description = "Name for the K3s VM."
  type        = string
  default     = "k3s-node-01"
}

variable "vm_description" {
  description = "Description for the VM."
  type        = string
  default     = "K3s node provisioned by Terraform"
}

variable "vm_template_id" {
  description = "VM ID of the Debian cloud-init template to clone."
  type        = number
}

variable "vm_username" {
  description = "Cloud-init username to create."
  type        = string
  default     = "debian"
}

variable "ssh_public_key" {
  description = "SSH public key injected into the cloud-init user."
  type        = string
  sensitive   = true
}

variable "storage_pool" {
  description = "Proxmox datastore or storage pool for the VM disk."
  type        = string
}

variable "disk_size_gb" {
  description = "VM disk size in GB."
  type        = number
  default     = 32
}

variable "cpu_cores" {
  description = "Number of vCPU cores."
  type        = number
  default     = 2
}

variable "memory_mb" {
  description = "Dedicated memory in MB."
  type        = number
  default     = 4096
}

variable "network_bridge" {
  description = "Proxmox network bridge for the primary VM network interface."
  type        = string
  default     = "vmbr0"
}

variable "ipv4_address" {
  description = "Static IPv4 address with CIDR, for example 192.168.2.50/24."
  type        = string
}

variable "ipv4_gateway" {
  description = "IPv4 gateway."
  type        = string
}

variable "dns_servers" {
  description = "DNS servers for cloud-init."
  type        = list(string)
  default     = ["192.168.2.1", "1.1.1.1"]
}
