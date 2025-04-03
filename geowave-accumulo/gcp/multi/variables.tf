variable region {
    default = "europe-west4"
}
variable "zone" {
    default = "europe-west4-a"
}
# don't set this to root
variable "gcp_ssh_user" {
    default = "manager"
}
variable "project" {
    default = "geobenchr-benchmark"
}
# NEED TO ADJUST THIS ON YOUR DEVICE, BECAUSE THIS IS THE PATH TO YOUR SSH PUBLIC KEY
variable "gcp_ssh_pub_key_file" {
    default = "/Users/gov/.ssh/id_ed25519.pub"
}


variable "manager_machine_type" {
    default = "n4-standard-4"
}
variable "worker_machine_type" {
    default = "n2-standard-4"
}
variable "benchmark_client_machine_type" {
    default = "e2-standard-4"
  
}

variable "worker_count" {
    default = 1
}
variable "benchmark_client_count" {
    default = 0
}