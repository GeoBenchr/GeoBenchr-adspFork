# Geobenchr for Geomesa-Accumulo (Multi-Node)
## Logging into the Google Cloud
Please follow the general documentation found in the repository README to help setup initial connection from the command line with `gcloud`.
## Setting up machine infrastructure
You will at least need to change the variable `gcp_ssh_pub_key_file` and `project` as this links to your local public ssh key found on your machine and to a Gcloud project you won't have access to.
```
terraform init
terraform apply --auto-approve

```
## Set important variables and configure machines
```
export SSH_USER=$(terraform output -raw ssh_user)
export GCP_IP=$(terraform output -raw external_ip_sut_namenode_manager)
export WORKER_COUNT=$(terraform output -raw num_workers)

export output=$(terraform output -json external_ip_sut_workers)
export machines=($(echo $output | jq -r '.[]'))
export length=${#machines[@]}
for ((i=1; i<=length; i++)); do
    declare "machine_$i=${machines[$i]}"
done

scp scripts/startManager.sh $SSH_USER@$GCP_IP:~/ 
for ((i=1; i<=length; i++)); do
    var="machine_$i"
    ip=$(eval echo \$$var)
    scp scripts/startWorker.sh $SSH_USER@$ip:~/
done

```
In the current state, you need to add the external IP to your local /etc/hosts file in order for the requests to correctly be able to access the tablet servers. This is a pain in the butt and not really production usable, but its what works for now. The step below will do so (depending on your set permissions, you might have to set these manually):
```
for ((i=1; i<=length; i++)); do
    var="machine_$i"
    ip=$(eval echo \$$var)
    echo "$ip accumulo-worker-$((i-1))" >> /etc/hosts
done
```
Setting them manually: 
``` 
sudo vi /etc/hosts
```
Add them in the following format (you can get the external ips using `terraform output`, with the external IPs being in order from 0 to n-1 workers from top to bottom as they are displayed):
```
<External_IP> <accumulo-worker-0>
<External_IP1> <accumulo-worker-1>
<External_IP2cd> <accumulo-worker-2>
```
Run the configuration scripts (If we were to pass the scripts as startup scripts, they run with the `root` account, which can cause some problems with Hadoop):
```
ssh $SSH_USER@$GCP_IP "chmod +x ~/startManager.sh; ~/startManager.sh $WORKER_COUNT"
for ((i=1; i<=length; i++)); do
    var="machine_$i"
    ip=$(eval echo \$$var)
    ssh $SSH_USER@$ip "chmod +x ~/startWorker.sh; ~/startWorker.sh $WORKER_COUNT"
    ssh $SSH_USER@$GCP_IP 'cat ~/.ssh/id_rsa.pub' | ssh $SSH_USER@$ip 'cat >> ~/.ssh/authorized_keys'
    ssh $SSH_USER@$ip 'cat ~/.ssh/id_rsa.pub' | ssh $SSH_USER@$GCP_IP 'cat >> ~/.ssh/authorized_keys'
done
```
Now you can actually start the cluster
```
ssh $SSH_USER@$GCP_IP "/opt/hadoop/bin/hdfs namenode -format"
ssh $SSH_USER@$GCP_IP "/opt/hadoop/sbin/start-dfs.sh"
ssh $SSH_USER@$GCP_IP "/opt/accumulo/bin/accumulo init --instance-name test -u root --password test"
ssh $SSH_USER@$GCP_IP "/opt/accumulo/bin/accumulo-cluster start"

```
You can now use your browser to check if Accumulo is running correctly by connecting to the monitor node of Accumulo.
```
http://<Manager_IP>:9995
```
## Copy data to the machine
If you want to copy all files onto the machine (not recommended, as your upload speed might be):
```
scp ../../../data/geomesa*.csv $SSH_USER@$GCP_IP:~/ 
```
If you only want to copy some (files are usually around 150 MB, keep that in mind when deciding on how many you want to upload to the instance):
```
scp ../../../data/geomesa_merged00.csv $SSH_USER@$GCP_IP:~/ 
scp ../../../data/geomesa_merged01.csv $SSH_USER@$GCP_IP:~/ 
scp ../../../data/geomesa_merged02.csv $SSH_USER@$GCP_IP:~/ 
scp ../../../data/geomesa_merged03.csv $SSH_USER@$GCP_IP:~/ 
```
Now copy some of the trip data as well:
```
scp ../../../data/geomesa_trips_geomesa_merged00.csv $SSH_USER@$GCP_IP:~/ 
scp ../../../data/geomesa_trips_geomesa_merged01.csv $SSH_USER@$GCP_IP:~/ 
scp ../../../data/geomesa_trips_geomesa_merged02.csv $SSH_USER@$GCP_IP:~/ 
scp ../../../data/geomesa_trips_geomesa_merged03.csv $SSH_USER@$GCP_IP:~/ 
```


## Setup the last parts
These commands install some needed dependencies:
```
ssh $SSH_USER@$GCP_IP 'cd /opt/geomesa-accumulo;yes | bin/install-dependencies.sh;yes | bin/install-shapefile-support.sh'
```
Here we create SimpleFeatureType schemas, which GeoMesa uses for storing spatiotemporal data. First we create one for point data, and then trip(line) data. However, GeoMesa does not offer the same kind of support for moving points when compared to MobilityDB's `tgeogpoint`.
```
ssh $SSH_USER@$GCP_IP 'cd /opt/geomesa-accumulo; bin/geomesa-accumulo create-schema -i test -z localhost -u root  -p test -c example -s "ride_id:Integer:index=full,rider_id:Integer:index=full,latitude:Double,longitude:Double,geom:Point:srid=4326,x:Double,y:Double,z:Double,timestamp:Date" -f ride_data'

ssh $SSH_USER@$GCP_IP 'cd /opt/geomesa-accumulo; bin/geomesa-accumulo create-schema -i test -z localhost -u root  -p test -c example -s "ride_id:Integer:index=full,rider_id:Integer:index=full,trip:MultiLineString:srid=4326,timestamp:List[Date]" -f trip_data'
```
### Setup a csv converter to convert the data into the correct format
```
scp ../../converter/ride_data.converter $SSH_USER@$GCP_IP:/opt/geomesa-accumulo
scp ../../converter/trip_data.converter $SSH_USER@$GCP_IP:/opt/geomesa-accumulo
```
### Ingest data
If you want to ingest all data (not recommended, unless you have a strong machine type set. The threading can cause performance issues/tablet server crashes within Accumulo):
```
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/ride_data.converter -c example -i test -z localhost -u root -p test -f ride_data -t 8 ~/geomesa_merged*.csv'
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/trip_data.converter -c example -i test -z localhost -u root -p test -f trip_data -t 8 ~/geomesa_trips_geomesa_merged*.csv'
```
If you want to ingest just some of the data:
```
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/ride_data.converter -c example -i test -z localhost -u root -p test -f ride_data ~/geomesa_merged00.csv'
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/ride_data.converter -c example -i test -z localhost -u root -p test -f ride_data ~/geomesa_merged01.csv'
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/ride_data.converter -c example -i test -z localhost -u root -p test -f ride_data ~/geomesa_merged02.csv'
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/ride_data.converter -c example -i test -z localhost -u root -p test -f ride_data ~/geomesa_merged03.csv'
```
Ingest trip data:
```
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/trip_data.converter -c example -i test -z localhost -u root -p test -f trip_data ~/geomesa_trips_geomesa_merged00.csv'
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/trip_data.converter -c example -i test -z localhost -u root -p test -f trip_data ~/geomesa_trips_geomesa_merged01.csv'
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/trip_data.converter -c example -i test -z localhost -u root -p test -f trip_data ~/geomesa_trips_geomesa_merged02.csv'
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/trip_data.converter -c example -i test -z localhost -u root -p test -f trip_data ~/geomesa_trips_geomesa_merged03.csv'
```

## Check if GeoMesa setup is correct by running a simple export that gets 50 values
```
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo export -i test -z localhost -u root  -p test -c example -m 50 -q "rider_id <= 30" -f ride_data'
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo export -i test -z localhost -u root  -p test -c example -m 50 -q "rider_id <= 30" -f trip_data'
```


## Local Benchmark experiment
#### GeoTools
Running this benchmark requires JDK 11 and Maven to be installed on your machine. Open a second terminal in the current folder:
```
export GCP_IP=$(terraform output -raw external_ip_sut_manager)
cd ../../../benchmark/geomesa/geotools/geootools
mvn clean install
java -jar target/geobenchr-1.0.jar test root test example $GCP_IP
```
#### Shell
Running this benchmark requires Python to be installed. Open a second terminal in the current folder
```
export SSH_USER=$(terraform output -raw ssh_user)
export GCP_IP=$(terraform output -raw external_ip_sut_manager)
cd ../../../benchmark/geomesa/shell_benchmark
python runMiniBenchmark $GCP_IP multi
```
## Check and setup benchmark client
### Not functional as of yet
Run this again from your local device.
```
GCP_IP2=$(terraform output -raw external_ip_client)
SSH_USER2=$(terraform output -raw ssh_user)
#copy the benchmark code to the benchmark machine
scp -r ../../benchmark/geomesa/geotools/ $SSH_USER2@$GCP_IP2:~/
scp scripts/startClient.sh $SSH_USER2@$GCP_IP2:~/
ssh $SSH_USER2@$GCP_IP2
```
Run this on the machine: 
```
chmod +x ~/startClient.sh
~/startClient.sh
```
## Run the benchmark 
```
cd ~/geotools/geootools
mvn clean install
mvn exec:java -Dexec.mainClass="com.example.Main" -Dexec.args=""
```