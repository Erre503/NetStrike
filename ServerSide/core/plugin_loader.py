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

def get_plugin_extension(nome_file):
    if nome_file.endswith('.sh'):
        return '.sh'
    if nome_file.endswith('.py'):
        return '.py'
    return None

def lista_plugin(): #crea una lista con tutti i file python all'interno della cartella
    var = []
    for file in os.listdir(FOLDER):
        if get_plugin_type(file)=='sh':
            if file[:-3] and file.endswith('.sh'):
                var.append(file)
        else:
            if file[:-3] and file.endswith('.py'):
                var.append(file)
    return var

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
    try:
        os.remove(FOLDER / nome)
        return True
    except Exception:
        print("Errore: impossibile eliminare il nome del file")
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
    # Add .py extension if missing
    if not nome_file.endswith('.py'):
        nome_file += '.py'

    file = FOLDER / nome_file

    if os.path.isfile(file):
        return f"Error: File {nome_file} already exists"

    # Add required import
    full_content = f"from core.interfaccia_plugin import Interfaccia_Plugin\n\n{contenuto}"
        
    try:
        # Write to temporary file
        file.write_text(full_content, encoding="utf-8")
        
        # Validate through temporary file
        spec = importlib.util.spec_from_file_location(nome_file[:-3], file)
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)

        # Class validation
        if not hasattr(modulo, "Plugin"):
            os.remove(file)
            raise AttributeError("Missing 'Plugin' class")

        classe_plugin = modulo.Plugin

        if not inspect.isclass(classe_plugin):
            os.remove(file)
            raise TypeError("'Plugin' is not a class")

        if not issubclass(classe_plugin, Interfaccia_Plugin):
            os.remove(file)
            raise TypeError("Must inherit from Interfaccia_Plugin")

        if len(classe_plugin.__abstractmethods__) > 0:
            os.remove(file)
            raise NotImplementedError(f"Unimplemented abstract methods: {classe_plugin.__abstractmethods__}")

        return f"Plugin created successfully: {nome_file}"

    except Exception as e:            
        # Temporary file is automatically deleted with the directory
        return f"Validation failed: {e}"

def creaPluginSh(nome_file, contenuto):
    if not nome_file.endswith('.sh'):
        nome_file = nome_file + ".sh"
    if nome_file in os.listdir(FOLDER):
        return False
    if interfacciaBash(contenuto):
        percorso_file = os.path.join(FOLDER, nome_file)
        with open(percorso_file, "w", encoding="utf-8") as file:
            file.write(contenuto)
        return True
    else:
        return False
    
    



def creaPlugin(nome_file, contenuto):
    if nome_file.endswith('.sh'):
        return creaPluginSh(nome_file, contenuto)
    if nome_file.endswith('.py'):
        return creaPluginPy(nome_file, contenuto)
    print("Il tipo di file non e' supportato")
    return None


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
        percorso_file = FOLDER / nome_plugin

        res['log'] = avvia_plugin_bash(percorso_file, vet_param)  # Esegui il plugin Bash
        res['status'] = 'finished'
    else:
        res['log'] = "Tipo di plugin non supportato."
        res['status'] = failed
    return res


