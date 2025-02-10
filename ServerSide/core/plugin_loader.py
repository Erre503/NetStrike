import os #libreria per poter lavorare con le cartelle e file dell'applicazione
import importlib #va a sostituire la funzione manuale di import dato che non siamo a conoscenza dei nomi dei file 
                 #e per rendere l'importazione dinamica
import sys  #serve per modificare a riga 38 i percorsi da cui prendere i file python
import abc
import inspect #serve per vedere i parametri

from pathlib import Path #serve per ottenere il riferimento al percorso del file corrente

def lista_plugin(folder): #crea una lista con tutti i file python all'interno della cartella
    var = []
    for file in os.listdir(folder):
        if file[:-3] and file.endswith('.py'):
            var.append(file)
    return var

def avvia_plugin(plugin, vet_param): #funzione del diagramma richiesta per avviare il plugin

    plugin.set_param(vet_param) #setta i parametri della funzione execute(passati in futuro dall'interfaccia)

    plugin.execute() #eseguo il 'main' del plugin

    return 

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
        return "Nome del File già presente"

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
            return "Errore: Il file non contiene nessun elemento 'Plugin'."
        
        # Ottieni la presunta classe Plugin
        classe_plugin = getattr(modulo, "Plugin")

        # Verifica che 'Plugin' sia una classe
        if not inspect.isclass(classe_plugin):
            return "Errore: 'Plugin' non è una classe."
        
        #verifica che tutti i metodi astratti siano implementati
        if isinstance(classe_plugin, abc.ABCMeta):
            if hasattr(classe_plugin, '__abstractmethods__') and len(classe_plugin.__abstractmethods__) > 0:
                print("Errore: La classe 'Plugin' è astratta e non implementa tutti i metodi richiesti.")

        return classe_plugin

    except Exception:
        return "Errore: il Plugin non appartiene alla classe 'Plugin' "


if(__name__ == "__main__"):
    print("Quale file PY vuoi eseguire?")
    folder = Path(__file__).resolve().parent.parent / "plugins"  # assegna il percorso della cartella basandosi su quello del plugin loader
                                                                 #(Path(__file__).resolve()) per avere il percorso assoluto
    sys.path.append(str(folder))  #aggiunge la cartella folder ai percorsi da cui vengono importati i file python
    # Carica i nomi dei plugin presenti
    for i in lista_plugin(folder): 
        print(i)
    nome_plugin = input() #il nome per fare i test è dato in input
    
    #esempio plugin
    contenuto = """from interfaccia_plugin import Interfaccia_Plugin

class Plugin(Interfaccia_Plugin):
    ip = ""
    metodo = ""

    @classmethod
    def execute(cls):
        print(cls.ip)
        print(cls.metodo)

    @classmethod
    def get_param(cls):
        vet_param = [{'key': 'ip', 'description': 'Questo parametro serve per indicare l indirizzo ip tramite stringa. es: -197.168.0.1-'}, 
                     {'key': 'metodo', 'description': 'Questo parametro serve per specificare il tipo di attacco che vuoi eseguire puoi scegliere tra -forte-, -debole-, -massimo-'}]
        return vet_param

    
    @classmethod
    def set_param(cls, vet_param):
        cls.ip = vet_param['ip']
        cls.metodo = vet_param['metodo']
        return True
    """
    
    plugin = creaPlugin(nome_plugin, contenuto)#salva il modulo(il file)
    if(plugin!=None):#se è None non provo ad eseguire il plugin
        parametri = plugin.get_param()
        key_values = []
        for parametro in parametri:
            key_values.append(parametro['key'])
        vet_param = {key_values[0]:'192.168.0.0', key_values[1] : 'forte'}
        avvia_plugin(plugin, vet_param)