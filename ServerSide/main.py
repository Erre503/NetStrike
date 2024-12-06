# Punto d'ingresso per hostare il servizio

import mysql.connector
import connectorPySql
import dbInitiatior

host_name = ''
user_name = ''
password = ''
connection = connectorPySql.createServerConnection(host_name, user_name, password)
dbInitiatior.create_database(connection)
