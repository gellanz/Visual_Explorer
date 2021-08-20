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

# Binutils for deb package
sudo apt-get -y install binutils

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

#Installing freeling
cd /
wget https://github.com/TALP-UPC/FreeLing/releases/download/4.2/freeling-4.2-bionic-amd64.deb
sudo ar x freeling-4.2-bionic-amd64.deb
sudo tar xvf control.tar.xz
sudo tar xvf data.tar.xz
rm -i freeling-4.2-bionic-amd64.deb xvf control.tar.xz data.tar.xz
cd

# Compilarlo, hacer carpeta build, poner los compilados, compilar la API de Python

# Installing Docker 
sudo apt-get install -y docker.io
sudo apt-get install -y docker-compose
export DOCKER_CLIENT_TIMEOUT=120
export COMPOSE_HTTP_TIMEOUT=120
grep vm.max_map_count /etc/sysctl.conf
sudo sysctl -w vm.max_map_count=262144

# Retrieving docker images
sudo cp /beats_elk/metricbeat.yml /usr/share/metricbeat
sudo cp /beats_elk/heartbeat.yml /usr/share/heartbeat
cd /docker
sudo docker-compose up
sudo systemctl enable docker.service
sudo systemctl enable containerd.service

