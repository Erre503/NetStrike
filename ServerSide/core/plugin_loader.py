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
    if nome_file.endswith('.ps1'):
        return 'ps1'
    return None

#crea una lista con tutti i file python all'interno della cartella
def lista_plugin(folder):  
    var = []
    for file in os.listdir(folder):
        if get_plugin_type(file) in ['sh', 'py', 'ps1']:
            var.append(file)
    return var

def cambiaNome(folder, nomeVecchio, nomeNuovo):
    try:
        trovato = False
        for file in os.listdir(folder):
            tipo = get_plugin_type(file)  # Ottieni il tipo del file
            if tipo and file[:-len(tipo)-1] == nomeVecchio:  
                vecchioFile = os.path.join(folder, file)
                nuovoFile = os.path.join(folder, nomeNuovo + "." + tipo)

                if os.path.exists(nuovoFile):
                    print("Errore: Il file "+nuovoFile+" esiste già.")
                    return False

                os.rename(vecchioFile, nuovoFile)
                print(f"File '{vecchioFile}' rinominato in '{nuovoFile}'")
                trovato = True
                break  # Interrompe il ciclo una volta trovato e rinominato il file

        if not trovato:
            print("Errore: Nessun file "+nomeVecchio+" trovato in "+folder)

        return trovato

    except Exception:
        print("Errore: impossibile rinominare il file.")
        return False


def avvia_plugin_ps1(nome_plugin, vet_param):
    try:
        percorso_file = folder / nome_plugin

        # Costruisci il comando con i parametri
        comando = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(percorso_file), "execute"]

        # Aggiungi i parametri a riga di comando
        for chiave, valore in vet_param.items():
            comando.append(f"-{chiave}")
            comando.append(str(valore))  # Converti il valore in stringa

        print(f"Eseguo comando PowerShell: {' '.join(comando)}")  # Debug

        # Esegui il comando
        subprocess.run(comando, check=True, env={**os.environ})
    except Exception as e:
        print(f"Errore nell'esecuzione del plugin PowerShell: {e}")



def avvia_plugin_bash(plugin, vet_param):
    try:
        # Imposta i parametri come variabili d'ambiente
        env_vars = {}
        for parametro, valore in vet_param.items():
            env_vars[parametro] = str(valore)  # Converte i parametri in stringa e li aggiunge al dizionario

        bash_path = "c:\Program Files\Git\bin\bash.exe"

        comando = [bash_path, plugin]  # Esegue il comando Bash

        # Esegui il comando Bash, passando le variabili d'ambiente
        subprocess.run(comando, check=True, env={**env_vars, **os.environ})  # Passa le variabili d'ambiente al comando
    except Exception:
        print("Errore nell'esecuzione del plugin Bash")


def avvia_plugin(nome_plugin, vet_param):
    tipo = get_plugin_type(nome_plugin)
    
    if tipo == 'py':
        try:
            modulo = importlib.import_module(nome_plugin[:-3])
            plugin_instance = modulo.Plugin()
            plugin_instance.set_param(vet_param)
            plugin_instance.execute()
        except Exception :
            print("Errore nell'importazione ed esecuzione del modulo Python")
    
    elif tipo == 'sh':
        percorso_file = folder / nome_plugin
        avvia_plugin_bash(percorso_file, vet_param)
    
    elif tipo == 'ps1':
        avvia_plugin_ps1(nome_plugin, vet_param)
    
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
    except Exception:
        print("Errore nella lettura del file")
        return False
    
def interfacciaPs1(percorso_file):
    try:
        with open(percorso_file, 'r', encoding='utf-8') as file:
            content = file.read()
            if "function get_param" not in content:
                print("Errore: La funzione 'get_param' non è presente nel plugin PowerShell.")
                return False
            if "function set_param" not in content:
                print("Errore: La funzione 'set_param' non è presente nel plugin PowerShell.")
                return False
            if "function execute" not in content:
                print("Errore: La funzione 'execute' non è presente nel plugin PowerShell.")
                return False
            return True
    except Exception:
        print("Errore nella lettura del file PowerShell")
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
            os.remove(percorso_file)
            return False
        
        # Ottieni la presunta classe Plugin
        classe_plugin = getattr(modulo, "Plugin")
        
        # Verifica che 'Plugin' sia una classe
        if not inspect.isclass(classe_plugin):
            print("Errore: 'Plugin' non è una classe.")
            os.remove(percorso_file)
            return False
        
        #verifica che tutti i metodi astratti siano implementati
        if isinstance(classe_plugin, abc.ABCMeta):
            if hasattr(classe_plugin, '__abstractmethods__') and len(classe_plugin.__abstractmethods__) > 0:
                print("Errore: La classe 'Plugin' è astratta e non implementa tutti i metodi richiesti.")
                os.remove(percorso_file)
                return False
        if verifica_sintassi_python(percorso_file):
            return True
        else:
            print(percorso_file)
            print("errore sintassi errata")
            os.remove(percorso_file)
            return False

    except Exception:
        print("Errore: il Plugin non appartiene alla classe 'Plugin' ")
        return False

def creaPluginSh(nome_file, contenuto):
    if not nome_file.endswith('.sh'):
        nome_file = nome_file + ".sh"
    
    folder = Path(__file__).resolve().parent.parent / "plugins"
    percorso_file = os.path.join(folder, nome_file)
    if nome_file in os.listdir(folder):
        print("Nome del File già presente")
        return False
    with open(percorso_file, "w", encoding="utf-8") as file:
        file.write(contenuto)
        print("File " + nome_file + " creato con successo nella cartella " + str(folder)) #stringa di debug
        print(" ") #crea uno spazio per rendere l'output più carino
    if interfacciaBash(percorso_file):
        if verifica_sintassi_bash(percorso_file):
            return True
        else:
            print("errore sintassi errata file sh")
            os.remove(percorso_file)
            return False
    else:
        print("il plugin non rispetta l'interfaccia")
        os.remove(percorso_file)
        return False

def creaPluginPs1(nome_file, contenuto):
    if not nome_file.endswith('.ps1'):
        nome_file = nome_file + ".ps1"

    folder = Path(__file__).resolve().parent.parent / "plugins"
    percorso_file = folder / nome_file

    if nome_file in os.listdir(folder):
        print("Nome del File già presente")
        return False

    with open(percorso_file, "w", encoding="utf-8") as file:
        file.write(contenuto)
        print("File "+nome_file+" creato con successo nella cartella "+str(folder))

    if interfacciaPs1(percorso_file):
        if verifica_sintassi_ps1(percorso_file):
            return True
        else:
            print("errore sintassi errata file ps1")
            os.remove(percorso_file)
            return False
    else:
        print("il plugin non rispetta l'interfaccia")
        os.remove(percorso_file)
        return False

    

def creaPlugin(nome_file, contenuto):
    if nome_file.endswith('.sh'):
        return creaPluginSh(nome_file, contenuto)
    if nome_file.endswith('.py'):
        return creaPluginPy(nome_file, contenuto)
    if nome_file.endswith('.ps1'):
        return creaPluginPs1(nome_file, contenuto)
    print("Il tipo di file non e' supportato")
    return None

def verifica_sintassi_python(percorso_file):
    try:
        subprocess.run(['python3', '-m', 'py_compile', percorso_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Il file ha una sintassi corretta.")
        return True
    except subprocess.CalledProcessError:
        print("Errore di sintassi nel file.")
        return False
    
def verifica_sintassi_bash(percorso_file):
    try:
        subprocess.run(['bash', '-n', percorso_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Il file ha una sintassi corretta.")
        return True
    except subprocess.CalledProcessError:
        print("Errore di sintassi nel file.")
        return False
    
def verifica_sintassi_ps1(percorso_file):
    try:
        comando = ["powershell", "-NoProfile", "-NonInteractive", "-Command", f"Get-Content '{str(percorso_file)}' | Out-String | Invoke-Expression"]
        subprocess.run(comando, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Il file PowerShell ha una sintassi corretta.")
        return True
    except subprocess.CalledProcessError:
        print("Errore di sintassi nel file")
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

def estraiParametriPs1(plugin):
    try:
        comando = ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(plugin), "get_param"]
        print(f"Comando eseguito: {' '.join(comando)}")
        parametri = subprocess.run(comando, capture_output=True, text=True, check=True)
        listaParametri = parametri.stdout.strip().split(", ")
        return listaParametri
    except Exception:
        print("Errore nell'estrazione dei parametri PowerShell")
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
    
    #esempio plugin
    contenuto = """

# File: esempio_plugin.ps1

param (
    [string]$ip,
    [string]$metodo,
    [string]$rangePorte,
    [int]$timeout
)

# Funzione per ottenere i parametri
function get_param {
    Write-Output "ip, metodo, rangePorte, timeout"
}

# Funzione principale di esecuzione
function execute {
    Write-Output "Esecuzione del plugin PowerShell con IP: $ip, Metodo: $metodo, RangePorte: $rangePorte, Timeout: $timeout"
}

# Controlla il comando ricevuto
if ($args[0] -eq "get_param") {
    get_param
} elseif ($args[0] -eq "execute") {
    execute
} else {
    Write-Output "Comando non riconosciuto."
}




    



    
"""

    
    creazione = creaPlugin(nome_plugin, contenuto)#salva il modulo(il file)
    if creazione:#se è None non provo ad eseguire il plugin
        if get_plugin_type(nome_plugin) == 'sh':
            plugin= folder / nome_plugin
            parametri = estraiParametriBash(plugin)  # Estrai i parametri dal file Bash
            print("Parametri del plugin Bash:" + str(parametri))
            vet_param = {
                "ip": "127.0.0.1", 
                "metodo": "tcp",   
                "rangePorte" : [1, 10] , 
                "timeout": 1         
            }
            avvia_plugin(nome_plugin, vet_param) 
        if get_plugin_type(nome_plugin) == 'py':
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
            avvia_plugin(nome_plugin, vet_param)
        if get_plugin_type(nome_plugin) == 'ps1':
            plugin = folder / nome_plugin
            parametri = estraiParametriPs1(plugin)
            print("Parametri del plugin PowerShell: " ,parametri)
            vet_param = {
                "ip": "127.0.0.1", 
                "metodo": "tcp",   
                "rangePorte" : [1, 10] , 
                "timeout": 1         
            }
            avvia_plugin(nome_plugin, vet_param)