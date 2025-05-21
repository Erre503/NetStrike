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
    Aggiorna la lista nell'interfaccia grafica.

    Args:
        items (dict): Dati per aggiornare la lista.
            Struttura attesa:
            - name (str): Nome.
            - id (str): ID univoco.
    """
    def aggiorna_lista(self, items):
        self.ui.svuota_lista()

        for item in items:
            self.ui.aggiungi_elemento(item["name"], str(item["id"]))

    """
    Mostra i dettagli dell'elemento selezionato nell'interfaccia grafica.

    Args:
        details (dict): Un dizionario contenente i dettagli.
            Struttura attesa:
            - description (str): Descrizione.
            - parameters (dict, opzionale): Parametri come chiave-valore.
    """
    def aggiorna_dettagli(self, details):
        self.ui.mostra_dettagli(details)

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

    def notifica(self):
        self.ui.notifica()
