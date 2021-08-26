
import MySQLdb
import nltk
import re
from nltk import FreqDist
import moduleAnalysisV2 as ma

daConexion = MySQLdb.connect(host="localhost",
                             port=2200,
                             user="root",
                             passwd="root",
                             db="document_analyzer")

# main

cursor = daConexion.cursor()

# getDocContent = "SELECT ID_DOCUMENT, CONTENT FROM document_analyzer.DOCUMENT WHERE PUBLICATION_DATE >= '2019-01-01 00:00:00' AND PUBLICATION_DATE <= '2019-05-13 00:00:00';"

# 17,152 2018 C
#getDocContent = "SELECT ID_DOCUMENT, CONTENT FROM document_analyzer.DOCUMENT WHERE PUBLICATION_DATE >= '2018-09-01 00:00:00' AND PUBLICATION_DATE <= '2018-12-31 00:00:00' LIMIT 10;"

#2017 A de enero a abril
# getDocContent = "SELECT ID_DOCUMENT, CONTENT FROM document_analyzer.DOCUMENT WHERE PUBLICATION_DATE >= '2017-01-01 00:00:00' AND PUBLICATION_DATE <= '2017-04-30 00:00:00'"

#getDocContent = "SELECT DOC.ID_DOCUMENT, DOC.CONTENT FROM document_analyzer.DOCUMENT DOC LEFT JOIN DOCUMENT_VSM_2017A VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT WHERE VSM.ID_DOCUMENT_VSM IS NULL AND PUBLICATION_DATE >= '2017-01-01 00:00:00' AND PUBLICATION_DATE <= '2017-04-30 00:00:00' ; "

#2016
#getDocContent = "SELECT DOC.ID_DOCUMENT, DOC.CONTENT FROM document_analyzer.DOCUMENT DOC LEFT JOIN DOCUMENT_VSM_2016 VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT WHERE VSM.ID_DOCUMENT_VSM IS NULL AND PUBLICATION_DATE >= '2016-01-01 00:00:00' AND PUBLICATION_DATE <= '2016-12-31 00:00:00' ; "

#2019 B
#getDocContent = "SELECT DOC.ID_DOCUMENT, DOC.CONTENT FROM document_analyzer.DOCUMENT DOC LEFT JOIN DOCUMENT_VSM_2019B VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT WHERE VSM.ID_DOCUMENT_VSM IS NULL AND PUBLICATION_DATE >= '2019-05-01 00:00:00' AND PUBLICATION_DATE <= '2019-08-14 00:00:00' ; "

#2019 B complemento
#getDocContent = "SELECT DOC.ID_DOCUMENT, DOC.CONTENT FROM document_analyzer.DOCUMENT DOC LEFT JOIN DOCUMENT_VSM_2019C VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT WHERE VSM.ID_DOCUMENT_VSM IS NULL AND PUBLICATION_DATE >= '2019-09-01 00:00:00' AND PUBLICATION_DATE <= '2019-11-19 00:00:00' ; "

#2019 B complemento
#getDocContent = "SELECT DOC.ID_DOCUMENT, DOC.CONTENT FROM document_analyzer.DOCUMENT DOC LEFT JOIN DOCUMENT_VSM_2020A VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT WHERE VSM.ID_DOCUMENT_VSM IS NULL AND PUBLICATION_DATE >= '2020-01-01 00:00:00' AND PUBLICATION_DATE <= '2020-02-04 00:00:00' ; "

# 2020 Automatización
getDocContent = "SELECT DOC.ID_DOCUMENT, DOC.CONTENT FROM document_analyzer.DOCUMENT DOC LEFT JOIN DOCUMENT_VSM_2020A VSM ON DOC.ID_DOCUMENT = VSM.ID_DOCUMENT WHERE VSM.ID_DOCUMENT_VSM IS NULL AND PUBLICATION_DATE >= (SELECT MIN(START_DATE) FROM document_analyzer.SETTING_LOAD_DOC WHERE PROCESS_NAME = 'LOAD_NEWS') AND PUBLICATION_DATE <= (SELECT MAX(END_DATE) FROM document_analyzer.SETTING_LOAD_DOC WHERE PROCESS_NAME = 'LOAD_NEWS') "



try:
    cursor.execute(getDocContent)



except MySQLdb.Error as error:
    print("Error: {}".format(error))

daConexion.close()

wordList = []

#print("document content: ", cursor.fetchall())

# ##################################################################
# Llamar Freeling para lematizar y tokenizar

import pyfreeling
#import sys, os

# Location of FreeLing configuration files.
DATA = "/usr"+"/share/freeling/"; # Without local

# Init locales
pyfreeling.util_init_locale("default");

# create language detector. Used just to show it. Results are printed
# but ignored (after, it is assumed language is LANG)
la=pyfreeling.lang_ident(DATA+"common/lang_ident/ident-few.dat");

# create options set for maco analyzer. Default values are Ok, except for data files.
LANG="es";
op= pyfreeling.maco_options(LANG);
op.set_data_files( "",
                   DATA + "common/punct.dat",
                   DATA + LANG + "/dicc.src",
                   DATA + LANG + "/afixos.dat",
                   "",
                   DATA + LANG + "/locucions.dat",
                   DATA + LANG + "/np.dat",
                   DATA + LANG + "/quantities.dat",
                   DATA + LANG + "/probabilitats.dat");

# create analyzers
tk=pyfreeling.tokenizer(DATA+LANG+"/tokenizer.dat");
sp=pyfreeling.splitter(DATA+LANG+"/splitter.dat");
sid=sp.open_session();
mf=pyfreeling.maco(op);

# activate mmorpho odules to be used in next call
mf.set_active_options(False, True, True, True,  # select which among created
                      True, True, False, True,  # submodules are to be used.
                      True, True, True, True);  # default: all created submodules are used

# create tagger, sense anotator, and parsers
tg = pyfreeling.hmm_tagger(DATA + LANG + "/tagger.dat", True, 2);
sen = pyfreeling.senses(DATA + LANG + "/senses.dat");
parser = pyfreeling.chart_parser(DATA + LANG + "/chunker/grammar-chunk.dat");
dep = pyfreeling.dep_txala(DATA + LANG + "/dep_txala/dependences.dat", parser.get_start_symbol());

# #########################################################################################################


for element in cursor:
    print("")
    print("id_new: ", element[0])
    #print("contend_word: " + str(element[1]))
    docContent = str(element[1])
    print("original new: ", docContent)

    #docContent = docContent.lower()
    # Freeling regresa los lemas en lower
    # Freeling usa las mayusculas para tokenizar

    #docContent = delAccent(docContent)

    # Lematizar el documento
    wordList = ma.callFreeling(docContent, tk, sp, mf, tg, sen, sid, parser, dep)

    print("Word List lematizada")
    print(wordList)

    # Freeling genera el split de textos
    #wordList = docContent.split()
    #print("wordList split: " + str(wordList))

    #lenWordList = len(wordList)
    #print("len(wordList): ", lenWordList)

    #print("wordList split: ", wordList)


    wordList = ma.delSpecialCharList(wordList)
    print("wordList without special characters: ")
    print(wordList)

    # Calcular la frecuencia de la tabla que contiene el vector de cada documento
    # Dejar El calculo de la frecuencia del lado del manejador
    #wordList = FreqDist(wordList)

    #print("wordList: ", wordList)
    #wordList = wordList.most_common(lenWordList)
    #print("word count : ", wordList)

    wordList = ma.delStopWord(wordList)
    print("word count without stop words: ")
    print(wordList)




    #Guardar los vectores en la bd
    for vector in wordList :
        ma.dbInsertDocVector (vector, idDocument = element[0], category = 'LEMMA', tf = 1)

#print("test gerSimpleWord_stop_word:" , getStopWord())



# Cerrar sesion Freeling
sp.close_session(sid);

# La carga de 2017 ya tiene la correccion que mantiene los numeros cuando se eliminan los caracteres especiales
