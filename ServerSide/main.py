# Punto d'ingresso del servizio
from asyncio.windows_events import NULL
from doctest import debug
from email.policy import default

from flask import Flask, request, jsonify
from sqlalchemy import Nullable
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']  = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)

#creazione delle classi per le tabelle nel database:
# plugTable:
#   id : Integer           //(mi rifiuto di spiegarlo)
#   name : String          //nome del plugin
#   params : String        //parametri modificabili di un plugin 
#   description : String   //descrizione del plugin

# log:
#   idLog : Integer        //(mi rifiuto di spiegarlo)
#   dateLog : String       //data dell'esecuzione
#   success : Boolean      //esito dell'attacco (riuscito? true:false)
#   result : String        //Informazioni ottenute dall'attacco sul suo esito

class plugTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    params = db.Column(db.String(300), default="")
    description = db.Column(db.String(300), default="Il plugin non esiste")
    def __repr__(self):
        return '<Name %r>' % self.id
    def to_dict(self):
       return { 
           'id': self.id,
           'name': self.name,
           'params': self.params,
           'description': self.description }

class log(db.Model):
    idLog = db.Column(db.Integer, primary_key=True)
    dateLog = db.Column(db.DateTime, nullable=False)
    success = db.Column(db.Boolean, default=False)
    result = db.Column(db.String(300), default="Il test non ha fornito risultati")
    def __repr__(self):
        return '<Name %r>' % self.idLog
    def to_dict(self): 
        return { 
            'idLog': self.idLog, 
            'dateLog': self.dateLog.strftime('%Y-%m-%d %H:%M:%S'), 
            'success': self.success, 
            'result': self.result }

# Output di default

#output di default all'accesso alla route del server con disclaimer
#Le persone che hanno partecipato a questo progetto non hanno responsabilità
#nella raccolta dei dati di chi accede a questo servizio
@app.route("/")
def index():
    return "This server is hosting a service and every access is saved, nor the host or the team of development takes accuntabilty for the inoformations collected."

# Funzione per i dettagli del plugin 

#Interfaccia con la tabella del database che permette di chiedere le informazioni di un plugin tramite id
@app.route("/plugin_details")
def plugTable(id = 0):
    plugin = plugTable.query.get(id) 
    if plugin:
       return jsonify(plugin.to_dict()) 
    else:
       return jsonify({'error': 'Plug not found'}), 404


if __name__ == "__main__":
      app.run(debug = true)
