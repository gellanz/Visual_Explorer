#!/usr/bin/env bash

# Update Packages
apt-get update
# Upgrade Packages
apt-get upgrade

# Basic Linux Stuff
apt-get install -y git

#dos2unix
apt-get install dos2unix

# Apache
apt-get install -y apache2

# Enable Apache Mods
a2enmod rewrite

# Restart Apache
sudo service apache2 restart

# Setting MySQL root user password root/root
debconf-set-selections <<< 'mysql-server mysql-server/root_password password root'
debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password root'


# Installing MySQL packages
apt-get install -y mysql-server mysql-client

# Allow External Connections on your MySQL Service
sudo sed -i -e 's/bind-addres/#bind-address/g' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo sed -i -e 's/skip-external-locking/#skip-external-locking/g' /etc/mysql/mysql.conf.d/mysqld.cnf
mysql -u root -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root'; FLUSH privileges;"
sudo service mysql restart

# Making executable the scripts
for file in "/scripts/*"; do dos2unix $file; done
for file in "/beats_elk/*"; do dos2unix $file; done
for file in "/docker/*"; do dos2unix $file; done

# echo -e "Si es la primera vez que se construirá la base de datos o si la máquina virtual
#          se destruyó, se tienen que ejecutar los siguientes comandos: \n
#          cd /scripts \n ./boot_db_first_time.sh"

# Installing Docker 
sudo apt-get install -y docker.io
sudo apt-get install -y docker-compose
grep vm.max_map_count /etc/sysctl.conf
sudo sysctl -w vm.max_map_count=262144

# Installing and configuring Metricbeam
curl -L -O https://artifacts.elastic.co/downloads/beats/metricbeat/metricbeat-7.13.2-amd64.deb
sudo dpkg -i metricbeat-7.13.2-amd64.deb
sudo metricbeat modules enable logstash
sudo metricbeat setup
sudo service metricbeat start

# Installing and configuring Heartbeat
curl -L -O https://artifacts.elastic.co/downloads/beats/heartbeat/heartbeat-7.13.2-amd64.deb
sudo dpkg -i heartbeat-7.13.2-amd64.deb
sudo cp /beats_elk/heartbeat.yml /etc/heartbeat/
heartbeat setup -e
sudo service heartbeat-elastic start

# Retrieving docker images
cd /docker
sudo docker-compose up
sudo systemctl enable docker.service
sudo systemctl enable containerd.service
