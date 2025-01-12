# Punto d'ingresso del servizio
from asyncio.windows_events import NULL
from doctest import debug
from email.policy import default
import json
from flask import Flask, request, jsonify
from sqlalchemy import Nullable, null
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
#from flask_classful import FlaskView,route   Prossima implementazione

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
    __tablename__ = 'plugTable'
    id = db.Column(db.Integer,Sequence('plugin_id_seq'), primary_key=True)
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
    __tablename__ = 'Log'
    idLog = db.Column(db.Integer,Sequence('logId'), primary_key=True)
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


"""
class ServerCore(FlaskView):
def __init__(self):
    print("init has been called")
"""
# Output di default

# output di default all'accesso alla route del server con disclaimer
# Le persone che hanno partecipato a questo progetto non hanno responsabilità
# nella raccolta dei dati di chi accede a questo servizio

@app.route("/")
def index():
    return "This server is hosting a service and every access is saved, neither the host or the team of development takes accuntabilty for the inoformations collected."

# Funzione per la lista dei plugin
# Questa funzione permette di chiedere la lista dei plugin con relativi id:
# la lista consiste di "id" e "nome".
# La funzione viene eseguita ogni volta che il client viene aperto.

@app.route("/plugin_list", endpoint='plugin_list', methods=["GET"])
def plug_table(): 
    pluginT = PlugTable.query.all()
    if pluginT==None or pluginT==any:
        return "error 404, no such plugin has been found"
    return jsonify(pluginT.list()) 


# Funzione per i dettagli del plugin 
# Questa funzione permette di chiedere la descrizione del plugin tramite id:
# la lista consiste di "descizione" e "parametri".
# La funzione viene eseguita ogni volta che il client selezione un plugin

@app.route("/plugin_details", endpoint='plugin_details',  methods=["GET"])
def plug_table(id = 0):
    plugin = PlugTable.query.get(id)    #gestione dell'id tramite il metodo http GET
    if plugin==None or plugin==any:
        return "error 404, no such plugin has been found"
    return jsonify(plugin) 

# Funzione per caricare il plugin 
# Questa funzione permette di importare il plugin nel server:
# tramite un'istanza del plugin loader il file del plugin viene messo in una cartella
# appartenente al server. 
# La funzione viene eseguita quando il client invia un nuovo plugin sul server

@app.route("/upload_plugin", endpoint='upload_plugin',  methods=["POST"])
def new_plugin():
    with open('data.json', 'r') as file:
        data = json.load(file)
    if not data or 'name' not in data or 'params' not in data or 'description' not in data:
        return "error 404, not valid record"
    new_plugin = PlugTable(
            name=data['name'],
            params=data['params'],
            description=data['description']
        )
    db.session.add(new_plugin)
    db.session.commit()

@app.route("/dummy", endpoint='dummy',  methods=["GET"])
def dummy():
    new_plugin = PlugTable(name = "")
    db.session.add(new_plugin)
    db.session.commit()
    return "the dummy has been placed"
# Funzione per i dettagli dei log degli attacchi
# Questa funzione permette di chiedere la lista dei log:
# la lista consiste in "id" e "name".
# La funzione viene eseguita ogni volta che il client richiede una cronologia

@app.route("/log_list", endpoint='log_list',  methods=["GET"])
def log():
    log = Log.query.all()
    if log==None or log==any:
        return "error 404"
    return jsonify(log) 

"""
ServerCore.register(app)
"""
if __name__ == "__main__":
        app.run(debug = True)

with app.app_context():
    db.create_all()

#creaPlugin