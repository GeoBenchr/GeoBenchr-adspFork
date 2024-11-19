variable region {
    default = "europe-west4"
}
variable "zone" {
    default = "europe-west4-a"
}

variable "project" {
    default = "<your projectID>"
}

# don't set this to root
variable "gcp_ssh_user" {
    default = "manager"
}

variable "gcp_ssh_pub_key_file" {
    default = "<path to your id_rsa.pub>"
}

variable "machine_type" {
    default = "e2-standard-2"
}