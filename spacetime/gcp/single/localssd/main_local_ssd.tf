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

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size  = var.boot_disk_size
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {}
  }

  tags = ["spacetime"]

  metadata = {
    ssh-keys = "${var.gcp_ssh_user}:${data.local_file.ssh_public_key.content}"
  }

  scratch_disk {
    interface = var.local_ssd_interface
  }

  scratch_disk {
    interface = var.local_ssd_interface
  }

  description = <<-EOT
    This VM should only be stopped or suspended using --discard-local-ssd=false to preserve local SSD data.
    For example:
    gcloud beta compute instances stop spacetime_instance \\
      --discard-local-ssd=false \\
      --zone=europe-west4-a
  EOT

  #mounts an configures SSDs
  metadata_startup_script = <<-EOT
    #!/bin/bash
    for device in /dev/nvme0n1 /dev/nvme1n1; do
      mkfs.ext4 -F $${device}
      mount_point="/mnt/disks/$$(basename $${device})"
      mkdir -p $${mount_point}
      mount $${device} $${mount_point}
      chmod -R 777 $${mount_point}
    done
  EOT
}

# --------------------------------------
# OUTPUT VARIABLES
# --------------------------------------

output "ssh_user" {
  value     = var.gcp_ssh_user
  sensitive = false
}

output "external_ip" {
  value = google_compute_instance.spacetime_instance.network_interface[0].access_config[0].nat_ip
}