import MySQLdb

daConexion = MySQLdb.connect(host="localhost",
                             port=2200,
                             user="root",
                             passwd="root",
                             db="document_analyzer")


cursor = daConexion.cursor()
cursor.execute("DESC st_newscrawlersn;")
# r = daConexion.store_result()
print(cursor.fetchmany(7))