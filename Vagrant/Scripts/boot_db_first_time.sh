#!/usr/bin/env bash
cd
cd /prueba
source mysql-faster-imports.sh
mysqlOptimizeForImports
mysql -uroot -proot -e "CREATE DATABASE IF NOT EXISTS document_analyzer"
for file in *.sql; do
mysql -u root -proot document_analyzer < $file
done
mysqlDefaultSettings
