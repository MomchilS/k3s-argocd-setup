output "vm_name" {
  description = "Name of the created VM."
  value       = proxmox_virtual_environment_vm.k3s.name
}

output "vm_id" {
  description = "ID of the created VM."
  value       = proxmox_virtual_environment_vm.k3s.vm_id
}

output "ipv4_address" {
  description = "Static IPv4 address configured through cloud-init."
  value       = var.ipv4_address
}

output "proxmox_node_name" {
  description = "Proxmox node where the VM is created."
  value       = proxmox_virtual_environment_vm.k3s.node_name
}
