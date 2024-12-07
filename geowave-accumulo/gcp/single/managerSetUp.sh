#!/bin/bash
# Update and install required packages
sudo apt update
sudo apt-get install -y --force-yes ssh pdsh openjdk-8-jdk maven git openssh-server wget libxml2-utils make g++ libsnappy1v5 </dev/null

# Configure Java 8 as the default
export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> ~/.bashrc
echo "export PATH=\$JAVA_HOME/bin:\$PATH" >> ~/.bashrc
source ~/.bashrc

# Add Hadoop configuration directory to the environment
export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop
echo "export HADOOP_CONF_DIR=/opt/hadoop/etc/hadoop" >> ~/.bashrc

# Add Hadoop binaries to the PATH
export PATH=$PATH:/opt/hadoop/bin:/opt/hadoop/sbin
echo "export PATH=\$PATH:/opt/hadoop/bin:/opt/hadoop/sbin" >> ~/.bashrc
source ~/.bashrc

# Setup passwordless SSH for Hadoop
ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys
chmod 0600 ~/.ssh/authorized_keys

# Install Zookeeper
export ZOOKEEPER_VERSION="3.4.14"
wget https://archive.apache.org/dist/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/zookeeper-${ZOOKEEPER_VERSION}.tar.gz
tar -xvf zookeeper-${ZOOKEEPER_VERSION}.tar.gz
sudo mv zookeeper-${ZOOKEEPER_VERSION} /opt/zookeeper
export ZOOKEEPER_HOME=/opt/zookeeper
echo "export ZOOKEEPER_HOME=/opt/zookeeper" >> ~/.bashrc
echo "export PATH=\$ZOOKEEPER_HOME/bin:\$PATH" >> ~/.bashrc
source ~/.bashrc
cd /opt/zookeeper
cp conf/zoo_sample.cfg conf/zoo.cfg
bin/zkServer.sh start

# Add namenode-manager to /etc/hosts
machine_name="geowave-benchmark-manager"
ip_address=$(nslookup $machine_name | awk '/^Address: / { print $2 }')
if ! grep -q "$ip_address $machine_name" /etc/hosts; then
    echo "$ip_address $machine_name" | sudo tee -a /etc/hosts
fi

# Install Hadoop
cd ~
export HADOOP_VERSION="3.3.6"
wget https://dlcdn.apache.org/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz
tar -xvf hadoop-${HADOOP_VERSION}.tar.gz
sudo mv hadoop-${HADOOP_VERSION} /opt/hadoop
cd /opt/hadoop
mkdir namenode
echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> etc/hadoop/hadoop-env.sh
bin/hadoop version

# Configure Hadoop
echo "<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://geowave-benchmark-manager:9000</value>
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
</configuration>" > etc/hadoop/yarn-site.xml

echo "export PDSH_RCMD_TYPE=ssh" >> etc/hadoop/hadoop-env.sh
echo "export PDSH_RCMD_TYPE=ssh" >> ~/.bashrc
export PDSH_RCMD_TYPE=ssh

# Install Accumulo
cd ~
export ACCUMULO_VERSION="2.0.1"
wget https://archive.apache.org/dist/accumulo/${ACCUMULO_VERSION}/accumulo-${ACCUMULO_VERSION}-bin.tar.gz
tar -xvf accumulo-${ACCUMULO_VERSION}-bin.tar.gz
sudo mv accumulo-${ACCUMULO_VERSION} /opt/accumulo
cd /opt/accumulo
echo "JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> conf/accumulo-env.sh
bin/build_native_components.sh
export ACCUMULO_HOME=/opt/accumulo
sed -i '/ZOOKEEPER_HOME=/a\
ACCUMULO_HOME=/opt/accumulo\
ZOOKEEPER_HOME=/opt/zookeeper\
HADOOP_HOME=/opt/hadoop' conf/accumulo-env.sh

# Copy ZooKeeper JARs to Accumulo's lib directory
cp /opt/zookeeper/lib/*.jar /opt/accumulo/lib/

find /opt/accumulo/lib/ -type f -name '*jline*.jar' ! -name 'jline-2.11.jar' -delete
find /opt/accumulo/lib/ -type f -name 'slf4j*.jar' ! -name 'slf4j-api-1.7.26.jar' -and ! -name 'slf4j-log4j12-1.7.26.jar' -delete

export PATH=$PATH:/opt/accumulo/bin
echo "export PATH=\$PATH:/opt/accumulo/bin" >> ~/.bashrc
source ~/.bashrc

# Update Accumulo configuration
sed -i 's/8020/9000/g' conf/accumulo.properties
sed -i 's/localhost/geowave-benchmark-manager/g' conf/accumulo.properties
sed -i 's/instance.name=/instance.name=test/g' conf/accumulo-client.properties
sed -i 's/auth.principal=/auth.principal=root/g' conf/accumulo-client.properties
sed -i 's/auth.token=/auth.token=test/g' conf/accumulo-client.properties
sed -i 's/instance.zookeepers=localhost/instance.zookeepers=geowave-benchmark-manager/g' conf/accumulo-client.properties
bin/accumulo-cluster create-config

#Upload Accumulo JARs to HDFS
hdfs dfs -mkdir -p /accumulo/lib
hdfs dfs -put /opt/accumulo/lib/*.jar /accumulo/lib/

#configure Accumulo for GeoWave
accumulo shell -u root <<EOF
createnamespace geowave
createuser geowave
grant NameSpace.CREATE_TABLE -ns geowave -u geowave
config -s general.vfs.context.classpath.geowave=hdfs://geowave-benchmark-manager:9000/accumulo/lib/[^.].*.jar
config -ns geowave -s table.classpath.context=geowave
exit
EOF

#install geowave
#https://geowave.s3.amazonaws.com/latest/standalone-installers/geowave_unix_2_0_2-SNAPSHOT.sh
cd ~
wget https://geowave.s3.amazonaws.com/2.0.1/standalone-installers/geowave_unix_2_0_1.sh
chmod +x geowave_unix_2_0_1.sh
sudo ./geowave_unix_2_0_1.sh <<EOF
o
/opt/geowave
1,2,4,5,6,7,8,10,11,13,14,23,24,25,26,27,28,29,30,31,33,42,43
EOF

echo "export GEOWAVE_HOME=/opt/geowave" >> ~/.bashrc
echo "export PATH=\$PATH:/opt/geowave/bin" >> ~/.bashrc
source ~/.bashrc

echo "export JAVA_OPTS='--illegal-access=warn'" >>~/.bashrc
source ~/.bashrc

# Increase ulimit for maximum open files
sudo bash -c "echo '* soft nofile 32768' >> /etc/security/limits.conf"
sudo bash -c "echo '* hard nofile 32768' >> /etc/security/limits.conf"

sudo mkdir -p /opt/geowave/logs
sudo chown -R "$USER":"$USER" /opt/geowave
sudo chmod -R 755 /opt/geowave
source ~/.bashrc

#export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
#echo "export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64" >> ~/.bashrc
#source ~/.bashrc

JAVA_OPTS="-Dlog4j.debug=true -Dlog4j.configuration=file:/opt/geowave/conf/log4j.properties" geowave help

echo "Hadoop, ZooKeeper, Accumulo and GeoWave installation and configuration complete!"