import os #libreria per poter lavorare con le cartelle e file dell'applicazione
import importlib #va a sostituire la funzione manuale di import dato che non siamo a conoscenza dei nomi dei file 
                 #e per rendere l'importazione dinamica
import sys  #serve per modificare a riga 38 i percorsi da cui prendere i file python

import inspect #serve per vedere i parametri

from pathlib import Path #serve per ottenere il riferimento al percorso del file corrente

def lista_plugin(folder): #crea una lista con tutti i file python all'interno della cartella
    var = []
    for file in os.listdir(folder):
        if file[:-3] and file.endswith('.py'):
            var.append(file)
    return var

def avvia_plugin(plugin, vet_param): #funzione del diagramma richiesta per avviare il plugin

    plugin.set_param(vet_param)

    plugin.execute()
    return 

def creaPlugin(nome_file, contenuto):

    #aggiungo l'estensione se il nome file non la ha
    if not nome_file.endswith('.py'):
        nome_file = nome_file + ".py"

    #requisito file
    req = "def execute():"

    # Percorso della cartella 'plugins'
    folder = Path(__file__).resolve().parent.parent / "plugins"
    
    # Percorso completo del file
    percorso_file = os.path.join(folder, nome_file)

    # Controlla se il plugin esiste già
    if nome_file in os.listdir(folder):
        return "Nome del File già presente"

    # verifica che il file rispetta i requisiti
    if req not in contenuto:
        return "Errore: il file non rispetta i requisiti: " + req

    #crea il file con il contenuto passato
    with open(percorso_file, "w", encoding="utf-8") as file:
        file.write(contenuto)
        return "File " + nome_file + " creato con successo nella cartella " + folder

    try:
        nome_plugin = nome_file[:-3]  # Rimuove l'estensione .py (verificata in precedenza)
        modulo = importlib.import_module(nome_plugin) # importo il modulo(il file)

        # Verifica che la classe 'Plugin' sia presente nel modulo
        if not hasattr(modulo, "Plugin"):
            return "Errore: Il file non contiene una classe 'Plugin'."
        
        # Ottieni la classe Plugin
        plugin_class = getattr(modulo, "Plugin")

        # Verifica che 'Plugin' sia una classe e che implementi i metodi richiesti
        if not inspect.isclass(plugin_class):
            return "Errore: 'Plugin' non è una classe."
        
        # Controlla se la classe implementa i metodi richiesti
        required_methods = ["get_param", "execute"]
        missing_methods = [method for method in required_methods if not hasattr(plugin_class, method)]

        if missing_methods:
            return f"Errore: la classe 'Plugin' manca dei seguenti metodi: {', '.join(missing_methods)}"

        return f"File {nome_file} creato con successo nella cartella {folder} e classe Plugin verificata."

    except Exception as e:
        return f"Errore durante il caricamento del plugin: {str(e)}"

  


#funzione per i parametri dinamica - problema, info per il parametro non disponibili

#def paramPlugin(nome_plugin):
#    modulo = importlib.import_module(nome_plugin)
#    parametri = inspect.signature(modulo.execute)
#    paramVet = []
#    for param in parametri.parameters.values():
#        paramVet.append(param.name)
#    return paramVet


if(__name__ == "__main__"):
    print("Quale file PY vuoi eseguire?")
    nome_plugin = input() #il nome per fare i test e' dato in input
    req = "execute" # Requisiti: la funzione 'esegui' deve essere presente
    #creaPlugin("prova.py", "def execute(): print(1)")
    folder = Path(__file__).resolve().parent.parent / "plugins"  # assegna il percorso della cartella basandosi su quello del plugin loader
                                                                 #(Path(__file__).resolve()) per avere il percorso assoluto
    sys.path.append(str(folder))  #aggiunge la cartella folder ai percorsi da cui vengono importati i file python

    # Carica i nomi dei plugin presenti
    for i in lista_plugin(folder): 
        print(i)

    plugin = caricaPlugin(folder, req, nome_plugin) #viene caricato il modulo del file richiesto in una variabile per poter essere eseguita

    if(plugin!=None):#se e' None non provo ad eseguire il plugin
        parametri = plugin.get_param()
        key_values = []
        for parametro in parametri:
            key_values.append(parametro['key'])
        vet_param = [{key_values[0]:'192.168.0.0'}, 
                     {key_values[1] : 'forte'}]
        avvia_plugin(vet_param)