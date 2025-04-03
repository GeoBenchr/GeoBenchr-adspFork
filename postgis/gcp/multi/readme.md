# Setting up MobilityDB and Citus together
Make sure to adjust the `variables.tf`file to match your configuration. Specifically, change the project and ssh key. MobilityDB uses a startup script, so give the machine a couple of minutes to configure everything. The current configuration runs on 8 N2 CPUs across 4 machines, if you want more you'll need to ask Google for a raise in the quota.
```
terraform init
terraform apply --auto-approve
```
## Set needed variables to connect to the machine
```
export SSH_USER=$(terraform output -raw ssh_user)
export GCP_IP=$(terraform output -raw external_ip_sut_manager)
export WORKER_COUNT=$(terraform output -raw worker_count)
```
## Copy files for tests onto the machine
Ensure that you have run the data preparation script found in the `data` folder.
### Copy all files (Warning: Will take a while)
```
scp ../../../data/merged* $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/trips* $SSH_USER@$GCP_IP:/tmp/
```
### Copy a sample set for smaller tests
```
scp ../../../data/merged00.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/merged01.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/merged02.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/trips_merged00.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/trips_merged01.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/trips_merged02.csv $SSH_USER@$GCP_IP:/tmp/
```
## Connect to the manager and configure MobilityDB to function correctly in a Citus cluster
```
scp scripts/setupRideData.sh $SSH_USER@$GCP_IP:~/ 
ssh $SSH_USER@$GCP_IP "chmod +x ~/setupRideData.sh; ~/setupRideData.sh $WORKER_COUNT"
``` 
## Local benchmark
Open another terminal window and navigate to the `benchmark/mobilitydb` folder. From the current folder:
```
cd ../../../benchmark/mobilitydb
```
Run the benchmark using: 
```
python3 runMiniBenchmark.py $GCP_IP 5432
```
## Benchmark client usage

### Load Benchmark onto client
GCP_IP2=$(terraform output -raw external_ip_client)
SSH_USER2=$(terraform output -raw ssh_user)
#copy the benchmark code to the benchmark machine
scp -r ../../benchmark/mobilitydb/* $SSH_USER2@$GCP_IP2:/tmp/
ssh $SSH_USER2@$GCP_IP2

