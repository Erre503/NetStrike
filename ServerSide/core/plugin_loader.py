import os #libreria per poter lavorare con le cartelle e file dell'applicazione
import importlib #va a sostituire la funzione manuale di import dato che non siamo a conoscenza dei nomi dei file
                 #e per rendere l'importazione dinamica
import sys  #serve per modificare a riga 38 i percorsi da cui prendere i file python
import abc
import inspect #serve per vedere i parametri
import subprocess #serve per i file bash
from pathlib import Path #serve per ottenere il riferimento al percorso del file corrente
from datetime import datetime
import platform

FOLDER = Path(__file__).resolve().parent.parent / "plugins"

def process_plugin_name(nome_file):
    processed = nome_file.rsplit('.', 1)
    return processed[0], processed[1]

def rinomina_plugin(nomeVecchio, nomeNuovo): #dato il nome del file da rinominare e quello nuovo, rinomina il file
    try:
        vecchio_path = FOLDER / nomeVecchio
        nuovo_path = FOLDER / nomeNuovo
        vecchio_path.rename(nuovo_path)
        return True
    except Exception:
        print("Errore: impossibile rinominare il nome del file")
        return False

def elimina_plugin(nome):
    file_path = FOLDER / nome

    try:
        os.remove(file_path)
        return True
    except FileNotFoundError:
        print(f"Errore: il file '{file_path}' non esiste.")
        return False
    except PermissionError:
        print(f"Errore: permesso negato per eliminare '{file_path}'.")
        return False
    except Exception as e:
        print(f"Errore: impossibile eliminare il file '{file_path}'. Dettagli: {e}")
        return False




def estraiParametriBash(plugin):
    try:
        comando = ["bash", plugin, "get_param"]
        parametri = subprocess.run(comando, capture_output=True, text=True, check=True)
        listaParametri = parametri.stdout.strip().split(", ")
        return listaParametri
    except Exception:
        return f"Errore nell'estrazione dei parametri Bash"

def interfacciaBash(content):
    functions_to_check = ['set_param', 'get_param', 'execute']
    for x in functions_to_check:
        if x not in content:
            return False
    return True

def avvia_plugin_bash(plugin, vet_param):
    try:
        # Prepare the command to execute the Bash script
        if platform.system() == "Windows":
            shell = "powershell"
            comando = f"& {{ {comando} }}"
        else:
            shell = "/bin/bash"
            comando = f"bash {plugin}"

        # Prepare the environment variables
        env_vars = {**os.environ, **vet_param}  # Combine existing and new environment variables

        # Execute the command in a shell
        ret = subprocess.run(comando, shell=True, check=True, env=env_vars, executable=shell, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return ret.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"Errore nell'esecuzione del plugin Bash: {e}"
    except Exception as e:
        return f"Errore generico: {e}"


def creaPluginPy(nome_file, contenuto):
    file_name = nome_file[:-3]
    file = FOLDER / nome_file

    if file.is_file():
        return False, None

    # Add required import
    full_content = f"from core.interfaccia_plugin import Interfaccia_Plugin \n\n{contenuto}"
        
    try:
        # Write to the file
        file.write_text(full_content)
        
        # Validate through the temporary file
        spec = importlib.util.spec_from_file_location(file_name, file)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)

        # Class validation
        if not hasattr(modulo, "Plugin"):
            raise AttributeError("Missing 'Plugin' class")

        classe_plugin = modulo.Plugin

        if not inspect.isclass(classe_plugin):
            raise TypeError("'Plugin' is not a class")

        if not issubclass(classe_plugin, modulo.Interfaccia_Plugin):  # Use modulo to access Interfaccia_Plugin
            raise TypeError("Must inherit from Interfaccia_Plugin")

        if len(classe_plugin.__abstractmethods__) > 0:
            raise NotImplementedError(f"Unimplemented abstract methods: {classe_plugin.__abstractmethods__}")

        # Import the module dynamically
        plugin_module = importlib.import_module('plugins.' + file_name)  # Remove ".py"
        plugin_instance = plugin_module.Plugin()  # Create the plugin instance
        params = plugin_instance.get_param()
        print(f"PARAMS PLUGLOADER: {params}")
        return True, params # Return success

    except (AttributeError, TypeError, NotImplementedError) as e:
        print(f"Validation failed: {e}")  # DEBUG
        if file.is_file():
            os.remove(file)
        return False, None  # Return failure

    except Exception as e:
        print(f"An unexpected error occurred: {e}")  # DEBUG
        if file.is_file():
            os.remove(file)
        return False, None  # Return failure

def creaPluginSh(nome_file, contenuto):
    if nome_file in os.listdir(FOLDER):
        return False, None
    if interfacciaBash(contenuto):
        percorso_file = os.path.join(FOLDER, nome_file)
        with open(percorso_file, "w", encoding="utf-8") as file:
            file.write(contenuto)
        return True, None
    else:
        if file.is_file():
            os.remove(file)
        return False, None
    
    



def creaPlugin(nome_file, contenuto):
    if nome_file.endswith('.sh'):
        return creaPluginSh(nome_file, contenuto)
    if nome_file.endswith('.py'):
        return creaPluginPy(nome_file, contenuto)
    print("Il tipo di file non e' supportato")
    return None


def avvia_plugin(nome_plugin, vet_param):
    res = {}
    res['datetime'] = datetime.now()
    file_name, extension = process_plugin_name(nome_plugin)
    if extension == 'py':
        try:
            # Importa dinamicamente il modulo Python
            modulo = importlib.import_module('plugins.'+file_name)  # Rimuove ".py"
            plugin_instance = modulo.Plugin()  # Crea l'istanza del plugin
            plugin_instance.set_param(vet_param)
            res['log'] = plugin_instance.execute()  # Esegui il plugin
            res['status'] = 'finished'


        except Exception as e:
            res['log'] = f"Errore nell'importazione ed esecuzione del modulo Python {nome_plugin}: {e}"
            res['status'] = 'failed'

    # Se il plugin è Bash
    elif extension == 'sh':
        # Verifica che il file esista
        percorso_file = FOLDER / nome_plugin

        res['log'] = avvia_plugin_bash(percorso_file, vet_param)  # Esegui il plugin Bash
        res['status'] = 'finished'
    else:
        res['log'] = "Tipo di plugin non supportato."
        res['status'] = failed
    return res