variable region {
    default = "europe-west4"
}
variable "zone" {
    default = "europe-west4-a"
}

variable "project" {
    default = "geobenchr-440309"
}

# don't set this to root
variable "gcp_ssh_user" {
    default = "manager"
}

# the absolute path to your public ssh-key
variable "gcp_ssh_pub_key_file" {
    default = "/home/ilja/.ssh/id_ed25519.pub"
}

variable "machine_type" {
    default = "e2-standard-2"
}