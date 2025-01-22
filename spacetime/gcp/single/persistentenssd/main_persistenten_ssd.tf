# --------------------------------------
# PROVIDER CONFIGURATION
# --------------------------------------

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

# --------------------------------------
# SSH KEY CONFIGURATION
# --------------------------------------

data "local_file" "ssh_public_key" {
  filename = var.gcp_ssh_pub_key_file
}

# --------------------------------------
# NETWORKING CONFIGURATION
# --------------------------------------

# Virtual Private Cloud (VPC) network
resource "google_compute_network" "vpc_network" {
  name = "vpc-network"
}

# Firewall rules
resource "google_compute_firewall" "default" {
  name    = "allow-all"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "all"    # This means all protocols (TCP, UDP, ICMP, etc.)
  }

  source_ranges = ["0.0.0.0/0"] # Make externally reachable
}

# --------------------------------------
# SPACETIME SINGLE-NODE INSTANCE
# --------------------------------------

resource "google_compute_instance" "spacetime_instance" {
  name         = "spacetime-instance"
  machine_type = var.machine_type
  zone         = var.zone

  # Boot disk
  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size  = var.boot_disk_size
      type  = "pd-ssd"  # Persistent SSD for boot disk
    }
  }

  # Additional persistent SSD
  attached_disk {
    initialize_params {
      size = 375  # Size in GB
      type = "pd-ssd"  # Persistent SSD
    }
  }

  # Networking
  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {}
  }

  tags = ["spacetime"]

  metadata = {
    ssh-keys = "${var.gcp_ssh_user}:${data.local_file.ssh_public_key.content}"
  }

  # Description
  description = "This VM uses persistent SSDs for durable storage."

  # Startup script for mounting and configuring persistent SSDs
  metadata_startup_script = <<-EOT
    #!/bin/bash
    mkfs.ext4 -F /dev/disk/by-id/google-${google_compute_instance.spacetime_instance.name}-disk-1
    mkdir -p /mnt/disks/disk-1
    mount /dev/disk/by-id/google-${google_compute_instance.spacetime_instance.name}-disk-1 /mnt/disks/disk-1
    chmod -R 777 /mnt/disks/disk-1
  EOT
}

# --------------------------------------
# OUTPUT VARIABLES
# --------------------------------------

output "ssh_user_spacetime_persistenten" {
  value     = var.gcp_ssh_user
  sensitive = false
}

output "external_ip_spacetime_persistenten" {
  value = google_compute_instance.spacetime_instance.network_interface[0].access_config[0].nat_ip
}
