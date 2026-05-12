resource "proxmox_virtual_environment_vm" "k3s" {
  name        = var.vm_name
  description = var.vm_description
  node_name   = var.proxmox_node_name
  vm_id       = var.vm_id
  tags        = ["terraform", "k3s"]

  clone {
    vm_id = var.vm_template_id
    full  = true
  }

  agent {
    enabled = true
  }

  operating_system {
    type = "l26"
  }

  cpu {
    cores = var.cpu_cores
    type  = "host"
  }

  memory {
    dedicated = var.memory_mb
  }

  disk {
    datastore_id = var.storage_pool
    interface    = "scsi0"
    size         = var.disk_size_gb
  }

  network_device {
    bridge = var.network_bridge
  }

  initialization {
    datastore_id = var.storage_pool

    dns {
      servers = var.dns_servers
    }

    ip_config {
      ipv4 {
        address = var.ipv4_address
        gateway = var.ipv4_gateway
      }
    }

    user_account {
      username = var.vm_username
      keys     = [var.ssh_public_key]
    }
  }
}
