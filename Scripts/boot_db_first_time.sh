#!/usr/bin/env bash
source mysql-faster-imports.sh
mysqlOptimizeForImports
cd 
cd /sql
mysql -uroot -proot -e "CREATE DATABASE IF NOT EXISTS document_analyzer"
for file in *.sql; do
mysql -u root -proot document_analyzer < $file
done
mysqlDefaultSettings
