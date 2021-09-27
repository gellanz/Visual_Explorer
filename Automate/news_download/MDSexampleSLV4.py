#!/usr/bin/env python
# -*- coding: utf-8 -*-
#import numpy as np
import MySQLdb #import mysql.connector
#from scipy.spatial import distance
#import matplotlib.pyplot as plt
#from sklearn import manifold

from nltk import word_tokenize
import re, urllib,urllib3,sys  #cambio urllib2 por urllib3
import collections
import time
import feedparser
import hashlib
import sys
#reload(sys)  # se comento esta linea
#sys.setdefaultencoding('utf-8') # se comento esta linea

from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

#recibe texto en forma de cadena y retorna las entidades
def get_continuous_chunks(text):
    listTokens = word_tokenize(text)

    chunked = ne_chunk(pos_tag(listTokens))
    #print chunked
    prev = None
    continuous_chunk = []
    current_chunk = []
    for i in chunked:
            if type(i) == Tree:

                    current_chunk.append(" ".join([token for token, pos in i.leaves()]))
            elif current_chunk:

                    named_entity = " ".join(current_chunk)
                    if named_entity not in continuous_chunk:
                            continuous_chunk.append(named_entity)
                            current_chunk = []
            else:
                    continue
    return continuous_chunk


def quitarStopWords(tokensList):

    archivo = open('stopWords.csv', 'r')
    stopwords = archivo.readlines()
    stopwordList=[]
    #print("stopwordList: ")
    #print(stopwordList)
    for stopword in stopwords:
        word=stopword.rstrip('\n')
        word=word.rstrip('\r')
        stopwordList.append(word)

    tokensLi=[]

    for word in tokensList:
        if not word in stopwordList:
            tokensLi.append(word)

    return tokensLi

def quitarCaracteres(cadena):

    textoLimpio=cadena.replace('\r',"")
    textoLimpio=textoLimpio.replace('\n',"")
    textoLimpio = textoLimpio.replace('u201d', "")
    textoLimpio = textoLimpio.replace('u201c', "")
    textoLimpio = textoLimpio.replace('u00bf', "¿")
    textoLimpio = textoLimpio.replace('u00f3', "ó")
    textoLimpio = textoLimpio.replace('u00fa', "ú")
    textoLimpio = textoLimpio.replace('u00e9', "é")
    textoLimpio = textoLimpio.replace('u00e1', "á")
    textoLimpio = textoLimpio.replace('u00ed', "í")
    textoLimpio = textoLimpio.replace('u00f1',"ñ")
    textoLimpio = textoLimpio.replace('&aacute;', "á")
    textoLimpio = textoLimpio.replace('&ntilde;', "ñ")
    textoLimpio = textoLimpio.replace('&oacute;', "ó")
    textoLimpio = textoLimpio.replace('&iacute;', "í")
    textoLimpio = textoLimpio.replace('&eacute;', "é")
    textoLimpio = textoLimpio.replace('&uacute;',"ú")
    textoLimpio = textoLimpio.replace('&Uacute;', "Ú")
    textoLimpio = textoLimpio.replace('&Aacute;',"Á")
    textoLimpio = textoLimpio.replace('&Oacute;', "Ó")
    textoLimpio = textoLimpio.replace('&Iacute;', "Í")
    textoLimpio = textoLimpio.replace('&Eacute;', "É")
    textoLimpio = textoLimpio.replace('&iexcl;', "¡")
    textoLimpio = textoLimpio.replace('&quot;', "")
    textoLimpio = textoLimpio.replace('&ldquo;', "")
    textoLimpio = textoLimpio.replace('&rdquo;', "")
    textoLimpio = textoLimpio.replace('&ldquo;', "")
    textoLimpio = textoLimpio.replace('&nbsp;', "")
    textoLimpio = textoLimpio.replace('&uuml;', "ü")

    return textoLimpio

def CargarDiccionarioLemas():
    file=open("diccionarioLematizador.txt","rb")
    lema_d={}

    for line in file:
        #print(line)
        bloques=line.split()
        a=bloques[0]
        b=bloques[1]
        #print("i",a,b)
        #print( bloques[0],bloques[1])
        lema_d.update({a:b})
    return lema_d

lema_d=CargarDiccionarioLemas()

def lematizador(lema_d,palabra):
    palabra=palabra.lower()
    if palabra in lema_d:
        lema=str(lema_d.get(palabra))
    else:
        lema=palabra
    return lema

def lematizerList(listSinStop):
    listWordsLematized=[]
    for palabra in listSinStop:
        listWordsLematized.append(lematizador(lema_d,palabra))

    return listWordsLematized



def computeMD5hash(string):
    m = hashlib.md5()
    m.update(string.encode('utf-8'))
    return m.hexdigest()

try:
    import urllib.request
except:
    pass

def MDStwoDimentions(matrizDocumentosNxM):
    File = open('matrizCuadrada.csv', 'w')
    VSMsquareCol = []
    for VSM1 in matrizDocumentosNxM:
        VSMsquareRow = []
        for  VSM12 in matrizDocumentosNxM:
             dist = distance.euclidean(VSM1, VSM12)
             File.write(str(dist)+",")
             VSMsquareRow.append(dist)
        File.write("\n")
        VSMsquareCol.append(VSMsquareRow)
    File.close()
    print (len(VSMsquareCol),len(VSMsquareCol[0]))

    dists = VSMsquareCol
    adist = np.array(dists)
    amax = np.amax(adist)
    adist /= amax

    mds = manifold.MDS(n_components=2, dissimilarity="precomputed", random_state=6)
    results = mds.fit(adist)
    coords = results.embedding_
    print (coords)
    return coords


def crearMatrizCuadrada(nombre,indicesOrdenados):

    bd = MySQLdb.connect("127.0.0.1", "root", "1234", "visualizadordenoticias")
    # Crear Tabla
    cursor = bd.cursor()
    print  (len(indicesOrdenados))
    sql = "SELECT * FROM " + nombre + "booleana where "
    i=0
    while i < len(indicesOrdenados):

        if i == len(indicesOrdenados) - 1:
            sql += "idNews = " + str(indicesOrdenados[i]) + ";"
            #vectoresDBase.append(indicesOrdenados[i])
        else:
            sql += "idNews = " + str(indicesOrdenados[i]) + " or "
            #vectoresDBase.append(indicesOrdenados[i])
        i = i + 1
    # print sql
    print ("sql was created")
    print (sql)
    # Ejecutamos el comando
    cursor.execute(sql)
    # Obtenemos todos los registros en una lista de listas
    vectores = cursor.fetchall()

    print (len(vectores))

    VSM1s=[]
    idNews=[]
    print ("cargando los vectores...")
    print (vectores[0][0])
    for vector in vectores:
        idNews.append(vector[0])
        list=vector[1].split(',')
        VSM = []
        for dimension in list:
            if dimension != '':
                #print type(int(dimension)),dimension
                VSM.append(float(dimension))
        VSM1s.append(VSM)

    # aqui se debe de crear un amatriz cuadrada, es decir , calcular la disancia entre docuementos
    print ("creando matriz cuadrada...")

    print (len(vectores),len(VSM1s))

    coords = MDStwoDimentions(VSM1s)

    ###Guardar Coordenadas en Archivo##############################################

    File = open(nombre+'Coordenadas.csv', 'w')
    for coord in coords:
        print (coord)
        File.writelines(str(coord)+"\n")
    File.close()
    ##################################################
    #Graficar en dos dimensiones
    plt.subplots_adjust(bottom=0.1)
    plt.scatter(
        coords[:, 0], coords[:, 1], marker='o'
    )
    for label, x, y in zip(idNews, coords[:, 0], coords[:, 1]):
        plt.annotate(
            label,
            xy=(x, y), xytext=(-20, 20),
            textcoords='offset points', ha='right', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

    plt.show()


#crearMatrizCuadrada("cienciaytecnologia",[1545,1546,1547])

def getURLS(url):
    slash=0
    urlNew=""
    for letra in url:
        if letra=="/":
            slash=slash+1
        if slash < 3:
            urlNew=urlNew+letra
        else:
             break
    return urlNew

#getURLS()


#print vecto4
def wordCountFromTable(list):
    vect1 = 'llevada 1 jiuquan 1 marcha 1 7 1 espacio 1 satélites 1 centro 1 lanzamiento 1 2 1 larga 1 tiangong 1 cohete 1'
    # vect2='vigor 1 servicios 1 entran 1 actualizaciones 1 partir 1 contrato 1 relación 1 nuevas 1 microsoft 1 hoy 1 espacio 1 satélites 1 centro 1'
    vect3 = 'llevada 1 jiuquan 1 marcha 1 7 1 espacio 1 satélites 1 centro 1 lanzamiento 1 2 1 larga 1 tiangong 1 cohete 1'

    vect4 = vect1 + " " + vect3
    vecto4 = vect4.split(' ')
    l1 = vecto4[0::2]
    l2 = vecto4[1::2]

    listWordBeforeToDict=[]
    listFreqBeforeToDict=[]
    for word,freq in zip(l1,l2):
        if word in listWordBeforeToDict:
            i=listWordBeforeToDict.index(word)
            #print i
            #listWordBeforeToDict.insert(i,word)
            sumFreq=listFreqBeforeToDict[i]+int(freq)
            listFreqBeforeToDict[i]=sumFreq
        else:
            listWordBeforeToDict.append(word)
            listFreqBeforeToDict.append(int(freq))

    json_projects = []
    for word,freq in zip(listWordBeforeToDict,listFreqBeforeToDict):
       json_project = {
           'text': word,
           'weight': freq,
           'color': "blue"
       }

       json_projects.append(json_project)

    return json_projects



def calcularNumerador(vect1,vect2):
    vector1=vect1.split(' ')
    vector2=vect2.split(' ')
    l1=vector1[0::2]
    l2=vector2[0::2]
    print (l1)
    print (l2)

    l3=set(l1)&set(l2)
    print (l3)

    numerador=0
    for caracteristica in list(l3):
        i1 = vector1.index(caracteristica)
        i2 = vector2.index(caracteristica)
        numerador=numerador+int(vector1[i1+1])* int(vector2[i2 + 1])

    return numerador

import math
def similitudCosine(numerador,sumA,sumB):

    norma = sumA*sumB
    if norma != 0:
        similarity = (numerador/ norma)
    else:
        similarity = 0
    return similarity



#################################################################################

#################################################################################
def contarPalabras(listaSinStopWordsTocount):
    cuenta1 = collections.Counter(listaSinStopWordsTocount)
    #print type(cuenta1)
    #print cuenta1

    datos = cuenta1.items()

    listCounted=[]

    for tupla in datos:

        listCounted.append(str(tupla[0]) + " " + str(tupla[1]))


    return  listCounted

def cambiarAcentos(row):
    File = open('correcciones.txt', 'r')
    correcciones = File.readlines()
    File.close()

    for correccion in correcciones:
        rem=correccion.split("||")
        #print rem
        row=row.replace(rem[0], rem[1].rstrip('\n'))
        #print rem[0]," - ",rem[1]

    return row

def quitarEtiquetasHTML(row):
    i = 0
    linea = ""
    escribir = True
    while(i<len(row)-1):
        n=row[i]
        m = row[i+1]
    #for n in row:
        if (n == '<'):
            escribir = False
        if (n == '>' and m != '<'):
            escribir = True
            linea = linea+" "

        if (escribir == True and n != '>'):
            if n != '\n':
                linea = linea + str(n)

        i=i+1
    #linea=cambiarAcentos(linea)
    linea=quitarCaracteres(linea)
    #print linea
    return linea

def getURLS(url):
    slash=0
    urlNew=""
    for letra in url:
        if letra=="/":
            slash=slash+1
        if slash < 3:
            urlNew=urlNew+letra
        else:
             break
    return urlNew

########ENTIDADES####################################
def contarEntidades(listaEntidades):

    listCounted=[]

    for tupla in listaEntidades:

        listCounted.append(str(tupla) + "||" + str(1))

    listCounted = '||'.join(listCounted)
    return  listCounted

def getLocationAndAddres(entity):
    import googlemaps

    gmaps = googlemaps.Client(key='AIzaSyCpTAIZUEvWBnbCqMNDE9n6-gEb8hyBczo')

    # Geocoding an address
    geocode_result = gmaps.geocode(entity.encode('utf8'))
    #print geocode_result

    longitud = geocode_result[0]['geometry']['location']['lng']
    latitud =  geocode_result[0]['geometry']['location']['lat']
    addres = geocode_result[0]['formatted_address']
    data = [longitud,latitud,addres]

    return data


def getEntities(text):
    from bs4 import BeautifulSoup
    import urllib, json, collections
    from pyproj import Proj, transform
    url = "http://localhost:8660/rest/annotate?text="+text+"&confidence=0.5&support=20 "

    #print url
    response = urllib.urlopen(url.encode('utf8'))

    data= response.read()
    #print data

    y=BeautifulSoup(data)

    entities= y.html.body.findAll()

    print ("entities: ", len(entities))
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
                None
    enti=contarEntidades(Entidades)
    ligas="||".join(ligasEntidades)
    corde="||".join(Coordenadas)

    data=[enti,ligas,corde]
    return data

############################################
from bs4 import BeautifulSoup as BS
import urllib3   #Cambio urllib2 por urllib3

def getHTML(link):

    response = urllib3.urlopen(link)

    html = response.read()

    pat1 = re.compile(r'htt.+//.+jpg', re.I | re.M)  # para extraer imagenes
    pat2 = re.compile(r'<p>.+</p>', re.I | re.M)
    linkks = re.findall(pat1, str(html))
    links=[]
    #seleccionando los links sin que sea faceook u otro similar
    for link in linkks:
        if "facebook" in link or "twitter" in link or "youtube" in link or "target" in link:None
        else:
            links.append(link)


    #print links
    if "elsiglodetorreon" in link:
        textoLimpio0 = re.findall(pat2, str(html))
        textoLimpio=[]
        for p in textoLimpio0:
            if "s de Tecnolog" in p:
                break
            else:
                textoLimpio.append(p)

        #print textoLimpio
    elif "aztecanoticias" in link:
        textoLimpio = re.findall(pat2, str(html))
    elif "jornada." in link:
        textoLimpio = re.findall(pat2, str(html))
    elif "info7" in link:
        textoLimpio = re.findall(pat2, str(html))
    else:
        soup = BS(html)

        text=str(soup.get_text())

        pat2 = re.compile(r'[a-zA-Z].+;?', re.I | re.M)  # para parsear el texto despues de utilizar la libreria soup

        texto = re.findall(pat2, str(text))

        textoLimpio=[]
        #print texto
        copiar=False
        i=0
        #print ">>>>>>>>>>>>>>>>HTML:",texto
        while i < len(texto):
            if copiar ==False:
                if "IN ENGLISH" in texto[i] and len(texto[i]) == 10:
                    i += 2
                    copiar = True

                elif "Organización Editorial Mexicana" in texto[i]:
                    i += 2
                    copiar = True
                elif 'articleBody"' in texto[i]:#elsiglodetorreon
                    texto[i] = texto[i].replace('articleBody": "<p>', " ")
                    textoL = texto[i].rstrip('\r')
                    textoLimpio.append(textoL.decode('utf8')+" ")
                elif "impresa" in texto[i] and "Facebook Twitter Google+ Email Gmail" in texto[i+1]:#yucatan
                    texto[i+1]=texto[i+1].replace("Facebook Twitter Google+ Email Gmail"," ")
                    i+=2
                    copiar=True
                #elif "CDATA[" in texto[i] and "udm_" in texto[i + 1]:  # yucatan
                 #   i += 8
                  #  copiar = True
                elif "Siguiente" in texto[i] and len(texto[i])==9:
                    i+=1
                    copiar=True
                elif "Comparte ésta nota por e-mail" in texto[i] and len(texto[i])==30:
                    i+=1
                    copiar = True
                elif "Página principal" in texto[i] and len(texto[i]) == 17:
                    i += 1
                    copiar = True
                elif "El Heraldo de Tabasco" in texto[i]:
                    texto[i] = texto[i].replace("El Heraldo de Tabasco", " ")
                    textoL = texto[i].rstrip('\r')
                    textoLimpio.append(textoL.decode('utf8'))
                elif "Portada del sitio " in texto[i]:
                    i += 1
                    copiar = True
                elif "todas las notas del Autor »" in texto[i] and len(texto[i]) == 28:
                    i+=1
                    copiar = True
                elif "Agencia Notimex" in texto[i] and len(texto[i]) == 16:
                    i += 1
                    copiar = True
                elif "Cortesia" in texto[i] and len(texto[i]) == 9:
                    i += 1
                    copiar = True
                elif "reproductorMultimedia" in texto[i] and len(texto[i]) == 45:
                    i = i + 3
                    copiar = True
                elif "Llamada para pintar" in texto[i] and len(texto[i]) == 43:
                    i=i+3
                    copiar = True
                elif "México" in texto[i] and len(texto[i]) == 7 and "CET" in texto[i+1] and len(texto[i+1]) == 25:
                    i = i + 3
                    copiar = True
                elif "hora" in texto[i] and  "color" in texto[i + 1]:
                    i = i + 3
                    copiar = True
                elif "home" in texto[i] and "slot" in texto[i + 1]:#radio Formula
                    i = i + 4
                    copiar = True
                elif "refresh" in texto[i] and "pageview" in texto[i + 1]:#yucatan
                    i = i + 3
                    copiar = True
                elif "Reducir" in texto[i] and "Por" in texto[i + 1]:
                    i = i + 3
                    copiar = True
                elif "function udm_" in texto[i] and "Portada" in texto[i + 1]:
                    copiar = True
                elif "Buscar" in texto[i] and "Oronoticias" in texto[i + 1]:
                    i = i + 2
                    copiar = True
                elif "googletag" in texto[i] and "NOTICIAS" in texto[i + 1]:
                    i = i + 2
                    copiar = True
                elif "By" in texto[i] and "Share" in texto[i + 1]:#lja
                    i = i + 6
                    copiar = True
                elif "barra_comparte" in texto[i] and "Tweet" in texto[i + 1]:
                    i = i + 2
                    copiar = True
                elif "Tweet" in texto[i] and "fuente" in texto[i + 2]:
                    i = i + 3
                    copiar = True
                elif "onReady" in texto[i] and "setVolume" in texto[i+1]:
                    i = i + 2
                    copiar = True
                elif "r.load" in texto[i] and "window" in texto[i + 1]:
                    i = i + 2
                    copiar = True
                elif "angle2" in texto[i] and "start" in texto[i + 1]:
                    i = i + 2
                    copiar = True
                elif "div." in texto[i] and "Coah" in texto[i + 1]:
                    i = i + 18
                    copiar = True
                #else:
                 #   copiar = True

            if copiar == True:
                if "em; " in texto[i]:None
                elif "//" in texto[i]:None
                elif ".init" in texto[i]:None
                elif ".push" in texto[i]:None
                elif "[CDATA" in texto[i]:None
                elif ".remove" in texto[i]:None
                elif "writePostTexto" in texto[i]:None
                elif "writeFooter" in texto[i]:None
                elif "writeColumnaDerechaNotas" in texto[i]:None
                elif "s usuarios. Ay" in texto[i]:None
                elif " Twitter Google+ " in texto[i] and len(texto[i])==38:break
                elif "Siguiente" in texto[i] and len(texto[i])==9:
                    textoLimpio.pop()
                    break
                elif "Contenido Relacionado" in texto[i] and len(texto[i]) == 21:
                    textoLimpio.pop()
                    break
                elif "Organización Editorial Mexicana S.A. de C.V." in texto[i]:
                    break
                elif "Noticias Destacadas" in texto[i] and len(texto[i]) == 19:break
                elif "Ultima modificación" in texto[i] and len(texto[i]) == 27:
                    textoLimpio.pop()
                    textoLimpio.pop()
                    textoLimpio.pop()
                    break
                elif "También te recomendamos" in texto[i] and len(texto[i]) == 24:break
                elif "Archivado en:" in texto[i] and len(texto[i]) == 13:break

                elif 'type":"LiveBlogPosting",' in texto[i] and len(texto[i]) == 26:break
                elif "COMENTARIOS" in texto[i] and "Nombre-Correo electrónico" in texto[i+1] :break
                elif "Publicidad" in texto[i] and "Nuestra señal" in texto[i + 2]: break
                elif "_mdtk" in texto[i] and "async" in texto[i + 1]:break
                elif "PICOS" in texto[i] and len(texto[i]) == 9:break
                elif "ANTERIOR" in texto[i] and ">>" in texto[i + 1]:break
                elif "Link" in texto[i] and "Tags" in texto[i + 1]:break
                elif "_mdtk" in texto[i] and "async" in texto[i + 1]:break
                elif "Pocket" in texto[i] and "Related" in texto[i + 1]:break
                elif "@hidrocalidod" in texto[i] and len(texto[i]) == 22:
                    textoLimpio.pop()

                elif "Fuente" in texto[i] and "Actualizado" in texto[i + 2]:break
                elif "Pocket" in texto[i] and "Related" in texto[i + 1]:break
                elif "gigya." in texto[i] and len(texto[i]) == 43 :break
                elif "Fuente" in texto[i] and "Noticias" in texto[i + 1] :break
                elif "right:10" in texto[i] and "Tweet" in texto[i + 1]:
                    textoLimpio.pop()
                    break
                elif "COMENTARIOS" in texto[i] and "tag" in texto[i + 1]:break#Azteca
                elif "com" in texto[i] and "client" in texto[i + 2]:#razon.mx
                    break
                elif "vdoxPlayer" in texto[i] and "vdoxPlayer" in texto[i + 1]:  #hidrocalido
                    textoLimpio.pop()
                    break
                # elif "debug:" in texto[i]:None
                # elif "debug:" in texto[i]:None
                # elif "debug:" in texto[i]:None
                # elif "debug:" in texto[i]:None
                # elif "debug:" in texto[i]:None


                else:
                    #if copiar == True:
                    textoL=texto[i].rstrip('\r')
                    textoLimpio.append(textoL.decode('utf8'))

            i=i+1

        #textoLimpio.sort(key=lambda tup: tup[0],reverse=True)

        #print textoLimpio[0][1]

    j=0
    linea=""
    #print "len: ",len(textoLimpio), "texto limpio : ####",textoLimpio[0]
    while j<len(textoLimpio):
        if "img src" in textoLimpio[j]:
            None
        else:
            #print textoLimpio[j]
            #print linea
            linea=linea+str(textoLimpio[j])+" "
        j=j+1

    if len(links)!=0:
        if len(links) > 3:
            ligas = ' '.join(links[0:3:])
        else:
            ligas = ' '.join(links)
        ligas = ligas.replace('<img src="', " ")
        ligas = ligas.replace('"', " ")
    else:
        ligas=""
    ligas=ligas.replace("'>","")
    ligas = ligas.replace("/>", "")
    datos={
        "images":ligas,
        "texto":linea
    }
    return datos

def entityExtractor(row):
    wordlist = word_tokenize(row)
    listEntities = [w.lower() for w in wordlist if re.search('^[A-Z][a-záéíóúñ]+$', w)]
    sinStopWords = quitarStopWords(listEntities)
    listEntities = [w.capitalize() for w in sinStopWords]
    strWordsCounted = contarPalabras(listEntities)
    entitiesCounted = ' '.join(strWordsCounted)
    return entitiesCounted

def getEntitiesClasified(entitiesCounted):
    return "in process"

def getLocations():
    from geopy.geocoders import Nominatim

    #print "To geolocate a query to an address and coordinates:"
    #geolocator = Nominatim()
    #location = geolocator.geocode("Pinotepa Nacional")
    #print((location.latitude, location.longitude))
    return "in process"

def getTextWithoutStopWords(row):
    try:
        #LIMPIAR Y CONTAR PALABRAS###################################
        row=quitarEtiquetasHTML(row)
        #row=quitarComillas(row)
        row = row.replace('"'," ")
        row = row.replace("'", " ")
        wordlist = word_tokenize(row)
        TextosinStopWords = quitarStopWords(wordlist)

        dataVector={
            "row":row,
            "TextosinStopWords":TextosinStopWords
        }

        return dataVector

    except BaseException as e:
        None


def getRaizVector(TextoWordsCounted):
    # calcular raiz##############################################
    RaizSumatoriaCuadradosTexto = 0
    for llaveNumero in TextoWordsCounted:
        numero = llaveNumero.split(' ')
        RaizSumatoriaCuadradosTexto = RaizSumatoriaCuadradosTexto + (int(numero[1]) * int(numero[1]))
    raiz = str(math.sqrt(RaizSumatoriaCuadradosTexto))
    if raiz == "0": raiz = '0'
    # print raiz
    return  str(raiz)




def getNews(Fecha,links):
    #print("ejecutando función: getNews(Fecha,links)")

    #listMd5=getMD5News()


    listMD5 = []
    for link in links:
        # print "link----------------------------------------\n"+link
        ligas = link.split('||')

        #print ("ligas", ligas[0], "<<<<>>>>", ligas[1].rstrip('\n'))
        Fuente = ligas[0]
        categoria = ligas[1].rstrip('\n')
        categoria = categoria.rstrip('\r')

        try:
            feed = feedparser.parse(Fuente)
            for item in feed["items"]:

                titulo = item["title"].replace('"', "")
                titulo = titulo.replace("'", "")
                titulo = titulo.replace('”', "")
                titulo = titulo.replace('“', "")
                #print titulo

                ############Revisar si ya existe lanoticia en la base de datos
                TituloMD5 = computeMD5hash(titulo)
                #print "TituloMD5: ", TituloMD5
                if TituloMD5 not in listMD5:

                    ###########################################################
                    listMD5.append(TituloMD5)
                    Fuente1 = getURLS(Fuente)
                    ##########################################################
                    liga = item["link"]
                    #print liga

                    if "yucatan" in liga:
                        texto = item["content"][0]['value']
                        row = quitarEtiquetasHTML(texto)
                        linkImages=""
                    elif "elsiglodetorreon" in liga:
                        descripcion=item["description"]
                        pat1 = re.compile(r'https://.+jpeg', re.I | re.M)  # para extraer imagenes
                        linksList = re.findall(pat1, str(descripcion))
                        linkImages=linksList[0]
                        descripcion = quitarEtiquetasHTML(item["description"])
                        row=descripcion

                    else:
                        descripcion = quitarEtiquetasHTML(item["description"])
                        datos = getHTML(liga)
                        row = datos["texto"]
                        linkImages = datos["images"]

                    ##############################################################
                    descripcion = descripcion.replace("'", "")
                    descripcion = descripcion.replace('“', "")
                    descripcion = descripcion.replace('”', "")
                    descripcion = descripcion.replace('"', "")
                    #print linkImages
                    if row=='':row=descripcion

                    #print "row",row
                    row = row.replace("'", "")
                    row = row.replace('“', "")
                    row = row.replace('”', "")
                    row = row.replace('"', "")

                    #TextWithoutStopWords = getTextWithoutStopWords(row.decode('utf8'))
                    #print("Eliminar stop words")
                    TextWithoutStopWords = getTextWithoutStopWords(row)  #Se elimino el decode en esta linea

                    texto = TextWithoutStopWords["row"]
                    #print "Texto: ",texto

                    ########Entities############################


                    #entities = get_continuous_chunks(texto)
                    #entitiesSinStopWords=quitarStopWords(entities)
                    #data = getEntities(row.decode('utf8'))
                    entitiesCounted=""#data[0]

                    #print entitiesCounted
                    ############################################

                    ######Aqui se debe de clasificar las entidades para posteriormente####
                    EntitiesRecognized = ""#data[1]

                    ############################################
                    # Locations
                    locations = ""#data[2]

                    #print (locations)
                    TextosinStopWords = TextWithoutStopWords["TextosinStopWords"]

                    #print "Texto sin stop",TextosinStopWords

                    #TextoLematizado=lematizerList(TextosinStopWords)

                    #se guarda en la base de datos como un String
                    TextoLematizadoString=' '.join(TextosinStopWords)

                    TextoWordsCounted = contarPalabras(TextosinStopWords)
                    numeroDePalabras = len(TextoWordsCounted)
                    # print numeroDePalabras
                    wordsCountedlematized = ' '.join(TextoWordsCounted)

                    #print "Texto lematizado: ",wordsCountedlematized

                    #print("Llamar getRaízVector")
                    raiz = getRaizVector(TextoWordsCounted)
                    #print raiz

                    fecha = Fecha.split('/')
                    Fecha1 = fecha[2] + '/' + fecha[0] + '/' + fecha[1]


                    #print entitiesCounted
                    try:
                        #print("Conectar a la base de datos")
                        bd = MySQLdb.connect(host="localhost", user="root", passwd="root", port=2200, db="document_analyzer")
                        #bd = mysql.connector.connect(host="localhost", user='yadira2', password='cic', database="document_analyzer")
                        cursor = bd.cursor()

                        #sql = "INSERT INTO newscrawlerSN(idnew_table,Fuente,Fecha,Titulo,TituloMD5,Link,Descripcion,Categoria,Texto,TextoLematizado,WordCountTexto,RaizSumatoriaCuadrados,Entities,EntitiesRecognized,numeroDePalabras,Images,Location) VALUES "
                        sql = "INSERT INTO ST_NEWSCRAWLERSN(ID_NEW_TABLE,Fuente,Fecha,Titulo,Titulo_MD5,Link,Descripcion,Categoria,Texto,TEXTO_LEMATIZADO,Word_Count_Texto,Raiz_Sumatoria_Cuadrados,Entities,Entities_Recognized,numero_De_Palabras,Images,Location) VALUES "
                        sql += "(0,'" + str(Fuente1) + "','" + str(Fecha1) + "'," + "'" + titulo + "','" + TituloMD5 + "','" + str(liga) + "','" + descripcion + "','" + categoria + "','" + texto + "','" + TextoLematizadoString + "','" + wordsCountedlematized + "','" + raiz + "','" + entitiesCounted + "','" + EntitiesRecognized+ "','"+str(numeroDePalabras)+ "','" + linkImages+ "','" + locations + "')"

                        #print(sql)
                        cursor.execute(sql)
                        bd.commit()


                    except BaseException as e:
                        try:
                            #sql = "INSERT INTO newscrawlerSN(idnew_table,Fuente,Fecha,Titulo,TituloMD5,Link,Descripcion,Categoria,Texto,TextoLematizado,WordCountTexto,RaizSumatoriaCuadrados,Entities,EntitiesRecognized,numeroDePalabras,Images,Location) VALUES "
                            sql = "INSERT INTO ST_NEWSCRAWLERSN(ID_NEW_TABLE,Fuente,Fecha,Titulo,TituloMD5,Link,Descripcion,Categoria,Texto,TEXTO_LEMATIZADO,Word_Count_Texto,Raiz_Sumatoria_Cuadrados,Entities,Entities_Recognized,numero_De_Palabras,Images,Location) VALUES "
                            sql += "(NULL,'" + Fuente1 + "','" + str(Fecha1) + "'," + "'" + titulo + "','" + TituloMD5 +"','" + liga + "','" + descripcion+ "','" + categoria + "','" + texto + "','" + TextoLematizadoString + "','" + wordsCountedlematized + "','" + raiz + "','" + entitiesCounted + "','" + EntitiesRecognized+ "','" + str(numeroDePalabras) + "','" + linkImages + "','" + locations + "')"
                            cursor.execute(sql)
                            bd.commit()
                            #print (sql)
                        except BaseException as e:

                            saveFile = open('sqlFailedReal.csv', 'a')
                            saveFile.write(sql.encode('utf8'))
                            saveFile.write('\n')
                            saveFile.close()
                            #print sql
                            print ('failed cursor execute ', str(e))
                else:
                    saveFile = open('newsRepeted.csv', 'a')
                    saveFile.write(titulo+","+Fuente+","+categoria)
                    saveFile.write('\n')
                    saveFile.close()
                    #print "REPETIDA: ",titulo+","+Fuente+","+categoria
        except BaseException as e:

            None
            #print titulo+","+Fuente+","+categoria

def main ():
    #print("ejecutando función: main")
    fecha = time.strftime("%x")

    print ("Fecha: "+ fecha)
    File = open('ligasRSS.txt', 'r')
    links = File.readlines()
    File.close()

    #print("Llamar:  getNews(fecha,links)")
    getNews(fecha,links)


def crowlerFromLinks():

    bd = mysql.connector.connect(user='root', password='1234', database='visualizadordenoticias')
    cursor = bd.cursor()
    # sql = "SELECT idnew_table,Titulo,WordCountTexto,Descripcion FROM  newsall WHERE FECHA='2016-11-25' and Categoria='cienciaYtecnologia'"
    #sql = "SELECT * FROM  newsall WHERE idnew_table > 191418"
    sql = "SELECT * FROM  newscrawlerSN where year(Fecha) = 2017"

    cursor.execute(sql)
    dataBase = cursor.fetchall()
    #los mayores
    #http://www.oem.com.mx,www.razon.com.mx
    print (len(dataBase))
    listMD5=[]
    for tupla in dataBase:
        try:

            titulo = tupla[3]
            titulo = titulo.replace("'", "")

            TituloMD5 = computeMD5hash(titulo)

            # print "TituloMD5: ", TituloMD5
            if TituloMD5 not in listMD5:

                Fuente = tupla[1]
                Fecha1 = tupla[2]
                ###########################################################
                listMD5.append(TituloMD5)

                ##########################################################
                liga = tupla[4]
                # print liga
                descripcion = tupla[5]
                # print descripcion

                # print titulo
                categoria = tupla[6]
                datos = getHTML(liga)
                row = datos["texto"]
                row = row.replace("'", "")

                if row == '': row = descripcion
                if row < len(descripcion): row = descripcion

                entitiesCounted = entityExtractor(row)
                # print type(entitiesCounted)
                ##############################################################


                # print row
                linkImages = datos["images"]
                # print linkImages



                TextWithoutStopWords = getTextWithoutStopWords(row.decode('utf8'))
                texto = TextWithoutStopWords["row"]
                # print "Texto: ",texto
                ########Entities############################
                entities = get_continuous_chunks(texto)
                entitiesSinStopWords = quitarStopWords(entities)
                entitiesCounted = contarEntidades(entitiesSinStopWords)
                # print entitiesCounted
                ############################################
                ######Aqui se debe de clasifiacar las entidades para posteriormente####
                EntitiesRecognized = getEntitiesClasified(entitiesCounted)

                ############################################
                # Locations
                locations = getLocations()

                # print (locations)
                TextosinStopWords = TextWithoutStopWords["TextosinStopWords"]

                # print "Texto sin stop",TextosinStopWords

                TextoLematizado = lematizerList(TextosinStopWords)

                TextoLematizadoString = ' '.join(TextosinStopWords)

                TextoWordsCounted = contarPalabras(TextosinStopWords)
                numeroDePalabras = len(TextoWordsCounted)
                # print numeroDePalabras
                wordsCountedlematized = ' '.join(TextoWordsCounted)

                # print "Texto lematizado: ",wordsCountedlematized

                raiz = getRaizVector(TextoWordsCounted)
                # print raiz



                # print entitiesCounted
                try:
                    bd = mysql.connector.connect(user='root', password='1234', database='visualizadordenoticias')
                    cursor = bd.cursor()

                    sql = "INSERT INTO newscrawlerSN(idnew_table,Fuente,Fecha,Titulo,TituloMD5,Link,Descripcion,Categoria,Texto,TextoLematizado,WordCountTexto,RaizSumatoriaCuadrados,Entities,EntitiesRecognized,numeroDePalabras,Images,Location) VALUES "
                    sql += "(NULL,'" + str(Fuente1) + "','" + str(Fecha1) + "'," + "'" + titulo.decode(
                        'utf-8') + "','" + TituloMD5 + "','" + str(liga) + "','" + descripcion.decode(
                        'utf-8') + "','" + categoria + "','" + texto.decode(
                        'utf-8') + "','" + TextoLematizadoString + "','" + wordsCountedlematized + "','" + raiz + "','" + entitiesCounted + "','" + EntitiesRecognized + "','" + str(
                        numeroDePalabras) + "','" + linkImages + "','" + locations + "')"
                    cursor.execute(sql)
                    bd.commit()
                    print (sql)

                except BaseException as e:
                    try:
                        sql = "INSERT INTO newscrawlerSN(idnew_table,Fuente,Fecha,Titulo,TituloMD5,Link,Descripcion,Categoria,Texto,TextoLematizado,WordCountTexto,RaizSumatoriaCuadrados,Entities,EntitiesRecognized,numeroDePalabras,Images,Location) VALUES "
                        sql += "(NULL,'" + Fuente1 + "','" + str(
                            Fecha1) + "'," + "'" + titulo + "','" + TituloMD5 + "','" + liga + "','" + descripcion + "','" + categoria + "','" + texto + "','" + TextoLematizadoString + "','" + wordsCountedlematized + "','" + raiz + "','" + entitiesCounted + "','" + EntitiesRecognized + "','" + str(
                            numeroDePalabras) + "','" + linkImages + "','" + locations + "')"
                        cursor.execute(sql)
                        bd.commit()
                        # print sql
                    except BaseException as e:

                        saveFile = open('sqlFailedReal.csv', 'a')
                        saveFile.write(sql.encode('utf8'))
                        saveFile.write('\n')
                        saveFile.close()
                        #print sql
                        print ('failed cursor execute ', str(e))

                print ("idnew_table: ",tupla[0])
            else:
                saveFile = open('newsRepeted.csv', 'a')
                saveFile.write(titulo + "," + Fuente + "," + categoria)
                saveFile.write('\n')
                saveFile.close()
                #print "REPETIDA: ", titulo + "," + Fuente + "," + categoria
        except BaseException as e:
            print (e)


def cambiarTextoSinLema():
    bd = mysql.connector.connect(user='root', password='1234', database='visualizadordenoticias')
    cursor = bd.cursor()
    # sql = "SELECT idnew_table,Titulo,WordCountTexto,Descripcion FROM  newsall WHERE FECHA='2016-11-25' and Categoria='cienciaYtecnologia'"
    #sql = "SELECT * FROM  newsall WHERE idnew_table > 191418"
    sql = "SELECT * FROM  newscrawlerSN where month(Fecha)=3"

    cursor.execute(sql)
    dataBase = cursor.fetchall()
    print (len(dataBase))
    for row in dataBase:
        idnew_table = row[0]
        Fuente = row[1]
        Fecha = row[2]
        Titulo = row[3]
        TituloMD5 = row[4]
        Link = row[5]
        Descripcion =row[6]
        Categoria =row[7]
        Texto =row[8]
        ############################################
        TextWithoutStopWords = getTextWithoutStopWords(Texto.decode('utf8'))
        texto = TextWithoutStopWords["row"]

        TextosinStopWords = TextWithoutStopWords["TextosinStopWords"]

        TextoLematizadoString = ' '.join(TextosinStopWords)

        TextoWordsCounted = contarPalabras(TextosinStopWords)

        raiz = getRaizVector(TextoWordsCounted)
        ############################################
        TextoLematizado = TextoLematizadoString
        WordCountTexto = ' '.join(TextoWordsCounted)
        RaizSumatoriaCuadrados = raiz
        Entities=row[12]
        EntitiesRecognized = row[13]
        numeroDePalabras =row[14]
        Images =row[15]
        Location =row[16]

        try:
            sql = "INSERT INTO newscrawlerSN(idnew_table,Fuente,Fecha,Titulo,TituloMD5,Link,Descripcion,Categoria,Texto,TextoLematizado,WordCountTexto,RaizSumatoriaCuadrados,Entities,EntitiesRecognized,numeroDePalabras,Images,Location) VALUES "
            sql += "(0,'" + Fuente + "','" + str(
                Fecha) + "'," + "'" + Titulo + "','" + TituloMD5 + "','" + Link + "','" + Descripcion + "','" + Categoria + "','" + Texto + "','" + TextoLematizado + "','" + WordCountTexto + "','" + RaizSumatoriaCuadrados + "','" + Entities + "','" + EntitiesRecognized + "','" + str(
                numeroDePalabras) + "','" + Images + "','" + Location + "')"
            cursor.execute(sql)
            bd.commit()
        except BaseException as e:
            print (e)
            print (sql)
            print ("err in id:", idnew_table)




main ()

#if __name__ == '__main__':
#
#
#    import schedule
#    import time
    #
    #    #cambiarTextoSinLema()
    #    schedule.every().day.at('11:00').do(main) # en esta linea se agrega la hora de ejecucion
    #    #schedule.every().day.at('12:05').do(main)
    #    print ("Running...")
        #    while True:
#        schedule.run_pending()


# /home/yadira/PycharmProjects/Thesis/src/NewsCrawler/MDSexampleSLV3.py