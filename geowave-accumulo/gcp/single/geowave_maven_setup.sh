#!/bin/bash

# Exit on error
set -e

echo "Überprüfe, ob Maven installiert ist..."
if ! command -v mvn &> /dev/null; then
    echo "Maven nicht gefunden! Installiere Maven..."
    sudo apt update
    sudo apt install -y maven
else
    echo "Maven ist bereits installiert."
fi

echo "Erstelle ein Maven-Projekt für GeoWave..."
PROJECT_DIR="geowave-maven"
if [ ! -d "$PROJECT_DIR" ]; then
    mvn archetype:generate -DgroupId=com.mycompany.geowave \
        -DartifactId=geowave-maven \
        -DarchetypeArtifactId=maven-archetype-quickstart \
        -DinteractiveMode=false
    echo "Maven-Projekt wurde erstellt!"
else
    echo "Maven-Projekt existiert bereits, überspringe Erstellung."
fi

cd $PROJECT_DIR

echo "Aktualisiere die pom.xml mit GeoWave-Abhängigkeiten..."
cat > pom.xml <<EOL
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.mycompany.geowave</groupId>
    <artifactId>geowave-maven</artifactId>
    <version>1.0-SNAPSHOT</version>
    <dependencies>
        <!-- GeoWave Core -->
        <dependency>
            <groupId>org.locationtech.geowave</groupId>
            <artifactId>geowave-core</artifactId>
            <version>2.0.1</version>
        </dependency>

        <!-- GeoWave Accumulo-Backend -->
        <dependency>
            <groupId>org.locationtech.geowave</groupId>
            <artifactId>geowave-store-accumulo</artifactId>
            <version>2.0.1</version>
        </dependency>

        <!-- Accumulo Core -->
        <dependency>
            <groupId>org.apache.accumulo</groupId>
            <artifactId>accumulo-core</artifactId>
            <version>2.0.1</version>
        </dependency>

        <!-- Hadoop Common -->
        <dependency>
            <groupId>org.apache.hadoop</groupId>
            <artifactId>hadoop-common</artifactId>
            <version>3.1.4</version>
        </dependency>

        <!-- Zookeeper -->
        <dependency>
            <groupId>org.apache.zookeeper</groupId>
            <artifactId>zookeeper</artifactId>
            <version>3.4.14</version>
        </dependency>
    </dependencies>
    <build>
        <plugins>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <version>3.8.1</version>
                <configuration>
                    <source>8</source>
                    <target>8</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
EOL

echo "pom.xml wurde erfolgreich aktualisiert!"

echo "Baue das Maven-Projekt..."
mvn clean install

echo "Maven-Build abgeschlossen!"

echo "GeoWave-Maven-Projekt ist fertig eingerichtet!"
