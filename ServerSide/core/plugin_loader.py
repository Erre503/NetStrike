import os #libreria per poter lavorare con le cartelle e file dell'applicazione
import importlib #va a sostituire la funzione manuale di import dato che non siamo a conoscenza dei nomi dei file

def caricaPlugin(folder, req, nome_plugin):
    plugin = 0
    for file in os.listdir(folder):

        if nome_plugin == file[:-3] and file.endswith('.py'):

            percorso_modulo = folder + "." + nome_plugin #stringa che contiene il percorso del file
            modulo = importlib.import_module(percorso_modulo) #contenuto del file (plug in) py

            if hasattr(modulo, req):
                plugin = modulo  # Aggiungi il contetunto del file plug in nel vettore plugins
            else:
                plugin = 1

    return plugin
