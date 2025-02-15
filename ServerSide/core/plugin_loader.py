import os #libreria per poter lavorare con le cartelle e file dell'applicazione
import importlib #va a sostituire la funzione manuale di import dato che non siamo a conoscenza dei nomi dei file 
                 #e per rendere l'importazione dinamica
import sys  #serve per modificare a riga 38 i percorsi da cui prendere i file python
import abc
import inspect #serve per vedere i parametri
import subprocess #serve per i file bash
from pathlib import Path #serve per ottenere il riferimento al percorso del file corrente

def get_plugin_type(nome_file):
    if nome_file.endswith('.sh'):
        return 'sh'
    if nome_file.endswith('.py'):
        return 'py'
    return None

def lista_plugin(folder): #crea una lista con tutti i file python all'interno della cartella
    var = []
    for file in os.listdir(folder):
        if get_plugin_type(file)=='sh':
            if file[:-3] and file.endswith('.sh'):
                var.append(file)
        else:
            if file[:-3] and file.endswith('.py'):
                var.append(file)
    return var

def cambiaNome(folder, nomeVecchio, nomeNuovo): #dato il nome del file da rinominare e quello nuovo, rinomina il file
    try:
        for file in os.listdir(folder):
            if get_plugin_type(file)=='sh':
                if file[:-3]==nomeVecchio:
                    vecchioFile= os.path.join(folder, nomeVecchio+".sh")
                    nuovoFile= os.path.join(folder, nomeNuovo+".sh")
                    os.rename(vecchioFile,nuovoFile)
            else:
                if file[:-3]==nomeVecchio:
                    vecchioFile= os.path.join(folder, nomeVecchio+".py")
                    nuovoFile= os.path.join(folder, nomeNuovo+".py")
                    os.rename(vecchioFile,nuovoFile)
    except Exception:
        print("Errore: impossibile rinominare il nome del file")


def avvia_plugin(nome_plugin, vet_param, type):
    # Se il plugin è Python
    if type == 'py':
        try:
            # Importa dinamicamente il modulo Python
            modulo = importlib.import_module(nome_plugin[:-3])  # Rimuove ".py"
            plugin_instance = modulo.Plugin()  # Crea l'istanza del plugin
            plugin_instance.set_param(vet_param)  # Imposta i parametri
            plugin_instance.execute()  # Esegui il plugin
        except Exception as e:
            print("Errore nell'importazione ed esecuzione del modulo Python")
    
    # Se il plugin è Bash
    elif type == 'sh':
        # Verifica che il file esista
        percorso_file = folder / nome_plugin
        avvia_plugin_bash(percorso_file, vet_param)  # Esegui il plugin Bash
    
    else:
        print("Tipo di plugin non supportato.")

def interfacciaBash(percorso_file):
    try:
        with open(percorso_file, 'r') as file: #apro il file e vedo se all'interno ci sono le funzioni richieste
            content = file.read()
            if "function set_param" not in content:
                print("Errore: La funzione 'set_param' non è presente nel plugin Bash.")
                return False
            if "function get_param" not in content:
                print("Errore: La funzione 'get_param' non è presente nel plugin Bash.")
                return False
            if "function execute" not in content:
                print("Errore: La funzione 'execute' non è presente nel plugin Bash.")
                return False
            return True
    except Exception as e:
        print("Errore nella lettura del file")
        return False

def estraiParametriBash(plugin):
    try:
        comando = ["bash", plugin, "get_param"]  
        parametri = subprocess.run(comando, capture_output=True, text=True, check=True)
        listaParametri = parametri.stdout.strip().split(", ")  
        return listaParametri
    except Exception:
        print("Errore nell'estrazione dei parametri Bash")
        return None


def avvia_plugin_bash(plugin, vet_param):
    try:
        # Imposta i parametri come variabili d'ambiente
        env_vars = {}
        for parametro, valore in vet_param.items():
            env_vars[parametro] = str(valore)  # Converte i parametri in stringa e li aggiunge al dizionario

        comando = ["bash", plugin]  # Esegue il comando Bash

        # Esegui il comando Bash, passando le variabili d'ambiente
        subprocess.run(comando, check=True, env={**env_vars, **os.environ})  # Passa le variabili d'ambiente al comando
    except Exception:
        print("Errore nell'esecuzione del plugin Bash")

def verifica_sintassi_python(percorso_file):
    try:
        result = subprocess.run(['python3', '-m', 'py_compile', percorso_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Il file ha una sintassi corretta.")
        return True
    except subprocess.CalledProcessError:
        print("Errore di sintassi nel file.")
        return False



def creaPluginPy(nome_file, contenuto):

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
        return None

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
            return None
        
        # Ottieni la presunta classe Plugin
        classe_plugin = getattr(modulo, "Plugin")
        
        # Verifica che 'Plugin' sia una classe
        if not inspect.isclass(classe_plugin):
            print("Errore: 'Plugin' non è una classe.")
            return None
        
        #verifica che tutti i metodi astratti siano implementati
        if isinstance(classe_plugin, abc.ABCMeta):
            if hasattr(classe_plugin, '__abstractmethods__') and len(classe_plugin.__abstractmethods__) > 0:
                print("Errore: La classe 'Plugin' è astratta e non implementa tutti i metodi richiesti.")
                return None
        if verifica_sintassi_python(percorso_file):
            return classe_plugin
        else:
            print("errore sintassi errata")
            return None

    except Exception:
        print("Errore: il Plugin non appartiene alla classe 'Plugin' ")
        return None

def verifica_sintassi_bash(percorso_file):
    try:
        subprocess.run(['bash', '-n', percorso_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Il file ha una sintassi corretta.")
        return True
    except subprocess.CalledProcessError:
        print("Errore di sintassi nel file.")
        return False


def creaPluginSh(nome_file, contenuto):
    if not nome_file.endswith('.sh'):
        nome_file = nome_file + ".sh"
    
    folder = Path(__file__).resolve().parent.parent / "plugins"
    percorso_file = os.path.join(folder, nome_file)
    if nome_file in os.listdir(folder):
        print("Nome del File già presente")
        return None
    with open(percorso_file, "w", encoding="utf-8") as file:
        file.write(contenuto)
        print("File " + nome_file + " creato con successo nella cartella " + str(folder)) #stringa di debug
        print(" ") #crea uno spazio per rendere l'output più carino
    if interfacciaBash(percorso_file):
        if verifica_sintassi_bash(percorso_file):
            return percorso_file
        else:
            print("errore sintassi errata")
            return None
    else:
        print("il plugin non rispetta l'interfaccia")
        return None

    

def creaPlugin(nome_file, contenuto):
    if nome_file.endswith('.sh'):
        return creaPluginSh(nome_file, contenuto)
    if nome_file.endswith('.py'):
        return creaPluginPy(nome_file, contenuto)
    print("Il tipo di file non e' supportato")
    return None



if(__name__ == "__main__"):
    print("Quale file PY vuoi eseguire?")
    folder = Path(__file__).resolve().parent.parent / "plugins"  # assegna il percorso della cartella basandosi su quello del plugin loader
                                                                 #(Path(__file__).resolve()) per avere il percorso assoluto
    sys.path.append(str(folder))  #aggiunge la cartella folder ai percorsi da cui vengono importati i file python
    # Carica i nomi dei plugin presenti
    for i in lista_plugin(folder): 
        print(i)
    nome_plugin = input() #il nome per fare i test è dato in input
    type = "py"
    
    #esempio plugin
    contenuto = """import socket  # serve per poter creare delle connessione con ad esempio udp e tcp
from interfaccia_plugin import Interfaccia_Plugin


class Plugin(Interfaccia_Plugin):
    #valori standard 
    ip = "127.0.0.1"  
    rangePorte = [1, 65535] 
    tipoScansione = 'TCP' 
    timeout = 1

    @classmethod
    def execute(cls):
        print("Esecuzione della scansione per l'IP " + cls.ip + ", Tipo:" + cls.metodo)
        porteAperte = scan_ports(cls.ip, cls.rangePorte, cls.metodo, cls.timeout)
        print("Porte aperte: " + str(porteAperte))


    @classmethod
    def get_param(cls):
        vet_param = [
            {'key': 'ip', 'description': 'Indirizzo IP da scansionare'},
            {'key': 'metodo', 'description': 'Metodo di scansione: TCP o UDP'},
            {'key': 'rangePorte', 'description': 'Range delle porte da scansionare'},
            {'key': 'timeout', 'description': 'Tempo massimo per tentare la connessione'}
        ]
        return vet_param
    
    @classmethod
    def set_param(cls, vet_param):
        cls.ip = vet_param['ip']
        cls.metodo = vet_param['metodo']
        cls.rangePorte = vet_param['rangePorte']
        cls.timeout = vet_param['timeout'] 
        return True
    

def scan_tcp(ip, porta, timeout):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Crea un oggetto TCP(i parametri indicano che e' ipv4 e tcp)
        sock.settimeout(timeout)  #funzione che imposta un tempo massimo per provare a connettersi alla porta
        result = sock.connect_ex((ip, porta))  # salva il tentativo di connessione nella porta in una variabile
        if result == 0:
            return "Porta " + str(porta) + " aperta"  # se e' 0 la connessione con la porta e' riuscita
        else:
            return "Porta " + str(porta) + " chiusa"
    except socket.error:
        return "Errore di connessione alla porta " + str(porta)
    finally:
        sock.close()  # Interrompe la connessione perche' non piu' necessaria


def scan_udp(ip, porta, timeout):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # dgram serve per avere un oggetto udp
        #sock.bind(('127.0.0.1', 12345))
        sock.settimeout(timeout) 
        sock.sendto(b'Hello', (ip, porta))  # invio 1 byte vuoto per verificare se la porta e' aperta
        sock.recvfrom(1024)  # funzione per ricevere il pacchetto ( parametro indica il massimo di byte ricevibili in 1 chiamata)
        return "Porta " + str(porta) + " aperta"
    except socket.error:
        return "Errore di connessione alla porta " + str(porta) + " (probabilmente chiusa)" #in caso scada il time out si da per chiusa la porta
    finally:
        sock.close()  


def scan_ports(ip, rangePorte, tipoScansione, timeout):
    porteAperte = [] 
    for porta in range(rangePorte[0], rangePorte[1] + 1): #il range esclude l'ultima porta, per questo +1
        if tipoScansione.lower() == 'tcp':  
            resScansione = scan_tcp(ip, porta, timeout)  
        elif tipoScansione.lower() == 'udp':  
            resScansione = scan_udp(ip, porta, timeout) 
        else:
            return "Erroe: il tipo di scansione non e' ne tcp ne udp"  # Se il tipo di scansione non è valido, restituisce un errore
        
        print(resScansione)  # Stampa il risultato della scansione per debug
        if "aperta" in resScansione:  
            porteAperte.append(porta)  
    
    return porteAperte 


    

    """
    
    plugin = creaPlugin(nome_plugin, contenuto)#salva il modulo(il file)
    if nome_plugin is not None:#se è None non provo ad eseguire il plugin
        if type == 'sh':
            plugin= folder / nome_plugin
            parametri = estraiParametriBash(plugin)  # Estrai i parametri dal file Bash
            print("Parametri del plugin Bash:" + str(parametri))
            vet_param = {
                "ip": "127.0.0.1", 
                "metodo": "tcp",   
                "startPort": "1",  
                "endPort": "208",  
                "timeout": 1         
            }
            avvia_plugin(nome_plugin, vet_param, type) 
        if type == 'py':
            modulo = importlib.import_module(nome_plugin[:-3])  # Rimuove ".py"
            plugin = modulo.Plugin()
            parametri = plugin.get_param()
            key_values = []
            for parametro in parametri:
                key_values.append(parametro['key'])
            vet_param = {
                        key_values[0]: '127.0.0.1',        # ip
                        key_values[1]: 'tcp',              # metodo di scansione
                        key_values[2]: [1,10],         # rangePorte
                        key_values[3]: 1                   # timeout
            }
            avvia_plugin(nome_plugin, vet_param, type)