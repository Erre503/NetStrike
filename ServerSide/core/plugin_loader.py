import os  # Libreria per operare con file e cartelle
import importlib  # Per importare dinamicamente moduli senza conoscere i loro nomi
import sys  # Per modificare il percorso da cui importare i file Python
from datetime import datetime
from pathlib import Path  # Per ottenere il percorso assoluto della cartella corrente


# Funzione che carica un plugin dal folder "plugins" e lo esegue se esistente
def caricaPlugin(nome_plugin):

    if (nome_plugin.endswith('.py')):  # Se il nome del file finisce con .py, rimuove l'estensione
        nome_plugin = nome_plugin[:-3]

    guardia = False
    for file in os.listdir('.plugins'):  # Esamina tutti i file nella cartella "plugins"
        if nome_plugin == file[:-3]:  # Se il nome del file corrisponde
            modulo = importlib.import_module(nome_plugin)  # Importa dinamicamente il modulo
            guardia = True

    if (guardia):  # Se il file è stato trovato e importato
        return modulo  # Ritorna il modulo importato
    else:
        print("File NON trovato")  # Se il file non è trovato, stampa un messaggio di errore
        return None


# Funzione che restituisce una lista di tutti i file Python nella cartella "plugins"
def lista_plugin():
    vet = []  # Lista che conterrà i nomi dei file Python
    for file in os.listdir(folder):  # Esamina tutti i file nella cartella "plugins"
        if file[:-3] and file.endswith('.py'):  # Se il file è un file Python
            vet.append(file)  # Aggiunge il nome del file alla lista
    return vet  # Restituisce la lista di file Python


# Funzione che esegue la funzione "execute" di un plugin caricato
def avvia_plugin(nome_plugin):  # funzione del diagramma richiesta per avviare il plugin
    try:
        modulo = importlib.import_module('plugins.'+nome_plugin)
        res['log'] = (modulo.execute())
        res['status'] = 'finished'
        res['datetime'] = datetime.now()
        return res
    except:
        return {'status':'Error', 'log': 'Error during the execution of the plugin: '+nome_plugin, 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}


# Funzione che crea un nuovo plugin con il contenuto specificato
def creaPlugin(nome_file, contenuto):
    if not nome_file.endswith('.py'):  # Se il nome del file non termina con ".py", lo aggiunge
        nome_file = nome_file + ".py"

    req = "def execute():"  # La funzione che il file deve contenere
    folder = Path(__file__).resolve().parent.parent / "plugins"
    # Percorso completo del file
    percorso_file = os.path.join(folder, nome_file)

    # Verifica se un file con lo stesso nome esiste già nella cartella "plugins"
    guardia = True
    for file in os.listdir(folder):
        if nome_file == file and file.endswith('.py'):  # Se il file esiste già
            guardia = False

    if (guardia):  # Se il file non esiste già
        if req in contenuto:  # Se il contenuto del file include la funzione "execute"
            with open(percorso_file, "w", encoding="utf-8") as file:  # Crea e scrive nel file
                file.write(contenuto)
            return "File " + nome_file + " creato con successo nella cartella plugins"
        else:
            return "Errore: il file non rispetta i requisiti: " + req  # Se il file non rispetta i requisiti, ritorna un errore
    else:
        return "Nome del File già presente"  # Se il file esiste già, ritorna un messaggio di errore


# Codice principale che esegue l'intero processo
if (__name__ == "__main__"):
    folder = Path(__file__).resolve().parent.parent / "plugins"  # Imposta il percorso della cartella "plugins"
    sys.path.append(str(folder))  # Aggiunge la cartella "plugins" alla lista dei percorsi di ricerca dei moduli Python

    print("Nome del Plug In da creare: ")
    nome_plugin = input()  # Chiede il nome del plugin da creare
    print(creaPlugin(nome_plugin, "def execute(): print(1)"))  # Crea il plugin con una funzione di esempio

    # Carica e stampa i nomi di tutti i plugin presenti
    for i in lista_plugin():
        print(i)

    # Carica il plugin richiesto dall'utente
    plugin = caricaPlugin()  # Viene caricato il modulo del file richiesto

    if (plugin != None):  # Se il plugin è stato trovato
        avvia_plugin(plugin)  # Esegui il plugin