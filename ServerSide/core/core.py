# Entry point of the service
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
import ast

# Initialize Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'  # Database URI for SQLite
db = SQLAlchemy(app)  # Initialize SQLAlchemy

# Configure JWT for authentication
app.config['JWT_SECRET_KEY'] = KeyManager.generate_key()  # Generate a secret key for JWT
jwt = JWTManager(app)  # Initialize JWTManager

# Variable to track the last update timestamp
last_update = round(time.time())

# Database table classes:

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

    def get_description(self):  # Renamed method for clarity
        return {
            'params': self.params,
            'description': self.description
        }

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
            'id': self.idLog,
            'name': self.dateLog.strftime('%Y-%m-%d %H:%M:%S')
        }

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
    params = db.Column(db.String(300), default="")
    script_id = db.Column(db.Integer, db.ForeignKey(PlugTable.id), nullable=False)

    def __repr__(self):
        return f"<Routine> \nid: {self.id}\nfrequency: {self.frequency}\nscript_id: {self.script_id}\nparams: {self.params}"

    def info(self):
        return frequency, params, script_id

# Default output for server access
@app.route("/")
@jwt_required()
def index():
    return "This server is hosting a service and every access is saved, neither the host or the team of development takes accountability for the information collected."

# Login route for user authentication
@app.route("/login", endpoint='login', methods=["POST"])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    print("username: "+username+"\tpassword: "+password)  # DEBUG
    if(username != "test" or password != "password"):
        print("Login failed")  # DEBUG
        return jsonify({'msg': 'Error, login failed'}), 401

    access_token = create_access_token(identity=username)  # Create JWT token
    print('AccessToken: '+access_token)  # DEBUG
    return jsonify(access_token=access_token), 200

# Function to get the list of plugins
@app.route("/script_list", endpoint='script_list', methods=["GET"])
@jwt_required()
def script_list():
    pluginT = PlugTable.query.all()  # Query all plugins
    if pluginT is None or not pluginT:
        return jsonify({"error": "Error 404, no such plugin has been found."}), 404
    return jsonify([plugin.list() for plugin in pluginT]), 200  # Return list of plugins

# Function to get details of a specific plugin
@app.route("/script_details/<int:id>", endpoint='script_details', methods=["GET"])
@jwt_required()
def script_details(id=0):
    plugin = PlugTable.query.get(id)  # Get plugin by ID
    if plugin is None:
        return jsonify({"error": "Error 404, no such plugin has been found."}), 404
    return jsonify(plugin.get_description()), 200  # Return plugin details

# Function to get the list of tests
@app.route("/test_list", endpoint='test_list', methods=["GET"])
@jwt_required()
def test_list():
    testT = Log.query.all()  # Query all logs
    if testT is None or not testT:
        return jsonify({"error": "Error 404, no such test has been found."}), 404
    return jsonify([test.logList() for test in testT]), 200  # Return list of tests

# Function to get details of a specific test
@app.route("/test_details/<int:id>", endpoint='test_details', methods=["GET"])
@jwt_required()
def test_details(id=0):
    test = Log.query.get(id)  # Get test by ID
    if test is None:
        return jsonify({"error": "Error 404, no such test has been found."}), 404
    return jsonify(test.logData()), 200  # Return test details

# Function to check for notifications based on timestamp
@app.route("/notification/<int:timestamp>", endpoint='notification', methods=["GET"])
@jwt_required()
def notification(timestamp):
    return jsonify({'update': (last_update - timestamp > 0)}), 200  # Check if there are updates

# Function to upload a new plugin
@app.route("/upload_script", endpoint='upload_script', methods=["POST"])
@jwt_required()
def upload_script():
    global last_update
    data = request.get_json()  # Get JSON data from request
    if not data or 'name' not in data:
        return jsonify({"error": "Invalid record"}), 400

    success, res = creaPlugin(data['name'], data['content'])  # Create plugin
    if success:
        print("PARAMSSSSS: ", res)
        params = ", ".join(res)  # Join parameters into a string
        # Create a new plugin instance
        new_plugin = PlugTable(
            name=data['name'],
            params=params,  # DEBUG
            description=''  # DEBUG
        )
        # Add the new plugin to the database
        db.session.add(new_plugin)
        db.session.commit()
        last_update = round(time.time())  # Update last update timestamp
        print("Updated time: "+str(last_update))
        return jsonify({"message": "Plugin uploaded successfully."}), 200  # Return success response
    else:
        return jsonify({"error": "Error during creation."}), 400

# Function to execute a plugin
@app.route("/execute/<int:id>", endpoint='execute', methods=["POST"])
@jwt_required()
def execute(id=0):
    parametri = request.get_json()  # Get parameters from request
    plugin = PlugTable.query.get(id)  # Get plugin by ID
    if plugin is None:
        return jsonify({"error": "Error 404, no such plugin has been found."}), 404

    result = avvia_plugin(plugin.name, parametri)  # Execute the plugin
    logUpdate(result)  # Log the result
    return jsonify(result), 200  # Return the result

# Function to modify plugin data
@app.route("/edit_script/<int:id>", endpoint='edit_script', methods=["PATCH"])
def edit_script(id=0):
    global last_update
    plugin = PlugTable.query.get(id)  # Get plugin by ID
    data = request.get_json()  # Get JSON data from request
    data = sanitize_dict(data)  # Sanitize input data
    if data['description'] is None and data['name'] is None:
        return jsonify({"error": "No parameters passed."}), 400  # No parameters passed
    if data['name'] and rinomina_plugin(plugin.name, data['name']):
        plugin.name = data['name']  # Update plugin name
        db.session.commit()
    if data['description']:
        plugin.description = data['description']  # Update plugin description
        db.session.commit()
    last_update = round(time.time())  # Update last update timestamp
    return jsonify({"message": "Plugin edited successfully."}), 200  # Return success response

# Function to remove a plugin from the system
@app.route("/remove_script/<int:id>", endpoint='remove_script', methods=["GET"])
def remove_script(id=0):
    global last_update
    plugin = PlugTable.query.get(id)  # Get plugin by ID
    
    if not plugin:
        abort(404, description="Plugin not found")  # Return 404 if plugin does not exist

    if elimina_plugin(plugin.name):  # Attempt to remove the plugin
        PlugTable.query.filter_by(id=id).delete()  # Delete plugin from database
        db.session.commit()
        last_update = round(time.time())  # Update last update timestamp
        return jsonify({"message": "Plugin removed successfully."}), 200  # Return success response

    abort(500, description="Failed to remove the plugin")  # Return 500 if removal fails

# Function to get the list of log messages
@app.route("/log_list", endpoint='log_list', methods=["GET"])
@jwt_required()
def log_list():
    log_entries = Log.query.all()  # Query all log entries
    if log_entries is None or not log_entries:
        return jsonify({"error": "Error 404, no log entries found."}), 404  # Return 404 if no log entries found
    return jsonify([log_entry.logList() for log_entry in log_entries]), 200  # Return list of log entries

# Function to create a new routine
@app.route("/create_routine", endpoint='create_routine', methods=["POST"])
@jwt_required()
def create_routine():
    data = sanitize_dict(request.get_json())  # Get and sanitize input data

    new_routine = Routine(
        frequency=data["frequency"],
        script_id=data["script"],
        params=str(data["params"])
    )
    db.session.add(new_routine)  # Add new routine to the database
    db.session.commit()
    plugin = PlugTable.query.get(data["script"])  # Get the associated plugin
    start_routine_execution(plugin.name, data["params"], data["frequency"])  # Start routine execution
    return jsonify({"message": "Routine created successfully."}), 200  # Return success response

def start_routine_execution(script_name, vet_param, frequency_seconds):
    """
    Starts a background thread that executes the plugin at fixed intervals.

    :param script_name: str, name of the plugin script (e.g. 'example.py')
    :param vet_param: list, list of parameters to pass to the plugin
    :param frequency_seconds: int, interval between executions in seconds
    """
    def routine_runner():
        with app.app_context():
            while True:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[{timestamp}] Executing routine: {script_name}")
                logUpdate(avvia_plugin(script_name, vet_param))  # Execute the plugin and log the result

                # Wait for the next execution
                time.sleep(frequency_seconds)

    # Start the thread in the background
    t = threading.Thread(target=routine_runner, daemon=True)
    t.start()
    return True

# Function to update the log with the result of a plugin execution
def logUpdate(result):
    newLog = Log(
        dateLog=datetime.fromisoformat(str(result['datetime'])),  # Convert datetime string to datetime object
        success=(result['status'] == 'finished'),  # Check if the execution was successful
        result=result['log']  # Log the result
    )
    db.session.add(newLog)  # Add new log entry to the database
    db.session.commit()
    return None

# Function to start the application and initialize the database
def start():
    with app.app_context():
        db.create_all()  # Create the database tables
        # Start all routines
        routines = Routine.query.all()  # Query all routines
        print(len(routines))
        print(routines)
        for routine in routines:
            plugin = PlugTable.query.get(routine.script_id)  # Get the associated plugin
            start_routine_execution(plugin.name, ast.literal_eval(routine.params), routine.frequency)  # Start routine execution

    # Run the Flask application with SSL
    app.run(ssl_context=("./certificates/server.crt", "./certificates/server.key"), host="0.0.0.0", port=5000, debug=False)
