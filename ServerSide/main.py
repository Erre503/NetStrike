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





#classi per le tabelle nel database:

# plugTable:
#   id : Integer           
#   name : String          //nome del plugin
#   params : String        //parametri modificabili di un plugin 
#   description : String   //descrizione del plugin

class PlugTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    params = db.Column(db.String(300), default="")
    description = db.Column(db.String(300), default="Il plugin non esiste")
    def __repr__(self):
        return '<Name %r>' % self.id
    def list(self):
       return { 
           'id': self.id,
           'name': self.name}
    def description(self):
       return { 
           'params': self.params,
           'description': self.description }

# log:
#   idLog : Integer        
#   dateLog : String       //data dell'esecuzione
#   success : Boolean      //esito dell'attacco (riuscito? true:false)
#   result : String        //Informazioni ottenute dall'attacco sul suo esito

class Log(db.Model):
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

# Funzione per la lista dei plugin
# Questa funzione permette di chiedere la lista dei plugin con relativi id:
# la lista consiste di "id" e "nome".
# La funzione viene eseguita ogni volta che il client viene aperto.

@app.route("/plugin_list")
def plug_table():
    plugin = PlugTable.query.get() 
    return jsonify(plugin.list()) 


# Funzione per i dettagli del plugin 
# Questa funzione permette di chiedere la descrizione del plugin tramite id:
# la lista consiste di "descizione" e "parametri".
# La funzione viene eseguita ogni volta che il client selezione un plugin

@app.route("/plugin_details")
def plug_table(id = 0):
    plugin = PlugTable.query.get(id) 
    return jsonify(plugin.description()) 


if __name__ == "__main__":
      app.run(debug = true)
