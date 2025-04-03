# data "terraform_remote_state" "main_state" {
#   backend = "local"

#   config = {
#     path = "../../base/terraform.tfstate"
#   }
# }

provider "google" {
  project = var.project
  region  = var.region
  zone    = var.zone
}

resource "google_compute_network" "vpc_network" {
  name = "vpc-network"
}

resource "google_compute_firewall" "default" {
  name    = "allow-all"
  network = google_compute_network.vpc_network.name

  allow {
    protocol = "all"    # This means all protocols (TCP, UDP, ICMP, etc.)
  }

  source_ranges = ["0.0.0.0/0"] # Make externally reachable
}


resource "google_compute_instance" "mobdb_manager" {
  name         = "mobdb-manager"
  machine_type = var.manager_machine_type
  zone         = var.zone
  tags         = [ "sut", "manager" ]
  boot_disk {
    initialize_params {
      image = "ubuntu-2204-lts"
      size = 100 # GB
    }
  }
  network_interface {
    network = google_compute_network.vpc_network.name

    access_config {
      // Ephemeral public IP
    }
  }

  metadata = {
    system-under-test = "mobilitydb"
    ssh-keys = "${var.gcp_ssh_user}:${file(var.gcp_ssh_pub_key_file)}"
  }

 metadata_startup_script = file("scripts/startManager.sh")

}


# resource "google_compute_instance" "benchmark_client" {
#   name         = "benchmark-client"
#   machine_type = var.worker_machine_type
#   zone         = var.zone
#   tags         = [ "client"]
#   boot_disk {
#     initialize_params {
#       image = "ubuntu-2204-lts"
#     }
#   }
#   network_interface {
#     network = google_compute_network.vpc_network.name

#     access_config {
#       // Ephemeral public IP
#     }
#   }

#   metadata = {
#     ssh-keys = "${var.gcp_ssh_user}:${file(var.gcp_ssh_pub_key_file)}"
#   }

#   metadata_startup_script = "${file("scripts/startClient.sh")}"

# }
output "external_ip_sut_manager" {
  value = google_compute_instance.mobdb_manager.network_interface[0].access_config[0].nat_ip
}

output "ssh_user" {
  value = var.gcp_ssh_user
}

# output "external_ip_client" {
#   value = google_compute_instance.benchmark_client.network_interface[0].access_config[0].nat_ip
# }