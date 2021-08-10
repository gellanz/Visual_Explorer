from elasticsearch import Elasticsearch
import MySQLdb
import pandas as pd

daConexion = MySQLdb.connect(host="localhost",
                             user="yadira",
                             passwd="cic",
                             db="document_analyzer")


cursor = daConexion.cursor()

getEntities = "SELECT DISTINCT IT.TARGET_ID ID_DOCUMENT, \
                       ENTITIES_RECOGNIZED ENTITIES, \
                       ST.TITULO TITULO, \
                       ST.FECHA FECHA, \
                       ST.TEXTO TEXTO \
                FROM ST_NEWSCRAWLERSN AS ST  \
                INNER JOIN INFO_TRACING AS IT  \
                    ON IT.ORIGINAL_ID_INT = ST.ID_ST_NEWSCRAWLERSN \
                WHERE ST.Fecha >= (SELECT DATE(MIN(START_DATE)) FROM document_analyzer.SETTING_LOAD_DOC WHERE PROCESS_NAME = 'LOAD_NEWS') AND \
					  ST.Fecha <= (SELECT DATE(MAX(END_DATE)) FROM document_analyzer.SETTING_LOAD_DOC WHERE PROCESS_NAME = 'LOAD_NEWS') \
                ; "


try:
    cursor.execute(getEntities)

except MySQLdb.Error as error:
    print("Error: {}".format(error))

daConexion.close()
document = {}

listPrevDocument = []
with open('/home/yadira/PycharmProjects/Thesis/src/load_entities.txt', 'r') as prevDocument:
    listPrevDocument = [linea.strip() for linea in prevDocument]

#print("Documentos cargados anteriormente:")
#print(listPrevDocument)

loadDocument = open("load_entities.txt", "a")

#es = Elasticsearch()


print("Imprime los elementos del cursor")
for element in cursor:
    print(element)

iter = 1

#id_index = 568460

print("Inicia For de carga")
for element in cursor:
    print("Iteración número: ", iter)
    print("Doc a procesar: ", element[0])

    dup = 0
    for prevDoc in listPrevDocument :
        if int(element[0]) == int(prevDoc):
            dup = 1
        #print("dup: ", dup, ",  element[0]: ", element[0], ",  prevDoc:", prevDoc)

    print("Iniciando carga a Elasticsearch")
    #print("dup: ", dup)

    if dup == 0:

        es = Elasticsearch()

        #print(document)
        print("")

        splitEntity = element[1].split("||")

        subID = 1
        for e in splitEntity:
            Entity = e.split(",")

            print("Entity:")
            print(Entity)

            document["idDocEntity"] = int(str(element[0]) + str("00") + str(subID))  #id_index

            print("element[0]:", element[0], "  subID:", subID, "    idDocEntity:", document["idDocEntity"])

            document["idDocument"] = int(element[0])
            document["entity"] = Entity[0]
            document["entityKW"] = Entity[0]
            if len(Entity) < 2 :
                document["catEntity"] = 'NO_ESPECIFICADO'
                document["catEntityKW"] = 'NO_ESPECIFICADO'
            else :
                document["catEntity"] = Entity[1]
                document["catEntityKW"] = Entity[1]
            document["dataSource"] = "DBpedia"


            document["titleFD"] = element[2]
            document["contentFD"] = element[4]
            document["publicationDate"] = element[3]

            subID = subID + 1
            print(document)

            es = Elasticsearch()
            res = es.index(index="named_entities", doc_type='entity', id=document["idDocEntity"], body=document)
            print("result: ", res['result'])

            es.indices.refresh(index="named_entities")

            document.clear()
            #id_index = id_index + 1

    loadDocument.write(str(element[0]))
    loadDocument.write("\n")

    iter = iter + 1

print("Finaliza ciclo for")

loadDocument.close()


# inicia 13:40 p.m.