#!/bin/sh
cd `dirname $0`
ROOT_PATH=`pwd`
java -Xms1024M -Xmx4096M -cp .:$ROOT_PATH:$ROOT_PATH/../lib/routines.jar:$ROOT_PATH/../lib/commons-collections-3.2.jar:$ROOT_PATH/../lib/log4j-1.2.15.jar:$ROOT_PATH/../lib/log4j-1.2.16.jar:$ROOT_PATH/../lib/dom4j-1.6.1.jar:$ROOT_PATH/../lib/trove.jar:$ROOT_PATH/../lib/mysql-connector-java-5.1.30-bin.jar:$ROOT_PATH/../lib/advancedPersistentLookupLib-1.0.jar:$ROOT_PATH/../lib/jboss-serialization.jar:$ROOT_PATH/st_da_document_news_v3_0_1.jar: document_analysis.st_da_document_news_v3_0_1.ST_DA_DOCUMENT_NEWS_V3 --context=Default "$@" 