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
ssh $SSH_USER@$GCP_IP "chmod +x ~/startManager.sh; ~/startManager.sh $WORKER_COUNT"
for ((i=1; i<=length; i++)); do
    var="machine_$i"
    ip=$(eval echo \$$var)
    ssh $SSH_USER@$ip "chmod +x ~/startWorker.sh; ~/startWorker.sh $WORKER_COUNT"
    ssh $SSH_USER@$GCP_IP 'cat ~/.ssh/id_rsa.pub' | ssh $SSH_USER@$ip 'cat >> ~/.ssh/authorized_keys'
    ssh $SSH_USER@$ip 'cat ~/.ssh/id_rsa.pub' | ssh $SSH_USER@$GCP_IP 'cat >> ~/.ssh/authorized_keys'
done
ssh $SSH_USER@$GCP_IP "/opt/hadoop/bin/hdfs namenode -format"
ssh $SSH_USER@$GCP_IP "/opt/hadoop/sbin/start-dfs.sh"
ssh $SSH_USER@$GCP_IP "/opt/accumulo/bin/accumulo init --instance-name test -u root --password test"
ssh $SSH_USER@$GCP_IP "/opt/accumulo/bin/accumulo-cluster start"

scp ../../../data/geomesa*.csv $SSH_USER@$GCP_IP:~/ 
ssh $SSH_USER@$GCP_IP 'cd /opt/geomesa-accumulo;yes | bin/install-dependencies.sh;yes | bin/install-shapefile-support.sh'
ssh $SSH_USER@$GCP_IP 'cd /opt/geomesa-accumulo; bin/geomesa-accumulo create-schema -i test -z localhost -u root  -p test -c example -s "ride_id:Integer:index=full,rider_id:Integer:index=full,latitude:Double,longitude:Double,geom:Point:srid=4326,x:Double,y:Double,z:Double,timestamp:Date" -f ride_data'

ssh $SSH_USER@$GCP_IP 'cd /opt/geomesa-accumulo; bin/geomesa-accumulo create-schema -i test -z localhost -u root  -p test -c example -s "ride_id:Integer:index=full,rider_id:Integer:index=full,trip:MultiLineString:srid=4326,timestamp:List[Date]" -f trip_data'
scp ../../converter/ride_data.converter $SSH_USER@$GCP_IP:/opt/geomesa-accumulo
scp ../../converter/trip_data.converter $SSH_USER@$GCP_IP:/opt/geomesa-accumulo
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/ride_data.converter -c example -i test -z localhost -u root -p test -f ride_data -t 8 ~/geomesa_merged*.csv'
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo ingest -C /opt/geomesa-accumulo/trip_data.converter -c example -i test -z localhost -u root -p test -f trip_data -t 8 ~/geomesa_trips_geomesa_merged*.csv'
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo export -i test -z localhost -u root  -p test -c example -m 50 -q "rider_id <= 30" -f ride_data'
ssh $SSH_USER@$GCP_IP '/opt/geomesa-accumulo/bin/geomesa-accumulo export -i test -z localhost -u root  -p test -c example -m 50 -q "rider_id <= 30" -f trip_data'