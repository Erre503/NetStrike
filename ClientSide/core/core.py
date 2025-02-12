# Libreria per la classe UpdateType
from core.updateType import UpdateType


# Libreria per comunicare tramite i protocolli HTTP/HTTPS.
import requests
from flask import jsonify
import time
import threading
import utils.security_functions as sf
import os


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
    Inizializza il ClientCore con il server URL e il gestore dell'interfaccia utente.

    Args:
        server_url (str): URL del server a cui inoltrare le richieste.
        ui_handler (UIUpdater): Oggetto che gestisce l'aggiornamento dell'interfaccia grafica.
    """

    def __init__(self, server_url, ui_handler, username, password):
        self.server_url = server_url
        self.ui_handler = ui_handler
        self.last_update = round(time.time())
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
            print("AGGIORNA LA CAZZO DI LISTA")
        else:
            raise ValueError(f"Tipo di aggiornamento non riconosciuto: {update_type}")
        # eccetera

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
            print(url)
            if(dati != None and sanitize):
                print("Sanifying...")
                dati = sf.sanitize_dict(dati)

            print("URL:",url + "\t DATA:",dati) #DEBUG

            if metodo == "GET":
                response = requests.get(url, headers=headers)
            elif metodo == "POST":
                response = requests.post(url, json=dati, headers=headers)
            elif metodo == "PATCH":
                response = requests.patch(url, json=dati, headers=headers)
            else:
                raise ValueError("Metodo HTTP non supportato.")

            if response.status_code == 200:
                ret = response.json()
                if(isinstance(ret, list)):
                    ret = sf.sanitize_list(ret)
                else:
                    ret = sf.sanitize_dict(ret)
            else:
                response = sf.sanitize_dict(response)
                print(f"Errore: {response.status_code}: {response.text}")

        except Exception as e:
            e = sf.sanitize_input(e)
            print(f"Errore durante la richiesta: {e}")

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
        token = self.invia_richiesta('/login', 'POST', {'username': username, 'password': password})['access_token']
        if token:
            sf.save_token(token)
            return token
        print('Errore di autenticazione')


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
        success = self.invia_richiesta('/register', 'POST', {'username': username, 'password': password})
        if success:
            print('Registrato con successo')
            self.login(username, password)
        else:
            print('Errore di registrazione')

    """
    Esegue il logout dell'utente, rimuovendo il token di autenticazione.

    Effetti:
        - Elimina il token JWT salvato utilizzando la funzione `clear_token`.
        - Stampa un messaggio di conferma che indica che il logout è stato effettuato con successo.
    """
    def logout(self):
        sf.clear_token()
        print("Logout effettuato con successo.")


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
        print(risultati) #DEBUG
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
                self.invia_richiesta('/upload_plugin', 'POST', {'content': file.read(), 'name': os.path.basename(file_path)}, False)
            self.ottieni_lista_plugin()
        except Exception as e:
            print(f"Errore durante il caricamento del plugin: {e}")

    """
    Modifica un plugin presente nel server.

    Args:
        id_plugin (str): L'ID del plugin da modificare.
        data (str): Il nuovo valore per il campo specificato (nome o descrizione).
        is_name (bool, opzionale): Se True, modifica il nome del plugin;
                                    altrimenti modifica la descrizione.
                                    Default: False.

    Effetti:
        - Invia una richiesta PATCH all'endpoint '/edit_plugin/<id_plugin>' con
          i dati aggiornati.
        - Specifica il campo da modificare (nome o descrizione) in base al valore di `is_name`.
    """
    def modifica_plugin(self, id_plugin, data, is_name=False):
        self.invia_richiesta('/edit_plugin/'+id_plugin, 'PATCH', { 'name' if is_name else 'description': data })

    """
    Avvia un thread separato per il polling delle notifiche dal server.

    Effetti:
        - Crea e avvia un thread in modalità daemon per eseguire la funzione `poll_notifications`
          senza bloccare il flusso principale del programma.
        - Il thread esegue continuamente il polling delle notifiche finché il programma è attivo.
    """
    def start_polling(self):
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
            dati = self.invia_richiesta("/notification/"+str(self.last_update))["update"]
            if dati != None and dati > 0:
                self.last_update = dati
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
        # Estrarre le informazioni (presenza di valori di default se mancanti)
        status = results.get("status", "unknown")
        log = results.get("log", "")
        datetime = results.get("datetime", "N/A")

        # Visualizzare i dati nella UI
        self.ui.mostra_risultato_test(
            status=status,
            log=log,
            datetime=datetime
        )
