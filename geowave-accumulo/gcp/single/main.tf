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
# BENCHMARKING MANAGER
# --------------------------------------

resource "google_compute_instance" "geowave_benchmark_manager" {
  name         = "geowave-benchmark-manager"
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size = 40 #GB
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {
      # This allows the VM to have an external IP
    }
  }

  tags = ["benchmark","geowave", "accumulo"]

  metadata = {
    ssh-keys = "${var.gcp_ssh_user}:${data.local_file.ssh_public_key.content}"
  }
}

# --------------------------------------
# BENCHMARKING CLIENT
# --------------------------------------

#To be added

# --------------------------------------
# OUTPUT VARIABLES
# --------------------------------------

output "ssh_user" {
  value     = var.gcp_ssh_user
  sensitive = false
}

output "external_ip" {
  value = google_compute_instance.geowave_benchmark_manager.network_interface[0].access_config[0].nat_ip
}