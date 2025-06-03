# Import necessary libraries for the ClientCore class
from core.updateType import UpdateType
from core.ui_updater import UIUpdater
import requests
from flask import jsonify
import time
import threading
import utilities.security_functions as sf
import os
import logging

# List of endpoints for which specific data sent and received should not be logged
PRIVATE_DATA_ENDPOINTS = ('/login', '/register')

"""
Main class for the client-side core.

This class manages the central logic for:
    - Communication with the graphical interface to update displayed information.
    - Interaction with the server (Core server-side):
        - Obtaining the list of plugins.
        - Requesting details of a plugin.
        - Starting a test.
        - Saving test results.

Attributes:
    server_url (str): URL of the server to which requests are forwarded.
    ui_handler (object): Object that manages the update of the graphical interface.
"""
class ClientCore:
    """
    Initializes the ClientCore with the server URL, UI handler,
    logs in with credentials, configures the logger, and starts polling for updates.

    Args:
        server_url (str): URL of the server to which requests are forwarded.
        ui_handler (UIUpdater): Object that manages the update of the graphical interface.
        username (str): Username for login.
        password (str): Password for login.
    """
    def __init__(self, server_url, ui_handler, username, password):
        self.server_url = server_url
        self.ui_handler = ui_handler
        self.last_update = round(time.time())
        self.poll = False
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler("app.log"),
                logging.StreamHandler()
            ]
        )
        logging.info("Application started.")
        logging.info("ClientCore initialized with server URL: %s", server_url)
        self.login(username, password)

    """
    Invokes methods of the UI handler to update the interface.

    Args:
        data (dict): Data to be displayed in the graphical interface.
        update_type (UpdateType): Type of update requested.

    Exceptions handled:
        - Unrecognized update type.
    """
    def aggiorna_ui(self, data, update_type):
        if update_type == UpdateType.LISTA:
            self.ui_handler.aggiorna_lista(data)
        elif update_type == UpdateType.DETTAGLI:
            self.ui_handler.aggiorna_dettagli(data)
        elif update_type == UpdateType.AGGIORNA_LISTA:
            self.ui_handler.notifica()
        elif update_type == UpdateType.RISULTATI_TEST:
            self.ui_handler.aggiorna_risultato_test(data)
        else:
            logging.error("Type of UIUpdate unknown: %s", update_type)

    """
    Sends a request to the server and handles the corresponding response.

    Args:
        endpoint (str): Specific server endpoint (e.g., '/script_list').
        metodo (str): HTTP method to use ('GET' or 'POST').
            Default: 'GET'.
        dati (dict, optional): Payload to send in case of a POST request.
            Default: None.

    Returns:
        ret (dict or None):
            dict: The decoded JSON response if the request was successful.
            None: If there was an error or the server returned an invalid response.

    Exceptions handled:
        - Timeout and connection errors.
        - Invalid responses from the server.

    Notes:
        The function automatically converts data to JSON format for the POST payload.
    """
    def invia_richiesta(self, endpoint, metodo="GET", dati=None, sanitize=True):
        ret = None
        try:
            url = f"{self.server_url}{endpoint}"
            headers = {"Authorization": f"Bearer {sf.get_token()}"}

            if dati and sanitize:
                dati = sf.sanitize_dict(dati)

            show_data = not(endpoint in PRIVATE_DATA_ENDPOINTS)
            if show_data:
                logging.debug("Sending %s request to %s with data: %s", metodo, url, dati)
            else:
                logging.debug("Sending %s request to %s", metodo, url)

            # Send the appropriate HTTP request based on the method
            if metodo == "GET":
                response = requests.get(url, headers=headers, verify='./certificates/server.crt')
            elif metodo == "POST":
                response = requests.post(url, json=dati, headers=headers, verify='./certificates/server.crt')
            elif metodo == "PATCH":
                response = requests.patch(url, json=dati, headers=headers, verify='./certificates/server.crt')
            else:
                logging.error("Unsupported method: %s", metodo)
                raise ValueError("Unsupported HTTP method.")

            if show_data:
                logging.debug("Received response: %s", response.text)
            else:
                logging.debug("Received response")

            # Check the response status code
            if response.status_code == 200:
                ret = response.json()
            else:
                logging.error("Error %s: %s", response.status_code, response.text)

        except Exception as e:
            logging.error("Error during request: %s", e)

        return ret

    """
    Performs user login using the provided credentials.

    Args:
        username (str): The username of the user attempting to log in.
        password (str): The password of the user.

    Returns:
        str or None:
            The JWT token if authentication is successful, otherwise None.

    Effects:
        - Sends a POST request to the '/login' endpoint with the user's credentials.
        - If authentication is successful, saves the JWT token using the `save_token` function.
        - Prints an error message in case of failed authentication.
    """
    def login(self, username, password):
        logging.info("Attempting to log in user: %s", username)
        token = self.invia_richiesta('/login', 'POST', {'username': username, 'password': password}, False)['access_token']
        if token:
            sf.save_token(token)
            logging.info("User  %s logged in successfully.", username)
            return token
        logging.warning("Authentication failed for user: %s", username)

    """
    Registers a new user with the provided credentials.

    Args:
        username (str): The username to register.
        password (str): The password to associate with the new user.

    Effects:
        - Sends a POST request to the '/register' endpoint with the user's credentials.
        - If registration is successful, logs in the user.
        - Prints an error message in case of failed registration.
    """
    def register(self, username, password):
        logging.info("Attempting to register user: %s", username)
        success = self.invia_richiesta('/register', 'POST', {'username': username, 'password': password}, False)
        if success:
            logging.info("Registration successful for user: %s", username)
            self.login(username, password)
        else:
            logging.warning("Registration failed for user: %s", username)

    """
    Logs out the user by removing the authentication token.

    Effects:
        - Deletes the saved JWT token using the `clear_token` function.
        - Prints a confirmation message indicating that the logout was successful.
    """
    def logout(self):
        sf.clear_token()
        logging.info("Logout effettuato con successo.")

    """
    Obtains the list of available plugins from the server.

    Effects:
       - Sends a GET request to the '/script_list' endpoint.
       - Updates the graphical interface with the received data.
    """
    def ottieni_lista_plugin(self):
        dati = self.invia_richiesta('/script_list')
        if dati:
            self.last_update = round(time.time())
            self.aggiorna_ui(dati, UpdateType.LISTA)

    """
    Obtains the details of an available plugin from the server.

    Args:
        id_plugin (id): Identifies the plugin for which details are requested.

    Effects:
       - Sends a GET request to the '/script_details/<id_plugin>' endpoint.
       - Updates the graphical interface with the received data.
    """
    def ottieni_dettagli_plugin(self, id_plugin):
        dati = self.invia_richiesta('/script_details/' + id_plugin)
        if dati:
            self.aggiorna_ui(dati, UpdateType.DETTAGLI)

    """
    Obtains the list of executed tests.

    Effects:
       - Sends a GET request to the '/test_list' endpoint.
       - Updates the graphical interface with the received data.
    """
    def ottieni_lista_test(self):
        dati = self.invia_richiesta('/test_list')
        if dati:
            self.aggiorna_ui(dati, UpdateType.LISTA)

    """
    Obtains the details of an executed test.

    Args:
        id_test (id): Identifies the test for which details are requested.

    Effects:
       - Sends a GET request to the '/test_details/<id_test>' endpoint.
       - Updates the graphical interface with the received data.
    """
    def ottieni_dettagli_test(self, id_test):
        dati = self.invia_richiesta('/test_details/' + id_test)
        if dati:
            self.aggiorna_ui(dati, UpdateType.DETTAGLI)

    """
    Obtains details based on the provided ID and type.

    Args:
        id (str): The ID of the item (plugin or test).
        type (str): The type of item ('plugin' or 'test').

    Effects:
        - Calls the appropriate method to obtain details based on the type.
    """
    def ottieni_dettagli(self, id, type):
        if type == 'plugin':
            self.ottieni_dettagli_plugin(id)
        else:
            self.ottieni_dettagli_test(id)

    """
    Executes a test for a specific plugin with the provided parameters.

    Args:
        id_plugin (id): Identifies the plugin to be used for the test.
        parametri (dict): Parameters required for the test.

    Effects:
        - Sends a POST request to the '/execute/<id_plugin>' endpoint.
        - Updates the interface with the test result.
    """
    def avvia_test(self, id_plugin, parametri):
        risultati = self.invia_richiesta('/execute/' + id_plugin, 'POST', parametri)
        if risultati:
            self.aggiorna_ui(risultati, UpdateType.RISULTATI_TEST)

    """
    Adds a plugin to the server by uploading a .py file.

    Args:
        file_path (str): The path of the .py file to upload.

    Effects:
        - Sends a POST request to the '/upload_script' endpoint.
    """
    def aggiungi_elemento(self, file_path):
        try:
            with open(file_path, 'r') as file:
                name = os.path.basename(file_path)
                parts = name.split('.')
                if len(parts) == 2 and sf.is_valid_input(parts[0]):
                    self.invia_richiesta('/upload_script', 'POST', {'content': file.read(), 'name': name}, sanitize=False)
                else:
                    logging.error("Nome file contiene valori non consentiti.")

            self.ottieni_lista_plugin()
        except Exception as e:
            logging.error(f"Errore durante il caricamento del plugin: {e}")

    """
    Modifies an existing plugin on the server.

    Args:
        id_plugin (str): The ID of the plugin to modify.
        name (str, optional): The new value for the name field, default is None.
        description (str, optional): The new value for the description field, default is None.

    Effects:
        - Sends a PATCH request to the '/edit_plugin/<id_plugin>' endpoint with the modified data.
    """
    def modifica_plugin(self, id_plugin, name=None, description=None):
        # INPUT VALUES ARE NOT BEING VERIFIED
        dati = self.invia_richiesta('/edit_script/' + id_plugin, 'PATCH', {'name': name, 'description': description})
        if dati:
            self.aggiorna_ui(dati, UpdateType.LISTA)

    """
    Removes a plugin from the server.

    Args:
        id_plugin (str): The ID of the plugin to remove.

    Effects:
        - Sends a GET request to the '/remove_script/<id_plugin>' endpoint.
        - Updates the plugin list after removal.
    """
    def rimuovi_plugin(self, id_plugin):
        self.invia_richiesta('/remove_script/' + id_plugin, 'GET')
        self.ottieni_lista_plugin()

    """
    Modifies an existing test on the server.

    Args:
        id_test (str): The ID of the test to modify.
        name (str): The new value for the name field.

    Effects:
        - Sends a PATCH request to the '/edit_test/<id_test>' endpoint with the modified data.
    """
    def modifica_test(self, id_test, name):
        if sf.is_valid_input(name):
            self.invia_richiesta('/edit_test/' + id_test, 'PATCH', {'name': name})
        else:
            logging.error("Valori inseriti non consentiti.")

    """
    Creates a routine that executes the specified plugin every 'frequency' days with the given parameters.

    Args:
        id_plugin (str): The ID of the plugin to execute.
        parametri (dict): Parameters required for the test.
        frequenza (int): Number of days to execute the specified plugin.
        primo_dt (datetime): Date and time of the first execution (subsequent executions will occur at the same time).
    """
    def crea_routine(self, id_plugin, params, frequency, first_dt):
        risultati = self.invia_richiesta('/create_routine', 'POST', {'script': id_plugin, 'params': params, 'frequency': frequency, 'first_dt': first_dt})
        if risultati:
            self.aggiorna_ui(risultati, UpdateType.RISULTATI_TEST)

    """
    Starts a separate thread for polling notifications from the server.

    Effects:
        - Creates and starts a daemon thread to execute the `poll_notifications` function
          without blocking the main program flow.
        - The thread continuously polls for notifications as long as the program is active.
    """
    def start_polling(self):
        logging.info("Starting polling for notifications.")
        self.poll = True
        polling_thread = threading.Thread(target=self.poll_notifications)
        polling_thread.daemon = True
        polling_thread.start()

    """
    Executes periodic polling to check for new notifications from the server.

    Effects:
        - Sends periodic requests to the endpoint '/notification/<last_update>'.
        - If new notifications are received, updates the local state and the user interface.

    Logic:
        - Executes an infinite loop that:
            1. Sends a GET request to the server providing the timestamp of the last update received ('last_update').
            2. If the server responds with significant data, updates `self.last_update`.
            3. Calls the `aggiorna_ui` method to notify the receipt of new data.
            4. Waits 5 seconds before the next request.
    """
    def poll_notifications(self):
        while self.poll:
            logging.debug("Polling for notifications...")
            dati = self.invia_richiesta("/notification/" + str(self.last_update))["update"]
            if dati is not None and dati:
                self.last_update = round(time.time())
                logging.info("Received new notifications, updating UI.")
                self.aggiorna_ui('', UpdateType.AGGIORNA_LISTA)
            time.sleep(5)

    """
    Stops the polling for notifications.

    Effects:
        - Sets the polling flag to False, stopping the polling thread.
    """
    def stop_polling(self):
        self.poll = False
