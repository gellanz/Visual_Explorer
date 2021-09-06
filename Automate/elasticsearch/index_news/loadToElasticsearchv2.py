from datetime import datetime
from elasticsearch import Elasticsearch
import MySQLdb
import pandas as pd



daConexion = MySQLdb.connect(host="localhost",
                             port=2200,
                             user="root",
                             passwd="root",
                             db="document_analyzer")

cursor = daConexion.cursor()

#getDocContent = "SELECT DOC.ID_DOCUMENT, MIN(DOC.SOURCE_NAME) AS SOURCE_NAME, MIN(DOC.PUBLICATION_DATE) AS PUBLICATION_DATE, MIN(DOC.TITLE) AS TITLE, MIN(DOC.CONTENT) ORIGINAL_CONTENT, MIN(DOC.CATEGORY) CATEGORY, GROUP_CONCAT(DISTINCT (CASE WHEN VSM.SIMPLE_CHARACTERISTIC IS NOT NULL THEN VSM.SIMPLE_CHARACTERISTIC ELSE VSM.CHARACTERISTIC END) SEPARATOR ' ') AS CONTENT FROM DOCUMENT AS DOC INNER JOIN DOCUMENT_VSM_2018A AS VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT GROUP BY DOC.ID_DOCUMENT;"

#2016
#getDocContent = "SELECT DOC.ID_DOCUMENT, MIN(DOC.SOURCE_NAME) AS SOURCE_NAME, MIN(DOC.PUBLICATION_DATE) AS PUBLICATION_DATE, MIN(DOC.TITLE) AS TITLE, MIN(DOC.CONTENT) ORIGINAL_CONTENT, MIN(DOC.CATEGORY) CATEGORY, GROUP_CONCAT(DISTINCT (CASE WHEN VSM.SIMPLE_CHARACTERISTIC IS NOT NULL THEN VSM.SIMPLE_CHARACTERISTIC ELSE VSM.CHARACTERISTIC END) SEPARATOR ' ') AS CONTENT FROM DOCUMENT AS DOC INNER JOIN DOCUMENT_VSM_2016 AS VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT GROUP BY DOC.ID_DOCUMENT;"

#2017 A
#getDocContent = "SELECT DOC.ID_DOCUMENT, MIN(DOC.SOURCE_NAME) AS SOURCE_NAME, MIN(DOC.PUBLICATION_DATE) AS PUBLICATION_DATE, MIN(DOC.TITLE) AS TITLE, MIN(DOC.CONTENT) ORIGINAL_CONTENT, MIN(DOC.CATEGORY) CATEGORY, GROUP_CONCAT(DISTINCT (CASE WHEN VSM.SIMPLE_CHARACTERISTIC IS NOT NULL THEN VSM.SIMPLE_CHARACTERISTIC ELSE VSM.CHARACTERISTIC END) SEPARATOR ' ') AS CONTENT FROM DOCUMENT AS DOC INNER JOIN DOCUMENT_VSM_2017A AS VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT GROUP BY DOC.ID_DOCUMENT;"

#2017 B
#getDocContent = "SELECT DOC.ID_DOCUMENT, MIN(DOC.SOURCE_NAME) AS SOURCE_NAME, MIN(DOC.PUBLICATION_DATE) AS PUBLICATION_DATE, MIN(DOC.TITLE) AS TITLE, MIN(DOC.CONTENT) ORIGINAL_CONTENT, MIN(DOC.CATEGORY) CATEGORY, GROUP_CONCAT(DISTINCT (CASE WHEN VSM.SIMPLE_CHARACTERISTIC IS NOT NULL THEN VSM.SIMPLE_CHARACTERISTIC ELSE VSM.CHARACTERISTIC END) SEPARATOR ' ') AS CONTENT FROM DOCUMENT AS DOC INNER JOIN DOCUMENT_VSM_2017C AS VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT GROUP BY DOC.ID_DOCUMENT;"

#2019 C
#getDocContent = "SELECT DOC.ID_DOCUMENT, MIN(DOC.SOURCE_NAME) AS SOURCE_NAME, MIN(DOC.PUBLICATION_DATE) AS PUBLICATION_DATE, MIN(DOC.TITLE) AS TITLE, MIN(DOC.CONTENT) ORIGINAL_CONTENT, MIN(DOC.CATEGORY) CATEGORY, GROUP_CONCAT(DISTINCT (CASE WHEN VSM.SIMPLE_CHARACTERISTIC IS NOT NULL THEN VSM.SIMPLE_CHARACTERISTIC ELSE VSM.CHARACTERISTIC END) SEPARATOR ' ') AS CONTENT, MIN(DOCUMENT_URL) DOCUMENT_URL, MIN(IMAGE_URL) IMAGE_URL,  MIN(SUMMARY) SUMMARY FROM DOCUMENT AS DOC INNER JOIN DOCUMENT_VSM_2019C AS VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT WHERE DATE(DOC.PUBLICATION_DATE) >= DATE('2019-09-01') AND DATE(DOC.PUBLICATION_DATE) <= DATE('2019-11-19') GROUP BY DOC.ID_DOCUMENT;"

#2019 C
#getDocContent = "SELECT DOC.ID_DOCUMENT, MIN(DOC.SOURCE_NAME) AS SOURCE_NAME, MIN(DOC.PUBLICATION_DATE) AS PUBLICATION_DATE, MIN(DOC.TITLE) AS TITLE, MIN(DOC.CONTENT) ORIGINAL_CONTENT, MIN(DOC.CATEGORY) CATEGORY, GROUP_CONCAT(DISTINCT (CASE WHEN VSM.SIMPLE_CHARACTERISTIC IS NOT NULL THEN VSM.SIMPLE_CHARACTERISTIC ELSE VSM.CHARACTERISTIC END) SEPARATOR ' ') AS CONTENT, MIN(DOCUMENT_URL) DOCUMENT_URL, MIN(IMAGE_URL) IMAGE_URL,  MIN(SUMMARY) SUMMARY FROM DOCUMENT AS DOC INNER JOIN DOCUMENT_VSM_2020A AS VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT WHERE DATE(DOC.PUBLICATION_DATE) >= DATE('2020-01-01') AND DATE(DOC.PUBLICATION_DATE) <= DATE('2020-02-04') GROUP BY DOC.ID_DOCUMENT;"

# Carga automatica
getDocContent = "SELECT DOC.ID_DOCUMENT, MIN(DOC.SOURCE_NAME) AS SOURCE_NAME, MIN(DOC.PUBLICATION_DATE) AS PUBLICATION_DATE, MIN(DOC.TITLE) AS TITLE, MIN(DOC.CONTENT) ORIGINAL_CONTENT, MIN(DOC.CATEGORY) CATEGORY, GROUP_CONCAT(DISTINCT (CASE WHEN VSM.SIMPLE_CHARACTERISTIC IS NOT NULL THEN VSM.SIMPLE_CHARACTERISTIC ELSE VSM.CHARACTERISTIC END) SEPARATOR ' ') AS CONTENT, MIN(DOCUMENT_URL) DOCUMENT_URL, MIN(IMAGE_URL) IMAGE_URL,  MIN(SUMMARY) SUMMARY FROM DOCUMENT AS DOC INNER JOIN DOCUMENT_VSM_2020A AS VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT WHERE DATE(DOC.PUBLICATION_DATE) >= (SELECT DATE(MIN(START_DATE)) FROM document_analyzer.SETTING_LOAD_DOC WHERE PROCESS_NAME = 'LOAD_NEWS') AND DATE(DOC.PUBLICATION_DATE) <= (SELECT DATE(MAX(END_DATE)) FROM document_analyzer.SETTING_LOAD_DOC WHERE PROCESS_NAME = 'LOAD_NEWS') GROUP BY DOC.ID_DOCUMENT;"



try:
    cursor.execute(getDocContent)

except MySQLdb.Error as error:
    print("Error: {}".format(error))

daConexion.close()
document = {}

prevDocument = pd.read_csv("load_document.txt", header=None, names=["idDocument"])
print("prevDocument: ", prevDocument)

loadDocument = open("load_document.txt", "a")

#es = Elasticsearch()

iter = 1

for element in cursor:
    print("Iteración número: ", iter)
    print("Doc a procesar: ", element[0])
    if element[0] not in prevDocument:
        es = Elasticsearch('localhost:9200', timeout=300)

        print(document)
        print("")

        #print("ID_DOCUMENT: ", element[0])
        #print("SOURCE_NAME: ", element[1])
        #print("publicationDate: ", element[2])
        #print("title: ", element[3])
        #print("originalContent: ", element[4])
        #print("category: ", element[5])
        #print("content: ", element[6])

        document["idDocument"] = element[0]
        document["sourceName"] = element[1]
        document["sourceNameKW"] = element[1]
        document["publicationDate"] = element[2]
        document["title"] = element[3]
        document["titleTest"] = element[3]
        document["titleTrigram"] = element[3]
        document["originalContent"] = element[4]
        document["category"] = element[5]
        document["categoryKW"] = element[5]
        document["content"] = element[6]
        document["contentFD"] = element[6]
        document["contentWsTk"] = element[6]
        document["documentURL"] = element[7]
        document["imageURL"] = element[8]
        document["summary"] = element[9]
        print(document)

        res = es.index(index="document_analyzer", doc_type='new', id=element[0], body=document)
        print("result: ", res['result'])

        #res = es.get(index="document_analyzer", doc_type='new', id=element[0])
        #print("source: ", res['_source'])

        es.indices.refresh(index="document_analyzer")

        loadDocument.write(str(element[0]))
        loadDocument.write("\n")
        document.clear()

        iter = iter + 1


loadDocument.close()



"""

doc = {
    'author': 'kimchy',
    'text': 'Elasticsearch: cool. bonsai cool.',
    'timestamp': datetime.now(),
}
res = es.index(index="news-index", doc_type='news', id=1, body=doc)
print("result: ", res['result'])

res = es.get(index="test-index", doc_type='tweet', id=1)
print("source: ", res['_source'])

es.indices.refresh(index="test-index")

res = es.search(index="test-index", body={"query": {"match_all": {}}})

print("Got %d Hits:" % res['hits']['total'])
for hit in res['hits']['hits']:
    print("%(timestamp)s %(author)s: %(text)s" % hit["_source"])

"""


