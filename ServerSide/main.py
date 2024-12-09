# Punto d'ingresso del servizio
from doctest import debug

from flask import Flask, request, jsonify

app = Flask(__name__)

#output di default all'accesso alla route del server con disclaimer
#Le persone che hanno partecipato a questo progetto non hanno responsabilità
#nella raccolta dei dati di chi accede a questo servizio
@app.route("/")
def home():
    return "This server is hosting a service and every access is saved, nor the host or the takes accuntabilty for the inoformations collected."

if __name__ == "__main__":
      app.run(debug = true)
