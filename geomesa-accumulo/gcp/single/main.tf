# main.tf

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

data "local_file" "ssh_public_key" {
  filename = "/Users/gov/.ssh/id_rsa.pub"
}

resource "google_compute_network" "vpc_network" {
  name = "vpc-network"
}

# Define firewall rules for necessary ports (SSH, Zookeeper, Hadoop, etc.)
resource "google_compute_firewall" "default" {
  name    = "allow-all"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "all"    # This means all protocols (TCP, UDP, ICMP, etc.)
  }

  source_ranges = ["0.0.0.0/0"] # Make externally reachable
}

# create a benchmarking client in the same network
resource "google_compute_instance" "benchmark_client" {
  count        = var.benchmark_client_count
  name         = "benchmark-client-vm-${count.index}"
  machine_type = var.benchmark_client_machine_type
  zone         = var.zone


  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size = 30 # GB
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {
      # This allows the VM to have an external IP
    }
  }

  tags = ["benchmark"]

  metadata = {
    ssh-keys = "${var.gcp_ssh_user}:${data.local_file.ssh_public_key.content}"
  }
}
# Define the Google Compute Engine VM instance
resource "google_compute_instance" "accumulo_manager" {
  name         = "accumulo-namenode-manager"
  # choose instance type that does not allow boosting
  machine_type = "n4-standard-4"
  zone         = var.zone

  boot_disk {
    initialize_params {
      image = "ubuntu-os-cloud/ubuntu-2004-lts"
      size = 100 # GB
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.name
    access_config {
      # This allows the VM to have an external IP
    }
  }

  tags = ["geomesa", "accumulo"]

  metadata = {
    ssh-keys = "${var.gcp_ssh_user}:${file(var.gcp_ssh_pub_key_file)}"
  }
  #metadata_startup_script = "${file("scripts/startManager.sh")}"
}


output "ssh_user"{ 
  value = var.gcp_ssh_user
}

output "external_ip_sut_manager" {
  value = google_compute_instance.accumulo_manager.network_interface[0].access_config[0].nat_ip
}
output "external_ip_client" {
  value = google_compute_instance.benchmark_client[*].network_interface[0].access_config[0].nat_ip
}
