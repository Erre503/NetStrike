import os #libreria per poter lavorare con le cartelle e file dell'applicazione
import importlib #va a sostituire la funzione manuale di import dato che non siamo a conoscenza dei nomi dei file
                 #e per rendere l'importazione dinamica
import sys  #serve per modificare a riga 38 i percorsi da cui prendere i file python
import abc
import inspect #serve per vedere i parametri
import subprocess #serve per i file bash
from pathlib import Path #serve per ottenere il riferimento al percorso del file corrente
from datetime import datetime

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
    res = {}
    res['datetime'] = datetime.now()
    if type == 'py':
        try:
            # Importa dinamicamente il modulo Python
            modulo = importlib.import_module('plugins.'+nome_plugin[:-3])  # Rimuove ".py"
            plugin_instance = modulo.Plugin()  # Crea l'istanza del plugin
            plugin_instance.set_param(vet_param)  # Imposta i parametri


            res['log'] = plugin_instance.execute()  # Esegui il plugin
            res['status'] = 'finished'


        except Exception as e:
            res['log'] = f"Errore nell'importazione ed esecuzione del modulo Python {nome_plugin}: {e}"
            res['status'] = 'failed'

    # Se il plugin è Bash
    elif type == 'sh':
        # Verifica che il file esista
        percorso_file = folder / nome_plugin

        res['log'] = avvia_plugin_bash(percorso_file, vet_param)  # Esegui il plugin Bash
        res['status'] = 'finished'
    else:
        res['log'] = "Tipo di plugin non supportato."
        res['status'] = failed
    return res

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
        print(f"Errore nell'estrazione dei parametri Bash")
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


def creaPluginPy(nome_file, contenuto):
    # Add .py extension if missing
    if not nome_file.endswith('.py'):
        nome_file += '.py'

    # Path to plugins directory
    folder = Path(__file__).resolve().parent.parent / "plugins"
    percorso_file = folder / nome_file

    # Check for existing file first
    if percorso_file.exists():
        print(f"Error: File {nome_file} already exists")
        return None

    # Add required import
    full_content = f"from core.interfaccia_plugin import Interfaccia_Plugin\n\n{contenuto}"

    # Use temporary directory for validation
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file = Path(temp_dir) / nome_file
        
        try:
            # Write to temporary file
            temp_file.write_text(full_content, encoding="utf-8")
            
            # Validate through temporary file
            spec = importlib.util.spec_from_file_location(nome_file[:-3], temp_file)
            modulo = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modulo)

            # Class validation
            if not hasattr(modulo, "Plugin"):
                raise AttributeError("Missing 'Plugin' class")

            classe_plugin = modulo.Plugin

            if not inspect.isclass(classe_plugin):
                raise TypeError("'Plugin' is not a class")

            if not issubclass(classe_plugin, Interfaccia_Plugin):
                raise TypeError("Must inherit from Interfaccia_Plugin")

            if len(classe_plugin.__abstractmethods__) > 0:
                raise NotImplementedError(f"Unimplemented abstract methods: {classe_plugin.__abstractmethods__}")

            # Only move to final location if all validations pass
            shutil.move(str(temp_file), str(folder))
            print(f"Plugin created successfully: {nome_file}")
            return classe_plugin

        except Exception as e:
            print(f"Validation failed: {e}")
            # Temporary file is automatically deleted with the directory
            return None

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
        return percorso_file
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
    type = "sh"

    #esempio plugin
    contenuto = """#!/bin/bash

# Funzione per impostare i parametri
function set_param {
    ip=$1
    metodo=$2
    startPort=$3
    endPort=$4
    timeout=$5
}

# Funzione per ottenere i parametri
function get_param {
    echo "ip, metodo, startPort, endPort, timeout"
}

# Funzione principale di esecuzione del programma
function execute {
    echo "Esecuzione della scansione per l'IP $ip, Metodo: $metodo"
    echo "Intervallo delle porte: $startPort a $endPort"
    echo "Timeout: $timeout"

    # Variabile per memorizzare le porte aperte
    open_ports=""

    # Simula la scansione delle porte
    for (( port=$startPort; port<=$endPort; port++ )); do
        if [[ $metodo == "tcp" ]]; then
            nc -zv -w $timeout $ip $port &>/dev/null
            if [ $? -eq 0 ]; then
                open_ports+="$port (TCP), "
            fi
        elif [[ $metodo == "udp" ]]; then
            nc -zvu -w $timeout $ip $port &>/dev/null
            if [ $? -eq 0 ]; then
                open_ports+="$port (UDP), "
            fi
        else
            echo "Metodo non valido. Usa 'tcp' o 'udp'."
            exit 1
        fi
    done

    # Rimuove l'ultima virgola e spazio (se ci sono porte aperte)
    if [ -n "$open_ports" ]; then
        open_ports=${open_ports%, }
        echo "Le porte aperte sono: $open_ports"
    else
        echo "Nessuna porta aperta trovata."
    fi
}

# Esecuzione dello script
echo "Inizializzo il plugin Bash..."
set_param "$ip" "$metodo" "$startPort" "$endPort" "$timeout"  # Passa i parametri da Python
execute


    """

    #plugin = creaPlugin(nome_plugin, contenuto)#salva il modulo(il file)
    if nome_plugin is not None:#se è None non provo ad eseguire il plugin
        if type == 'sh':
            plugin= folder / nome_plugin
            parametri = estraiParametriBash(plugin)  # Estrai i parametri dal file Bash
            print("Parametri del plugin Bash:" + str(parametri))
            vet_param = {
                "ip": "172.20.0.40",
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
