#!/usr/bin/env bash
source mysql-faster-imports.sh
mysqlOptimizeForImports
source /scripts/stop_ELK.sh
cd 
cd /sql
mysql -uroot -proot -e "CREATE DATABASE IF NOT EXISTS document_analyzer"
for file in *.sql; do
    echo "exporting $file"
    mysql -u root -proot document_analyzer < $file
done
mysqlDefaultSettings
source /scripts/start_ELK.sh
