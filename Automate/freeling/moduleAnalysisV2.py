
import MySQLdb
import nltk
import re
from nltk import FreqDist

daConexion = MySQLdb.connect(host="localhost",
                             port=2200,
                             user="root",
                             passwd="root",
                             db="document_analyzer")


def getStopWord(): # Regresa la lista de stop words

    cursor = daConexion.cursor()

    stopWordQuery = "SELECT SIMPLE_WORD FROM document_analyzer.STOP_WORD;"

    try:
        cursor.execute(stopWordQuery)

    except MySQLdb.Error as error:
       print("Error: {}".format(error))

    stop_word = []

    for element in cursor:
        #print("stop_word: " + str(element))
        stop_word.append(element[0])
    #print("simple_word_list_stop_word: " + str(stop_word))

    cursor.close()

    return stop_word

# No se deben eliminar los acentos ya que cambia el sentido de las palabras,
# ademas de que las noticias de los periodicos deben estar escritas correctamente por ser una fuente oficial
def delAccent (text):
    text = text.replace('á', 'a')
    text = text.replace('é', 'e')
    text = text.replace('í', 'i')
    text = text.replace('ó', 'o')
    text = text.replace('ú', 'u')

    return text

# wordList = ["Son", "los", "hidalguenses", "quienes", "estableceron", "el", "plan"]
def delSpecialChar (wordList) :

    word_list2 = []

    for element in wordList:
        # print (element)
        element_tmp = re.sub(r'[^a-z || ^á-ú ]*', r'', element)
        element_tmp = re.sub(r' ', r'', element_tmp)
        if len(element_tmp) > 1:
            word_list2.append(element_tmp)
        # print (element_tmp)
    # print(word_list)
    # print(word_list2)

    wordList = word_list2

    return wordList

# Lista de listas donde el primer elemento de cada lista es el token
def delSpecialCharList (wordList) :

    word_list2 = []

    for element in wordList:
        # print (element)
        word_tmp = []

        element_tmp = re.sub(r'[^a-z || ^á-ú||^_||^0-9||^ñ]*', r'', element[1])
        element_tmp = re.sub(r' ', r'', element_tmp)
        word_tmp = [element[0], element_tmp, element[2], element[3]]
        if len(element_tmp) > 1:
            word_list2.append(word_tmp)
        # print (element_tmp)
    # print(word_list)
    # print(word_list2)

    #wordList = word_list2

    return word_list2


#input example [('de', 29), ('la', 26), ('que', 10)]
def delStopWord(wordList):

    sw = getStopWord()
    #print("input to dell stop word wordList: ", wordList)

    for element in range(len(wordList)-1, -1, -1):
        #print("element: ", element)
        wordTmp = wordList[element][1]
        #print("wordTmp: ", wordTmp)
        if len(wordTmp) < 2 :
            wordList.pop(element)
        else :
            for word in sw :
                #print("wordTmp: ", wordTmp, "  word: ", word)
                if wordTmp == word :
                    #print("wordTmp: ", wordTmp, "  word: ", word)
                    #print("pop(element)", wordList[element])
                    wordList.pop(element)
    return wordList

#input: ['de', 'la', 'que', 'el', 'en']
def delSingleStopWord(wordList):

    sw = getStopWord()
    #print("input to dell stop word wordList: ", wordList)

    for element in range(len(wordList)-1, -1, -1):
        #print("element: ", element)
        wordTmp = wordList[element]
        #print("wordTmp: ", wordTmp)
        if len(wordTmp) < 2 :
            wordList.pop(element)
        else :
            for word in sw :
                #print("wordTmp: ", wordTmp, "  word: ", word)
                if wordTmp == word :
                    #print("wordTmp: ", wordTmp, "  word: ", word)
                    #print("pop(element)", wordList[element])
                    wordList.pop(element)
                else: a = 1

    return wordList

def saveMissedWord(word):
    f = open("/home/yadira/PycharmProjects/Thesis/Resources/synonymsMissedWord.txt", "a")
    f.write("\n" + word)
    f.close()

def insertDocAnalyzer(insertString):
    cursor = daConexion.cursor()

    try:
        cursor.execute(insertString)
        daConexion.commit()
        print("successful db operation: ", insertString)
    except MySQLdb.Error as error:
        print("Error: {}".format(error))

    cursor.close()


# Análisis freeling
def callFreeling(docContent, tk, sp, mf, tg, sen, sid, parser, dep) :
    docContent = docContent
    wordList = []

    print("\ndocContent inside callFreeling: \n")
    print(docContent)

    l = tk.tokenize(docContent);
    ls = sp.split(sid, l, False);

    ls = mf.analyze(ls);
    ls = tg.analyze(ls);
    ls = sen.analyze(ls);
    ls = parser.analyze(ls);
    ls = dep.analyze(ls);

    ## output results
    line = 0
    for s in ls:
        word_tmp = []
        #print("s: ")
        #print(s)
        ws = s.get_words();
        #print("ws: ")
        #print(ws)
        for w in ws:
            #print("Form: " + w.get_form() + " " + "Lema: " + w.get_lemma() + " " + "tag: " + w.get_tag() + " " + "senses: " + w.get_senses_string());
            #s : Iterador para cada linea
            lemma = w.get_lemma()
            tag = w.get_tag()
            sense = w.get_senses_string()
            word_tmp = [line, lemma, tag, sense ]
            #print("word_tmp: ", word_tmp)
            wordList.append(word_tmp)
        #print("")
        line = line + 1

    return (wordList)


def dbInsertDocVector (vector, idDocument, category, tf):

    #vector = vectorIn
    #idDocument = idDocumentIn
    #category = categoryIn
    #tf = tfIn

    # insertDocVector = ("INSERT INTO DOCUMENT_VSM_2019A (ID_DOCUMENT, CHARACTERISTIC, CATEGORY, TF, LINE, TAG, SENSE) VALUES (" +

    sense = vector[3]

    insertDocVector = ("INSERT INTO DOCUMENT_VSM_2020A (ID_DOCUMENT, CHARACTERISTIC, CATEGORY, TF, LINE, TAG, SENSE) VALUES (" +
                       str(idDocument) + "," +          # idDocument
                       "'" + vector[1] + "', " +
                       "'" + category + "', "  +
                       str(tf) + ", " +
                       str((vector[0] + 1)) + ", " +          # line
                       "'" + vector[2] + "', " +
                       "'" + sense[0:245] + "' );")

    print("insertDocVector:")
    print(insertDocVector)

    cursor = daConexion.cursor()
    try:
        cursor.execute(insertDocVector)
        daConexion.commit()
    except MySQLdb.Error as error:
        print("Error: {}".format(error))

    cursor.close()
