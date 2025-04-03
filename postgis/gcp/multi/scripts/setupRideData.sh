sudo service postgresql restart
sudo -i -u postgres psql -c "SELECT citus_set_coordinator_host('mobdb-manager', 5432);"
for (( i = 0; i < $1; i++ )) 
do
    sudo -i -u postgres psql -c "SELECT * FROM citus_add_node('mobdb-worker-$i',5432);"
done

sudo -i -u postgres psql -c "SET citus.max_intermediate_result_size to -1;"
sudo -i -u postgres psql -c "CREATE TABLE cycling_data (
    ride_id float,
    rider_id float,
    latitude float,
    longitude float,
    x float,
    y float,
    z float,
    timestamp timestamp
);"

sudo -i -u postgres psql -c "SELECT create_distributed_table('cycling_data','rider_id');"

sudo -i -u postgres psql -c "COPY cycling_data FROM '/tmp/merged00.csv' DELIMITER ',' CSV;"
sudo -i -u postgres psql -c "COPY cycling_data FROM '/tmp/merged01.csv' DELIMITER ',' CSV;"
sudo -i -u postgres psql -c "COPY cycling_data FROM '/tmp/merged02.csv' DELIMITER ',' CSV;"
sudo -i -u postgres psql -c "COPY cycling_data FROM '/tmp/merged03.csv' DELIMITER ',' CSV;"
sudo -i -u postgres psql -c "COPY cycling_data FROM '/tmp/merged04.csv' DELIMITER ',' CSV;"
sudo -i -u postgres psql -c "COPY cycling_data FROM '/tmp/merged05.csv' DELIMITER ',' CSV;"
sudo -i -u postgres psql -c "COPY cycling_data FROM '/tmp/merged06.csv' DELIMITER ',' CSV;"
sudo -i -u postgres psql -c "COPY cycling_data FROM '/tmp/merged07.csv' DELIMITER ',' CSV;"

sudo -i -u postgres psql -c "ALTER TABLE cycling_data ADD COLUMN point_geom geography(Point, 4326);"

sudo -i -u postgres psql -c "UPDATE cycling_data SET point_geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326);"

sudo -i -u postgres psql -c "CREATE INDEX idx_cycling_data_point_geom ON cycling_data USING GIST (point_geom);"
sudo -i -u postgres psql -c "CREATE INDEX idx_cycling_data_latitude ON cycling_data (latitude);"
sudo -i -u postgres psql -c "CREATE INDEX idx_cycling_data_longitude ON cycling_data (longitude);"

sudo -i -u postgres psql -c "CREATE TABLE cycling_trips (
  ride_id float,
  rider_id float,
  trip tgeogpoint
);"
sudo -i -u postgres psql -c "SELECT create_distributed_table('cycling_trips','ride_id');"
sudo -i -u postgres psql -c "COPY cycling_trips FROM '/tmp/trips_merged00.csv' DELIMITER ';' CSV HEADER;"
sudo -i -u postgres psql -c "COPY cycling_trips FROM '/tmp/trips_merged01.csv' DELIMITER ';' CSV HEADER;"
sudo -i -u postgres psql -c "COPY cycling_trips FROM '/tmp/trips_merged02.csv' DELIMITER ';' CSV HEADER;"
sudo -i -u postgres psql -c "COPY cycling_trips FROM '/tmp/trips_merged03.csv' DELIMITER ';' CSV HEADER;"
sudo -i -u postgres psql -c "COPY cycling_trips FROM '/tmp/trips_merged04.csv' DELIMITER ';' CSV HEADER;"
sudo -i -u postgres psql -c "COPY cycling_trips FROM '/tmp/trips_merged05.csv' DELIMITER ';' CSV HEADER;"
sudo -i -u postgres psql -c "COPY cycling_trips FROM '/tmp/trips_merged06.csv' DELIMITER ';' CSV HEADER;"
sudo -i -u postgres psql -c "COPY cycling_trips FROM '/tmp/trips_merged07.csv' DELIMITER ';' CSV HEADER;"

sudo -i -u postgres psql -c "CREATE TABLE cycling_trips_ref (
    ride_id float PRIMARY KEY,
    rider_id float,
    trip tgeogpoint 
);"

sudo -i -u postgres psql -c "SELECT create_reference_table('cycling_trips_ref');"
sudo -i -u postgres psql -c "INSERT INTO cycling_trips_ref SELECT * FROM cycling_trips;"

sudo -i -u postgres psql -c "SELECT ride_id, rider_id FROM cycling_trips_ref ORDER BY ride_id LIMIT 50;"

sudo -i -u postgres psql -c "SELECT * FROM cycling_data LIMIT 10;"
sudo -i -u postgres psql -c "SELECT * FROM cycling_trips LIMIT 10;"