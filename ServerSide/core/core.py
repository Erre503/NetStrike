# Punto d'ingresso del servizio
from utils.security_functions import *
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from .plugin_loader import caricaPlugin, lista_plugin, avvia_plugin, creaPlugin
import time
# from flask_classful import FlaskView, route   Prossima implementazione

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)
last_update = round(time.time())
# classi per le tabelle nel database:

# plugTable:
#   id : Integer
#   name : String          //nome del plugin
#   params : String        //parametri modificabili di un plugin
#   description : String   //descrizione del plugin

class PlugTable(db.Model):
    __tablename__ = 'plugTable'
    id = db.Column(db.Integer, Sequence('plugin_id_seq'), primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    params = db.Column(db.String(300), default="")
    description = db.Column(db.String(300), default="Il plugin non esiste")

    def __repr__(self):
        return '<Name %r>' % self.id

    def list(self):
        return {
            'id': self.id,
            'name': self.name
        }

    def get_description(self):  # Renamed method
        return {
            'params': self.params,
            'description': self.description
        }

# log:
#   idLog : Integer
#   dateLog : String       //data dell'esecuzione
#   success : Boolean      //esito dell'attacco (riuscito? true:false)
#   result : String        //Informazioni ottenute dall'attacco sul suo esito

class Log(db.Model):
    __tablename__ = 'Log'
    idLog = db.Column(db.Integer, Sequence('logId'), primary_key=True)
    dateLog = db.Column(db.DateTime, nullable=False)
    success = db.Column(db.Boolean, default=False)
    result = db.Column(db.String(300), default="Il test non ha fornito risultati")

    def __repr__(self):
        return '<Name %r>' % self.idLog

    def logList(self):
        return {
            'idLog': self.idLog,
            'dateLog': self.dateLog.strftime('%Y-%m-%d %H:%M:%S')            
        }

    def logData(self):
        return {
            'success': self.success,
            'result': self.result
        }

# Output di default

# output di default all'accesso alla route del server con disclaimer
# Le persone che hanno partecipato a questo progetto non hanno responsabilità
# nella raccolta dei dati di chi accede a questo servizio

@app.route("/")
def index():
    return "This server is hosting a service and every access is saved, neither the host or the team of development takes accountability for the information collected."

# Funzione per la lista dei plugin
@app.route("/plugin_list", endpoint='plugin_list', methods=["GET"])
def plug_table():
    pluginT = PlugTable.query.all()
    if pluginT is None or not pluginT:
        return "error 404, no such plugin has been found"
    return jsonify([plugin.list() for plugin in pluginT])

# Funzione per i dettagli del plugin
@app.route("/plugin_details/<int:id>", endpoint='plugin_details', methods=["GET"])
def plug_table_details(id=0):
    plugin = PlugTable.query.get(id)  # gestione dell'id tramite il metodo http GET
    if plugin is None:
        return "error 404, no such plugin has been found"
    return jsonify(plugin.get_description())  # Use the renamed method

@app.route("/test_list", endpoint='test_list', methods=["GET"])
def test_table():
    testT = Log.query.all()
    if testT is None or not testT:
        return "error 404, no such test has been found"
    return jsonify([test.list() for test in testT])

@app.route("/test_details/<int:id>", endpoint='test_details', methods=["GET"])
def test_table_details(id=0):
    test = Log.query.get(id)  # gestione dell'id tramite il metodo http GET
    if test is None:
        return "error 404, no such plugin has been found"
    return jsonify(test.to_dict())  # Use the renamed method

@app.route("/notification/<int:timestamp>", endpoint='notification', methods=["GET"])
def get_notification(timestamp):
    return jsonify(last_update-timestamp)


# Funzione per caricare il plugin
@app.route("/upload_plugin", endpoint='upload_plugin', methods=["POST"])
def new_plugin():
    global last_update
    # Get the JSON data from the request
    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({"error": "Invalid record"}), 404

    created = creaPlugin(data['name'], data['content'])
    if created:
        # Create a new plugin instance
        new_plugin = PlugTable(
            name=data['name'],
            params='',  # DEBUG
            description=''  # DEBUG
        )
        # Add the new plugin to the database
        db.session.add(new_plugin)
        db.session.commit()
        last_update = round(time.time())
        print("Updated time: "+str(last_update))
        # Return a success response
        return jsonify({"message": "Plugin uploaded successfully"}), 201
    else:
        return jsonify({"error": "Error during creation"}), 404

# Esecuzione del plugin
@app.route("/test_execute/<int:id>", endpoint='test_execute', methods=["POST"])
def plug_table_details(id=0,parametri=''):
    plugin = PlugTable.query.get(id)  # gestione dell'id tramite il metodo http GET
    if plugin is None:
        return "error 404, no such plugin has been found"
    result = avvia_plugin(plugin.name[:-3],parametri)
    logUpdate(result)
    return jsonify(result) # Use the renamed method

@app.route("/dummy", endpoint='dummy', methods=["GET"])
def dummy():
    new_plugin = PlugTable(name="")
    db.session.add(new_plugin)
    db.session.commit()
    return "the dummy has been placed"


# Funzione per modificare i dati di un plugin
@app.route("/edit_plugin/<int:id>", endpoint='edit_plugin', methods=["PATCH"])
def modifyPlugin(id=0):
    plugin = PlugTable.query.get(id)
    data = request.get_json()
    if data.description == NULL and data.name == NULL:
        return "nessun parametro passato"
    if data.name:
        plugin.name = data.name
        return "nome aggiornato"
    else:
        plugin.description = data.description
        return "descrizione aggiornata"

# Funzione per ottenere la lista dei messaggi di log
@app.route("/log_list", endpoint='log_list', methods=["GET"])
def log():
    log_entries = Log.query.all()
    if log_entries is None or not log_entries:
        return "error 404"
    return jsonify([log_entries.logList()])
# 
def logUpdate(result):
    print(type(result['datetime']))
    print(type(datetime.datetime.fromisoformat(result['datetime'])))
    newLog = Log(
        dateLog = datetime.datetime.fromisoformat(result['datetime']),
        success=(result['status']=='finished'),  # DEBUG
        result = result['log']  # DEBUG
    )
    db.session.add(newLog)
    db.session.commit()
    return void

def start():
    with app.app_context():
        db.create_all()  # This will create the tables again
    app.run(host="0.0.0.0", port=5000, debug=True)

# creaPlugin
