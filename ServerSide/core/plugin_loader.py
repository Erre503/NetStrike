import os #libreria per poter lavorare con le cartelle e file dell'applicazione
import importlib #va a sostituire la funzione manuale di import dato che non siamo a conoscenza dei nomi dei file
                 #e per rendere l'importazione dinamica
import sys  #serve per modificare a riga 38 i percorsi da cui prendere i file python
import abc
import inspect #serve per vedere i parametri
from datetime import datetime
from pathlib import Path #serve per ottenere il riferimento al percorso del file corrente

def lista_plugin(folder): #crea una lista con tutti i file python all'interno della cartella
    var = []
    for file in os.listdir(folder):
        if file[:-3] and file.endswith('.py'):
            var.append(file)
    return var

def cambiaNome(folder, nomeVecchio, nomeNuovo): #dato il nome del file da rinominare e quello nuovo, rinomina il file
    try:
        for file in os.listdir(folder):
            if file[:-3]==nomeVecchio:
                vecchioFile= os.path.join(folder, nomeVecchio+".py")
                nuovoFile= os.path.join(folder, nomeNuovo+".py")
                os.rename(vecchioFile,nuovoFile)
    except Exception:
        print("Errore: impossibile rinominare il nome del file")


def avvia_plugin(nome_plugin, vet_param): #funzione del diagramma richiesta per avviare il plugin
    try:
        modulo = importlib.import_module('plugins.'+nome_plugin)
        modulo.set_param(vet_param)
        res = {}
        res['log'] = modulo.execute()
        res['status'] = 'finished'
        res['datetime'] = datetime.now()
        return res
    except:
        return {'status':'Error', 'log': 'Error during the execution of the plugin: '+nome_plugin, 'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S')}


def creaPlugin(nome_file, contenuto):

    #aggiungo l'estensione se il nome file non la ha
    if not nome_file.endswith('.py'):
        nome_file = nome_file + ".py"

    # Percorso della cartella 'plugins'
    folder = Path(__file__).resolve().parent.parent / "plugins"

    # Percorso completo del file
    percorso_file = os.path.join(folder, nome_file)

    # Controlla se il plugin esiste già
    if nome_file in os.listdir(folder):
        print("Nome del File già presente")

    #crea il file con il contenuto passato
    with open(percorso_file, "w", encoding="utf-8") as file:
        file.write(contenuto)
        print("File " + nome_file + " creato con successo nella cartella " + str(folder)) #stringa di debug
        print(" ") #crea uno spazio per rendere l'output più carino

    try:
        nome_plugin = nome_file[:-3]  # Rimuove l'estensione .py (verificata in precedenza)
        modulo = importlib.import_module(nome_plugin)

        # Verifica che esista un elemento 'Plugin' sia presente nel modulo
        if not hasattr(modulo, "Plugin"):
            print("Errore: Il file non contiene nessun elemento 'Plugin'.")

        # Ottieni la presunta classe Plugin
        classe_plugin = getattr(modulo, "Plugin")

        # Verifica che 'Plugin' sia una classe
        if not inspect.isclass(classe_plugin):
            print("Errore: 'Plugin' non è una classe.")

        #verifica che tutti i metodi astratti siano implementati
        if isinstance(classe_plugin, abc.ABCMeta):
            if hasattr(classe_plugin, '__abstractmethods__') and len(classe_plugin.__abstractmethods__) > 0:
                print("Errore: La classe 'Plugin' è astratta e non implementa tutti i metodi richiesti.")

        return classe_plugin

    except Exception:
        print("Errore: il Plugin non appartiene alla classe 'Plugin' ")