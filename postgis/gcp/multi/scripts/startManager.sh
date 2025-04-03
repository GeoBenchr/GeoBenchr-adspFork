export DEBIAN_FRONTEND=noninteractive
sudo apt update 
sudo apt upgrade -y   
sudo apt install -y sudo curl gnupg2 systemctl </dev/null
sudo apt install -y postgresql-common </dev/null
sudo yes '' | /usr/share/postgresql-common/pgdg/apt.postgresql.org.sh
sudo apt install -y build-essential cmake libproj-dev libjson-c-dev libprotobuf-c-dev postgresql-16 git postgresql-server-dev-16 libgsl-dev </dev/null
sudo service postgresql start  
sudo apt install -y libgeos++-dev libgeos3.10.2 libgeos-c1v5 libgeos-dev libgeos-doc postgresql-16-postgis-3 </dev/null
git clone https://github.com/MobilityDB/MobilityDB && \
mkdir MobilityDB/build && \
cd MobilityDB/build && \
cmake .. && \
make && \
sudo make install  
curl https://install.citusdata.com/community/deb.sh | sudo bash
# install the server and initialize db
sudo apt -y install postgresql-16-citus-12.1 &> /dev/null
sudo echo "shared_preload_libraries = 'citus, postgis-3'" >> /etc/postgresql/16/main/postgresql.conf  
sudo echo "max_locks_per_transaction = 128" >> /etc/postgresql/16/main/postgresql.conf  
sudo printf "listen_addresses = '*'\n" >> /etc/postgresql/16/main/postgresql.conf  
sudo echo "# TYPE DATABASE USER CIDR-ADDRESS  METHOD" >> /etc/postgresql/16/main/pg_hba.conf
sudo echo "host    all             all             0.0.0.0/0            trust" >> /etc/postgresql/16/main/pg_hba.conf 
sudo echo "host    all             all             127.18.0.0/32        trust" >> /etc/postgresql/16/main/pg_hba.conf 

# Also allow the host unrestricted access to connect to itself
sudo echo "host    all             all             127.0.0.1/32          trust" >> /etc/postgresql/16/main/pg_hba.conf 
sudo echo "host    all             all             ::1/128               trust" >> /etc/postgresql/16/main/pg_hba.conf 
sudo /etc/init.d/postgresql restart && \
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'test';" && \
PGPASSWORD=test sudo -u postgres psql -c "CREATE EXTENSION PostGIS;" && \
PGPASSWORD=test sudo -u postgres psql -c "CREATE EXTENSION MobilityDB;" && \
PGPASSWORD=test sudo -u postgres psql -c "CREATE EXTENSION citus;" && \
sudo service postgresql restart
# and make it start automatically when computer does
sudo update-rc.d postgresql enable