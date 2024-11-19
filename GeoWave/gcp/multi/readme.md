# Setting up GeoWave
Make sure to adjust the `variables.tf`file to match your configuration.
```
terraform init
terraform apply --auto-approve
```
## Set needed variables to connect to the machine
```
export SSH_USER=$(terraform output -raw ssh_user)
export GCP_IP=$(terraform output -raw external_ip_sut_manager)
```

