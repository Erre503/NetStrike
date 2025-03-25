from enum import Enum
import os

"""
Enumeratore che definisce i tipi di aggiornamenti per l'interfaccia grafica.

Questo enumeratore viene utilizzato per identificare il tipo di aggiornamento da effettuare
nell'interfaccia grafica, consentendo al core client-side di comunicare chiaramente con
il gestore dell'interfaccia (UI handler).

Membri:
    LISTA_PLUGIN (str): Indica che l'interfaccia deve aggiornare la lista dei plugin.
    DETTAGLI_PLUGIN (str): Indica che l'interfaccia deve mostrare i dettagli di un plugin.
    LISTA_TEST (str): Indica che l'interfaccia deve aggiornare la lista dei test.
    DETTAGLI_TEST (str): Indica che l'interfaccia deve mostrare i dettagli di un test.
    RISULTATI_TEST (str): Indica che l'interfaccia deve visualizzare i risultati di un test.
"""


class UpdateType(Enum):
    LISTA_PLUGIN = 0
    DETTAGLI_PLUGIN = 1
    LISTA_TEST = 2
    DETTAGLI_TEST = 3
    RISULTATI_TEST = 4
