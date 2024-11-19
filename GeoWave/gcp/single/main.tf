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
# BENCHMARKING CLIENT
# --------------------------------------

resource "google_compute_instance" "benchmark_client" {
  name         = "benchmark_client_geoWave"
  machine_type = var.machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size = 50#GB
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
    ssh-keys = "${var.gcp_ssh_user}:${file(var.gcp_ssh_pub_key_file)}"
  }

  # Uncomment if you want to use a startup script
  # metadata_startup_script = "${file("scripts/startManager.sh")}"
}

# --------------------------------------
# OUTPUT VARIABLES
# --------------------------------------

output "ssh_user" {
  value     = var.gcp_ssh_user
  sensitive = true
}

output "external_ip" {
  value = {
    manager = google_compute_instance.benchmark_client.network_interface[0].access_config[0].nat_ip
    }
}