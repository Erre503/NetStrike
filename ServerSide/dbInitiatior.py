#Creazione database
  
def create_database(connection):

    #reads the SqlFile for the default database
    initialQuery = ''
    fd = open('basicDB.sql', 'r')
    initialQuery = fd.read()
    fd.close()
    cursor = connection.cursor()
    try:
        cursor.execute(initialquery)
        print("Database created successfully")
    except Error as err:
        print(f"Error: '{err}'")
