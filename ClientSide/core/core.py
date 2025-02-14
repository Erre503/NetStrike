# Libreria per la classe UpdateType
from core.updateType import UpdateType


# Libreria per comunicare tramite i protocolli HTTP/HTTPS.
import requests
from flask import jsonify
import time
import threading
import utils.security_functions as sf
import os
import logging

#Lista di endpoint di cui non loggare gli specifici dati inviati e ricevuti
PRIVATE_DATA_ENDPOINTS = ('/login', '/register')

"""
Classe principale per il lato client del core.

Questa classe si occupa di gestire la logica centrale per:
    - La comunicazione con l'interfaccia grafica per aggiornare le informazioni visualizzate.

    - L'interazione con il server (Core server-side):
        Ottenere la lista dei plugin.
        Richiedere dettagli di un plugin.
        Avviare un test.
        Salvare risultati dei test.

Attributes:
    server_url (str): URL del server a cui inoltrare le richieste.
    ui_handler (object): Oggetto che gestisce l'aggiornamento dell'interfaccia grafica.
"""


class ClientCore:
    """
    Inizializza il ClientCore con il server URL, il gestore dell'interfaccia utente,
    esegue login con le credenziali, configura il logger e avvia il poll degli aggiornamenti.

    Args:
        server_url (str): URL del server a cui inoltrare le richieste.
        ui_handler (UIUpdater): Oggetto che gestisce l'aggiornamento dell'interfaccia grafica.
        username (str): Nome utente per effettuare il login
        password (str): Password per effettuare il login
    """

    def __init__(self, server_url, ui_handler, username, password):
        self.server_url = server_url
        self.ui_handler = ui_handler
        self.last_update = round(time.time())
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
        self.start_polling()

    """
    Invoca metodi del gestore dell'interfaccia grafica per aggiornarla.

    Args:
        data (dict): Dati da visualizzare nell'interfaccia grafica.
        update_type (UpdateType): Tipo di aggiornamento richiesto.

    Eccezioni gestite:
        - Tipo di aggiornamento non riconosciuto.
    """

    def aggiorna_ui(self, data, update_type):
        if update_type == UpdateType.LISTA_PLUGIN:
            self.ui_handler.aggiorna_lista_plugin(data)
        elif update_type == UpdateType.DETTAGLI_PLUGIN:
            self.ui_handler.aggiorna_dettagli_plugin(data)
        elif update_type == UpdateType.RISULTATI_TEST:
            self.ui_handler.aggiorna_risultato_test(data)

        elif update_type == UpdateType.AGGIORNA_LISTA:
            print("AGGIORNA LA CAZZO DI LISTA") #Chage
        else:
            logging.error("Type of UIUpdate unknown: %s",update_type)

    """
    Invia una richiesta al server e gestisce la relativa risposta.

    Args:
        endpoint (str): Endpoint specifico del server (es. '/plugins').
        metodo (str): Metodo HTTP da usare ('GET' o 'POST').
            Default: 'GET'.
        dati (dict, opzionale): Payload da inviare in caso di richiesta POST.
            Default: None.

    Returns:
        ret (dict o None):
            dict: La risposta decodificata in formato JSON se la richiesta è riuscita.
            None: Se c'è stato un errore o il server ha restituito una risposta non valida.

    Eccezioni gestite:
        - Timeout e errori di connessione.
        - Risposte non valide dal server.

    Note:
        La funzione converte automaticamente i dati in formato JSON per il payload POST.
    """

    def invia_richiesta(self, endpoint, metodo="GET", dati=None, sanitize=True):
        ret = None
        try:
            url = f"{self.server_url}{endpoint}"
            headers = {"Authorization": f"Bearer {sf.get_token()}"}
            show_data= not(endpoint in PRIVATE_DATA_ENDPOINTS)

            if show_data:
                logging.debug("Sending %s request to %s with data: %s",metodo, url,dati)
            else:
                logging.debug("Sending %s request to %s", metodo, url)

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

            if response.status_code == 200:
                ret = response.json()
                if isinstance(ret, list):
                    ret = sf.sanitize_list(ret)
                else:
                    ret = sf.sanitize_dict(ret)
            else:
                logging.error("Error %s: %s", response.status_code, response.text)

        except Exception as e:
            logging.error("Error during request: %s", sf.sanitize_input(e))

        return ret

    """
    Esegue il login dell'utente utilizzando le credenziali fornite.

    Args:
        username (str): Il nome utente dell'utente che desidera effettuare il login.
        password (str): La password dell'utente.

    Returns:
        str or None:
            Il token JWT se l'autenticazione ha successo, altrimenti None.

    Effetti:
        - Invia una richiesta POST all'endpoint '/login' con le credenziali dell'utente.
        - Se l'autenticazione ha successo, salva il token JWT utilizzando la funzione `save_token`.
        - Stampa un messaggio di errore in caso di autenticazione fallita.
    """
    def login(self, username, password):
        logging.info("Attempting to log in user: %s", username)
        token = self.invia_richiesta('/login', 'POST', {'username': username, 'password': password}, False)['access_token']
        if token:
            sf.save_token(token)
            logging.info("User %s logged in successfully.", username)
            return token
        logging.warning("Authentication failed for user: %s", username)




    """
    Registra un nuovo utente con le credenziali fornite.

    Args:
        username (str): Il nome utente da registrare.
        password (str): La password da associare al nuovo utente.

    Effetti:
        - Invia una richiesta POST all'endpoint '/register' con le credenziali dell'utente.
        - Se la registrazione ha successo, esegue il login dell'utente.
        - Stampa un messaggio di errore in caso di registrazione fallita.
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
    Esegue il logout dell'utente, rimuovendo il token di autenticazione.

    Effetti:
        - Elimina il token JWT salvato utilizzando la funzione `clear_token`.
        - Stampa un messaggio di conferma che indica che il logout è stato effettuato con successo.
    """
    def logout(self):
        sf.clear_token()
        logging.info("Logout effettuato con successo.")

    """
    Ottiene la lista dei plugin disponibili dal server.

    Effetti:
       - Invia una richiesta GET all'endpoint '/plugin_list'.
       - Aggiorna l'interfaccia grafica con i dati ricevuti.
    """

    def ottieni_lista_plugin(self):
        dati = self.invia_richiesta('/plugin_list')
        if dati:
            self.last_update = round(time.time())
            self.aggiorna_ui(dati, UpdateType.LISTA_PLUGIN)

    """
    Ottiene i dettagli di un plugin disponibile dal server.

    Args:
        id_plugin (id): Identifica il plugin di cui si richiedono i dettagli.

    Effetti:
       - Invia una richiesta GET all'endpoint '/plugin_details/<id_plugin>'.
       - Aggiorna l'interfaccia grafica con i dati ricevuti.
    """

    def ottieni_dettagli_plugin(self, id_plugin):
        dati = self.invia_richiesta('/plugin_details/'+id_plugin)
        if dati:
            self.aggiorna_ui(dati, UpdateType.DETTAGLI_PLUGIN)

    """
    Ottiene la lista dei test eseguiti.

    Effetti:
       - Invia una richiesta GET all'endpoint '/test_list'.
       - Aggiorna l'interfaccia grafica con i dati ricevuti.
    """

    def ottieni_lista_test(self):
        dati = self.invia_richiesta('/test_list')
        if dati:
            self.aggiorna_ui(dati, UpdateType.LISTA_TEST)

    """
    Ottiene i dettagli di un test eseguito.

    Args:
        id_test (id): Identifica il test di cui si richiedono i dettagli.

    Effetti:
       - Invia una richiesta GET all'endpoint '/test_details/<id_test>'.
       - Aggiorna l'interfaccia grafica con i dati ricevuti.
    """

    def ottieni_dettagli_test(self, id_test):
        dati = self.invia_richiesta('/test_details/'+id_test)
        if dati:
            self.aggiorna_ui(dati, UpdateType.DETTAGLI_TEST)

    """
    Esegui un test per un plugin specifico con i parametri forniti.

    Args:
        id_plugin (id): Identifica il plugin da utilizzare per il test.
        parametri (dict): Parametri necessari per il test.

    Effetti:
        - Invia una richiesta POST all'endpoint '/test_execute/<id_plugin>'.
        - Aggiorna l'interfaccia con il risultato del test.
    """

    def avvia_test(self, id_plugin, parametri):
        risultati = self.invia_richiesta('/test_execute/'+id_plugin, 'POST', parametri)
        if risultati:
            self.aggiorna_ui(risultati, UpdateType.RISULTATI_TEST)

    """
    Aggiunge un plugin al server inviando un file .py.

    Args:
        file_path (str): Il percorso del file .py da caricare.

    Effetti:
        - Invia una richiesta POST all'endpoint '/upload_plugin'.
    """

    def aggiungi_plugin(self, file_path):
        try:
            with open(file_path, 'r') as file:
                if(sf.is_valid_input(os.path.basename(file_path))):
                    self.invia_richiesta('/upload_plugin', 'POST', {'content': file.read(), 'name': os.path.basename(file_path)}, False)
                else:
                    logging.error("Nome file contiene valori non consentiti.")

            self.ottieni_lista_plugin()
        except Exception as e:
            logging.error(f"Errore durante il caricamento del plugin: {e}")

    """
    Modifica un plugin presente nel server.

    Args:
        id_plugin (str): L'ID del plugin da modificare.
        name (str, opzionale): Il nuovo valore per il campo nome, impostato a default None.
        description (str, opzionale): Il nuovo valore per il campo descrizione, impostato a default None.

    Effetti:
        - Invia una richiesta PATCH all'endpoint '/edit_plugin/<id_plugin>' con
          i dati modificati.
    """
    def modifica_plugin(self, id_plugin, name=None, description=None):
        if(sf.is_valid_input(name) and sf.is_valid_input(description)):
            self.invia_richiesta('/edit_plugin/'+id_plugin, 'PATCH', { 'name':name, 'description': description })
        else:
            logging.error("Valori inseriti non consentiti.")

    """
    Modifica un test presente nel server.

    Args:
        id_test (str): L'ID del test da modificare.
        name (str): Il nuovo valore per il campo nome.

    Effetti:
        - Invia una richiesta PATCH all'endpoint '/edit_test/<id_test>' con
          i dati modificati.
    """
    def modifica_test(self, id_test, name):
        if(sf.is_valid_input(name)):
            self.invia_richiesta('/edit_test/'+id_test, 'PATCH', {'name':name})
        else:
            logging.error("Valori inseriti non consentiti.")

    """
    Crea una routine che esegue il plugin 'id_plugin' ogni 'frequenza' giorni con i parametri specificati.

    Args:
        id_plugin(str): L'ID del plugin da eseguire.
        parametri(dict): Paramertri necessari per il test.
        frequenza(int): Numero di giorni ogni quanto eseguire il plugin specificato.
    """
    def crea_routine(self, id_plugin, parametri, frequenza):
        risultati = self.invia_richiesta('/set_routine', 'POST', {'id_plugin':id_plugin, 'parametri':parametri, 'frequenza':frequenza})
        if risultati:
            self.aggiorna_ui(risultati, UpdateType.RISULTATI_TEST)    

    """
    Avvia un thread separato per il polling delle notifiche dal server.

    Effetti:
        - Crea e avvia un thread in modalità daemon per eseguire la funzione `poll_notifications`
          senza bloccare il flusso principale del programma.
        - Il thread esegue continuamente il polling delle notifiche finché il programma è attivo.
    """
    def start_polling(self):
        logging.info("Starting polling for notifications.")
        polling_thread = threading.Thread(target=self.poll_notifications)
        polling_thread.daemon = True
        polling_thread.start()

    """
    Esegue il polling periodico per verificare la presenza di nuove notifiche dal server.

    Effetti:
        - Invia richieste periodiche all'endpoint '/notification/<last_update>'.
        - Se vengono ricevute nuove notifiche, aggiorna lo stato locale e l'interfaccia utente.

    Logica:
        - Esegue un ciclo infinito che:
            1. Invia una richiesta GET al server fornendo il timestamp dell'ultimo aggiornamento ricevuto ('last_update').
            2. Se il server risponde con dati significativi, aggiorna `self.last_update`.
            3. Richiama il metodo `aggiorna_ui` per notificare la ricezione dei nuovi dati.
            4. Attende 5 secondi prima della successiva richiesta.
    """
    def poll_notifications(self):
        while True:
            logging.debug("Polling for notifications...")
            dati = self.invia_richiesta("/notification/"+str(self.last_update))["update"]
            if dati is not None and dati > 0:
                self.last_update = dati
                logging.info("Received new notifications, updating UI.")
                self.aggiorna_ui('', UpdateType.AGGIORNA_LISTA)
            time.sleep(5)



"""
Gestisce l'aggiornamento dell'interfaccia grafica.

Questa classe fornisce metodi per aggiornare diversi elementi
dell'interfaccia utente, come la lista dei plugin, i dettagli di un
plugin selezionato e i risultati dei test eseguiti.

Attributi:
    ui: Un riferimento all'interfaccia grafica da aggiornare.
        Questo oggetto rappresenta il framework UI utilizzato, come
        PyQt, Tkinter o un altro sistema di interfaccia grafica.
"""
class UIUpdater:
    """
    Inizializza un'istanza di UIUpdater.

    Args:
        ui: Il riferimento all'interfaccia grafica che sarà aggiornata
            tramite i metodi di questa classe.
    """
    def __init__(self):
        self.ui = None

    """
    Associa l'interfaccia grafica all'istanza di UIUpdater.

    Args:
        ui: Istanza della UI che verrà aggiornata dai metodi di questa classe.

    Effetti:
        - L'attributo `ui` viene aggiornato per puntare alla UI specificata.
    """
    def initUI(self, ui):
        self.ui = ui

    """
    Aggiorna la lista dei plugin nell'interfaccia grafica.

    Args:
        plugins (dict): Dati per aggiornare la lista dei plugin.
            Struttura attesa:
            - name (str): Nome del plugin.
            - id (str): ID univoco del plugin.
    """
    def aggiorna_lista_plugin(self, plugins):
        self.ui.svuota_lista_plugin()

        for plugin in plugins:
            self.ui.aggiungi_plugin(plugin["name"], plugin["id"])

    """
    Mostra i dettagli di un plugin selezionato nell'interfaccia grafica.

    Args:
        plugin_details (dict): Un dizionario contenente i dettagli del plugin.
            Struttura attesa:
            - description (str): Descrizione del plugin.
            - parameters (dict, opzionale): Parametri del plugin come chiave-valore.
    """
    def aggiorna_dettagli_plugin(self, plugin_details):
        self.ui.mostra_dettagli_plugin(
            description=plugin_details["description"],
            parameters=plugin_details.get("params", {})  # Parametri opzionali
        )

    """
    Mostra i risultati di un test eseguito nell'interfaccia grafica.

    Args:
        results (dict): Un dizionario contenente i risultati del test.
            Struttura attesa:
            - status (str): Stato del test (es. "success", "failed").
            - log (str): Log dettagliato del test.
            - datetime (str): Timestamp del test formattato (es. "YYYY-MM-DD HH:MM:SS").
    """
    def aggiorna_risultato_test(self, results):
        status = results.get("status", "unknown")
        log = results.get("log", "")
        datetime = results.get("datetime", "N/A")

        self.ui.mostra_risultato_test(
            status=status,
            log=log,
            datetime=datetime
        )
