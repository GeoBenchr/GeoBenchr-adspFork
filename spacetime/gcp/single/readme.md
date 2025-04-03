# Spacetime

This folder contains Terraform files for a single-node setup for Spacetime with the following requirements:

- n2-standard-16 instance (16 vCPUs, 64 GiB RAM)
- 2 x 375 GB Local SSDs with an NVMe interface

You may need to increase the quota of your project to be able to run these files.

## Setting up SpaceTime
Make sure to adjust the `variables.tf`file to match your configuration and that your GCloud authentication worked. Then run:
```
terraform init
terraform apply --auto-approve
```
## Set needed variables in terminal to connect to the machine
```
export SSH_USER=$(terraform output -raw ssh_user)
export GCP_IP=$(terraform output -raw external_ip)
```
If multiple persons work on the same project, you may have to import already created resources.
For example:
```
terraform import google_compute_network.vpc_network projects/geobenchr-440309/global/networks/vpc-network
terraform import google_compute_firewall.default projects/geobenchr-440309/global/firewalls/allow-all
```
## Stop the VM with preservation of local SSD content
```
gcloud beta compute instances stop spacetime_instance\
    --discard-local-ssd=false \
    --zone=europe-west4-a
```