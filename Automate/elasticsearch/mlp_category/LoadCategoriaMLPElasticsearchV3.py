from joblib import dump, load
import MySQLdb

clf_reload = load('modelo_MLP_600_9cat.joblib')

from elasticsearch import Elasticsearch
import pandas as pd

i = 1
#for idDocument in range(247000, 248000, 1): # inicio 13:02, fin: 13:43 10.7 RAM, No usa mucha RAM
#for idDocument in range(248001, 250000, 1):  # inicio 13:45, fin:15:29 aprox  10.7 RAM,No usa mucha RAM
#for idDocument in range(250001, 254000, 1):  # inicio 15:30, fin: 18:15  10.7 RAM, No usa mucha RAM
#for idDocument in range(1, 100000, 1):  # inicio 20 sep 18:22, fin:   10.7 RAM,
#for idDocument in range(100000, 150001, 1):  # inicio 20 sep 18:22, fin:   10.7 RAM,
#for idDocument in range(150001, 269560, 1):  # inicio 25 sep 12:45, fin:   11.4 RAM,
#for idDocument in range(269560, 282164, 1):  # inicio 27 nov 16:31, fin:   12.2 RAM,
#for idDocument in range(282165, 283979, 1):  # inicio 03 dic 16:38, fin:   12.6 RAM,
#for idDocument in range(283975, 300000, 1):  # (inicio 11:50 a.m.  termina por error de timeout)
#for idDocument in range(291005, 300000, 1):  # (inicio 4:18 p.m. terminamos el proceso para agregar el último ID real)


# Recuperar los Ids de los documentos que se desean actualizar
# 294190

daConexion = MySQLdb.connect(host="localhost",
                             port=2200,
                             user="root",
                             passwd="root",
                             db="document_analyzer")

cursor = daConexion.cursor()

getIdDocument = "SELECT MIN(ID_DOCUMENT) MIN_ID_DOCUMENT, MAX(ID_DOCUMENT) MAX_ID_DOCUMENT FROM DOCUMENT WHERE DATE(PUBLICATION_DATE) >=  (SELECT DATE(MIN(START_DATE)) FROM document_analyzer.SETTING_LOAD_DOC WHERE PROCESS_NAME = 'LOAD_NEWS') AND DATE(PUBLICATION_DATE) >= (SELECT DATE(MAX(END_DATE)) FROM document_analyzer.SETTING_LOAD_DOC WHERE PROCESS_NAME = 'LOAD_NEWS'); "

try:
    cursor.execute(getIdDocument)

except MySQLdb.Error as error:
    print("Error: {}".format(error))

daConexion.close()

for element in cursor:
    print("min_id_document: ", element[0])
    print("max_id_document: ", element[1])

    min_id_document = element[0]
    max_id_document = element[1]


url = "/home/yadira/PycharmProjects/Thesis/src/ClasificarNoticias/te_600_9Cat_df_term_doc.csv"
# header = X_test.head(1)
header = pd.read_csv(url, header=0, nrows=1)
# print("header")
# print(header.head(20))



#for idDocument in range(291599, 294064, 1):
for idDocument in range(min_id_document, max_id_document, 1):
    print("Iteración número: ", i)

    es = Elasticsearch('148.204.66.69')
    document = es.search(index="document_analyzer", body={"query": {"term": {"idDocument": idDocument}}})

    # pprint.pprint(document)
    # for hit in document['hits']['hits']:
    #    print("idDocument: %(idDocument)s  \t category: %(category)s \n content: %(content)s \n" % hit["_source"])


    # print( "idDocument: %(idDocument)s " % hit["_source"])

    documentDF = pd.DataFrame()
    documentDF = documentDF.append(header, ignore_index=True)
    # print("documentDF.append(header, ignore_index = True)")
    # print(documentDF)

    documentDF = documentDF.drop([0], axis=0)

    # print("documentDF.drop([0],axis=0)")
    # print(documentDF)

    # print("document['hits']['hits']['_source']")
    # print(document['hits']['hits'][0]['_source'])

    # #####################################

    if len(document['hits']['hits']) > 0:
        sourceDict = document['hits']['hits'][0]['_source']
        # print("sourceDict")
        # print(sourceDict)

        # id_doc = [sourceDict.get("idDocument")]
        # cat = [sourceDict.get("category")]

        # print("id_doc: ", id_doc)
        # print("cat: ", cat)

        documentDF["ID_DOCUMENT"] = [sourceDict.get("idDocument")]
        documentDF["CATEGORY"] = [sourceDict.get("category")]

        # print("documentDF : ")
        # print(documentDF)
        # print(documentDF["ID_DOCUMENT"], documentDF["CATEGORY"])

        text = sourceDict.get("content")
        text = text.split(" ")

        for word in text:
            if len(word.replace("_", "")) > 1:
                if set([word]).issubset(documentDF.columns):
                    documentDF[word] = 1

                    # print("documentDF con el VSM")
        # print(documentDF.head(10))

        # ###########################################################################

        # print("\ndocumentDF")
        # documentDF.head(20)

        # print("documentDF = documentDF.fillna(0)")
        documentDF = documentDF.fillna(0)

        # print("documentDF = documentDF.fillna(0)  ")
        # print(documentDF)

        documentDF = documentDF.drop("ID_DOCUMENT", axis=1)
        documentDF = documentDF.drop("CATEGORY", axis=1)
        # documentDF.head(20)    #Entrada del predictor

        # print("documentDF drop id y cat")
        # print(documentDF.head(5))

        catMLP = clf_reload.predict(documentDF)
        catMLP = catMLP[0]

        print("idDocument: ", [sourceDict.get("idDocument")])
        print("category: ", [sourceDict.get("category")])
        print("catMLP: ", catMLP)

        # Actualizar los la categoría cálculada en el índice

        documentUP = {}
        # documentUP["idDocument"] = sourceDict.get("idDocument")
        # documentUP["categoryMLP"] = catMLP

        documentUP = {"doc": {"categoryMLP": catMLP}}

        es = Elasticsearch('148.204.66.69')

        # result = es.index(index='document_analyzer', doc_type='new', id=sourceDict.get("idDocument"), body=documentUP)
        result = es.update(index='document_analyzer', doc_type="new", id=sourceDict.get("idDocument"), body=documentUP)
        print("result: ", result['result'])

        es.indices.refresh(index='document_analyzer')

        documentUP.clear()

    else:
        print("El documento con id %s no se encuentra en el índice".format(idDocument))

    i = i + 1

#  /home/yadira/PycharmProjects/Thesis/src/ClasificarNoticias/LoadCategoriaMLPElasticsearch.py
