#Libreria per la classe UpdateType
from enum import Enum

#Libreria per comunicare tramite i protocolli HTTP/HTTPS.
import requests

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

"""
class ClientCore:

    """
    Inizializza il ClientCore con il server URL e il gestore dell'interfaccia utente.

    Args:
        server_url (str): URL del server a cui inoltrare le richieste.
        ui_handler (object): Oggetto che gestisce l'aggiornamento dell'interfaccia grafica.
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
        if(update_type == UpdateType.LISTA_PLUGIN):
            self.ui_handler.update_list(data)
        elif(update_type == UpdateType.DETTAGLI_PLUGIN):
            self.ui_handler.update_details(data)
        elif(update_type == UpdateType.RISULTATI_TEST):
            self.ui_handler.update_results(data)
        else:
            raise ValueError(f"Tipo di aggiornamento non riconosciuto: {update_type}")
        #eccetera

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
            if metodo == "GET":
                response = requests.get(url)
            elif metodo == "POST":
                response = requests.post(url, json=dati)
            else:
                raise ValueError("Metodo HTTP non supportato.")

            if response.status_code == 200:
                ret = response.json()
            else:
                # Logga l'errore (opzionale) e restituisci None
                print(f"Errore: {response.status_code}: {response.text}")

        except Exception as e:
            print(f"Errore durante la richiesta: {e}")

        return ret

    """
    Ottiene la lista dei plugin disponibili dal server.

    Effetti:
       - Invia una richiesta GET all'endpoint '/plugins'.
       - Aggiorna l'interfaccia grafica con i dati ricevuti.
    """
    def ottieni_lista_plugin(self):
        dati = self.invia_richiesta('/plugins')
        if dati:
            self.aggiorna_ui(dati, UpdateType.LISTA_PLUGIN)

    """
    Ottiene i dettagli di un plugin disponibile dal server.
    
    Args:
        nome_plugin (str): Identifica il plugin di cui si richiedono i dettagli.

    Effetti:
       - Invia una richiesta POST all'endpoint '/plugin_details'.
       - Aggiorna l'interfaccia grafica con i dati ricevuti.
    """
    def ottieni_dettagli_plugin(self, nome_plugin):
        dati = self.invia_richiesta('/plugin_details', 'POST', nome_plugin)
        if dati:
            self.aggiorna_ui(dati, UpdateType.DETTAGLI_PLUGIN)

    """
    Avvia un test per un plugin specifico con i parametri forniti.
    
    Args:
        nome_plugin (str): Identifica il plugin da utilizzare per il test.
        parametri (dict): Parametri necessari per il test.
    
    Effetti:
        - Invia una richiesta POST all'endpoint '/tests_start'.
        - Aggiorna l'interfaccia con il risultato del test.
    """
    def avvia_test(self, nome_plugin, parametri):
        payload = {"nome_plugin": nome_plugin, "parametri": parametri}
        risultati  = self.invia_richiesta('/tests_start', 'POST', payload)
        if risultati:
            self.aggiorna_ui(risultati, UpdateType.RISULTATI_TEST)

    """
    Salva i risultati di un test.
    
    Args:
        nome_plugin (str): Identifica il plugin che si e' utilizzato per il test.
        risultati (dict): Risultati del test.
    
    Effetti:
        - Invia una richiesta POST all'endpoint '/tests_save'.
        - Aggiorna l'interfaccia con il risultato del test.
    """
    def salva_risultati(self, nome_plugin, risultati):
        payload = {"nome_plugin": nome_plugin, "risultati": risultati}
        conferma = self.invia_richiesta('/tests_save', 'POST', payload)
        if conferma:
            self.aggiorna_ui(conferma, UpdateType.SALVATAGGIO_RISULTATI)


#Piccolo test (ancora da completare)
if(__name__ == "__main__"):
    i = ""
    c = ClientCore('http://127.0.0.1/', None)
    while(i != "exit"):
        i = input("Enter command: ")
        if(i =='0'):
            print(c.aggiorna_ui(None, UpdateType.RISULTATI_TEST))
        elif(i == '1'):
            print(c.invia_richiesta(None))