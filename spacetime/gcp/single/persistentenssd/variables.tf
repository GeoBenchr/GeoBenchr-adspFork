# --------------------------------------
# PROJECT CONFIGURATION
# --------------------------------------

variable "project" {
    description = "The GCP project ID where resources will be created."
    type        = string
    default     = "geobenchr-440309"
}

variable "region" {
    description = "The GCP region for resource deployment."
    type        = string
    default     = "europe-west4"
}

variable "zone" {
    description = "The GCP zone within the selected region."
    type        = string
    default     = "europe-west4-a"
}

# --------------------------------------
# SSH CONFIGURATION
# --------------------------------------

variable "gcp_ssh_user" {
    description = "The username for SSH access to the instances. Don't set this to root!"
    type        = string
    default     = "manager"
}

variable "gcp_ssh_pub_key_file" {
    description = "The absolute path to your public SSH key file."
    type        = string
    default     = "/home/ilja/.ssh/id_ed25519.pub"
}

# --------------------------------------
# INSTANCE CONFIGURATION
# --------------------------------------

variable "machine_type" {
    description = "The machine type for the instance."
    type        = string
    default     = "n2-standard-16"
}

variable "boot_disk_size" {
    description = "The size of the boot disk in GB."
    type        = number
    default     = 100
}

variable "local_ssd_count" {
    description = "The number of local SSDs to attach to the instance."
    type        = number
    default     = 2
}

variable "local_ssd_interface" {
    description = "The interface type for local SSDs."
    type        = string
    default     = "NVME"
}