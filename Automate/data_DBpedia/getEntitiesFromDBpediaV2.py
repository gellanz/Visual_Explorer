#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
from bs4 import BeautifulSoup
#import urllib, json,collections
import urllib3, json,collections
from pyproj import Proj, transform
from geopy.geocoders import Nominatim
import time

def checkEntitiesIfExist(entity):
    import csv
    f = open('fileEntities.csv', 'rb')
    reader = csv.reader(f)
        #entitiesList = csv.reader(csvfile, delimiter='\n', quotechar=',')
    isThere=False
    for row in reader:
        if entity in row:
            isThere=True
            print (entity+" is here..")
            break
    f.close()
    return isThere
        #print (type(row),row)


#CONTAR ENTIDADES##########################
def contarEntidades(listaEntidades):

    listCounted=[]

    for tupla in listaEntidades:

        listCounted.append(str(tupla) + "||" + str(1))

    listCounted = '||'.join(listCounted)
    return  listCounted


def getLocationAndAddres(entity):
    import googlemaps

    gmaps = googlemaps.Client(key='AIzaSyCpTAIZUEvWBnbCqMNDE9n6-gEb8hyBczo')
    longitud = 0
    latitud = 0
    addres = ""
    # Geocoding an address
    try:
        entity = "Oaxaca"
        geocode_result = gmaps.geocode(entity)
        #print (geocode_result)
        if len(geocode_result) != 0:
            longitud = geocode_result[0]['geometry']['location']['lng']
            latitud =  geocode_result[0]['geometry']['location']['lat']
            addres = geocode_result[0]['formatted_address']
            data = [longitud,latitud,addres]
    except BaseException as e:
            print (e)

    data = [longitud, latitud, addres]
    print (data)
    return data

#getLocationAndAddres("entity")

def getEntities(text):
    url = "http://localhost:8660/rest/annotate?text="+text+"&confidence=0.5&support=20"

    #print (url)
    #response = urllib.urlopen(url.encode('utf8'))
    response = urllib3.urlopen(url)

    data= response.read()
    #print (data)

    y=BeautifulSoup(data)

    entities= y.html.body.findAll()

    print ("entities: ", len(entities), entities)
    inProj = Proj(init='epsg:4326')
    outProj = Proj(init='epsg:3857')

    Entidades=[]
    ligasEntidades=[]
    Coordenadas=[]

    for entity in entities:
        if "title" in entity.attrs:
            try:
                data = getLocationAndAddres(entity.text)
                x2, y2 = transform(inProj, outProj, data[0], data[1])
                nombre=entity.text
                Entidades.append(nombre)
                liga=entity["title"]
                ligasEntidades.append(liga)
                coor=str(x2)+","+str(y2)
                Coordenadas.append(coor)
            except BaseException as e:
                print (e)

    enti=contarEntidades(Entidades)
    ligas="||".join(ligasEntidades)
    corde="||".join(Coordenadas)

    data=[enti,ligas,corde]
    return data

import MySQLdb #import mysql.connector
bd = MySQLdb.connect(host="localhost", port=2200, user="root", passwd="root", db="document_analyzer")

def getEntitiesFromDB():

    cursor = bd.cursor()

    sql="SELECT idnew_table,Texto FROM newscrawlerSN WHERE idnew_table = 169249"
    cursor.execute(sql)
    data = cursor.fetchall()
    print ("getting entities from DB...", len(data))

    for row in data:
        try:
            #text="Ciudad de México.- El rector de la Universidad Nacional Autónoma de México (UNAM), Enrique Graue Wiechers, dio la bienvenida a 567 estudiantes extranjeros provenientes de 160 instituciones de educación superior de 32 países.A través de un mensaje transmitido en video, el académico explicó a los jóvenes que la universidad es autónoma porque se rige por sus anhelos y aspiraciones.Que también es nacional porque representa los intereses de la nación y, de alguna forma, anhela encontrar representado su cultura y ámbito académico.Graue Wiechers subrayó que la UNAM está entre las mejores 200 universidades del mundo y tiene la capacidad de recibir a cualquier alumno, sin importar de qué lugar provenga. “Disfruten de la universidad, aprendan de ella y conozcan a México”, dijo a los estudiantes extranjeros.Detalló que los nuevos alumnos realizarán una estancia académica en esta casa de estudios durante el semestre Primavera 2017, tanto en Ciudad Universitaria como en las facultades de Estudios Superiores (FES) y Escuelas Nacionales de Estudios Superiores (ENES) de varias entidades del país.Los jóvenes provienen de Australia, Alemania, Brasil, Canadá, Chile, China, Ecuador, Estados Unidos, España, Francia, Japón, Dinamarca, Reino Unido, República Checa y Rusia, entre otros.Durante la ceremonia de recibimiento realizada en el Auditorio Raoul Fournier de la Facultad de Medicina, los jóvenes escucharon un poco de esta institución e información de los servicios académicos, deportivos, culturales y de transporte a los que tendrán acceso."
            datos=getEntities(row[1])
            sql = "UPDATE newscrawlerSN SET Entities='" + str(datos[0]) + "',EntitiesRecognized='" + str(datos[1]) +"',Location='" + str(datos[2]) +"' WHERE idnew_table=" + str(row[0])
            cursor.execute(sql)
            bd.commit()
            bd.close()
            print (sql)
        except BaseException as e:

            print (e)


#text = "Ciudad de México.- El rector de la Universidad Nacional Autónoma de México (UNAM), Enrique Graue Wiechers, dio la bienvenida a 567 estudiantes extranjeros provenientes de 160 instituciones de educación superior de 32 países.A través de un mensaje transmitido en video, el académico explicó a los jóvenes que la universidad es autónoma porque se rige por sus anhelos y aspiraciones.Que también es nacional porque representa los intereses de la nación y, de alguna forma, anhela encontrar representado su cultura y ámbito académico.Graue Wiechers subrayó que la UNAM está entre las mejores 200 universidades del mundo y tiene la capacidad de recibir a cualquier alumno, sin importar de qué lugar provenga. “Disfruten de la universidad, aprendan de ella y conozcan a México”, dijo a los estudiantes extranjeros.Detalló que los nuevos alumnos realizarán una estancia académica en esta casa de estudios durante el semestre Primavera 2017, tanto en Ciudad Universitaria como en las facultades de Estudios Superiores (FES) y Escuelas Nacionales de Estudios Superiores (ENES) de varias entidades del país.Los jóvenes provienen de Australia, Alemania, Brasil, Canadá, Chile, China, Ecuador, Estados Unidos, España, Francia, Japón, Dinamarca, Reino Unido, República Checa y Rusia, entre otros.Durante la ceremonia de recibimiento realizada en el Auditorio Raoul Fournier de la Facultad de Medicina, los jóvenes escucharon un poco de esta institución e información de los servicios académicos, deportivos, culturales y de transporte a los que tendrán acceso."
text = "ven y conoce cozumel y prueba los mariscos"

#location = geolocator.geocode("Ciudad de México")

#print (location)
#getEntitiesFromDB()

def createFileText():
    cursor = bd.cursor()

    sql = "select idnew_table from newscrawlerSN"
    cursor.execute(sql)
    data = cursor.fetchall()
    text = open("idsNews.csv",'w')

    print (len(data))
    for i in data:
        text.write(str(i[0])+'\n')
    text.close()

#createFileText()
def createFileEntity():
    docEntities = open('data/jsonEntities.txt')
    entitiesList = docEntities.readlines()

    docEntitiesT = open('data/EntitiesType.txt','w')
    lsEn=[]
    for entity in entitiesList:
        ls = entity.split('||')
        if ls[0] not in lsEn:
            lsEn.append(ls[0])
            docEntitiesT.write(ls[0]+"||"+ls[1]+"\n")
    docEntitiesT.close() #

#createFileEntity()
#######################################################################

#Función que actualiza las entidades nombradas
def updatEntities():

    print("ejecutar updatEntities")

    cursor2 = bd.cursor()
    sql = "SELECT ID_ST_NEWSCRAWLERSN FROM ST_NEWSCRAWLERSN WHERE FECHA >= (SELECT MIN(START_DATE) FROM SETTING_LOAD_DOC WHERE PROCESS_NAME = 'LOAD_NEWS') AND FECHA <= (SELECT MIN(END_DATE) FROM SETTING_LOAD_DOC WHERE PROCESS_NAME = 'LOAD_NEWS') AND LENGTH(ENTITIES) < 2 "
    print("sql satement")
    print(sql)

    cursor2.execute(sql)

    for element in cursor2:
        print("Ids in cursor2: ", element)


    #ids = open("/home/yadira/PycharmProjects/Thesis/src/NewsCrawler/idsNews.csv", 'r')
    #idss = ids.readlines()
    docEntities = open('EntitiesType.txt','r')
    entitiesList = docEntities.readlines()
    docEntities.close()
    fileLocation = open('locations.txt', 'r')
    listLocation = fileLocation.readlines()
    listLocation2=[]
    for i in listLocation:
        listLocation2.append(i.rstrip('\n'))

    #print ("idss" , idss)

    #for id in idss:
    for id in cursor2 :
     if int(id[0]) > 841250:
        cursor = bd.cursor()
        print("cursor: ", cursor)
        #sql = "SELECT Texto FROM newscrawlerSN WHERE idnew_table = "+id.rstrip('\n')
        sql = "SELECT Texto FROM ST_NEWSCRAWLERSN WHERE ID_ST_NEWSCRAWLERSN = " + str(id[0])
        cursor.execute(sql)
        data = cursor.fetchall()
        texto = data[0][0]
        locations=[]
        entitiesInText=[]
        entitiesRecognized=[]
        locs=""
        #print (id[0].rstrip('\n'))
        print(id[0])
        for entity in entitiesList:
            enti = entity.split('||')

            nameEntity = enti[0].replace('_',' ')
            if nameEntity in texto:
                entitiesInText.append(nameEntity)
                entitiesRecognized.append(enti[0]+","+enti[1].rstrip('\n'))
                tipo = enti[1].rstrip('\n')
                #if tipo in listLocation2:

                    #si entra en esta condicion entoces quiere decir que tiene location
                    #datosLoc = getLocationAndAddres(nameEntity)
                    #locations.append(str(datosLoc[0])+","+str(datosLoc[1]))
                #else:
                    #datosLoc = []

        strEntitiesCounted = contarEntidades(entitiesInText)
        locs = '||'.join(locations)
        entiRecog = '||'.join(entitiesRecognized)
        #sql = "UPDATE newscrawlerSN SET Entities='" + strEntitiesCounted + "',EntitiesRecognized='" + entiRecog + "',Location='" + locs + "' WHERE idnew_table=" + id
        sql = "UPDATE ST_NEWSCRAWLERSN SET Entities='" + strEntitiesCounted + "',Entities_Recognized='" + entiRecog + "',Location='" + locs + "' WHERE ID_ST_NEWSCRAWLERSN=" + str(id[0])
        print(sql)
        cursor.execute(sql)
        bd.commit()
        print ("updating entities id", id[0])

print ("updating entities starting")
updatEntities()
print ("updating entities")



print ("updating locations")


geolocator = Nominatim()
def updatLocations():

    ids = open("idsNews.csv", 'r')
    idss = ids.readlines()
    fileLocation = open('data/locations.txt', 'r')
    listLocation = fileLocation.readlines()
    listLocation2=[]
    for i in listLocation:
        listLocation2.append(i.rstrip('\n'))
    for id in idss:
        if int(id) > 603177:
            cursor = bd.cursor()
            sql = "SELECT EntitiesRecognized FROM newscrawlerSN WHERE idnew_table = "+id.rstrip('\n')
            cursor.execute(sql)
            data = cursor.fetchall()
            texto = data[0][0]
            entidTipos = texto.split('||')
            locations = []
            if len(entidTipos) > 0:
                for entidTipo in entidTipos:
                    enTip = entidTipo.split(',')
                    if len(enTip) > 1:
                        if enTip[1] in listLocation2:
                            entity = enTip[0].replace('_',' ')
                            try:
                                location = geolocator.geocode(entity)
                                lat = location.latitude
                                lon = location.longitude
                                inProj = Proj(init='epsg:4326')
                                outProj = Proj(init='epsg:3857')
                                x2, y2 = transform(inProj, outProj, lon, lat)
                                coor = str(x2) + "," + str(y2)
                                 #print (coor)
                                #print (location)
                                locations.append(coor)
                                time.sleep(1)
                                break
                            except BaseException as e:
                                print (e)

                locs = '||'.join(locations)
                sql = "UPDATE newscrawlerSN SET Location='" + locs + "' WHERE idnew_table=" + id
                cursor.execute(sql)
            bd.commit()


            print (id.rstrip('\n'))


#updatLocations()


def probarLibreriaLocation():
    print ("")
    entity = "México"
    location = geolocator.geocode(entity)
    lat = location.latitude
    lon = location.longitude

#probarLibreriaLocation()

























