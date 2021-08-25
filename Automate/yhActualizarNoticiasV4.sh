#!/bin/bash

# Deben activarse las lineas que inician con doble gato ##

scheduledTime="15:05:" #En esta linea va la hora que se requiere
echo "This tool helps to execute a set of commands in a particular day time."
while :
do
   echo "The commands will be executed at ${scheduledTime} hours"
   echo "Pres CTRL+C to stop..."
   until [[ "$(date)" =~ ${scheduledTime} ]]; do
      sleep 30
   done
      echo "Commands execution initiated......"

      echo Actualización de noticias

      echo ""
      echo Inicia la descarga de noticias desde Internet
      cd /home/yadira/PycharmProjects/Thesis/src/NewsCrawler/
      python3 '/home/yadira/PycharmProjects/Thesis/src/NewsCrawler/MDSexampleSLV4.py'
      echo Se ejecuto la descarga de noticias desde Internet


      echo ""
      echo Actualizar variables de carga

      FECHA_HOY=`date +"%Y-%m-%d"`
      echo El valor de la variable FECHA_HOY es $FECHA_HOY

      SQL_STATEMENT="UPDATE SETTING_LOAD_DOC SET START_DATE = '$FECHA_HOY', END_DATE = '$FECHA_HOY' WHERE PROCESS_NAME = 'LOAD_NEWS';"
      echo El valor de la variable SQL_STATEMENT es $SQL_STATEMENT

      # Actualizar la fecha de carga
      # mysql -h localhost -u yadira3 -pcic document_analyzer -e "$SQL_STATEMENT"
      # credenciales para la bd dentro de la máquina virtual
      mysql -u root -proot document_analyzer -e "$SQL_STATEMENT"

      echo Se ejecuto la actualizacion de la fecha de carga

      # Actualizar las entidades nombradas
      echo ""
      echo Inicia la actualización de Entidades Nombradas
      # cd /home/yadira/PycharmProjects/Thesis/src/NewsCrawler/
      cd /automate/data_DBpedia
      # python3 '/home/yadira/PycharmProjects/Thesis/src/NewsCrawler/getEntitiesFromDBpediaV2.py'
      python3 getEntitiesFromDBpediaV2.py
      echo Se ejecuto la actualización de Entidades Nombradas

      # Cargar las noticias de stage a las tablas CORE, Doc: “ETL ST_DA_DOCUMENT_NEWS”
      echo ""
      echo Inicia “ETL ST_DA_DOCUMENT_NEWS”
      # cd /home/yadira/Documents/Automatizar/ST_DA_DOCUMENT_NEWS_V3/
      cd /automate/stage_to_core
      ./ST_DA_DOCUMENT_NEWS_V3_run.sh
      echo Se ejecuto “ETL ST_DA_DOCUMENT_NEWS”

      # Generar vectores y cargarlos en DOCUMENT_VSM
      echo ""
      echo Inicia la generación de vectores
      # cd /home/yadira/PycharmProjects/Thesis/src/
      cd /automate/freeling 
      # python3 '/home/yadira/PycharmProjects/Thesis/src/newsAnalysisV4.py'
      python3 newsAnalysisV4.py
      echo Se ejecuto la generación de vectores

      # Homologar sinónimos
      echo ""
      echo Inicia la homologación de sinónimos
      SQL_HOMOLOGAR="UPDATE document_analyzer.DOCUMENT_VSM_2020A INNER JOIN document_analyzer.SYNONYM ON DOCUMENT_VSM_2020A.CHARACTERISTIC = SYNONYM.SYNONYM SET DOCUMENT_VSM_2020A.SIMPLE_CHARACTERISTIC = SYNONYM.WORD WHERE SYNONYM.ACTIVE = 1 ;" 
      echo El valor de la variable SQL_HOMOLOGAR es $SQL_HOMOLOGAR
      # mysql -h localhost -u yadira3 -pcic document_analyzer -e "$SQL_HOMOLOGAR"
      # credenciales para la bd dentro de la máquina virtual
      mysql -u root -proot document_analyzer -e "$SQL_HOMOLOGAR"
      echo Se ejecuto la homologación de sinónimos
     
      # Indexar las noticias
      echo ""
      cd /automate/elasticsearch/index_news
      echo Inicia la indexación de noticias
      python3 loadToElasticsearchv2.py
      echo Se ejecuto la indexación de noticias

      # Indexar las Entidades Nombradas 
      echo ""
      echo Inicia la indexación de Entidades Nombradas
      SQL_UPD_INT_IDS="UPDATE INFO_TRACING SET ORIGINAL_ID_INT = CAST(ORIGINAL_ID AS UNSIGNED) ;"
      echo El valor de la variable SQL_UPD_INT_IDS es $SQL_UPD_INT_IDS
      # mysql -h localhost -u yadira3 -pcic document_analyzer -e "$SQL_UPD_INT_IDS"
      # credenciales para la bd dentro de la máquina virtual
      mysql -u root -proot document_analyzer -e "$SQL_UPD_INT_IDS"
      # python3 '/home/yadira/PycharmProjects/Thesis/src/entityLoadToElasticsearch v2.py'
      cd /automate/elasticsearch/named_entities
      python3 entityLoadToElasticsearchv2.py
      echo Se ejecuto la indexación de Entidades Nombradas

      # Cargar la categoría MLP
      echo ""
      echo Inicia la carga de la categoría MLP
      # python3 '/home/yadira/PycharmProjects/Thesis/src/ClasificarNoticias/LoadCategoriaMLPElasticsearchV3.py'
      cd /automate/elasticsearch/mlp_category
      python3 LoadCategoriaMLPElasticsearchV3.py
      echo Se ejecuto la carga de la categoría MLP

      echo "All commands were executed."
      sleep 60
done



