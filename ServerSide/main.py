# Punto d'ingresso del servizio
from doctest import debug

from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Home"

if __name__ == "__main__":
      app.run(debug = true)
