sudo apt update
sudo apt-get install -y --force-yes ssh pdsh openjdk-11-jdk maven git openssh-server wget libxml2-utils make g++ libsnappy1v5 openjdk-8-jdk </dev/null

echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> ~/.bashrc
source ~/.bashrc

#setup passwordless ssh for Hadoop
ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys

#install zookeeper
export ZOOKEEPER_VERSION="3.9.3"
wget https://downloads.apache.org/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz
tar -xvf apache-zookeeper-${ZOOKEEPER_VERSION}-bin.tar.gz
sudo mv apache-zookeeper-${ZOOKEEPER_VERSION}-bin /opt/zookeeper
cd /opt/zookeeper
cp conf/zoo_sample.cfg conf/zoo.cfg
bin/zkServer.sh start

#Optional, check if it worked
#bin/zkCli.sh -server 127.0.0.1:2181

#add namenode-manager to /etc/hosts
machine_name="accumulo-namenode-manager"
ip_address=$(nslookup $machine_name | awk '/^Address: / { print $2 }')
if ! grep -q "$ip_address $machine_name" /etc/hosts; then
    echo "$ip_address $machine_name" | sudo tee -a /etc/hosts
fi

#install hadoop
cd ~
export HADOOP_VERSION="3.4.0"
wget https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz
tar -xvf hadoop-${HADOOP_VERSION}.tar.gz
sudo mv hadoop-${HADOOP_VERSION} /opt/hadoop
cd /opt/hadoop
mkdir namenode
echo "export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> etc/hadoop/hadoop-env.sh
#optional, test if works
bin/hadoop -version

echo "<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://accumulo-namenode-manager:9000</value>
    </property>
</configuration>" > etc/hadoop/core-site.xml
echo "<configuration>
    <property>
        <name>dfs.replication</name>
        <value>1</value>
    </property>
</configuration>" > etc/hadoop/hdfs-site.xml

echo "<configuration>
    <property>
        <name>yarn.acl.enable</name>
        <value>false</value>
    </property>
    <property>
        <name>yarn.admin.acl</name>
        <value>*</value>
    </property>
    <property>
        <name>yarn.log-aggregation-enable</name>
        <value>false</value>
    </property>
    <property>
        <name>yarn.resourcemanager.hostname</name>
        <value>accumulo-namenode-manager</value>
    </property>
    <property>
        <name>yarn.resourcemanager.scheduler.class</name>
        <value>org.apache.hadoop.yarn.server.resourcemanager.scheduler.fair.FairScheduler</value>
    </property>
    <property>
        <name>yarn.scheduler.minimum-allocation-mb</name>
        <value>1024</value>
    </property>
    <property>
        <name>yarn.scheduler.maximum-allocation-mb</name>
        <value>8192</value>
    </property>
</configuration>"> etc/hadoop/yarn-site.xml

echo "export PDSH_RCMD_TYPE=ssh" >> etc/hadoop/hadoop-env.sh
echo "export PDSH_RCMD_TYPE=ssh" >> ~/.bashrc
export PDSH_RCMD_TYPE=ssh

#install accumulo 
cd ~
export ACCUMULO_VERSION="2.1.3"
wget https://dlcdn.apache.org/accumulo/${ACCUMULO_VERSION}/accumulo-${ACCUMULO_VERSION}-bin.tar.gz
tar -xvf accumulo-${ACCUMULO_VERSION}-bin.tar.gz
sudo mv accumulo-${ACCUMULO_VERSION} /opt/accumulo
cd /opt/accumulo
echo "JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64" >> conf/accumulo-env.sh
bin/accumulo-util build-native
export ACCUMULO_HOME=/opt/accumulo
export ZOOKEEPER_HOME=/opt/zookeeper
export HADOOP_HOME=/opt/hadoop
sed -i '/ZOOKEEPER_HOME=/a\
ACCUMULO_HOME=/opt/accumulo\
ZOOKEEPER_HOME=/opt/zookeeper\
HADOOP_HOME=/opt/hadoop' conf/accumulo-env.sh

#replace 8020 in accumulo.properties with 9000
sed -i 's/8020/9000/g' conf/accumulo.properties
sed -i 's/localhost/accumulo-namenode-manager/g' conf/accumulo.properties
#replace instance_name= in accumulo-client.properties with instance_name=test
sed -i 's/instance.name=/instance.name=test/g' conf/accumulo-client.properties
sed -i 's/auth.principal=/auth.principal=root/g' conf/accumulo-client.properties
sed -i 's/auth.token=/auth.token=test/g' conf/accumulo-client.properties
sed -i 's/instance.zookeepers=localhost/instance.zookeepers=accumulo-namenode-manager/g' conf/accumulo-client.properties
bin/accumulo-cluster create-config
#make services remotely reachable instead of just from localhost
sed -i 's/localhost/accumulo-namenode-manager/g' conf/cluster.yaml


cd ~
export TAG="5.0.1"
export SCALA_VERSION="2.12"
export VERSION="2.12-${TAG}" # note: 2.12 is the Scala build version
# download and unpackage the most recent distribution:
wget "https://github.com/locationtech/geomesa/releases/download/geomesa-${TAG}/geomesa-accumulo_${VERSION}-bin.tar.gz"
tar xvf geomesa-accumulo_${VERSION}-bin.tar.gz
sudo mv geomesa-accumulo_${VERSION} /opt/geomesa-accumulo 
sudo mv /opt/geomesa-accumulo/dist/accumulo/geomesa-accumulo-distributed-runtime_${SCALA_VERSION}-${TAG}.jar /opt/accumulo/lib

cd /opt/accumulo

#bin/accumulo-cluster start