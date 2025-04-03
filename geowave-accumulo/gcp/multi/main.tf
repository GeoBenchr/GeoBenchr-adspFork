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
# GEOWAVE NAMENODE MANAGER
# --------------------------------------

resource "google_compute_instance" "namenode_manager" {
  name         = "geowave-namenode-manager"
  machine_type = var.manager_machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size  = 50 # GB
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {}
  }

  tags = ["geowave", "accumulo", "namenode"]

  metadata = {
    ssh-keys = "${var.gcp_ssh_user}:${data.local_file.ssh_public_key.content}"
  }
}

# --------------------------------------
# GEOWAVE WORKER NODES
# --------------------------------------

resource "google_compute_instance" "worker_nodes" {
  count        = var.worker_count
  name         = "geowave-worker-${count.index}"
  machine_type = var.worker_machine_type
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size  = 50 # GB
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {}
  }

  tags = ["geowave", "accumulo", "worker"]

  metadata = {
    ssh-keys = "${var.gcp_ssh_user}:${data.local_file.ssh_public_key.content}"
  }
}

# --------------------------------------
# BENCHMARKING CLIENT
# --------------------------------------

#To Be Added

# --------------------------------------
# OUTPUT VARIABLES
# --------------------------------------

output "ssh_user" {
  value     = var.gcp_ssh_user
  sensitive = false
}

output "namenode_manager_ip" {
  value = google_compute_instance.namenode_manager.network_interface[0].access_config[0].nat_ip
}

output "worker_node_ips" {
  value = [for instance in google_compute_instance.worker_nodes : instance.network_interface[0].access_config[0].nat_ip]
}


