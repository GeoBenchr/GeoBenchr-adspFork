# Setting up GeoWave
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

## Copy set-up-script to the VM
If you are using Windows Subsystem for Linux (WSL), you may encounter issues with SSH keys if they are located in the Windows file system. To avoid permission-related problems, copy your SSH keys to the WSL file system before proceeding.
```
scp managerSetUp.sh $SSH_USER@$GCP_IP:~/  
```

## Run the script for the Geowave-Manager machine 
Don't connect to the maschine and run the script locally, this will cause premission issues.
```
ssh $SSH_USER@$GCP_IP 'chmod +x ~/managerSetUp.sh; ~/managerSetUp.sh'
```

## Initialize Hadoop and Accumulo
````
ssh $SSH_USER@$GCP_IP "/opt/hadoop/bin/hdfs namenode -format"
ssh $SSH_USER@$GCP_IP "/opt/hadoop/sbin/start-dfs.sh"
ssh $SSH_USER@$GCP_IP "/opt/accumulo/bin/accumulo init --instance-name test -u root --password test"
ssh $SSH_USER@$GCP_IP "/opt/accumulo/bin/accumulo-cluster start"
````

## Initilaize Geowave
Connect to the maschine:
````
ssh $SSH_USER@$GCP_IP
````
and run the following to add Accumulo to Geowave:  
````
geowave store add -t accumulo \
    --zookeeper geowave-benchmark-manager:2181 \
    --instance test \
    --user root \
    --password test \
    --gwNamespace geowave \
    accumuloStore
````
# Example:
## Copy sample to the geowave-benchmark-manager machine
```
scp ../../../data/merged00.csv $SSH_USER@$GCP_IP:~/
```
## Create an index
````
accumulo shell -u root -p test
createnamespace geowave

geowave index add accumuloStore simraIndex \
    -t spatial_temporal \
    --numPartitions 4
````
## Ingest data
WIP
````
geowave ingest localToGW \
    /home/manager/merged00.csv \
    accumuloStore \
    simraIndex \
    --typeName rideData \
    --csvColumns "ride_id,rider_id,latitude,longitude,x,y,z,timestamp" \
    --geometryColumn geom \
    --timeColumn timestamp
````
