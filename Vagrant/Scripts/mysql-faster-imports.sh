#!/usr/bin/env bash

# USAGE:    mysqlOptimizeForImports <- before importing
#           mysqlDefaultSettings <- to go back to normal

# Based on https://dba.stackexchange.com/questions/83125/mysql-any-way-to-import-a-huge-32-gb-sql-dump-faster/83385#83385

mysqlStateFile="/prueba/mysql.optimized.for.exports"
mysqlConfigLocation="/etc/mysql/my.cnf" # <-- change to the correct for your system, should be for global mysql settings

function mysqlOptimizeForImports {
    echo 'Configuring Mysql for faster imports'
    
    __optimize && echo '1' >> "$mysqlStateFile"
}
function __optimize {
    if [ -f "$mysqlStateFile" ]; then
        __restore
    fi
    echo '[mysqld]' | sudo tee -a "$mysqlConfigLocation"                            # rows added 1
    echo 'innodb_buffer_pool_size = 2G' | sudo tee -a "$mysqlConfigLocation"        # rows added 2
    echo 'innodb_log_buffer_size = 256M' | sudo tee -a "$mysqlConfigLocation"       # rows added 3
    echo 'innodb_log_file_size = 1G' | sudo tee -a "$mysqlConfigLocation"           # rows added 4
    echo 'innodb_write_io_threads = 12' | sudo tee -a "$mysqlConfigLocation"        # rows added 5
    echo 'innodb_flush_log_at_trx_commit = 0' | sudo tee -a "$mysqlConfigLocation"  # rows added 6
    sudo service mysql restart --innodb-doublewrite=0

    echo
    echo 'Sanity checkout, should be 12 ==>'
    echo 
    mysql -uroot .proot -e "SHOW GLOBAL VARIABLES LIKE '%innodb_write_io_threads%'"
}
function __restore {
    sudo sed -i '$ d' "$mysqlConfigLocation"    # row removed 1
    sudo sed -i '$ d' "$mysqlConfigLocation"    # row removed 2
    sudo sed -i '$ d' "$mysqlConfigLocation"    # row removed 3
    sudo sed -i '$ d' "$mysqlConfigLocation"    # row removed 4
    sudo sed -i '$ d' "$mysqlConfigLocation"    # row removed 5
    sudo sed -i '$ d' "$mysqlConfigLocation"    # row removed 6
}

function mysqlDefaultSettings {
    if [ -f "$mysqlStateFile" ]; then
        echo "restoring settings"
        __restore

        rm -- "$mysqlStateFile"
    fi

    sudo service mysql restart

    echo
    echo 'Sanity checkout, should be 4 ==>'
    mysql -uroot -proot -e "SHOW GLOBAL VARIABLES LIKE '%innodb_write_io_threads%'"
}