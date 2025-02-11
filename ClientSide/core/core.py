# Libreria per la classe UpdateType
import os
from enum import Enum

# Libreria per comunicare tramite i protocolli HTTP/HTTPS.
import requests
from flask import jsonify

"""
Enumeratore che definisce i tipi di aggiornamenti per l'interfaccia grafica.

Questo enumeratore viene utilizzato per identificare il tipo di aggiornamento da effettuare
nell'interfaccia grafica, consentendo al core client-side di comunicare chiaramente con
il gestore dell'interfaccia (UI handler).

Membri:
    PLUGIN_LIST (str): Indica che l'interfaccia deve aggiornare la lista dei plugin.
    PLUGIN_DETAILS (str): Indica che l'interfaccia deve mostrare i dettagli di un singolo plugin.
    TEST_RESULTS (str): Indica che l'interfaccia deve visualizzare i risultati di un test.
"""


class UpdateType(Enum):
    LISTA_PLUGIN = "lista_plugin"
    DETTAGLI_PLUGIN = "dettagli_plugin"
    RISULTATI_TEST = "risultati_test"
    SALVATAGGIO_RISULTATI = "salvataggio_risultati"


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

    def __init__(self, server_url, ui_handler):
        self.server_url = server_url
        self.ui_handler = ui_handler

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

    def invia_richiesta(self, endpoint, metodo="GET", dati=None):
        ret = None
        try:
            url = f"{self.server_url}{endpoint}"
            print(url)
            if metodo == "GET":
                response = requests.get(url)
            elif metodo == "POST":
                response = requests.post(url, json=dati)
            else:
                raise ValueError("Metodo HTTP non supportato.")

            if response.status_code == 200:
                ret = response.json()
            else:
                # Logga l'errore e restituisci None
                print(f"Errore: {response.status_code}: {response.text}")

        except Exception as e:
            # Logga l'errore e restituisci None
            print(f"Errore durante la richiesta: {e}")

        return ret

    """
    Ottiene la lista dei plugin disponibili dal server.

    Effetti:
       - Invia una richiesta GET all'endpoint '/plugins'.
       - Aggiorna l'interfaccia grafica con i dati ricevuti.
    """

    def ottieni_lista_plugin(self):
        dati = self.invia_richiesta('/plugin_list')
        if dati:
            self.aggiorna_ui(dati, UpdateType.LISTA_PLUGIN)

    """
    Ottiene i dettagli di un plugin disponibile dal server.

    Args:
        id_plugin (id): Identifica il plugin di cui si richiedono i dettagli.

    Effetti:
       - Invia una richiesta POST all'endpoint '/plugin_details'.
       - Aggiorna l'interfaccia grafica con i dati ricevuti.
    """

    def ottieni_dettagli_plugin(self, id_plugin):
        dati = self.invia_richiesta('/plugin_details/'+id_plugin, 'GET')
        if dati:
            self.aggiorna_ui(dati, UpdateType.DETTAGLI_PLUGIN)

    """
    Avvia un test per un plugin specifico con i parametri forniti.

    Args:
        id_plugin (id): Identifica il plugin da utilizzare per il test.
        parametri (dict): Parametri necessari per il test.

    Effetti:
        - Invia una richiesta POST all'endpoint '/tests_start'.
        - Aggiorna l'interfaccia con il risultato del test.
    """

    def avvia_test(self, id_plugin, parametri):
        risultati = self.invia_richiesta('/test_execute/'+id_plugin, 'POST', parametri)
        print(risultati)
        if risultati:
            self.aggiorna_ui(risultati, UpdateType.RISULTATI_TEST)

    """
    Aggiunge un plugin al server inviando un file .py.

    Args:
        file_path (str): Il percorso del file .py da caricare.

    Effetti:
        - Invia una richiesta POST all'endpoint '/aggiungi_plugin'.
    """

    def aggiungi_plugin(self, file_path):
        try:
            with open(file_path, 'r') as file:
                self.invia_richiesta('/upload_plugin', 'POST', {'file_content': file.read(), 'name': os.path.basename(file_path)})
            self.ottieni_lista_plugin()
        except Exception as e:
            print(f"Errore durante il caricamento del plugin: {e}")


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
        self.ui.aggiornaListaPlugin()

        for plugin in plugins:
            print(plugin)
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