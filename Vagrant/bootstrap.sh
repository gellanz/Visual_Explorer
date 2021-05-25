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


# Installing packages
apt-get install -y mysql-server mysql-client

# Allow External Connections on your MySQL Service
sudo sed -i -e 's/bind-addres/#bind-address/g' /etc/mysql/mysql.conf.d/mysqld.cnf
sudo sed -i -e 's/skip-external-locking/#skip-external-locking/g' /etc/mysql/mysql.conf.d/mysqld.cnf
mysql -u root -proot -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'root'; FLUSH privileges;"
sudo service mysql restart

echo -e "Si es la primera vez que se construirá la base de datos o si la máquina virtual
         se destruyó, se tienen que ejecutar los siguientes comandos: \n
         cd /scripts \n ./boot_db_first_time.sh"

cd /scripts
dos2unix boot_db_first_time.sh
dos2unix mysql-faster-imports.sh

