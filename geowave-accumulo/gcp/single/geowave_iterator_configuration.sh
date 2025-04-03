#!/bin/bash

# Variablen setzen
ACCUMULO_USER="root"
ACCUMULO_PASSWORD="test"
ACCUMULO_NAMESPACE="geowave"
HDFS_PATH="/accumulo/classpath"
ACCUMULO_MASTER_FQDN="geowave-benchmark-manager"
ITERATOR_JAR="/opt/geowave/lib/geowave-accumulo-iterator.jar"

echo -e "\nStep 1: Installiere den GeoWave Accumulo Iterator...\n"

# Falls GeoWave nicht installiert ist, Installation starten
if [[ ! -d "/opt/geowave" ]]; then
    echo "GeoWave nicht gefunden. Installation wird durchgeführt..."
    wget https://geowave.s3.amazonaws.com/latest/standalone-installers/geowave_unix_latest.sh -O /tmp/geowave_install.sh
    chmod +x /tmp/geowave_install.sh
    sudo /tmp/geowave_install.sh -q -p /opt/geowave
fi


echo -e "\nStep 2: Hochladen des Iterators nach HDFS...\n"


# Iterator JAR nach HDFS hochladen
hdfs dfs -put -f "$ITERATOR_JAR" $HDFS_PATH/

echo -e "\nStep 3: Registrieren des Iterators in Accumulo...\n"

# Iterator in Accumulo registrieren
accumulo shell -u $ACCUMULO_USER -p $ACCUMULO_PASSWORD -e "
    config -ns $ACCUMULO_NAMESPACE -s table.classpath.context=geowave;
    config -t $ACCUMULO_NAMESPACE -s table.iterator.majc.geowave-iterator=30,org.locationtech.geowave.datastore.accumulo.iterator.GeoWaveIterator;
    config -t $ACCUMULO_NAMESPACE -s table.iterator.minc.geowave-iterator=30,org.locationtech.geowave.datastore.accumulo.iterator.GeoWaveIterator;
    config -t $ACCUMULO_NAMESPACE -s table.iterator.scan.geowave-iterator=30,org.locationtech.geowave.datastore.accumulo.iterator.GeoWaveIterator;
"

echo -e "\nGeoWave Accumulo Iterator wurde erfolgreich installiert, hochgeladen und registriert.\n"