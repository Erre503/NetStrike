import os

def execute():
    hostname = "google.com"
    response = os.popen("ping -n 3 " + hostname).read()

    return response

    


execute()




