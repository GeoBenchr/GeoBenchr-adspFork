#!/bin/bash

# Variablen setzen
ACCUMULO_USER="root"
ACCUMULO_PASSWORD="test"
ACCUMULO_NAMESPACE="geowave"
HDFS_PATH="/accumulo/classpath"
ACCUMULO_MASTER_FQDN="geowave-benchmark-manager"
ACCUMULO_ROOT="/accumulo"

echo -e "Konfiguriere Accumulo für GeoWave...\n"
cat << EOF > /tmp/accumulo-commands
createnamespace $ACCUMULO_NAMESPACE
config -s general.vfs.context.classpath.geowave=hdfs://$ACCUMULO_MASTER_FQDN:9000$HDFS_PATH/[^.].*.jar
config -ns $ACCUMULO_NAMESPACE -s table.classpath.context=geowave
exit
EOF

accumulo shell -u $ACCUMULO_USER -p $ACCUMULO_PASSWORD -f /tmp/accumulo-commands

echo -e "\nAccumulo wurde für GeoWave konfiguriert.\n"
echo -e "Neustart der erforderlichen Dienste...\n"

echo "Starte Accumulo neu..."
accumulo-cluster restart

echo -e "\nGeoWave-Konfiguration für Accumulo abgeschlossen.\n"
