# Punto d'ingresso del servizio
from utilities.security_functions import *
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Sequence
from core.plugin_loader import *
import time
from datetime import datetime
from utilities.key_manager import KeyManager
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity
import threading

# from flask_classful import FlaskView, route   Prossima implementazione

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)

app.config['JWT_SECRET_KEY'] =  KeyManager.generate_key()
jwt = JWTManager(app)

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
    name = db.Column(db.String(50), nullable=False, unique=True)
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

    #CHANGE
    def logList(self):
        return {
            'id': self.idLog,
            'name': self.dateLog.strftime('%Y-%m-%d %H:%M:%S')
        }

    #CHANGE
    def logData(self):
        return {
            'success': self.success,
            'result': self.result,
            'date': self.dateLog.strftime('%Y-%m-%d %H:%M:%S')
        }

class Routine(db.Model):
    __tablename__ = "routine"
    id = db.Column(db.Integer, Sequence('id'), primary_key=True)
    frequency = db.Column(db.Integer, nullable=False)
    next_execution =db.Column(db.DateTime, default=datetime.now())
    script_id = db.Column(db.Integer, db.ForeignKey(PlugTable.id), nullable=False)
    params = db.Column(db.String(300), default="")

    def __repr__(self):
        return f"<Routine> \nid: {self.id}\nfrequency: {self.frequency}\nnext_execution: {self.next_execution}\nscript_id: {self.script_id}\nparams: {self.params}"

# Output di default

# output di default all'accesso alla route del server con disclaimer
# Le persone che hanno partecipato a questo progetto non hanno responsabilità
# nella raccolta dei dati di chi accede a questo servizio

@app.route("/")
@jwt_required()
def index():
    return "This server is hosting a service and every access is saved, neither the host or the team of development takes accountability for the information collected."

@app.route("/login", endpoint='login', methods=["POST"])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    print("username: "+username+"\tpassword: "+password) #DEBUG
    if(username != "test" or password != "password"):
        print("Login failed") #DEBUG
        return jsonify({'msg':'Error, login failed'}), 401

    access_token = create_access_token(identity=username)
    print('AccessToken: '+access_token) #DEBUG
    return jsonify(access_token=access_token), 200

# Funzione per la lista dei plugin
@app.route("/plugin_list", endpoint='plugin_list', methods=["GET"])
@jwt_required()
def plug_table():
    pluginT = PlugTable.query.all()
    if pluginT is None or not pluginT:
        return "error 404, no such plugin has been found"
    return jsonify([plugin.list() for plugin in pluginT])

# Funzione per i dettagli del plugin
@app.route("/plugin_details/<int:id>", endpoint='plugin_details', methods=["GET"])
@jwt_required()
def plug_table_details(id=0):
    plugin = PlugTable.query.get(id)  # gestione dell'id tramite il metodo http GET
    if plugin is None:
        return "error 404, no such plugin has been found"
    return jsonify(plugin.get_description())

@app.route("/test_list", endpoint='test_list', methods=["GET"])
@jwt_required()
def test_table():
    testT = Log.query.all()
    if testT is None or not testT:
        return "error 404, no such test has been found"
    return jsonify([test.logList() for test in testT])

@app.route("/test_details/<int:id>", endpoint='test_details', methods=["GET"])
@jwt_required()
def test_table_details(id=0):
    test = Log.query.get(id)  # gestione dell'id tramite il metodo http GET
    if test is None:
        return "error 404, no such plugin has been found"
    return jsonify(test.logData())  # Use the renamed method

@app.route("/notification/<int:timestamp>", endpoint='notification', methods=["GET"])
@jwt_required()
def get_notification(timestamp):
    return jsonify({'update':last_update-timestamp})


# Funzione per caricare il plugin
@app.route("/upload_plugin", endpoint='upload_plugin', methods=["POST"])
@jwt_required()
def new_plugin():
    global last_update
    # Get the JSON data from the request
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({"error": "Invalid record"}), 404

    success, res = creaPlugin(data['name'], data['content'])
    if success:
        print("PARAMSSSSS: ", res)
        params = ""
        for param in res:
            params += (param+" , ")
        params = params[:-3]
        # Create a new plugin instance
        new_plugin = PlugTable(
            name=data['name'],
            params=params,  # DEBUG
            description=''  # DEBUG
        )
        # Add the new plugin to the database
        db.session.add(new_plugin)
        db.session.commit()
        last_update = round(time.time())
        print("Updated time: "+str(last_update))
        # Return a success response
        return jsonify({"message": "Plugin uploaded successfully"}), 200
    else:
        return jsonify({"error": "Error during creation"}), 404

# Esecuzione del plugin
@app.route("/test_execute/<int:id>", endpoint='test_execute', methods=["POST"])
@jwt_required()
def test_execute(id=0):
    parametri = request.get_json()
    plugin = PlugTable.query.get(id)  # gestione dell'id tramite il metodo http GET
    if plugin is None:
        return "error 404, no such plugin has been found"

    result = avvia_plugin(plugin.name ,parametri)
    logUpdate(result)
    return jsonify(result) # Use the renamed method



# Funzione per modificare i dati di un plugin
@app.route("/edit_plugin/<int:id>", endpoint='edit_plugin', methods=["PATCH"])
def modifyPlugin(id=0):
    global last_update
    plugin = PlugTable.query.get(id)
    data = request.get_json()
    data = sanitize_dict(data)
    if data['description'] == None and data['name'] == None:
        return "nessun parametro passato"
    if data['name'] and rinomina_plugin(plugin.name, data['name']):
        plugin.name = data['name']
        db.session.commit()
    if data['description']:
       plugin.description = data['description']
       db.session.commit()
    last_update = round(time.time())
    return jsonify({"message": "Plugin edited successfully"}), 200

#Eliminare dal sistema un plugin
@app.route("/remove_plugin/<int:id>", endpoint='remove_plugin', methods=["GET"])
def modifyPlugin(id=0):
    global last_update
    plugin = PlugTable.query.get(id)
    
    if not plugin:
        abort(404, description="Plugin not found")  # Return 404 if plugin does not exist

    if elimina_plugin(plugin.name):
        PlugTable.query.filter_by(id=id).delete()
        db.session.commit()
        last_update = round(time.time())
        return jsonify({"message": "Plugin removed successfully"}), 200  # Return a JSON response with status 200

    abort(500, description="Failed to remove the plugin")  # Return 500 if elimina_plugin fails


# Funzione per ottenere la lista dei messaggi di log
@app.route("/log_list", endpoint='log_list', methods=["GET"])
@jwt_required()
def log():
    log_entries = Log.query.all()
    if log_entries is None or not log_entries:
        return "error 404"
    return jsonify([log_entries.logList()])

@app.route("/create_routine", endpoint='create_routine', methods=["POST"])
@jwt_required()
def create_routine():
    data = sanitize_dict(request.get_json())

    new_routine = Routine(
        frequency = data["frequency"],
        #next_execution = data["first_dt"],
        script_id = data["script"],
        params = str(data["params"])
    )
    db.session.add(new_routine)
    db.session.commit()
    plugin = PlugTable.query.get(data["script"])
    start_routine_execution(plugin.name, data["params"], data["frequency"], plugin.name.split('.')[1])
    return "Success",200

def start_routine_execution(script_name, vet_param, frequency_seconds, script_type):
    """
    Starts a background thread that executes the plugin at fixed intervals.

    :param script_name: str, name of the plugin script (e.g. 'example.py')
    :param vet_param: list, list of parameters to pass to the plugin
    :param frequency_seconds: int, interval between executions in seconds
    :param script_type: str, type of the script ('py', 'sh', etc.)
    """
    
    def routine_runner():
        with app.app_context():
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Executing routine: {script_name}")
                logUpdate(avvia_plugin(script_name, vet_param, script_type))

                # Wait for the next execution
                time.sleep(frequency_seconds)

    # Start the thread in the background
    t = threading.Thread(target=routine_runner, daemon=True)
    t.start()
    return True


# Update del Log
def logUpdate(result):
    newLog = Log(
        dateLog = datetime.fromisoformat(str(result['datetime'])),
        success=(result['status']=='finished'),  # DEBUG
        result = result['log']  # DEBUG
    )
    db.session.add(newLog)
    db.session.commit()
    return None



def start():
    with app.app_context():
        db.create_all()  # This will create the tables again
    app.run(ssl_context=("./certificates/server.crt", "./certificates/server.key"), host="0.0.0.0", port=5000, debug=False)

