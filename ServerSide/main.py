# Punto d'ingresso del servizio
from asyncio.windows_events import NULL
from doctest import debug

from flask import Flask, request, jsonify

app = Flask(__name__)

#output di default all'accesso alla route del server con disclaimer
#Le persone che hanno partecipato a questo progetto non hanno responsabilità
#nella raccolta dei dati di chi accede a questo servizio
@app.route("/")
def home():
    return "This server is hosting a service and every access is saved, nor the host or the team of development takes accuntabilty for the inoformations collected."

#Interfaccia con la tabella del database tramite GET e POST
#Se la richiesta è un POST la funzione aggiunge il parametro passato come plugin nella tabella
#Se la richiesta è un GET la funzione cerca il plugin tramite id nella tabella
@app.route("/plugin_details",methods=["POST","GET"])
def plugTable():
    if request.method == "POST":
        return NULL
    else:
        return NULL

if __name__ == "__main__":
      app.run(debug = true)
