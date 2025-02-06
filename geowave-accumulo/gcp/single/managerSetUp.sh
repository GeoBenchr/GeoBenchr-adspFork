#!/bin/bash

# Version constants
HADOOP_VERSION="2.6.0"
ZOOKEEPER_VERSION="3.4.5"
ACCUMULO_VERSION="1.7.2"

# Update and install required packages
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -q
sudo apt-get install -y ssh pdsh openjdk-8-jdk maven git openssh-server wget libxml2-utils make g++ libsnappy1v5 </dev/null

# Configure Java 8 as the default
sudo update-alternatives --set java /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java
sudo update-alternatives --set javac /usr/lib/jvm/java-8-openjdk-amd64/bin/javac

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
wget https://archive.apache.org/dist/zookeeper/zookeeper-${ZOOKEEPER_VERSION}/zookeeper-${ZOOKEEPER_VERSION}.tar.gz
tar -xvf zookeeper-${ZOOKEEPER_VERSION}.tar.gz
sudo mv zookeeper-${ZOOKEEPER_VERSION} /opt/zookeeper

# Set ZooKeeper environment variables
export ZOOKEEPER_HOME=/opt/zookeeper
echo "export ZOOKEEPER_HOME=/opt/zookeeper" >> ~/.bashrc
echo "export PATH=\$ZOOKEEPER_HOME/bin:\$PATH" >> ~/.bashrc
source ~/.bashrc

# Configure and Start ZooKeeper
cd /opt/zookeeper
cp conf/zoo_sample.cfg conf/zoo.cfg
bin/zkServer.sh start

# Install Accumulo
wget https://archive.apache.org/dist/accumulo/${ACCUMULO_VERSION}/accumulo-${ACCUMULO_VERSION}-bin.tar.gz
tar -xvf accumulo-${ACCUMULO_VERSION}-bin.tar.gz
sudo mv accumulo-${ACCUMULO_VERSION} /opt/accumulo

# Configure Accumulo
echo "export ACCUMULO_HOME=/opt/accumulo" >> ~/.bashrc
echo "export PATH=\$PATH:/opt/accumulo/bin" >> ~/.bashrc
source ~/.bashrc

# Create Accumulo configuration file
cp /opt/accumulo/conf/templates/accumulo-site.xml /opt/accumulo/conf/accumulo-site.xml
cat <<EOT > /opt/accumulo/conf/accumulo-site.xml
<configuration>
    <property>
        <name>instance.zookeeper.host</name>
        <value>geowave-benchmark-manager:2181</value>
    </property>
    <property>
        <name>instance.name</name>
        <value>test</value>
    </property>
    <property>
        <name>general.rpc.auth</name>
        <value>root</value>
    </property>
    <property>
        <name>general.rpc.token</name>
        <value>test</value>
    </property>
    <property>
        <name>instance.dfs.dir</name>
        <value>hdfs://geowave-benchmark-manager:9000/accumulo</value>
    </property>
</configuration>
EOT

# Download and configure GeoWave
wget https://s3.amazonaws.com/geowave-rpms/release-jars/JAR/geowave-tools-2.0.1-cdh5-accumulo1.7.jar -P /opt/geowave
export GEOWAVE_HOME=/opt/geowave
echo "export GEOWAVE_HOME=/opt/geowave" >> ~/.bashrc
echo "export PATH=\$PATH:/opt/geowave/bin" >> ~/.bashrc
source ~/.bashrc

echo "Hadoop, ZooKeeper, Accumulo, and GeoWave installation complete!"
