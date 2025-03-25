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
            self.ui.aggiungi_plugin(plugin["name"], str(plugin["id"]))

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
