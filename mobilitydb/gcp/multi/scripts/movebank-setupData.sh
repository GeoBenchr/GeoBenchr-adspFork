sudo service postgresql restart
sudo -i -u postgres psql -c "SELECT citus_set_coordinator_host('mobdb-manager', 5432);"
for (( i = 0; i < $1; i++ )) 
do
    sudo -i -u postgres psql -c "SELECT * FROM citus_add_node('mobdb-worker-$i',5432);"
done

sudo -i -u postgres psql -c "SET citus.max_intermediate_result_size to -1;"
sudo -i -u postgres psql -c "CREATE TABLE movebank_data (
    timestamp timestamp,
    lon float,
    lat float,
    individual_id float,
    tag_id float,
    dataset_id float,
    index float
);"

sudo -i -u postgres psql -c "SELECT create_distributed_table('movebank_data','individual_id');"

for file in /tmp/moveBank*.csv; do
    sudo -i -u postgres psql -c "COPY movebank_data FROM '$file' DELIMITER ',' CSV;"
done

sudo -i -u postgres psql -c "ALTER TABLE movebank_data ADD COLUMN point_geom geography(Point, 4326);"

sudo -i -u postgres psql -c "UPDATE movebank_data SET point_geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326);"

sudo -i -u postgres psql -c "CREATE INDEX idx_movebank_data_point_geom ON movebank_data USING GIST (point_geom);"
sudo -i -u postgres psql -c "CREATE INDEX idx_movebank_data_latitude ON movebank_data (lat);"
sudo -i -u postgres psql -c "CREATE INDEX idx_movebank_data_longitude ON movebank_data (lon);"

sudo -i -u postgres psql -c "SELECT * FROM movebank_data LIMIT 10;"