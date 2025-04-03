apt update 
apt upgrade -y 
# dependencies for MobilityDB
apt install build-essential cmake libproj-dev libjson-c-dev libprotobuf-c-dev postgresql-16 git sudo postgresql-server-dev-16 libgsl-dev -y 

# Start PostgreSQL

sudo service postgresql initdb
sudo service postgresql start
sudo apt install libgeos++-dev libgeos3.10.2 libgeos-c1v5 libgeos-dev libgeos-doc postgresql-16-postgis-3 gnupg2 -y
# Download and Install MobilityDB
git clone https://github.com/MobilityDB/MobilityDB
mkdir MobilityDB/build
cd MobilityDB/build
cmake ..
make
sudo make install
echo "shared_preload_libraries = 'postgis-3'
max_locks_per_transaction = 128
listen_addresses = '*'" >> /etc/postgresql/14/main/postgresql.conf
echo "# TYPE DATABASE USER CIDR-ADDRESS  METHOD
host  all  all 0.0.0.0/0 scram-sha-256" >> /etc/postgresql/14/main/pg_hba.conf
sudo /etc/init.d/postgresql restart

#Enable PostGIS and Citus
ENTRYPOINT
sudo -u postgres psql -c "CREATE DATABASE mobility;"
sudo -u postgres psql mobility -c "CREATE EXTENSION PostGIS"
sudo -u postgres psql mobility -c "CREATE EXTENSION MobilityDB"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'test'"