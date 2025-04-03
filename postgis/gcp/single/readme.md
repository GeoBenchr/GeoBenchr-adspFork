# Setting up PostGIS
Make sure to adjust the `variables.tf`file to match your configuration. Specifically, change the project and ssh key. PostGIS uses a startup script, so give the machine a couple of minutes to configure everything.
```
terraform init
terraform apply --auto-approve
```
## Set needed variables to connect to the machine
```
export SSH_USER=$(terraform output -raw ssh_user)
export GCP_IP=$(terraform output -raw external_ip_sut_manager)
```
## Copy files for tests onto the machine
Ensure that you have run the data preparation script found in the `data` folder.
### Copy all files (Warning: Will take a while)
```
scp ../../../data/merged* $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/geomesa_trips* $SSH_USER@$GCP_IP:/tmp/
```
### Copy a sample set for smaller tests
```
scp ../../../data/merged00.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/merged01.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/merged02.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/merged03.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/geomesa_trips_geomesa_merged00.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/geomesa_trips_geomesa_trips_merged01.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/geomesa_trips_geomesa_trips_merged02.csv $SSH_USER@$GCP_IP:/tmp/
scp ../../../data/geomesa_trips_geomesa_trips_merged03.csv $SSH_USER@$GCP_IP:/tmp/
```

## Pass MobilityDB script to manager and run it
This part sets up the cycling data in MobilityDB, both in point and trip format.
```
scp scripts/setupRideData.sh $SSH_USER@$GCP_IP:~/ 
ssh $SSH_USER@$GCP_IP 'chmod +x ~/setupRideData.sh; ~/setupRideData.sh'
```
This script does the following:
1. We first create a table for point data, which includes several variables: 
- ride_id float,
- rider_id float,
- latitude float,
- longitude float,
- x float, (no real use)
- y float,(no real use)
- z float, (no real use)
- timestamp timestamp
2. We adjust the table to store longitude and latitude in point form as well, and ingest data
3. We create a trip table, which only contains:
- ride_id float,
- rider_id float,
- trip GEOMETRY(MultiLineString, 4326) (this contains the trip)
- time timestamp[] (Array of timestamps)
4. We then ingest some sample data and run queries to ensure that both tables have results

## Local benchmark
Open another terminal window and navigate to the `benchmark/mobilitydb` folder. From the current folder:
```
cd ../../../benchmark/postgis
```
Run the benchmark using (more details can be found in the benchmark folder)
```
python3 runMiniBenchmark.py $GCP_IP 5432
```
## Benchmark client usage

### Load Benchmark onto client
```
GCP_IP2=$(terraform output -raw external_ip_client)
SSH_USER2=$(terraform output -raw ssh_user)
#copy the benchmark code to the benchmark machine
scp -r ../../benchmark/mobilitydb/* $SSH_USER2@$GCP_IP2:/tmp/
ssh $SSH_USER2@$GCP_IP2
```
