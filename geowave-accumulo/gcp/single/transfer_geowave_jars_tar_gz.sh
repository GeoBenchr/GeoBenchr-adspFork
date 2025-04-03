#!/bin/bash

hdfs dfs -mkdir /accumulo/classpath
find /opt/geowave/lib/ -type f -name "*.jar" | tar -czvf geowave-jars.tar.gz -T -
hdfs dfs -put -f geowave-jars.tar.gz /accumulo/classpath/
hdfs dfs -cat /accumulo/classpath/geowave-jars.tar.gz | tar -xz --directory=/accumulo/classpath/

echo "All GeoWave JARs are now in /accumulo/classpath/"
