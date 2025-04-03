sudo -i -u postgres psql -c "CREATE TABLE movebank_data (
    timestamp timestamp,
    lon float,
    lat float,
    individual_id float,
    tag_id float,
    dataset_id float,
    index float
);"

for file in /tmp/moveBank*.csv; do
    sudo -i -u postgres psql -c "COPY movebank_data FROM '$file' DELIMITER ',' CSV;"
done



sudo -i -u postgres psql -c "ALTER TABLE movebank_data ADD COLUMN point_geom geography(Point, 4326);"
sudo -i -u postgres psql -c "UPDATE movebank_data SET point_geom = ST_SetSRID(ST_MakePoint(lon, lat), 4326);"

sudo -i -u postgres psql -c "CREATE INDEX idx_movebank_data_point_geom ON movebank_data USING GIST (point_geom);"
sudo -i -u postgres psql -c "CREATE INDEX idx_movebank_data_latitude ON movebank_data (lat);"
sudo -i -u postgres psql -c "CREATE INDEX idx_movebank_data_longitude ON movebank_data (lon);"

# sudo -i -u postgres psql -c "CREATE TABLE cycling_trips (
#   ride_id float,
#   rider_id float,
#   trip tgeogpoint
# );"

# sudo -i -u postgres psql -c "COPY cycling_trips FROM '/tmp/trips_merged00.csv' DELIMITER ';' CSV HEADER;"

sudo -i -u postgres psql -c "SELECT * FROM movebank_data LIMIT 10;"
# sudo -i -u postgres psql -c "SELECT * FROM cycling_trips LIMIT 10;"