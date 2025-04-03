#!/bin/bash

mkdir -p /tmp/geowave-jars
find /opt/geowave/lib/ -type f -name "*.jar" -exec cp {} /tmp/geowave-jars/ \;
echo "All GeoWave JARs are compressed and flattened!"
hdfs dfs -mkdir -p /accumulo/classpath/
echo "Created classpath for Accumulo in HDFS!"
echo "Starting transfer of GeoWave JARs..."
hdfs dfs -copyFromLocal /tmp/geowave-jars/*.jar /accumulo/classpath/
echo "Transfer completed!"
rm -rf /tmp/geowave-jars

echo "All GeoWave JARs are copied to /accumulo/classpath/"
